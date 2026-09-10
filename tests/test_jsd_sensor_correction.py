"""Regression tests for the v1.3.7 shared-support JSD correction."""

from __future__ import annotations

import warnings

import numpy as np
from scipy.spatial.distance import jensenshannon

from src.integrity.family_calibration import conformal_family_pvalues
from src.integrity.signals import (
    _hist_1d_with_edges,
    _safe_edges_from_ref,
    jsd_feature_shift,
    score_drift_jsd,
)


def test_identical_distributions_are_finite_and_zero() -> None:
    rng = np.random.default_rng(137)
    sample = rng.normal(size=(512, 4))
    feature = jsd_feature_shift(sample, sample.copy())
    score = score_drift_jsd(sample[:, 0], sample[:, 0].copy())
    assert np.isfinite(feature) and abs(feature) <= 1e-15
    assert np.isfinite(score) and abs(score) <= 1e-15


def test_fully_disjoint_support_is_finite_and_high_without_warning() -> None:
    rng = np.random.default_rng(137)
    reference = rng.uniform(0.0, 1.0, size=1000)
    current = rng.uniform(10.0, 11.0, size=1000)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        feature = jsd_feature_shift(reference[:, None], current[:, None])
        score = score_drift_jsd(reference, current)
    assert not caught
    assert 0.5 < feature <= np.log(2.0) + 1e-15
    assert 0.5 < score <= np.log(2.0) + 1e-15


def test_partially_disjoint_support_is_finite() -> None:
    rng = np.random.default_rng(27)
    reference = rng.uniform(0.0, 1.0, size=1000)
    current = rng.uniform(0.5, 1.5, size=1000)
    values = (
        jsd_feature_shift(reference[:, None], current[:, None]),
        score_drift_jsd(reference, current),
    )
    assert all(np.isfinite(value) and value > 0.0 for value in values)


def test_shifted_constant_and_degenerate_reference_are_finite() -> None:
    reference = np.ones(128)
    shifted = np.full(128, 2.0)
    same = np.ones(128)
    shifted_values = (
        jsd_feature_shift(reference[:, None], shifted[:, None]),
        score_drift_jsd(reference, shifted),
    )
    same_values = (
        jsd_feature_shift(reference[:, None], same[:, None]),
        score_drift_jsd(reference, same),
    )
    assert all(np.isfinite(value) and value > 0.5 for value in shifted_values)
    assert all(np.isfinite(value) and abs(value) <= 1e-15 for value in same_values)


def test_shared_edge_pmfs_are_valid_and_jsd_is_symmetric() -> None:
    reference = np.linspace(0.0, 1.0, 257)
    current = np.linspace(-2.0, 3.0, 257)
    edges = _safe_edges_from_ref(reference, bins=40)
    assert edges is not None
    assert np.isneginf(edges[0]) and np.isposinf(edges[-1])
    p = _hist_1d_with_edges(reference, edges)
    q = _hist_1d_with_edges(current, edges)
    assert np.isfinite(p).all() and np.isfinite(q).all()
    assert np.isclose(p.sum(), 1.0) and np.isclose(q.sum(), 1.0)
    assert np.isclose(jensenshannon(p, q) ** 2, jensenshannon(q, p) ** 2)


def test_outputs_are_deterministic() -> None:
    rng = np.random.default_rng(91)
    reference = rng.normal(size=(256, 3))
    current = reference + 0.25
    first = jsd_feature_shift(reference, current)
    second = jsd_feature_shift(reference, current)
    assert first == second
    assert score_drift_jsd(reference[:, 0], current[:, 0]) == score_drift_jsd(
        reference[:, 0], current[:, 0]
    )


def test_valid_finite_jsd_never_reaches_family_calibration_as_nan() -> None:
    rng = np.random.default_rng(314)
    reference = rng.normal(size=256)
    shifts = np.linspace(-1.0, 1.0, 21)
    jsd = np.array([score_drift_jsd(reference, reference + shift) for shift in shifts])
    assert np.isfinite(jsd).all()
    calibration = np.column_stack([jsd[:20], np.linspace(0.0, 1.0, 20)])
    audited = np.array([[jsd[20], 0.5]])
    pvalue = conformal_family_pvalues(calibration, audited)
    assert pvalue.shape == (1,) and np.isfinite(pvalue).all()


def test_family_calibration_fails_closed_on_nonfinite_sensor() -> None:
    calibration = np.array([[0.0, 0.0], [0.1, 0.2], [0.2, 0.1]])
    for invalid in (np.nan, np.inf, -np.inf):
        try:
            conformal_family_pvalues(calibration, np.array([[0.3, invalid]]))
        except ValueError as exc:
            assert "finite" in str(exc)
        else:
            raise AssertionError(f"family calibration accepted {invalid!r}")
