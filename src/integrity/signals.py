# DONE

# src/integrity/signals.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Union

import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import ks_2samp


# ----------------------------
# Helpers
# ----------------------------
def _finite(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return x[np.isfinite(x)]


def _clip_by_quantiles(x: np.ndarray, q: Tuple[float, float] = (0.005, 0.995)) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return x
    lo, hi = np.quantile(x, q)
    if not np.isfinite(lo) or not np.isfinite(hi) or lo >= hi:
        return x
    return np.clip(x, lo, hi)


def _hist_1d_with_edges(x: np.ndarray, edges: np.ndarray) -> np.ndarray:
    """
    Stable 1D histogram -> probability mass function using fixed bin edges.
    """
    x = _finite(x)
    nb = int(len(edges) - 1)
    if x.size == 0 or nb <= 0:
        h = np.ones(max(nb, 1), dtype=float)
        return h / h.sum()

    h, _ = np.histogram(x, bins=edges, density=True)
    h = h.astype(float) + 1e-12
    return h / h.sum()


def _safe_edges_from_ref(x_ref: np.ndarray, bins: int) -> Optional[np.ndarray]:
    """
    Build histogram bin edges from reference data only (recommended for drift).
    Returns None if degenerate.
    """
    x_ref = _finite(x_ref)
    if x_ref.size == 0:
        return None
    if np.allclose(x_ref.min(), x_ref.max()):
        return None
    try:
        return np.histogram_bin_edges(x_ref, bins=bins)
    except Exception:
        return None


def _degenerate_fallback_drift(x_ref: np.ndarray, x_cur: np.ndarray) -> float:
    """
    Fallback drift score when histogram edges cannot be defined reliably from reference.
    We avoid returning a hard 0.0 in cases where the current distribution differs.

    Strategy:
      - If both are empty or both are (near) constant with similar mean -> 0
      - Else: use a bounded mean-shift proxy: tanh(|mean_cur - mean_ref|)
    """
    xr = _finite(x_ref)
    xc = _finite(x_cur)
    if xr.size == 0 or xc.size == 0:
        return 0.0

    mr = float(np.mean(xr))
    mc = float(np.mean(xc))
    # If both are near-constant and means match, call it no drift
    if np.allclose(float(np.min(xr)), float(np.max(xr))) and np.allclose(float(np.min(xc)), float(np.max(xc))):
        return 0.0 if np.allclose(mr, mc) else float(np.tanh(abs(mc - mr)))

    # General bounded proxy
    return float(np.tanh(abs(mc - mr)))


# ----------------------------
# 1) Feature-wise JSD (core)
# ----------------------------
def jsd_feature_shift(
    X_ref: np.ndarray,
    X_cur: np.ndarray,
    bins: int = 40,
    clip_q: Tuple[float, float] = (0.005, 0.995),
) -> float:
    """
    Mean Jensen–Shannon divergence across dimensions using 1D histograms.

    Key detail (important for correctness):
      - Uses *shared bin edges* per feature, derived from the reference distribution.

    Notes:
      - Robust to heavy tails via quantile clipping
      - Stable if a feature becomes (near) constant
      - Returns JS divergence (not distance)
    """
    X_ref = np.asarray(X_ref, dtype=float)
    X_cur = np.asarray(X_cur, dtype=float)

    if X_ref.ndim != 2 or X_cur.ndim != 2:
        raise ValueError("X_ref and X_cur must be 2D arrays")
    if X_ref.shape[1] != X_cur.shape[1]:
        raise ValueError("Feature dimension mismatch")

    jsds = []
    for j in range(X_ref.shape[1]):
        xr = _clip_by_quantiles(_finite(X_ref[:, j]), clip_q)
        xc = _clip_by_quantiles(_finite(X_cur[:, j]), clip_q)

        edges = _safe_edges_from_ref(xr, bins=bins)
        if edges is None:
            # Don't blindly set to 0: if current differs, reflect it with a bounded proxy
            jsds.append(_degenerate_fallback_drift(xr, xc))
            continue

        p = _hist_1d_with_edges(xr, edges)
        q = _hist_1d_with_edges(xc, edges)
        # jensenshannon returns sqrt(JS divergence) by default -> square it
        jsds.append(float(jensenshannon(p, q) ** 2))

    return float(np.mean(jsds)) if jsds else 0.0


# ----------------------------
# 2) MMD (RBF) for covariate shift
# ----------------------------
@dataclass(frozen=True)
class MMDConfig:
    max_samples: int = 512                 # subsample per set to control O(n^2)
    gamma: Union[str, float] = "median"    # "median" or numeric
    rng_seed: int = 0                      # for reproducible subsampling
    max_pairs: int = 4096                  # for median heuristic


def _rbf_kernel(X: np.ndarray, Y: np.ndarray, gamma: float) -> np.ndarray:
    # ||x-y||^2 = x^2 + y^2 - 2xy
    X2 = np.sum(X * X, axis=1, keepdims=True)
    Y2 = np.sum(Y * Y, axis=1, keepdims=True).T
    D2 = X2 + Y2 - 2.0 * (X @ Y.T)
    return np.exp(-gamma * np.maximum(D2, 0.0))


def _median_heuristic_gamma(
    X: np.ndarray,
    rng: np.random.Generator,
    max_pairs: int = 4096,
) -> float:
    """
    Median heuristic for RBF:
      sigma^2 ~ median(||x - x'||^2) / 2
      gamma  = 1 / (2*sigma^2)  ->  gamma ~ 1 / median(||x - x'||^2)

    We use the common convention:
      gamma = 1 / (2 * median(d2))

    Uses random pairs and enforces i != j to avoid zero distances.
    """
    n = int(X.shape[0])
    if n < 2:
        return 1.0

    # Bounded number of pairs (fast + stable)
    m = min(int(max_pairs), max(2, 10 * n))
    i = rng.integers(0, n, size=m)
    j = rng.integers(0, n, size=m)

    same = (i == j)
    if np.any(same):
        j[same] = (j[same] + 1) % n

    d2 = np.sum((X[i] - X[j]) ** 2, axis=1)
    d2 = d2[np.isfinite(d2)]
    d2 = d2[d2 > 0]

    med = float(np.median(d2)) if d2.size else 1.0
    return 1.0 / (2.0 * max(med, 1e-12))


def mmd_rbf(X_ref: np.ndarray, X_cur: np.ndarray, cfg: Optional[MMDConfig] = None) -> float:
    """
    Unbiased MMD^2 with RBF kernel.

    Returns:
      MMD (sqrt of MMD^2) as float for interpretability.

    Uses subsampling to control O(n^2).
    """
    if cfg is None:
        cfg = MMDConfig()

    X_ref = np.asarray(X_ref, dtype=float)
    X_cur = np.asarray(X_cur, dtype=float)

    rng = np.random.default_rng(int(cfg.rng_seed))

    def _subsample(X: np.ndarray) -> np.ndarray:
        n = int(X.shape[0])
        if n <= int(cfg.max_samples):
            return X
        idx = rng.choice(n, size=int(cfg.max_samples), replace=False)
        return X[idx]

    X = _subsample(X_ref)
    Y = _subsample(X_cur)

    n = int(X.shape[0])
    m = int(Y.shape[0])
    if n < 2 or m < 2:
        return 0.0

    # gamma selection
    if isinstance(cfg.gamma, str) and cfg.gamma.lower().strip() == "median":
        Z = np.vstack([X, Y])
        gamma = _median_heuristic_gamma(Z, rng=rng, max_pairs=int(cfg.max_pairs))
    else:
        gamma = float(cfg.gamma)

    Kxx = _rbf_kernel(X, X, gamma)
    Kyy = _rbf_kernel(Y, Y, gamma)
    Kxy = _rbf_kernel(X, Y, gamma)

    # Unbiased MMD^2:
    np.fill_diagonal(Kxx, 0.0)
    np.fill_diagonal(Kyy, 0.0)

    mmd2 = (Kxx.sum() / (n * (n - 1))) + (Kyy.sum() / (m * (m - 1))) - (2.0 * Kxy.mean())
    mmd2 = float(max(mmd2, 0.0))
    return float(np.sqrt(mmd2))


# ----------------------------
# 3) Score drift (model output distribution drift)
# ----------------------------
def score_drift_jsd(
    scores_ref: np.ndarray,
    scores_cur: np.ndarray,
    bins: int = 40,
    clip_q: Tuple[float, float] = (0.005, 0.995),
) -> float:
    """
    JSD between score distributions (e.g., decision_function outputs).

    Recommended usage:
      - scores_ref = model scores on *clean* evaluation set
      - scores_cur = model scores on attacked / shifted evaluation set

    Uses shared bin edges derived from the reference scores.
    """
    s_ref = _clip_by_quantiles(_finite(scores_ref), clip_q)
    s_cur = _clip_by_quantiles(_finite(scores_cur), clip_q)
    if s_ref.size == 0 or s_cur.size == 0:
        return 0.0

    edges = _safe_edges_from_ref(s_ref, bins=bins)
    if edges is None:
        return _degenerate_fallback_drift(s_ref, s_cur)

    p = _hist_1d_with_edges(s_ref, edges)
    q = _hist_1d_with_edges(s_cur, edges)
    return float(jensenshannon(p, q) ** 2)


# ----------------------------
# 4) KS aggregated (interpretable)
# ----------------------------
def ks_feature_shift(
    X_ref: np.ndarray,
    X_cur: np.ndarray,
) -> Tuple[float, float, int]:
    """
    KS drift summary across features.

    Returns:
      mean_ks_stat: mean KS statistic across features
      frac_reject_05: fraction of features with p-value < 0.05 (uncorrected)
      n_used: number of features actually used (finite data in both sets)

    Notes:
      - If n_used == 0, returns (0.0, nan, 0) to avoid implying "no drift".
      - If you want multiple-testing correction (FDR), do it at analysis time.
    """
    X_ref = np.asarray(X_ref, dtype=float)
    X_cur = np.asarray(X_cur, dtype=float)
    if X_ref.ndim != 2 or X_cur.ndim != 2:
        raise ValueError("X_ref and X_cur must be 2D arrays")
    if X_ref.shape[1] != X_cur.shape[1]:
        raise ValueError("Feature dimension mismatch")

    stats = []
    pvals = []
    n_used = 0

    for j in range(X_ref.shape[1]):
        a = _finite(X_ref[:, j])
        b = _finite(X_cur[:, j])
        if a.size == 0 or b.size == 0:
            continue
        res = ks_2samp(a, b, alternative="two-sided", mode="auto")
        stats.append(float(res.statistic))
        pvals.append(float(res.pvalue))
        n_used += 1

    if n_used == 0:
        return 0.0, float("nan"), 0

    frac_reject = float(np.mean(np.array(pvals) < 0.05))
    return float(np.mean(stats)), frac_reject, n_used
