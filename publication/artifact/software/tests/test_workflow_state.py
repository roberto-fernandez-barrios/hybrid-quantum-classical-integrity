"""Intervention semantics of the workflow state and the finite-shot arithmetic of Proposition 7(iii) (artifact 1.3.1).

The tests check the executable counterpart of Section 1 and Section 6 of
``manuscript/FORMAL_CORE.md``: an intervention overwrites declared nodes,
keeps every non-descendant fixed and recomputes the descendants; the three
kernel notions ``K_sem`` / ``K_hat`` / ``K_obs`` respond to different
intervention classes; and exact equality with the ideal kernel is not a
universally failing acceptance rule under finite-shot estimation.
"""

from __future__ import annotations

import unittest
from fractions import Fraction
from math import comb

from src.integrity.workflow_state import (
    DERIVED_NODES,
    PRIMITIVE_NODES,
    State,
    Workflow,
    binomial_equality_probability,
    descendants,
    exact_equality_false_alarm,
    finite_shot_equality_probability,
    intervention_class,
)


def _workflow() -> Workflow:
    # A deliberately small, fully deterministic workflow on tuples.
    return Workflow(
        preprocess=lambda P, X: tuple(P * x for x in X),
        semantic_kernel=lambda C: tuple(tuple(1.0 if i == j else C for j in range(2)) for i in range(2)),
        # "estimation": round every off-diagonal entry on a grid of resolution 1/E, shifted by the seed.
        estimate=lambda K, E, xi: tuple(tuple(round(v * E + xi) / E if i != j else 1.0 for j, v in enumerate(row)) for i, row in enumerate(K)),
        post_process=lambda g, K: g(K),
        predict=lambda f, Xt, K: tuple(f(x, K) for x in Xt),
        conclude=lambda y_hat, y: sum(1 for a, b in zip(y_hat, y) if a == b) / len(y),
    )


def _baseline() -> State:
    return State.from_primitives(
        _workflow(),
        X=(0.2, 0.6, 0.9, 0.4),
        P=1.0,
        C=0.5,
        E=4,
        xi=0,
        g=lambda K: K,
        f=lambda x, K: 1 if x + K[0][1] > 0.9 else 0,
        y=(0, 1, 1, 0),
    )


class InterventionSemanticsTests(unittest.TestCase):
    def test_descendant_closure_follows_the_declared_graph(self) -> None:
        self.assertEqual(descendants(["y"]), frozenset({"R"}))
        self.assertEqual(descendants(["C"]), frozenset({"K_sem", "K_hat", "K_obs", "y_hat", "R"}))
        self.assertEqual(descendants(["xi"]), frozenset({"K_hat", "K_obs", "y_hat", "R"}))
        self.assertEqual(descendants(["K_obs"]), frozenset({"y_hat", "R"}))
        self.assertEqual(descendants(["X_tilde"]), frozenset({"y_hat", "R"}))
        self.assertEqual(set(PRIMITIVE_NODES) & set(DERIVED_NODES), set())

    def test_label_only_intervention_recomputes_only_the_conclusion(self) -> None:
        s0 = _baseline()
        sa = s0.intervene(y=(1, 0, 1, 0))
        changed = s0.changed_nodes(sa)
        self.assertEqual(changed, frozenset({"y", "R"}))
        self.assertEqual(sa["y_hat"], s0["y_hat"])
        self.assertEqual(sa["X_tilde"], s0["X_tilde"])
        self.assertEqual(intervention_class(["y"]), "label_only")

    def test_feature_attack_on_the_representation_recomputes_predictions_and_conclusion(self) -> None:
        s0 = _baseline()
        sa = s0.intervene(X_tilde=(0.9, 0.9, 0.9, 0.9))
        changed = s0.changed_nodes(sa)
        self.assertIn("X_tilde", changed)
        self.assertIn("y_hat", changed)
        self.assertNotIn("X", changed)  # the upstream source is untouched by construction
        self.assertNotIn("K_sem", changed)
        self.assertEqual(sa["y"], s0["y"])
        self.assertEqual(intervention_class(["X_tilde"]), "feature_side")

    def test_circuit_intervention_changes_semantic_estimated_and_observed_kernels(self) -> None:
        s0 = _baseline()
        sa = s0.intervene(C=0.75)
        changed = s0.changed_nodes(sa)
        self.assertTrue({"C", "K_sem", "K_hat", "K_obs"} <= changed)
        self.assertNotIn("y", changed)
        self.assertEqual(intervention_class(["C"]), "circuit_side")

    def test_estimation_variation_keeps_the_semantic_kernel_fixed(self) -> None:
        s0 = _baseline()
        sa = s0.intervene(xi=1)
        changed = s0.changed_nodes(sa)
        self.assertIn("K_hat", changed)
        self.assertNotIn("K_sem", changed)
        self.assertNotIn("C", changed)
        self.assertEqual(intervention_class(["xi"]), "estimation_variation")
        self.assertEqual(intervention_class(["E"]), "estimation_variation")

    def test_post_processing_substitution_changes_only_the_observed_kernel_branch(self) -> None:
        s0 = _baseline()
        k_obs = tuple(tuple(0.99 if i != j else 1.0 for j in range(2)) for i in range(2))
        sa = s0.intervene(K_obs=k_obs)
        changed = s0.changed_nodes(sa)
        self.assertIn("K_obs", changed)
        self.assertNotIn("K_sem", changed)
        self.assertNotIn("K_hat", changed)
        self.assertNotIn("C", changed)
        self.assertEqual(intervention_class(["K_obs"]), "post_processing")
        # A trusted semantic probe K_sem(C) cannot see this class; only a reference on K_obs can.
        self.assertEqual(sa["K_sem"], s0["K_sem"])
        self.assertNotEqual(sa["K_obs"], s0["K_obs"])

    def test_mixed_and_unknown_override_sets_are_named(self) -> None:
        self.assertEqual(intervention_class(["C", "y"]), "mixed")
        self.assertEqual(intervention_class(["f"]), "other")
        with self.assertRaises(KeyError):
            descendants(["K_secret"])
        with self.assertRaises(ValueError):
            _baseline().intervene()


class FiniteShotEqualityTests(unittest.TestCase):
    """Proposition 7(iii): exact equality is not a universally failing rule under shot noise."""

    def test_counterexample_p_half_two_shots(self) -> None:
        # Pr[X/2 = 1/2] = Pr[X = 1] = 1/2, so the exact-equality rule has false-alarm probability 1/2, not 1.
        self.assertAlmostEqual(binomial_equality_probability(0.5, 2), 0.5)
        self.assertAlmostEqual(exact_equality_false_alarm([0.5], 2), 0.5)

    def test_false_alarm_equals_one_only_off_the_support(self) -> None:
        self.assertEqual(binomial_equality_probability(1 / 3, 2), 0.0)
        self.assertEqual(exact_equality_false_alarm([1 / 3], 2), 1.0)
        self.assertEqual(exact_equality_false_alarm([1.0], 5), 0.0)  # degenerate entry (unit diagonal)
        self.assertEqual(exact_equality_false_alarm([0.0], 5), 0.0)

    def test_exact_binomial_mass_on_the_support(self) -> None:
        for shots in (2, 4, 8, 16):
            for k in range(shots + 1):
                p = Fraction(k, shots)
                expected = comb(shots, k) * float(p) ** k * float(1 - p) ** (shots - k)
                self.assertAlmostEqual(binomial_equality_probability(float(p), shots), expected)

    def test_kernel_with_several_entries_multiplies_and_never_exceeds_one_entry(self) -> None:
        self.assertAlmostEqual(finite_shot_equality_probability([0.5, 0.5], 2), 0.25)
        self.assertLessEqual(exact_equality_false_alarm([0.5, 0.25], 4), 1.0)
        self.assertGreaterEqual(exact_equality_false_alarm([0.5, 0.25], 4), exact_equality_false_alarm([0.5], 4))

    def test_the_universal_claim_is_false(self) -> None:
        # The statement "Pr[K_hat = K_0] = 0 under non-degenerate shot noise" fails on the support.
        witnesses = [(p, n) for n in (2, 4, 10) for p in (0.5, 0.25, 0.1) if finite_shot_equality_probability([p], n) > 0]
        self.assertTrue(witnesses)
        self.assertTrue(all(exact_equality_false_alarm([p], n) < 1.0 for p, n in witnesses))


if __name__ == "__main__":
    unittest.main()
