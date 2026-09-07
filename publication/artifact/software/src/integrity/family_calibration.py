"""Family-wise (policy-level) calibration of a sensor family from clean draws.

Artifact 1.2.0, Gate F (``manuscript/paper15_v12_policy_prereg.md``).

A regime is a family of sensors that a batch-level auditor can evaluate on a
fresh batch. Calibrating each sensor at a nominal level ``alpha`` and firing
when *any* sensor fires does not control the false-alarm rate of the decision.
This module calibrates the family as a whole with a rank-based (Tippett)
combination:

* for every sensor ``s`` the calibration rank score of a value ``v`` is the
  fraction of calibration values strictly below ``v`` (ties count against
  firing);
* the family score is the maximum rank score over the family, i.e. one minus
  the smallest calibration p-value;
* the family threshold is the ``ceil((n + 1)(1 - alpha))``-th smallest family
  score over the calibration draws, and the family fires when its score is
  strictly greater than that threshold.

For a single-sensor family the rule coincides with the per-sensor rule of the
1.1.0 null-calibration gate up to ties. Thresholds must be computed from
calibration draws only; the empirical false-alarm rate is measured on
disjoint evaluation draws.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

import numpy as np


def order_statistic_rank(n: int, alpha: float) -> int:
    """Rank of the calibration order statistic used as threshold (1-based)."""

    if n <= 0:
        raise ValueError("n must be positive")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    return int(math.ceil((n + 1) * (1.0 - alpha)))


def rank_scores(values: np.ndarray, calibration: np.ndarray) -> np.ndarray:
    """Fraction of calibration values strictly below each value.

    ``values`` may contain NaN (undefined sensor); NaN maps to a score of 0.0,
    i.e. an undefined sensor never contributes to firing.
    """

    cal = np.sort(np.asarray(calibration, dtype=float))
    if cal.size == 0 or np.isnan(cal).any():
        raise ValueError("calibration values must be non-empty and finite")
    v = np.asarray(values, dtype=float)
    out = np.zeros(v.shape, dtype=float)
    finite = np.isfinite(v)
    out[finite] = np.searchsorted(cal, v[finite], side="left") / float(cal.size)
    return out


def family_scores(
    values: Mapping[str, np.ndarray],
    calibration: Mapping[str, np.ndarray],
    family: Sequence[str],
) -> np.ndarray:
    """Maximum calibration rank score over the sensors of ``family``."""

    if not family:
        raise ValueError("family must contain at least one sensor")
    scores = np.stack([rank_scores(values[s], calibration[s]) for s in family], axis=0)
    return scores.max(axis=0)


def family_threshold(calibration_family_scores: np.ndarray, alpha: float) -> float:
    """Threshold on the family score: the ceil((n+1)(1-alpha))-th smallest calibration score."""

    scores = np.sort(np.asarray(calibration_family_scores, dtype=float))
    n = int(scores.size)
    rank = order_statistic_rank(n, alpha)
    if rank > n:
        # ceil((n+1)(1-alpha)) can exceed n for tiny n; then no finite calibration
        # value bounds the score and the rule can never fire.
        return math.inf
    return float(scores[rank - 1])


def calibrate_family(
    calibration: Mapping[str, np.ndarray],
    family: Sequence[str],
    alpha: float,
) -> tuple[float, np.ndarray]:
    """Return ``(threshold, calibration_family_scores)`` for a family of sensors."""

    cal_scores = family_scores(calibration, calibration, family)
    return family_threshold(cal_scores, alpha), cal_scores


def family_fires(
    values: Mapping[str, np.ndarray],
    calibration: Mapping[str, np.ndarray],
    family: Sequence[str],
    threshold: float,
) -> np.ndarray:
    """Boolean fire vector: family score strictly greater than the threshold."""

    return family_scores(values, calibration, family) > threshold
