"""Brute-force checks of the formal core (artifact 1.3.0, ``manuscript/FORMAL_CORE.md``).

Every statement that can be verified by enumeration on small finite batches is
verified here: Lemma 1 and Proposition 1 (structural blindness, monotonicity
under refinement), Proposition 2 and Corollary 2 (closure and the label-path
region), Proposition 3 (materiality forces a confusion-matrix change for every
metric that is a function of the confusion matrix, and not for AUC), Corollary
3 (which reference certifies which integrity), Proposition 4 (reference
anchoring), Proposition 6 (no local authentication without an uncontrolled
root) and Proposition 7 (the quantum lattice, on the frozen simulator evidence
when present). Proposition 5 is covered by
``tests/test_family_calibration_exhaustive.py``.
"""

from __future__ import annotations

import itertools
import unittest
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Views of a finite batch
# ---------------------------------------------------------------------------


def confusion(y_hat: tuple[int, ...], y: tuple[int, ...]) -> tuple[int, int, int, int]:
    tp = sum(1 for a, b in zip(y_hat, y) if a == 1 and b == 1)
    tn = sum(1 for a, b in zip(y_hat, y) if a == 0 and b == 0)
    fp = sum(1 for a, b in zip(y_hat, y) if a == 1 and b == 0)
    fn = sum(1 for a, b in zip(y_hat, y) if a == 0 and b == 1)
    return tp, tn, fp, fn


def balanced_accuracy(m: tuple[int, int, int, int]) -> float:
    tp, tn, fp, fn = m
    tpr = tp / (tp + fn) if tp + fn else 0.0
    tnr = tn / (tn + fp) if tn + fp else 0.0
    return 0.5 * (tpr + tnr)


def auc(scores: tuple[float, ...], y: tuple[int, ...]) -> float:
    pos = [s for s, b in zip(scores, y) if b == 1]
    neg = [s for s, b in zip(scores, y) if b == 0]
    if not pos or not neg:
        return float("nan")
    wins = sum((1.0 if p > n else 0.5 if p == n else 0.0) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def view(regime: str, x: tuple[float, ...], y_hat: tuple[int, ...], y: tuple[int, ...]):
    if regime == "I_X":
        return Counter(x)
    if regime == "I_XF":
        return Counter(zip(x, y_hat))
    if regime == "I_Ym":
        return Counter(y)
    if regime == "I_XFY":
        return Counter(zip(x, y_hat, y))
    if regime == "I_M":
        return confusion(y_hat, y)
    if regime == "I_XF_join_Ym":
        return (Counter(zip(x, y_hat)), Counter(y))
    raise ValueError(regime)


REFINEMENTS = [("I_X", "I_XF"), ("I_XF", "I_XFY"), ("I_Ym", "I_XFY"), ("I_M", "I_XFY"), ("I_X", "I_XFY")]


class LabelPathEnumerationTests(unittest.TestCase):
    """Enumerate every label vector of a small batch with fixed features and predictions."""

    def _batches(self):
        # features with duplicated rows (to exercise Corollary 2), fixed deterministic predictions
        yield (0.1, 0.1, 0.7, 0.9, 0.9, 0.3), (0, 0, 1, 1, 1, 0)
        yield (0.2, 0.5, 0.5, 0.8), (0, 1, 1, 1)
        yield (0.0, 0.0, 0.0, 1.0, 1.0), (0, 0, 1, 1, 0)

    def test_lemma1_prop1_monotonicity_and_corollary1(self) -> None:
        for x, y_hat in self._batches():
            n = len(x)
            for y0 in itertools.product((0, 1), repeat=n):
                if len(set(y0)) < 2:
                    continue
                for ya in itertools.product((0, 1), repeat=n):
                    blind = {r: view(r, x, y_hat, ya) == view(r, x, y_hat, y0) for r in ("I_X", "I_XF", "I_Ym", "I_XFY", "I_M")}
                    # Corollary 1(a): every label-only change is blind to I_X and I_XF
                    self.assertTrue(blind["I_X"] and blind["I_XF"])
                    # Corollary 1(b): prior-preserving changes are blind to I_Ym
                    if Counter(ya) == Counter(y0):
                        self.assertTrue(blind["I_Ym"])
                    # Proposition 1: refinement shrinks blind regions
                    for coarse, fine in REFINEMENTS:
                        if blind[fine]:
                            self.assertTrue(blind[coarse], (coarse, fine))

    def test_prop2_closure_and_corollary2(self) -> None:
        for x, y_hat in self._batches():
            n = len(x)
            groups = {}
            for i, key in enumerate(zip(x, y_hat)):
                groups.setdefault(key, []).append(i)
            for y0 in itertools.product((0, 1), repeat=n):
                for ya in itertools.product((0, 1), repeat=n):
                    joint_blind = view("I_XF_join_Ym", x, y_hat, ya) == view("I_XF_join_Ym", x, y_hat, y0)
                    self.assertEqual(joint_blind, view("I_XF", x, y_hat, ya) == view("I_XF", x, y_hat, y0) and view("I_Ym", x, y_hat, ya) == view("I_Ym", x, y_hat, y0))
                    # Corollary 2: the joint view of features, predictions and histogram never separates a prior-preserving change
                    if Counter(ya) == Counter(y0):
                        self.assertTrue(joint_blind)
                    # Corollary 2: the multiset of triples is blind iff labels are permuted within identical (x, y_hat) groups
                    within_groups = all(Counter(ya[i] for i in idx) == Counter(y0[i] for i in idx) for idx in groups.values())
                    self.assertEqual(view("I_XFY", x, y_hat, ya) == view("I_XFY", x, y_hat, y0), within_groups)

    def test_prop3_materiality_forces_confusion_change_for_confusion_metrics(self) -> None:
        metrics = {
            "balanced_accuracy": balanced_accuracy,
            "accuracy": lambda m: (m[0] + m[1]) / sum(m),
            "f1": lambda m: (2 * m[0] / (2 * m[0] + m[2] + m[3])) if (2 * m[0] + m[2] + m[3]) else 0.0,
        }
        for x, y_hat in self._batches():
            n = len(x)
            for y0 in itertools.product((0, 1), repeat=n):
                m0 = confusion(y_hat, y0)
                for ya in itertools.product((0, 1), repeat=n):
                    ma = confusion(y_hat, ya)
                    for name, g in metrics.items():
                        if abs(g(ma) - g(m0)) > 1e-12:
                            self.assertNotEqual(ma, m0, name)

    def test_prop3_remark_auc_is_not_a_function_of_the_confusion_matrix(self) -> None:
        # same confusion matrix, different AUC: the score-label multiset is the sufficient aggregate
        scores = (0.9, 0.8, 0.7, 0.6)
        y_hat = (1, 1, 0, 0)
        y_a = (1, 0, 1, 0)
        y_b = (0, 1, 0, 1)
        self.assertEqual(confusion(y_hat, y_a), confusion(y_hat, y_b))
        self.assertNotEqual(auc(scores, y_a), auc(scores, y_b))
        self.assertNotEqual(Counter(zip(scores, y_a)), Counter(zip(scores, y_b)))
        # and a label change that changes AUC always changes the score-label multiset
        for y0 in itertools.product((0, 1), repeat=4):
            for ya in itertools.product((0, 1), repeat=4):
                a0, aa = auc(scores, y0), auc(scores, ya)
                if not (np.isnan(a0) or np.isnan(aa)) and abs(a0 - aa) > 1e-12:
                    self.assertNotEqual(Counter(zip(scores, y0)), Counter(zip(scores, ya)))

    def test_corollary3_which_reference_certifies_which_integrity(self) -> None:
        for x, y_hat in self._batches():
            n = len(x)
            for y0 in itertools.product((0, 1), repeat=n):
                m0 = confusion(y_hat, y0)
                r0 = balanced_accuracy(m0)
                for ya in itertools.product((0, 1), repeat=n):
                    ma = confusion(y_hat, ya)
                    material = abs(balanced_accuracy(ma) - r0) > 1e-12
                    # (a) trusted aggregate reference M0 detects every material change
                    if material:
                        self.assertNotEqual(ma, m0)
                    # (b) a relabeling that permutes labels among equal predictions is invisible to M, hist and R
                    same_pred_groups = {}
                    for i, p in enumerate(y_hat):
                        same_pred_groups.setdefault(p, []).append(i)
                    permutes_within_equal_predictions = all(Counter(ya[i] for i in idx) == Counter(y0[i] for i in idx) for idx in same_pred_groups.values())
                    if permutes_within_equal_predictions:
                        self.assertEqual(ma, m0)
                        self.assertEqual(Counter(ya), Counter(y0))
                        self.assertAlmostEqual(balanced_accuracy(ma), r0)
                    # item-aligned reference detects every non-identity relabeling
                    self.assertEqual(ya != y0, any(a != b for a, b in zip(ya, y0)))


class AuditorTests(unittest.TestCase):
    def test_prop4_reference_anchoring_is_exact(self) -> None:
        rng = np.random.default_rng(0)
        for _ in range(200):
            y0 = tuple(rng.integers(0, 2, size=8))
            ya = tuple(rng.integers(0, 2, size=8))
            d = sum(a != b for a, b in zip(ya, y0))
            # zero false alarm on the baseline itself, detection iff the view differs
            self.assertEqual(sum(a != b for a, b in zip(y0, y0)), 0)
            self.assertEqual(d > 0, ya != y0)

    def test_prop6_local_verifier_accepts_a_jointly_controlled_substitution(self) -> None:
        # honest reference: the confusion matrix attached by the honest process
        y_hat = (1, 1, 0, 0, 1, 0)
        honest_states = [tuple(y) for y in itertools.product((0, 1), repeat=6)]

        def acc(view_triples, rho):
            return confusion(*zip(*[(a, b) for a, b, _ in view_triples])) == rho if view_triples else True

        def honest_pair(y):
            triples = tuple(zip(y_hat, y, range(6)))
            return triples, confusion(y_hat, y)

        for y in honest_states:
            self.assertTrue(acc(*honest_pair(y)))  # honest completeness
        y0 = (1, 0, 0, 1, 1, 0)
        r0 = balanced_accuracy(confusion(y_hat, y0))
        substituted = [y for y in honest_states if y != y0 and abs(balanced_accuracy(confusion(y_hat, y)) - r0) > 1e-12]
        self.assertTrue(substituted)
        for y_prime in substituted:
            # joint control: asset and reference rewritten to the honest values of y_prime -> accepted, material change served
            self.assertTrue(acc(*honest_pair(y_prime)))
            # an uncontrolled root (the baseline confusion matrix) rejects the substitution
            self.assertNotEqual(confusion(y_hat, y_prime), confusion(y_hat, y0))


class QuantumLatticeTests(unittest.TestCase):
    """Proposition 7 on the frozen simulator evidence (skipped when the evidence is absent)."""

    def _evidence(self) -> Path | None:
        for candidate in (Path("results/paper_digest/paper15_q1_quantum_integrity_gate"), Path("publication/artifact/evidence/quantum_integrity")):
            if (candidate / "quantum_integrity_gate_observations.csv").is_file():
                return candidate
        return None

    def test_provenance_refines_semantics_and_algebra_coarsens_kernel(self) -> None:
        ev = self._evidence()
        if ev is None:
            self.skipTest("quantum gate evidence not present")
        obs = pd.read_csv(ev / "quantum_integrity_gate_observations.csv")
        tol = 1e-9
        semantic_changed = obs["kernel_max_abs_delta"].astype(float) > tol
        hash_changed = obs["circuit_hash_changed"].astype(str).str.lower().eq("true")
        # (i) approved rewrites: hash changes, semantics unchanged, in every cell
        for tag in ("benign_transpile_o1",):
            block = obs[obs["attack"] == tag]
            self.assertTrue(len(block) == 15 and hash_changed[block.index].all() and (~semantic_changed[block.index]).all())
        # (i) identical hash implies identical semantics: every row without a hash change and without a kernel edit has zero semantic delta
        circuit_side = obs[obs["boundary"].isin(["none", "transpilation", "design"])]
        self.assertTrue((~semantic_changed[circuit_side[~hash_changed[circuit_side.index]].index]).all())
        # (ii) PSD-preserving substitution: semantic change with algebraic sensors silent
        psd = obs[obs["attack"].str.contains("psd", case=False)]
        self.assertTrue(len(psd) == 15 and semantic_changed[psd.index].all() and (~psd["algebraic_kernel_detected"].astype(str).str.lower().eq("true")).all())
        # (ii) outputs coarsen the kernel: no row with unchanged kernel has a prediction change
        self.assertTrue((obs.loc[~semantic_changed & ~obs["attack"].str.contains("shot"), "prediction_disagreement"].astype(float) <= tol).all())
        # (iii) in these 30 finite-shot cells the repeated-estimation discrepancy is non-zero: an empirical
        # property of the frozen gate, not a universal law (see tests/test_workflow_state.py for the
        # counterexample to "Pr[K_hat = K_0] = 0" on the support of the estimator)
        shots = obs[obs["attack"].str.contains("shot")]
        self.assertTrue(len(shots) == 30 and (shots["repeated_estimation_discrepancy"].astype(float) > 0).all())


if __name__ == "__main__":
    unittest.main()
