"""Design and consistency tests for the committed 1.2.0 policy evidence.

These tests skip when the derived evidence is not present (fresh checkout
without ``results/`` or without the compact artifact); they run in CI against
the compact artifact under ``publication/artifact``.
"""

from __future__ import annotations

from pathlib import Path
import unittest

import pandas as pd


def _evidence_dir() -> Path | None:
    for candidate in (Path("results/paper_digest/paper15_v12_policy"), Path("publication/artifact/evidence/policy")):
        if (candidate / "policy_evidence_manifest.json").is_file():
            return candidate
    return None


class PolicyEvidenceDesignTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ev = _evidence_dir()
        if self.ev is None:
            self.skipTest("policy evidence has not been built in this checkout")

    def test_family_rule_never_exceeds_union_rule_and_label_path_is_zero(self) -> None:
        fpr = pd.read_csv(self.ev / "family_false_alarm_overall.csv")
        for regime, block in fpr.groupby("regime"):
            union = float(block[block["rule"] == "union"]["pooled_rate"].iloc[0])
            family = float(block[block["rule"] == "family"]["pooled_rate"].iloc[0])
            self.assertLessEqual(family, union + 1e-12, regime)
            self.assertEqual(int(block["n_draws"].iloc[0]), 12000)
        label = pd.read_csv(self.ev / "family_label_path_summary.csv")
        for regime in ("I_X", "I_XF"):
            self.assertEqual(int(label[(label["subset"] == "all_label_interventions") & (label["regime"] == regime)]["n_fire"].sum()), 0)
        prior = label[(label["subset"] == "prior_preserving_label_interventions") & (label["regime"] == "I_Ym")]
        self.assertEqual(int(prior["n_fire"].sum()), 0)
        exact = label[(label["subset"] == "material_label_interventions") & (label["regime"] == "I_XFY_trusted")].iloc[0]
        self.assertEqual(int(exact["n"]), int(exact["n_fire"]))
        self.assertEqual(int(exact["n"]), 2617)

    def test_policy_metrics_are_internally_consistent(self) -> None:
        m = pd.read_csv(self.ev / "policy_metrics.csv")
        self.assertEqual(set(m["policy"]), {"serve_always", "union_uncalibrated", "family_calibrated", "family_calibrated_strict"})
        self.assertEqual(set(m["regime"]), {"I_X", "I_XF", "I_Ym", "I_XFY", "I_XFY_trusted"})
        for _, r in m.iterrows():
            self.assertEqual(int(r["unsafe_allow"] + r["true_hold"] + r["true_block"]), int(r["n_material"]))
            self.assertEqual(int(r["n_material"] + r["n_immaterial"]), int(r["n_intervened"]))
            self.assertLessEqual(int(r["residual_blind_material"]), int(r["n_material"]))
            if r["policy"] == "serve_always":
                self.assertEqual(int(r["unsafe_allow"]), int(r["n_material"]))
                self.assertEqual(float(r["decision_fpr"]), 0.0)
            if r["regime"] == "I_XFY_trusted" and r["policy"] != "serve_always":
                self.assertEqual(int(r["unsafe_allow"]), 0)
                self.assertEqual(int(r["false_hold"] + r["false_block"]), 0)
        primary = m[m["tau"] == 0.0].set_index(["regime", "policy"])
        for regime in ("I_X", "I_XF", "I_Ym"):
            self.assertEqual(int(primary.loc[(regime, "family_calibrated_strict"), "unsafe_allow"]), 0)
            self.assertEqual(float(primary.loc[(regime, "family_calibrated_strict"), "decision_fpr"]), 1.0)
        self.assertEqual(int(primary.loc[("I_X", "family_calibrated"), "residual_blind_material"]), 2617)

    def test_witnesses_and_composition(self) -> None:
        w = pd.read_csv(self.ev / "counterexample_witnesses.csv").set_index("witness")
        self.assertEqual(int(w.loc["W8", "count"]), int(w.loc["W8", "denominator"]))
        self.assertEqual(int(w.loc["W2", "count"]), 2617)
        self.assertEqual(int(w.loc["W7", "count"]), 1534)
        comp = pd.read_csv(self.ev / "policy_contract_composition.csv")
        self.assertEqual(len(comp), 6)
        self.assertTrue(bool(comp["agreement"].all()))


if __name__ == "__main__":
    unittest.main()
