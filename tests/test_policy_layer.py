"""Unit tests for the artifact 1.2.0 policy layer and family-wise calibration.

The tests need neither the derived evidence nor Qiskit. They cover the
rank-score statistic, the single-sensor equivalence with the 1.1.0 per-sensor
rule, the empirical false-alarm level of the family rule under exchangeable
draws, the decision lattice, the fail-closed strict policy, and the
composition with the frozen contract actions.
"""

from __future__ import annotations

import unittest

import numpy as np

from src.hsaas.policy import BOUNDARIES, POLICIES, REGIMES, Evidence, compose, decide, unverified_boundaries
from src.integrity.family_calibration import (
    calibrate_family,
    family_fires,
    family_scores,
    family_threshold,
    order_statistic_rank,
    rank_scores,
)


class FamilyCalibrationTests(unittest.TestCase):
    def test_rank_score_counts_strictly_smaller_calibration_values(self) -> None:
        cal = np.array([0.1, 0.2, 0.2, 0.3])
        scores = rank_scores(np.array([0.05, 0.2, 0.25, 0.4, np.nan]), cal)
        self.assertTrue(np.allclose(scores, [0.0, 0.25, 0.75, 1.0, 0.0]))

    def test_single_sensor_family_matches_per_sensor_order_statistic_rule(self) -> None:
        rng = np.random.default_rng(0)
        cal = {"s": rng.normal(size=200)}
        rank = order_statistic_rank(200, 0.05)
        self.assertEqual(rank, 191)
        per_sensor_threshold = float(np.sort(cal["s"])[rank - 1])
        q, _ = calibrate_family(cal, ["s"], 0.05)
        values = {"s": rng.normal(size=5000)}
        expected = values["s"] > per_sensor_threshold
        observed = family_fires(values, cal, ["s"], q)
        self.assertTrue(np.array_equal(expected, observed))

    def test_family_rule_controls_false_alarms_under_exchangeability(self) -> None:
        rng = np.random.default_rng(1)
        family = [f"s{i}" for i in range(6)]
        rates = []
        for _ in range(40):
            cal = {s: rng.exponential(size=200) for s in family}
            q, _ = calibrate_family(cal, family, 0.05)
            fresh = {s: rng.exponential(size=200) for s in family}
            union = np.any(np.stack([fresh[s] > np.sort(cal[s])[190] for s in family]), axis=0)
            rates.append((float(np.mean(family_fires(fresh, cal, family, q))), float(np.mean(union))))
        family_rate = float(np.mean([r[0] for r in rates]))
        union_rate = float(np.mean([r[1] for r in rates]))
        self.assertLess(abs(family_rate - 0.05), 0.02)
        self.assertGreater(union_rate, 0.15)

    def test_threshold_is_order_statistic_of_calibration_family_scores(self) -> None:
        scores = np.linspace(0.0, 1.0, 200)
        self.assertAlmostEqual(family_threshold(scores, 0.05), float(np.sort(scores)[190]))
        self.assertEqual(family_threshold(np.array([0.1, 0.2]), 0.05), float("inf"))
        with self.assertRaises(ValueError):
            family_scores({"a": np.zeros(3)}, {"a": np.zeros(3)}, [])


class PolicyDecisionTests(unittest.TestCase):
    def test_serve_always_allows_everything(self) -> None:
        for regime in REGIMES:
            exact = False if REGIMES[regime].trusted_reference else None
            self.assertEqual(decide("serve_always", regime, Evidence(True, True, exact)).action, "allow")

    def test_block_is_reserved_for_exact_violations_under_trusted_reference(self) -> None:
        d = decide("family_calibrated", "I_XFY_trusted", Evidence(False, False, True))
        self.assertEqual(d.action, "block")
        self.assertIn("exact_invariant_violated", d.reasons)
        for regime in ("I_X", "I_XF", "I_Ym", "I_XFY"):
            for policy in ("union_uncalibrated", "family_calibrated", "family_calibrated_strict"):
                self.assertNotEqual(decide(policy, regime, Evidence(True, True, None)).action, "block")

    def test_union_and_family_policies_use_their_own_statistic(self) -> None:
        self.assertEqual(decide("union_uncalibrated", "I_XFY", Evidence(True, False, None)).action, "hold")
        self.assertEqual(decide("family_calibrated", "I_XFY", Evidence(True, False, None)).action, "allow")
        self.assertEqual(decide("family_calibrated", "I_XFY", Evidence(False, True, None)).action, "hold")

    def test_strict_policy_holds_on_unverified_protected_boundary(self) -> None:
        for regime in ("I_X", "I_XF", "I_Ym"):
            d = decide("family_calibrated_strict", regime, Evidence(False, False, None))
            self.assertEqual(d.action, "hold")
            self.assertTrue(any(r.startswith("unverified_boundary:label") for r in d.reasons))
        for regime in ("I_XFY", "I_XFY_trusted"):
            exact = False if REGIMES[regime].trusted_reference else None
            d = decide("family_calibrated_strict", regime, Evidence(False, False, exact))
            self.assertEqual(d.action, "allow")
            self.assertEqual(unverified_boundaries(REGIMES[regime]), ())

    def test_residual_blind_region_is_declared_on_allow(self) -> None:
        d = decide("family_calibrated", "I_XF", Evidence(False, False, None))
        self.assertEqual(d.action, "allow")
        self.assertIn("allowed_with_residual_blind_region:label", d.reasons)
        self.assertEqual(unverified_boundaries(REGIMES["I_XF"], BOUNDARIES), ("label",))

    def test_evidence_shape_is_validated(self) -> None:
        with self.assertRaises(ValueError):
            decide("family_calibrated", "I_XFY_trusted", Evidence(False, False, None))
        with self.assertRaises(ValueError):
            decide("family_calibrated", "I_X", Evidence(False, False, False))
        with self.assertRaises(ValueError):
            decide("unknown_policy", "I_X", Evidence(False, False, None))

    def test_decisions_are_deterministic_and_total(self) -> None:
        for policy in POLICIES:
            for regime, spec in REGIMES.items():
                for union in (False, True):
                    for family in (False, True):
                        exact_options = (False, True) if spec.trusted_reference else (None,)
                        for exact in exact_options:
                            first = decide(policy, regime, Evidence(union, family, exact))
                            second = decide(policy, regime, Evidence(union, family, exact))
                            self.assertEqual(first, second)
                            self.assertTrue(first.reasons)

    def test_composition_is_lattice_maximum(self) -> None:
        self.assertEqual(compose("allow", "allow"), "allow")
        self.assertEqual(compose("hold", "allow"), "hold")
        self.assertEqual(compose("allow", "block"), "block")
        self.assertEqual(compose("block", "hold"), "block")
        with self.assertRaises(ValueError):
            compose("allow", "deny")


if __name__ == "__main__":
    unittest.main()
