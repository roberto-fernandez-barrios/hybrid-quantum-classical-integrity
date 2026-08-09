from __future__ import annotations

import copy
import unittest

import numpy as np
from sklearn.metrics import balanced_accuracy_score

from src.hsaas.contracts import audit_hybrid_run, verify_audit_envelope


class HsaasContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.x_train = np.array([[0.0, 0.2], [0.4, 0.6], [0.8, 1.0], [1.2, 1.4]])
        self.x_test = np.array([[0.1, 0.3], [0.9, 1.1], [1.3, 1.5], [0.5, 0.7]])
        self.train_kernel = np.array(
            [
                [1.0, 0.3, 0.2, 0.1],
                [0.3, 1.0, 0.25, 0.2],
                [0.2, 0.25, 1.0, 0.35],
                [0.1, 0.2, 0.35, 1.0],
            ]
        )
        self.test_kernel = np.array(
            [
                [0.8, 0.3, 0.2, 0.1],
                [0.2, 0.4, 0.7, 0.3],
                [0.1, 0.2, 0.4, 0.9],
                [0.3, 0.8, 0.2, 0.1],
            ]
        )
        self.labels = np.array([0, 1, 1, 0])
        self.predictions = np.array([0, 1, 0, 0])
        self.execution = {
            "executor": "local_exact_statevector",
            "shots": None,
            "qpu": False,
        }

    def _kwargs(self) -> dict[str, object]:
        return {
            "scenario": "test",
            "reference_inputs": {"train": self.x_train, "test": self.x_test},
            "observed_inputs": {"train": self.x_train, "test": self.x_test},
            "reference_preprocessing": {"scaler": "minmax2pi", "dimension": 2},
            "observed_preprocessing": {"scaler": "minmax2pi", "dimension": 2},
            "reference_circuit_sha256": "a" * 64,
            "observed_circuit_sha256": "a" * 64,
            "reference_train_kernel": self.train_kernel,
            "observed_train_kernel": self.train_kernel,
            "reference_test_kernel": self.test_kernel,
            "observed_test_kernel": self.test_kernel,
            "expected_execution": self.execution,
            "observed_execution": self.execution,
            "repeated_estimation_discrepancy": 0.0,
            "reference_predictions": self.predictions,
            "observed_predictions": self.predictions,
            "reference_labels": self.labels,
            "observed_labels": self.labels,
            "reported_metrics": {
                "balanced_accuracy": balanced_accuracy_score(self.labels, self.predictions)
            },
        }

    def test_clean_envelope_allows_and_hash_chain_detects_mutation(self) -> None:
        envelope = audit_hybrid_run(**self._kwargs())
        self.assertEqual(envelope["overall_status"], "pass")
        self.assertEqual(envelope["fail_closed_action"], "allow")
        self.assertTrue(verify_audit_envelope(envelope))

        mutated = copy.deepcopy(envelope)
        mutated["contracts"][0]["evidence"]["observed_input_sha256"] = "0" * 64
        self.assertFalse(verify_audit_envelope(mutated))

    def test_approved_semantic_circuit_rewrite_allows(self) -> None:
        kwargs = self._kwargs()
        kwargs["observed_circuit_sha256"] = "b" * 64
        kwargs["approved_circuit_rewrite"] = True
        envelope = audit_hybrid_run(**kwargs)
        self.assertEqual(envelope["fail_closed_action"], "allow")
        self.assertTrue(verify_audit_envelope(envelope))

    def test_psd_preserving_substitution_blocks_despite_valid_algebra(self) -> None:
        kwargs = self._kwargs()
        kwargs["observed_train_kernel"] = 0.95 * self.train_kernel + 0.05 * np.eye(4)
        kwargs["observed_test_kernel"] = 0.95 * self.test_kernel
        envelope = audit_hybrid_run(**kwargs)
        circuit = next(item for item in envelope["contracts"] if item["name"] == "circuit_kernel")
        algebra = circuit["evidence"]["algebraic"]
        self.assertLessEqual(algebra["symmetry_residual"], 1e-12)
        self.assertLessEqual(algebra["diagonal_residual"], 1e-12)
        self.assertGreaterEqual(algebra["minimum_eigenvalue"], -1e-12)
        self.assertIn("semantic_kernel_mismatch", circuit["violations"])
        self.assertEqual(envelope["fail_closed_action"], "block")

    def test_prior_preserving_label_change_blocks_at_evaluation_contract(self) -> None:
        kwargs = self._kwargs()
        observed_labels = np.array([1, 1, 0, 0])
        kwargs["observed_labels"] = observed_labels
        kwargs["reported_metrics"] = {
            "balanced_accuracy": balanced_accuracy_score(observed_labels, self.predictions)
        }
        envelope = audit_hybrid_run(**kwargs)
        evaluation = next(
            item for item in envelope["contracts"] if item["name"] == "evaluation_report"
        )
        self.assertEqual(evaluation["evidence"]["label_prior_abs_delta"], 0.0)
        self.assertIn("label_provenance_mismatch", evaluation["violations"])
        self.assertEqual(envelope["fail_closed_action"], "block")

    def test_approved_stochastic_estimation_holds_for_review(self) -> None:
        kwargs = self._kwargs()
        observed_train = self.train_kernel.copy()
        observed_train[0, 1] += 0.02
        observed_train[1, 0] += 0.02
        kwargs["observed_train_kernel"] = observed_train
        kwargs["observed_test_kernel"] = self.test_kernel + 0.01
        kwargs["approved_stochastic_estimation"] = True
        kwargs["repeated_estimation_discrepancy"] = 0.05
        envelope = audit_hybrid_run(**kwargs)
        self.assertEqual(envelope["overall_status"], "review")
        self.assertEqual(envelope["fail_closed_action"], "hold")
        self.assertTrue(verify_audit_envelope(envelope))


if __name__ == "__main__":
    unittest.main()
