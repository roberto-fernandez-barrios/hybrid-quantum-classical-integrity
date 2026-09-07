"""Adaptive cluster-preserving feature perturbation (class F5 of the adversary model).

Artifact 1.3.0, Gate A (``manuscript/paper15_v13_prereg.md``). The executed
feature-side drifts of the frozen suite (feature-wise mean shift, scaling
drift) are detected in every cell of the frozen design because the projected
features hold tight clusters of rows that a fresh clean batch reproduces and
that any in-place displacement smears (``null_mass_point_profile.csv`` of
artifact 1.1.0). An adaptive attacker who knows that fingerprint leaves the
clustered entries untouched and applies the same mechanism to the remaining
entries only.

Cluster membership is decided on the audited batch itself, per feature: an
entry ``x[i, j]`` is *clustered* when at least ``ceil(min_mass * n)`` rows of
the batch (itself included, and never fewer than two) lie within
``window_sd * sd_j`` of it, where ``sd_j`` is the population standard
deviation of feature ``j`` over the batch. Entries of a constant feature are
all clustered. Every non-clustered entry receives the mechanism:

* ``mean_shift``: ``x + d_j`` with ``d_j ~ N(0, strength)`` drawn once per
  feature (the per-feature random offsets of the executed ``MeanShift``);
* ``scaling_drift``: ``x * (1 + strength)`` (the executed ``ScalingDrift``).

Only the selection of entries differs from the executed mechanisms, so the
comparison with the frozen F2 rows at matched strength isolates the value of
the cluster fingerprint. Labels are never touched.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

from .base import Attack, AttackResult


MECHANISMS = ("mean_shift", "scaling_drift")


@dataclass(frozen=True)
class ClusterPreservingCfg:
    mechanism: str = "mean_shift"
    strength: float = 0.05
    window_sd: float = 0.01
    min_mass: float = 0.05


def cluster_mask(X: np.ndarray, window_sd: float, min_mass: float) -> np.ndarray:
    """Boolean mask of clustered entries (True = left untouched by the attacker)."""

    X = np.asarray(X, dtype=float)
    if X.ndim != 2:
        raise ValueError("X must be a 2-D array")
    n, d = X.shape
    if n == 0:
        return np.zeros((0, d), dtype=bool)
    need = max(2, int(math.ceil(float(min_mass) * n)))
    mask = np.zeros((n, d), dtype=bool)
    for j in range(d):
        col = X[:, j]
        finite = np.isfinite(col)
        if not finite.any():
            mask[:, j] = True
            continue
        sd = float(np.std(col[finite]))
        if sd == 0.0 or not np.isfinite(sd):
            mask[:, j] = True
            continue
        width = float(window_sd) * sd
        order = np.argsort(col, kind="stable")
        sorted_col = col[order]
        # count of rows within +-width of each sorted value (inclusive), itself included
        lo = np.searchsorted(sorted_col, sorted_col - width, side="left")
        hi = np.searchsorted(sorted_col, sorted_col + width, side="right")
        counts = hi - lo
        clustered_sorted = counts >= need
        mask[order, j] = clustered_sorted
        mask[~finite, j] = True
    return mask


class ClusterPreservingPerturbation(Attack):
    name = "cluster_preserving"

    def __init__(self, cfg: ClusterPreservingCfg):
        if cfg.mechanism not in MECHANISMS:
            raise ValueError(f"ClusterPreservingCfg.mechanism must be one of {MECHANISMS}, got {cfg.mechanism!r}")
        if float(cfg.strength) < 0.0:
            raise ValueError("ClusterPreservingCfg.strength must be >= 0")
        if float(cfg.window_sd) < 0.0:
            raise ValueError("ClusterPreservingCfg.window_sd must be >= 0")
        if not (0.0 < float(cfg.min_mass) <= 1.0):
            raise ValueError("ClusterPreservingCfg.min_mass must lie in (0, 1]")
        self.cfg = cfg

    def apply(self, X: np.ndarray, seed: int, y: Optional[np.ndarray] = None) -> AttackResult:
        X = np.asarray(X, dtype=float)
        frozen = cluster_mask(X, self.cfg.window_sd, self.cfg.min_mass)
        strength = float(self.cfg.strength)
        X_att = X.copy()
        if self.cfg.mechanism == "mean_shift":
            rng = np.random.default_rng(int(seed))
            dvec = rng.normal(loc=0.0, scale=strength, size=(X.shape[1],)) if X.shape[1] else np.zeros(0)
            shifted = X + dvec[None, :]
            X_att = np.where(frozen, X, shifted)
        else:
            X_att = np.where(frozen, X, X * (1.0 + strength))
        delta = X_att - X
        n_entries = int(X.size)
        n_frozen = int(frozen.sum())
        moved = ~frozen
        mean_abs_delta = float(np.mean(np.abs(delta))) if n_entries else 0.0
        mean_abs_delta_moved = float(np.mean(np.abs(delta[moved]))) if moved.any() else 0.0
        row_frozen_fraction = float(np.mean(frozen.all(axis=1))) if X.shape[0] else 0.0
        col_frozen = frozen.mean(axis=0) if X.shape[1] else np.zeros(0)
        meta = {
            "family": "adaptive_covariate_shift",
            "priority_group": "adaptive",
            "strength": strength,
            "strength_nominal": strength,
            "strength_eff": mean_abs_delta,
            "mechanism": str(self.cfg.mechanism),
            "window_sd": float(self.cfg.window_sd),
            "min_mass": float(self.cfg.min_mass),
            "frozen_entry_fraction": (n_frozen / n_entries) if n_entries else 0.0,
            "perturbed_entry_fraction": (1.0 - n_frozen / n_entries) if n_entries else 0.0,
            "fully_frozen_row_fraction": row_frozen_fraction,
            "max_feature_frozen_fraction": float(col_frozen.max()) if col_frozen.size else 0.0,
            "min_feature_frozen_fraction": float(col_frozen.min()) if col_frozen.size else 0.0,
            "mean_abs_delta": mean_abs_delta,
            "mean_abs_delta_moved": mean_abs_delta_moved,
            "max_abs_delta": float(np.max(np.abs(delta))) if n_entries else 0.0,
            "n_samples": int(X.shape[0]),
            "n_features": int(X.shape[1]) if X.ndim == 2 else 0,
        }
        return AttackResult(X_att=np.asarray(X_att), y_att=y, meta=meta)
