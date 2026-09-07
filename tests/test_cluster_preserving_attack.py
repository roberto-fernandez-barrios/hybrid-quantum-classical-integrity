"""Unit tests of the adaptive cluster-preserving perturbation (class F5, artifact 1.3.0)."""

from __future__ import annotations

import unittest

import numpy as np

from src.attacks.cluster_preserving import ClusterPreservingCfg, ClusterPreservingPerturbation, cluster_mask
from src.attacks.mean_shift import MeanShift, MeanShiftCfg
from src.attacks.scaling_drift import ScalingDrift, ScalingDriftCfg


def _batch(n_cluster: int = 90, n_free: int = 38, d: int = 4, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n_cluster + n_free, d))
    X[:n_cluster] = 0.5  # exact cluster in every feature
    X[:n_cluster] += rng.normal(scale=1e-5, size=(n_cluster, d))  # sub-window jitter
    return X


class ClusterMaskTests(unittest.TestCase):
    def test_clustered_entries_are_identified_and_free_entries_are_not(self) -> None:
        X = _batch()
        mask = cluster_mask(X, window_sd=0.01, min_mass=0.05)
        self.assertTrue(mask[:90].all())
        self.assertFalse(mask[90:].any())

    def test_constant_feature_is_fully_frozen(self) -> None:
        X = np.column_stack([np.ones(20), np.arange(20, dtype=float)])
        mask = cluster_mask(X, window_sd=0.01, min_mass=0.05)
        self.assertTrue(mask[:, 0].all())
        self.assertFalse(mask[:, 1].any())

    def test_minimum_mass_governs_membership(self) -> None:
        X = np.arange(40, dtype=float)[:, None]
        X[:3] = 100.5  # three tied rows (value outside the range): a cluster at min_mass 0.05 (need 2) but not at 0.2 (need 8)
        self.assertEqual(int(cluster_mask(X, 0.01, 0.05)[:, 0].sum()), 3)
        self.assertEqual(int(cluster_mask(X, 0.01, 0.20)[:, 0].sum()), 0)


class PerturbationTests(unittest.TestCase):
    def test_mean_shift_moves_only_free_entries_with_the_executed_offsets(self) -> None:
        X = _batch()
        atk = ClusterPreservingPerturbation(ClusterPreservingCfg(mechanism="mean_shift", strength=0.1))
        out = atk.apply(X, seed=123)
        self.assertTrue(np.array_equal(out.X_att[:90], X[:90]))
        reference = MeanShift(MeanShiftCfg(delta=0.1, per_feature=True)).apply(X, seed=123).X_att
        self.assertTrue(np.allclose(out.X_att[90:], reference[90:]))
        self.assertEqual(out.meta["family"], "adaptive_covariate_shift")
        self.assertEqual(out.meta["mechanism"], "mean_shift")
        self.assertAlmostEqual(out.meta["frozen_entry_fraction"], 90 / 128)
        self.assertGreater(out.meta["mean_abs_delta_moved"], 0.0)
        self.assertIsNone(out.y_att)

    def test_scaling_drift_moves_only_free_entries(self) -> None:
        X = _batch(seed=2)
        atk = ClusterPreservingPerturbation(ClusterPreservingCfg(mechanism="scaling_drift", strength=0.05))
        out = atk.apply(X, seed=5)
        self.assertTrue(np.array_equal(out.X_att[:90], X[:90]))
        reference = ScalingDrift(ScalingDriftCfg(alpha=0.05)).apply(X, seed=5).X_att
        self.assertTrue(np.allclose(out.X_att[90:], reference[90:]))

    def test_deterministic_in_seed_and_labels_untouched(self) -> None:
        X = _batch(seed=3)
        y = np.arange(len(X)) % 2
        atk = ClusterPreservingPerturbation(ClusterPreservingCfg(mechanism="mean_shift", strength=0.02))
        a = atk.apply(X, seed=9, y=y)
        b = atk.apply(X, seed=9, y=y)
        self.assertTrue(np.array_equal(a.X_att, b.X_att))
        self.assertTrue(np.array_equal(a.y_att, y))

    def test_configuration_validation(self) -> None:
        with self.assertRaises(ValueError):
            ClusterPreservingPerturbation(ClusterPreservingCfg(mechanism="other"))
        with self.assertRaises(ValueError):
            ClusterPreservingPerturbation(ClusterPreservingCfg(strength=-1.0))
        with self.assertRaises(ValueError):
            ClusterPreservingPerturbation(ClusterPreservingCfg(min_mass=0.0))


if __name__ == "__main__":
    unittest.main()
