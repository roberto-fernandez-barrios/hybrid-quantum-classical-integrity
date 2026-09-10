"""Adversarial and exhaustive tests of the family-wise calibration rules (artifact 1.3.0).

The adopted rule (full conformal max-rank p-value) rests on a deterministic
counting statement: for any augmented set of ``n + 1`` sensor vectors, at most
``floor(alpha (n + 1))`` of its members would fire if they were the audited
one. Under exchangeability the audited member is a uniformly random member, so
the firing probability is at most ``floor(alpha (n+1)) / (n+1) <= alpha``. The
tests below check the counting statement exhaustively over every weak ordering
(ties included) for small ``n`` and one, two and three sensors, over random
tied configurations with many sensors, and they reproduce the finite
counterexamples that broke the 1.2.0 rule, which must keep failing so that a
regression cannot re-introduce the asymmetric construction.
"""

from __future__ import annotations

import itertools
import math
import unittest

import numpy as np

from src.integrity.family_calibration import (
    augmented_family_scores,
    conformal_family_fires,
    conformal_family_pvalues,
    conformal_firing_count,
    firing_members,
    legacy_v12_calibrate_family,
    legacy_v12_family_fires,
    legacy_v12_firing_members,
    legacy_v136_conformal_family_pvalues,
    order_statistic_rank,
    split_conformal_family,
)


ALPHAS = (0.05, 0.1, 0.2, 0.25, 0.4, 0.5)


def weak_orderings(n: int) -> np.ndarray:
    """All weak orderings of ``n`` labelled elements as integer level vectors ``(count, n)``.

    A weak ordering is an ordered set partition; element ``i`` receives the
    index of its block. Ties are exactly the elements sharing a block.
    """

    out: list[list[int]] = []

    def partitions(items: list[int]):
        if not items:
            yield []
            return
        first, rest = items[0], items[1:]
        for smaller in partitions(rest):
            for k in range(len(smaller)):
                yield smaller[:k] + [[first] + smaller[k]] + smaller[k + 1 :]
            yield [[first]] + smaller

    for part in partitions(list(range(n))):
        for order in itertools.permutations(range(len(part))):
            levels = [0] * n
            for level, block_index in enumerate(order):
                for element in part[block_index]:
                    levels[element] = level
            out.append(levels)
    return np.asarray(out, dtype=float)


def firing_counts_vectorized(configs: np.ndarray, alpha: float) -> np.ndarray:
    """Number of members that would fire (adopted rule) for every configuration ``(C, n+1, m)``."""

    n_plus_1 = configs.shape[1]
    below = (configs[:, None, :, :] < configs[:, :, None, :]).sum(axis=2)  # (C, n+1, m)
    scores = below.max(axis=2) / (n_plus_1 - 1)  # (C, n+1)
    n_ge = (scores[:, None, :] >= scores[:, :, None]).sum(axis=2)  # (C, n+1)
    return (n_ge <= conformal_firing_count(n_plus_1 - 1, alpha)).sum(axis=1)


class CountingBoundExhaustiveTests(unittest.TestCase):
    def test_fubini_counts(self) -> None:
        self.assertEqual(len(weak_orderings(3)), 13)
        self.assertEqual(len(weak_orderings(4)), 75)
        self.assertEqual(len(weak_orderings(5)), 541)

    def test_single_sensor_all_weak_orderings(self) -> None:
        for n_plus_1 in (3, 4, 5, 6, 7):
            configs = weak_orderings(n_plus_1)[:, :, None]
            for alpha in ALPHAS:
                bound = conformal_firing_count(n_plus_1 - 1, alpha)
                self.assertLessEqual(int(firing_counts_vectorized(configs, alpha).max()), bound, (n_plus_1, alpha))

    def test_two_sensors_all_weak_orderings(self) -> None:
        for n_plus_1 in (3, 4, 5):
            single = weak_orderings(n_plus_1)
            configs = np.stack(np.broadcast_arrays(single[:, None, :], single[None, :, :]), axis=-1).reshape(-1, n_plus_1, 2)
            self.assertEqual(configs.shape[0], len(single) ** 2)
            for alpha in ALPHAS:
                bound = conformal_firing_count(n_plus_1 - 1, alpha)
                # process in chunks to bound memory
                worst = 0
                for start in range(0, configs.shape[0], 50000):
                    worst = max(worst, int(firing_counts_vectorized(configs[start : start + 50000], alpha).max()))
                self.assertLessEqual(worst, bound, (n_plus_1, alpha))

    def test_three_sensors_all_weak_orderings_of_four(self) -> None:
        single = weak_orderings(4)
        grid = np.array(list(itertools.product(range(len(single)), repeat=3)))
        configs = np.stack([single[grid[:, 0]], single[grid[:, 1]], single[grid[:, 2]]], axis=-1)
        self.assertEqual(configs.shape, (len(single) ** 3, 4, 3))
        for alpha in ALPHAS:
            bound = conformal_firing_count(3, alpha)
            worst = 0
            for start in range(0, configs.shape[0], 50000):
                worst = max(worst, int(firing_counts_vectorized(configs[start : start + 50000], alpha).max()))
            self.assertLessEqual(worst, bound, alpha)

    def test_random_tied_configurations_many_sensors(self) -> None:
        rng = np.random.default_rng(1303)
        for n_plus_1, m, alphabet in ((5, 3, 2), (5, 5, 3), (8, 4, 2), (12, 6, 3), (21, 10, 4), (21, 10, 1000)):
            configs = rng.integers(0, alphabet, size=(4000, n_plus_1, m)).astype(float)
            for alpha in ALPHAS:
                bound = conformal_firing_count(n_plus_1 - 1, alpha)
                self.assertLessEqual(int(firing_counts_vectorized(configs, alpha).max()), bound, (n_plus_1, m, alphabet, alpha))

    def test_firing_members_matches_vectorized_definition(self) -> None:
        rng = np.random.default_rng(7)
        pts = rng.integers(0, 3, size=(9, 4)).astype(float)
        for alpha in ALPHAS:
            expected = firing_counts_vectorized(pts[None, :, :], alpha)[0]
            self.assertEqual(int(firing_members(pts, alpha).sum()), int(expected))
        scores = augmented_family_scores(pts)
        self.assertEqual(scores.shape, (9,))
        self.assertTrue(np.all((scores >= 0) & (scores <= 1)))


class CounterexamplesOfTheSupersededRuleTests(unittest.TestCase):
    """The five-vector configuration that broke Proposition 5(b) of artifact 1.2.0."""

    @staticmethod
    def _cyclic_configuration() -> np.ndarray:
        # sensor 1: j1 > j2 > j3 > x > y; sensor 2: j2 > j3 > j1 > x > y; sensor 3: j3 > j1 > j2 > x > y
        return np.array(
            [[5, 3, 4], [4, 5, 3], [3, 4, 5], [2, 2, 2], [1, 1, 1]],
            dtype=float,
        )

    def test_legacy_rule_exceeds_its_published_bound(self) -> None:
        pts = self._cyclic_configuration()
        alpha = 0.2
        n = pts.shape[0] - 1
        fires = legacy_v12_firing_members(pts, alpha)
        self.assertEqual(int(fires.sum()), 3)  # 3 of 5 members fire when audited: probability 0.60
        published_bound = (n + 2 - order_statistic_rank(n, alpha)) / (n + 1)  # (n+2-k)/(n+1) = 0.40
        self.assertGreater(fires.mean(), published_bound)
        self.assertGreater(fires.mean(), alpha)

    def test_adopted_rule_respects_the_bound_on_the_same_configuration(self) -> None:
        pts = self._cyclic_configuration()
        for alpha in ALPHAS:
            self.assertLessEqual(int(firing_members(pts, alpha).sum()), conformal_firing_count(4, alpha))
        self.assertEqual(int(firing_members(pts, 0.2).sum()), 0)

    def test_random_search_finds_legacy_violations_but_never_adopted_ones(self) -> None:
        rng = np.random.default_rng(2026)
        legacy_violations = 0
        for _ in range(600):
            n_plus_1 = int(rng.integers(4, 9))
            m = int(rng.integers(2, 5))
            pts = rng.integers(0, 4, size=(n_plus_1, m)).astype(float)
            alpha = float(rng.choice([0.1, 0.2, 0.25, 0.4]))
            bound = conformal_firing_count(n_plus_1 - 1, alpha)
            self.assertLessEqual(int(firing_members(pts, alpha).sum()), bound)
            if int(legacy_v12_firing_members(pts, alpha).sum()) > bound:
                legacy_violations += 1
        self.assertGreater(legacy_violations, 0)


class LargeSampleBehaviourTests(unittest.TestCase):
    def test_single_continuous_sensor_coincides_with_per_sensor_rule(self) -> None:
        rng = np.random.default_rng(0)
        cal = rng.normal(size=200)
        aud = rng.normal(size=5000)
        rank = order_statistic_rank(200, 0.05)
        self.assertEqual(rank, 191)
        expected = aud > np.sort(cal)[rank - 1]
        observed = conformal_family_fires(cal[:, None], aud[:, None], alpha=0.05)
        self.assertTrue(np.array_equal(expected, observed))
        p = conformal_family_pvalues(cal[:, None], aud[:, None])
        self.assertTrue(np.all((p >= 1 / 201) & (p <= 1.0)))

    def test_exact_level_under_exchangeable_continuous_draws(self) -> None:
        rng = np.random.default_rng(11)
        family = 10
        fires = []
        for _ in range(300):
            latent = rng.normal(size=(201, 1))
            pts = 0.7 * latent + rng.normal(size=(201, family))  # dependent sensors
            fires.append(conformal_family_fires(pts[:200], pts[200:201], alpha=0.05)[0])
        rate = float(np.mean(fires))
        self.assertLess(rate, 0.05 + 0.03)

    def test_heavily_tied_draws_stay_below_alpha_and_legacy_rule_does_not(self) -> None:
        rng = np.random.default_rng(5)
        adopted, legacy = [], []
        for _ in range(200):
            pts = rng.integers(0, 3, size=(21, 4)).astype(float)
            adopted.append(firing_members(pts, 0.2).mean())
            legacy.append(legacy_v12_firing_members(pts, 0.2).mean())
        self.assertLessEqual(max(adopted), conformal_firing_count(20, 0.2) / 21 + 1e-12)
        self.assertGreater(max(legacy), 0.2)

    def test_current_nan_fails_closed_and_legacy_v136_is_reproducible(self) -> None:
        rng = np.random.default_rng(3)
        cal = rng.normal(size=(50, 2))
        aud = np.array([[10.0, np.nan], [np.nan, np.nan]])
        with self.assertRaises(ValueError):
            conformal_family_pvalues(cal, aud)
        p = legacy_v136_conformal_family_pvalues(cal, aud)
        self.assertLess(p[0], 0.05)
        self.assertEqual(p[1], 1.0)
        with self.assertRaises(ValueError):
            conformal_family_pvalues(np.array([[np.nan, 1.0]]), aud)


class SplitConstructionTests(unittest.TestCase):
    def test_split_rule_counting_bound_for_every_reference(self) -> None:
        rng = np.random.default_rng(9)
        for n_cal_plus_1, m in ((5, 2), (6, 3), (9, 4)):
            single = weak_orderings(n_cal_plus_1)
            for _ in range(8):
                reference = rng.integers(0, 3, size=(7, m)).astype(float)
                # random tied configurations of the calibration set plus the audited vector
                configs = rng.integers(0, 3, size=(120, n_cal_plus_1, m)).astype(float)
                for alpha in (0.2, 0.25, 0.5):
                    bound = conformal_firing_count(n_cal_plus_1 - 1, alpha)
                    for cfg in configs:
                        fires = 0
                        for j in range(n_cal_plus_1):
                            cal = np.delete(cfg, j, axis=0)
                            _, f = split_conformal_family(reference, cal, cfg[j : j + 1], alpha)
                            fires += int(f[0])
                        self.assertLessEqual(fires, bound)
            _ = single  # exhaustive single-sensor orderings are covered by the adopted rule tests

    def test_split_rule_pvalue_range(self) -> None:
        rng = np.random.default_rng(4)
        reference = rng.normal(size=(100, 3))
        calibration = rng.normal(size=(100, 3))
        values = rng.normal(size=(20, 3))
        p, fires = split_conformal_family(reference, calibration, values, 0.05)
        self.assertTrue(np.all((p >= 1 / 101) & (p <= 1.0)))
        self.assertTrue(np.array_equal(fires, p <= 0.05 + 1e-12))


if __name__ == "__main__":
    unittest.main()
