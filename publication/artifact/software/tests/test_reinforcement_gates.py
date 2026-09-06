"""Unit tests for the artifact 1.1.0 reinforcement-gate code paths.

These tests do not require the derived evidence or Qiskit runs; they check the
null-control sampler, the frozen-fingerprint guarantee, the prespecified
threshold rank, the cluster-mass helper, the cross-validation tie rule, and the
equivalence of the refactored subsampler with the historical implementation.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from dataclasses import asdict

import numpy as np

from src.attacks.sham import CleanResample, CleanResampleCfg, IdentityAttack
from src.experiments.build_q1_reinforcement_evidence import _max_window_mass, _order_statistic_rank
from src.experiments.run_benchmark import RunCfg, _cfg_fingerprint, _stratified_subsample, _stratified_subsample_indices
from src.qml.classical import ClassicalCfg, select_svc_params_cv


def _legacy_stratified_subsample(X: np.ndarray, y: np.ndarray, n_max: int, *, seed: int):
    """Verbatim copy of the 1.0.0 implementation used to freeze the evaluation batches."""

    X = np.asarray(X)
    y = np.asarray(y).astype(int)
    if n_max <= 0 or len(y) <= n_max:
        return X, y
    rng = np.random.default_rng(int(seed))
    idx_all = np.arange(len(y))
    classes, counts = np.unique(y, return_counts=True)
    frac = float(n_max) / float(len(y))
    chosen = []
    for c, cnt in zip(classes, counts):
        idx_c = idx_all[y == c]
        k = max(1, int(round(float(cnt) * frac)))
        k = min(k, len(idx_c))
        chosen.append(rng.choice(idx_c, size=k, replace=False))
    idx = np.concatenate(chosen) if chosen else rng.choice(idx_all, size=n_max, replace=False)
    if len(idx) > n_max:
        idx = rng.choice(idx, size=n_max, replace=False)
    idx = np.sort(idx)
    return X[idx], y[idx]


def _frozen_cfg(**overrides: object) -> RunCfg:
    base = dict(
        protocol="id",
        data="data/cicids_subset.csv",
        data_train=None,
        data_test=None,
        svd_dim=8,
        seed=42000042,
        split_seed=42,
        model_seed=42,
        outdir="results/raw/x",
        classical_models=("svc_rbf",),
        run_quantum=True,
        q_feature_maps=("zz",),
        q_reps=1,
        q_shots=1024,
        q_backend_method="exact_statevector",
        q_max_iter=1000,
        scale_classical="standard",
        scale_quantum="minmax2pi",
        sig_bins=40,
        sig_clip_q_lo=0.005,
        sig_clip_q_hi=0.995,
        mmd_max_samples=512,
        mmd_gamma="median",
        mmd_max_pairs=4096,
        attack_suite="paper_core",
        atk_meta_whitelist=(),
        max_train=128,
        max_test=128,
    )
    base.update(overrides)
    return RunCfg(**base)


class CleanResampleTests(unittest.TestCase):
    def _pool(self, n_pool: int = 60, d: int = 3):
        rng = np.random.default_rng(1)
        X_pool = rng.normal(size=(n_pool, d))
        y_pool = rng.integers(0, 2, size=n_pool)
        perm = rng.permutation(n_pool)
        return {
            "X": X_pool,
            "y": y_pool,
            "calibration_idx": np.sort(perm[: n_pool // 2]),
            "evaluation_idx": np.sort(perm[n_pool // 2 :]),
        }

    def test_draws_only_from_designated_half_without_replacement(self) -> None:
        pool = self._pool()
        X = np.zeros((20, 3))
        for half in ("calibration", "evaluation"):
            out = CleanResample(CleanResampleCfg(pool_half=half, draw_index=3)).apply(X, seed=7, y=np.zeros(20, dtype=int), pool=pool)
            self.assertEqual(out.X_att.shape, (20, 3))
            allowed = pool["X"][pool[f"{half}_idx"]]
            for row in out.X_att:
                self.assertTrue(any(np.array_equal(row, cand) for cand in allowed))
            self.assertEqual(len(np.unique(out.X_att, axis=0)), 20)
            self.assertEqual(out.meta["family"], "null_control")
            self.assertEqual(out.meta["pool_half"], half)

    def test_deterministic_in_seed_and_fail_closed_on_small_pool(self) -> None:
        pool = self._pool()
        X = np.zeros((10, 3))
        a = CleanResample().apply(X, seed=11, y=np.zeros(10, dtype=int), pool=pool)
        b = CleanResample().apply(X, seed=11, y=np.zeros(10, dtype=int), pool=pool)
        self.assertTrue(np.array_equal(a.X_att, b.X_att))
        with self.assertRaises(ValueError):
            CleanResample().apply(np.zeros((40, 3)), seed=1, y=np.zeros(40, dtype=int), pool=pool)
        with self.assertRaises(ValueError):
            CleanResample().apply(X, seed=1, y=np.zeros(10, dtype=int), pool=None)

    def test_identity_control_is_exactly_invariant(self) -> None:
        X = np.random.default_rng(2).normal(size=(12, 4))
        out = IdentityAttack().apply(X, seed=0, y=np.arange(12) % 2)
        self.assertTrue(np.array_equal(out.X_att, X))


class FingerprintStabilityTests(unittest.TestCase):
    def test_default_reinforcement_options_do_not_change_frozen_fingerprint(self) -> None:
        cfg = _frozen_cfg()
        legacy = {k: v for k, v in asdict(cfg).items() if k not in ("svc_tune", "qsvc_tune")}
        expected = hashlib.sha1(json.dumps(legacy, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:10]
        self.assertEqual(_cfg_fingerprint(cfg), expected)

    def test_tuned_configuration_gets_a_distinct_fingerprint(self) -> None:
        self.assertNotEqual(_cfg_fingerprint(_frozen_cfg()), _cfg_fingerprint(_frozen_cfg(svc_tune="cv5", qsvc_tune="cv5")))


class SubsampleEquivalenceTests(unittest.TestCase):
    def test_refactored_subsampler_matches_historical_sequence(self) -> None:
        rng = np.random.default_rng(3)
        for n, n_max in ((900, 128), (900, 256), (50, 128), (3000, 128)):
            X = rng.normal(size=(n, 5))
            y = rng.integers(0, 2, size=n)
            for seed in (42000043, 43000042, 7):
                X_old, y_old = _legacy_stratified_subsample(X, y, n_max, seed=seed)
                X_new, y_new = _stratified_subsample(X, y, n_max, seed=seed)
                idx = _stratified_subsample_indices(y, n_max, seed=seed)
                self.assertTrue(np.array_equal(X_old, X_new))
                self.assertTrue(np.array_equal(y_old, y_new))
                self.assertTrue(np.array_equal(X[idx], X_old))


class CalibrationHelperTests(unittest.TestCase):
    def test_prespecified_order_statistic_rank(self) -> None:
        self.assertEqual(_order_statistic_rank(200, 0.05), 191)
        self.assertEqual(_order_statistic_rank(19, 0.05), 19)

    def test_max_window_mass(self) -> None:
        values = np.array([0.0, 0.001, 0.002, 0.5, 1.0, 1.0005])
        self.assertAlmostEqual(_max_window_mass(values, 0.01), 3 / 6)
        self.assertAlmostEqual(_max_window_mass(values, 0.0), 1 / 6)
        self.assertAlmostEqual(_max_window_mass(values, 10.0), 1.0)


class CrossValidationTieRuleTests(unittest.TestCase):
    def test_selection_from_grid_and_smallest_c_on_ties(self) -> None:
        rng = np.random.default_rng(4)
        X = np.vstack([rng.normal(loc=-5.0, size=(40, 2)), rng.normal(loc=5.0, size=(40, 2))])
        y = np.array([0] * 40 + [1] * 40)
        tuned, info = select_svc_params_cv(X, y, ClassicalCfg(), seed=42, n_splits=5)
        self.assertIn(tuned.C, (0.1, 1.0, 10.0, 100.0))
        self.assertEqual(info["mode"], "cv5")
        self.assertEqual(info["scoring"], "balanced_accuracy")
        # perfectly separable data: every grid point reaches balanced accuracy 1, so ties resolve to the smallest C
        self.assertEqual(tuned.C, 0.1)
        self.assertEqual(tuned.gamma, "scale")
        self.assertEqual(len(info["grid_table"]), 16)


if __name__ == "__main__":
    unittest.main()
