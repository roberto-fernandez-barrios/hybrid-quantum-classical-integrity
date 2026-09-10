"""Family-wise (decision-level) calibration of a sensor family from clean draws.

Artifact 1.3.0, Gate F (``manuscript/paper15_v13_prereg.md``, amendment A2 of
the 1.2.0 protocol). A regime is a family of sensors that a batch-level auditor
evaluates on a fresh batch. Calibrating each sensor at a nominal level ``alpha``
and firing when *any* sensor fires does not control the false-alarm rate of the
decision; the family has to be calibrated as a whole.

Adopted rule: full conformal max-rank p-value (``conformal_family_pvalues``)
---------------------------------------------------------------------------

Given ``n`` calibration vectors ``v_1..v_n`` (one value per sensor of the
family) and an audited vector ``v``, form the augmented set of ``n + 1``
vectors and give every member ``j`` the leave-one-out family score

    U~_j = max_{s in family} #{i != j : v[s, i] < v[s, j]} / n,

computed against the *other n members of the augmented set*. The conformal
p-value of the audited vector is

    p = (1 + #{i <= n : U~_i >= U~_{n+1}}) / (n + 1),

and the family fires iff ``p <= alpha``. Ties count against firing. If the
``n + 1`` vectors are exchangeable, ``P(p <= alpha) <= floor(alpha (n+1)) / (n+1)
<= alpha`` for every ``alpha``, with no assumption on ties or continuity
(Proposition 5(b) of ``manuscript/FORMAL_CORE.md``; the deterministic counting
bound behind it is checked exhaustively in
``tests/test_family_calibration_exhaustive.py``). For a single sensor without
ties the rule coincides with "fire iff the audited value exceeds the
``ceil((n+1)(1-alpha))``-th smallest calibration value", i.e. the per-sensor
rule of artifact 1.1.0.

Split construction (``split_conformal_family``)
-----------------------------------------------

The reference set defines the rank transform, a disjoint calibration set
calibrates the family score, and the audited vector is compared with the
calibration scores. Valid under exchangeability of (calibration set, audited
vector) conditional on the reference set; it uses half of the draws and has
half the p-value resolution. Reported as a sensitivity construction only.

Superseded rule of artifact 1.2.0 (``legacy_v12_*``)
----------------------------------------------------

The 1.2.0 rule scored the calibration draws against the calibration set only
(each against the other ``n - 1``) and the audited batch against all ``n``
calibration draws, then fired when the audited family score exceeded the
``ceil((n+1)(1-alpha))``-th smallest calibration score. With several sensors
and tied max-rank scores the scores are not exchangeable and the published
bound ``alpha + 1/(n+1)`` is false (finite counterexample: five vectors, three
sensors, ``alpha = 0.2``, firing probability 0.60 against a claimed 0.40). The
functions are kept only to reproduce the 1.2.0 columns of the comparison
tables; they must not be used for decisions.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

import numpy as np


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def order_statistic_rank(n: int, alpha: float) -> int:
    """Rank of the calibration order statistic used by the 1.1.0 per-sensor rule (1-based)."""

    if n <= 0:
        raise ValueError("n must be positive")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    return int(math.ceil((n + 1) * (1.0 - alpha)))


def conformal_firing_count(n: int, alpha: float) -> int:
    """Largest integer ``k`` with ``k / (n + 1) <= alpha``: the exact level is ``k / (n + 1)``."""

    if n <= 0:
        raise ValueError("n must be positive")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    return int(math.floor(alpha * (n + 1) + 1e-12))


def _coerce_matrix(values: Mapping[str, np.ndarray] | np.ndarray, family: Sequence[str] | None) -> np.ndarray:
    """Stack a mapping ``sensor -> 1-D array`` into an ``(k, m)`` matrix."""
    if isinstance(values, Mapping):
        if not family:
            raise ValueError("family must contain at least one sensor")
        cols = [np.asarray(values[s], dtype=float).reshape(-1) for s in family]
        if len({c.shape[0] for c in cols}) != 1:
            raise ValueError("sensor arrays must have equal length")
        mat = np.stack(cols, axis=1)
    else:
        mat = np.asarray(values, dtype=float)
        if mat.ndim == 1:
            mat = mat.reshape(-1, 1)
        if mat.ndim != 2:
            raise ValueError("values must be a 1-D or 2-D array")
    return mat.copy()


def _matrix(values: Mapping[str, np.ndarray] | np.ndarray, family: Sequence[str] | None) -> np.ndarray:
    """Current scientific matrix conversion: reject every NaN or infinity."""

    mat = _coerce_matrix(values, family)
    if not np.isfinite(mat).all():
        raise ValueError("current scientific sensor values must all be finite")
    return mat


def _legacy_audited_matrix(values: Mapping[str, np.ndarray] | np.ndarray, family: Sequence[str] | None) -> np.ndarray:
    """Reproduce v1.3.6 audited-NaN semantics: map NaN to ``-inf``.

    This conversion is intentionally isolated from every current scientific
    entry point.  It exists only to reproduce immutable releases whose audited
    NaN coordinate was treated as unable to contribute to firing.
    """

    mat = _coerce_matrix(values, family)
    if np.isinf(mat).any():
        raise ValueError("legacy sensor values may contain NaN but not infinity")
    mat[np.isnan(mat)] = -np.inf
    return mat


def counts_strictly_below(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    """``out[k, s] = #{r : reference[r, s] < values[k, s]}`` for every audited row ``k``."""

    out = np.empty(values.shape, dtype=int)
    for s in range(reference.shape[1]):
        col = np.sort(reference[:, s])
        out[:, s] = np.searchsorted(col, values[:, s], side="left")
    return out


# ---------------------------------------------------------------------------
# Adopted rule: full conformal max-rank p-value
# ---------------------------------------------------------------------------


def _conformal_pvalues_from_matrices(cal: np.ndarray, aud: np.ndarray) -> np.ndarray:
    """Evaluate the adopted conformal rule on already validated matrices."""

    if cal.shape[1] != aud.shape[1]:
        raise ValueError("calibration and audited vectors must have the same sensors")
    n, _ = cal.shape
    if n < 1:
        raise ValueError("calibration must be non-empty")
    # base[i, s] = #{i' <= n, i' != i : cal[i', s] < cal[i, s]} (self never counts: strict).
    base = counts_strictly_below(cal, cal)
    # audited scores against the n calibration draws
    aud_counts = counts_strictly_below(cal, aud)
    aud_scores = aud_counts.max(axis=1) / n
    # calibration LOO scores in the augmented set: add one when the audited value is below.
    add = (aud[:, None, :] < cal[None, :, :]).astype(int)  # (k, n, m)
    tilde = (base[None, :, :] + add).max(axis=2) / n  # (k, n)
    n_ge = (tilde >= aud_scores[:, None]).sum(axis=1)
    return (1 + n_ge) / (n + 1)


def conformal_family_pvalues(
    calibration: Mapping[str, np.ndarray] | np.ndarray,
    values: Mapping[str, np.ndarray] | np.ndarray,
    family: Sequence[str] | None = None,
) -> np.ndarray:
    """Conformal p-value of every audited vector against the calibration draws.

    ``calibration`` holds the ``n`` calibration vectors and ``values`` the ``k``
    audited vectors (each audited vector is treated on its own: the augmented
    set is the calibration set plus that single vector). Returns an array of
    ``k`` p-values in ``{1/(n+1), ..., 1}``.  Current scientific use fails
    closed if any calibration or audited coordinate is NaN or infinite.
    """

    return _conformal_pvalues_from_matrices(
        _matrix(calibration, family), _matrix(values, family)
    )


def legacy_v136_conformal_family_pvalues(
    calibration: Mapping[str, np.ndarray] | np.ndarray,
    values: Mapping[str, np.ndarray] | np.ndarray,
    family: Sequence[str] | None = None,
) -> np.ndarray:
    """Reproduce v1.3.6 only: audited NaN maps to ``-inf`` and never fires."""

    return _conformal_pvalues_from_matrices(
        _matrix(calibration, family), _legacy_audited_matrix(values, family)
    )


def conformal_family_fires(
    calibration: Mapping[str, np.ndarray] | np.ndarray,
    values: Mapping[str, np.ndarray] | np.ndarray,
    family: Sequence[str] | None = None,
    alpha: float = 0.05,
) -> np.ndarray:
    """Boolean fire vector of the adopted rule: ``p <= alpha``."""

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    p = conformal_family_pvalues(calibration, values, family)
    return p <= alpha + 1e-12


def legacy_v136_conformal_family_fires(
    calibration: Mapping[str, np.ndarray] | np.ndarray,
    values: Mapping[str, np.ndarray] | np.ndarray,
    family: Sequence[str] | None = None,
    alpha: float = 0.05,
) -> np.ndarray:
    """Boolean v1.3.6 reproduction wrapper with legacy audited-NaN handling."""

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    p = legacy_v136_conformal_family_pvalues(calibration, values, family)
    return p <= alpha + 1e-12


def augmented_family_scores(points: np.ndarray) -> np.ndarray:
    """Leave-one-out family scores of every member of one augmented set ``(n+1, m)``.

    Used by the exhaustive tests: for a fixed augmented set the scores do not
    depend on which member is audited, and the audited member ``j`` fires iff
    ``#{i : U~_i >= U~_j} <= floor(alpha (n+1))``.
    """

    pts = _matrix(points, None)
    n_plus_1 = pts.shape[0]
    below = (pts[None, :, :] < pts[:, None, :]).sum(axis=1)  # (n+1, m): others strictly below each member
    return below.max(axis=1) / (n_plus_1 - 1)


def firing_members(points: np.ndarray, alpha: float) -> np.ndarray:
    """Boolean vector: which members of the augmented set would fire if audited (adopted rule)."""

    scores = augmented_family_scores(points)
    n_ge = (scores[None, :] >= scores[:, None]).sum(axis=1)  # includes itself
    return n_ge <= conformal_firing_count(points.shape[0] - 1, alpha)


# ---------------------------------------------------------------------------
# Split construction (sensitivity)
# ---------------------------------------------------------------------------


def split_family_scores(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    """Family score ``max_s #{r : reference[r, s] < v_s} / |reference|`` of every row of ``values``."""

    ref = _matrix(reference, None)
    val = _matrix(values, None)
    if ref.shape[1] != val.shape[1]:
        raise ValueError("reference and values must have the same sensors")
    return counts_strictly_below(ref, val).max(axis=1) / ref.shape[0]


def split_conformal_family(
    reference: np.ndarray,
    calibration: np.ndarray,
    values: np.ndarray,
    alpha: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    """Split construction: returns ``(p_values, fires)`` for every row of ``values``.

    The reference set fixes the rank transform; the calibration set (disjoint
    from the reference) provides the null scores; the p-value of an audited
    vector is ``(1 + #{c : U(c) >= U(v)}) / (|calibration| + 1)``.
    """

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    cal_scores = split_family_scores(reference, calibration)
    aud_scores = split_family_scores(reference, values)
    n_ge = (cal_scores[None, :] >= aud_scores[:, None]).sum(axis=1)
    p = (1 + n_ge) / (cal_scores.shape[0] + 1)
    return p, p <= alpha + 1e-12


# ---------------------------------------------------------------------------
# Superseded 1.2.0 rule (comparison only)
# ---------------------------------------------------------------------------


def rank_scores(values: np.ndarray, calibration: np.ndarray) -> np.ndarray:
    """Fraction of calibration values strictly below each value (1.2.0 helper; NaN -> 0)."""

    cal = np.sort(np.asarray(calibration, dtype=float))
    if cal.size == 0 or np.isnan(cal).any():
        raise ValueError("calibration values must be non-empty and finite")
    v = np.asarray(values, dtype=float)
    out = np.zeros(v.shape, dtype=float)
    finite = np.isfinite(v)
    out[finite] = np.searchsorted(cal, v[finite], side="left") / float(cal.size)
    return out


def legacy_v12_family_scores(
    values: Mapping[str, np.ndarray],
    calibration: Mapping[str, np.ndarray],
    family: Sequence[str],
) -> np.ndarray:
    """1.2.0 family score: maximum calibration rank score over the sensors (asymmetric)."""

    if not family:
        raise ValueError("family must contain at least one sensor")
    scores = np.stack([rank_scores(values[s], calibration[s]) for s in family], axis=0)
    return scores.max(axis=0)


def legacy_v12_family_threshold(calibration_family_scores: np.ndarray, alpha: float) -> float:
    """1.2.0 threshold: the ``ceil((n+1)(1-alpha))``-th smallest calibration family score."""

    scores = np.sort(np.asarray(calibration_family_scores, dtype=float))
    n = int(scores.size)
    rank = order_statistic_rank(n, alpha)
    if rank > n:
        return math.inf
    return float(scores[rank - 1])


def legacy_v12_calibrate_family(
    calibration: Mapping[str, np.ndarray],
    family: Sequence[str],
    alpha: float,
) -> tuple[float, np.ndarray]:
    """1.2.0 calibration: ``(threshold, calibration_family_scores)``; comparison only."""

    cal_scores = legacy_v12_family_scores(calibration, calibration, family)
    return legacy_v12_family_threshold(cal_scores, alpha), cal_scores


def legacy_v12_family_fires(
    values: Mapping[str, np.ndarray],
    calibration: Mapping[str, np.ndarray],
    family: Sequence[str],
    threshold: float,
) -> np.ndarray:
    """1.2.0 fire vector: family score strictly greater than the threshold; comparison only."""

    return legacy_v12_family_scores(values, calibration, family) > threshold


def legacy_v12_firing_members(points: np.ndarray, alpha: float) -> np.ndarray:
    """Which members of an augmented set would fire under the 1.2.0 rule if audited (tests)."""

    pts = _matrix(points, None)
    n_plus_1, m = pts.shape
    out = np.zeros(n_plus_1, dtype=bool)
    for j in range(n_plus_1):
        cal = np.delete(pts, j, axis=0)
        cal_map = {str(s): cal[:, s] for s in range(m)}
        fam = [str(s) for s in range(m)]
        q, _ = legacy_v12_calibrate_family(cal_map, fam, alpha)
        aud_map = {str(s): pts[j : j + 1, s] for s in range(m)}
        out[j] = bool(legacy_v12_family_fires(aud_map, cal_map, fam, q)[0])
    return out
