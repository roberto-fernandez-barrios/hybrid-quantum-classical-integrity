from __future__ import annotations

from pathlib import Path
import unittest

import pandas as pd

from src.experiments.build_q1_gate1_evidence import (
    FULL_SIGNAL_COLS,
    KEY_COLS,
    _deduplicate,
)


def _row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "protocol": "id",
        "dataset_tag": "fixture",
        "svd_dim": 8,
        "split_seed": 42,
        "model_seed": 42,
        "model": "svc_rbf",
        "attack": "clean",
        "bal_acc": 0.75,
        "impact_bal_acc": 0.0,
        "_source_file": "a.csv",
    }
    row.update({column: 0.0 for column in FULL_SIGNAL_COLS})
    row.update(overrides)
    return row


class DeduplicationTests(unittest.TestCase):
    def test_exact_computational_repetitions_are_collapsed(self) -> None:
        first = _row(_source_file="a.csv")
        second = _row(_source_file="b.csv")

        dedup, counts = _deduplicate(pd.DataFrame([first, second]))

        self.assertEqual(len(dedup), 1)
        self.assertFalse(dedup.duplicated(KEY_COLS).any())
        self.assertEqual(counts["duplicate_rows_removed"], 1)
        self.assertEqual(counts["raw_svc_rows"], 2)
        self.assertEqual(counts["unique_svc_rows"], 1)

    def test_conflicting_repetitions_fail_closed(self) -> None:
        first = _row(_source_file="a.csv", impact_bal_acc=0.0)
        second = _row(_source_file="b.csv", impact_bal_acc=0.1)

        with self.assertRaisesRegex(ValueError, "conflicting numerical evidence"):
            _deduplicate(pd.DataFrame([first, second]))


class CommittedEvidenceTests(unittest.TestCase):
    def test_gate1_evidence_has_the_expected_design(self) -> None:
        digest = Path("results/paper_digest/paper15_q1_gate1_id_seeds_20_q1")
        paired_path = digest / "gate1_paired_zz_minus_svc_primary_clustered.csv"
        blind_path = digest / "gate1_structurally_blind_positive_impact_cases.csv"
        if not paired_path.exists() or not blind_path.exists():
            self.skipTest("Gate 1 derived evidence has not been built in this checkout")

        paired = pd.read_csv(paired_path)
        impact = paired[paired["metric"] == "impact_mean"]
        self.assertEqual(set(impact["svd_dim"]), {8, 10, 12})
        self.assertEqual(set(impact["n"]), {5})
        self.assertTrue(impact["all_positive"].all())
        self.assertTrue((impact["ci95_low"] > 0).all())

        blind = pd.read_csv(blind_path)
        self.assertFalse(blind.empty)
        self.assertEqual(set(blind["attack_family"]), {"target_shift"})
        self.assertTrue((blind["prediction_change_mean"].abs() <= 1e-12).all())
        self.assertTrue(blind["feature_prediction_structurally_blind"].all())


if __name__ == "__main__":
    unittest.main()
