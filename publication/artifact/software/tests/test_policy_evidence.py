"""Design and consistency tests for the committed policy and adversarial evidence (artifact 1.3.0).

These tests skip when the derived evidence is not present (fresh checkout
without ``results/`` or without the compact artifact); they run in CI against
the compact artifact under ``publication/artifact``.
"""

from __future__ import annotations

from pathlib import Path
import unittest

import pandas as pd


def _evidence_dir(name: str, manifest: str) -> Path | None:
    for candidate in (Path(f"results/paper_digest/{name}"), Path(f"publication/artifact/evidence/{ {'paper15_v12_policy': 'policy', 'paper15_v13_adversarial': 'adversarial'}[name] }")):
        if (candidate / manifest).is_file():
            return candidate
    return None


class PolicyEvidenceDesignTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ev = _evidence_dir("paper15_v12_policy", "policy_evidence_manifest.json")
        if self.ev is None:
            self.skipTest("policy evidence has not been built in this checkout")

    def test_conformal_rule_never_exceeds_union_rule_and_label_path_is_zero(self) -> None:
        fpr = pd.read_csv(self.ev / "family_false_alarm_overall.csv")
        primary = fpr[fpr["aggregate"] == "all_eight_environments"]
        self.assertEqual(set(fpr["aggregate"]), {"all_eight_environments", "excluding_E1", "E1_only"})
        for regime, block in primary.groupby("regime"):
            union = float(block[block["rule"] == "union"]["pooled_rate"].iloc[0])
            legacy = float(block[block["rule"] == "family_v12"]["pooled_rate"].iloc[0])
            family = float(block[block["rule"] == "family"]["pooled_rate"].iloc[0])
            self.assertLessEqual(family, union + 1e-12, regime)
            self.assertLessEqual(family, legacy + 1e-12, regime)
            self.assertEqual(int(block["n_draws"].iloc[0]), 12000)
        label = pd.read_csv(self.ev / "family_label_path_summary.csv")
        for regime in ("I_X", "I_XF"):
            self.assertEqual(int(label[(label["subset"] == "all_label_interventions") & (label["regime"] == regime)]["n_fire"].sum()), 0)
        prior = label[(label["subset"] == "prior_preserving_label_interventions") & (label["regime"] == "I_Ym")]
        self.assertEqual(int(prior["n_fire"].sum()), 0)
        exact = label[(label["subset"] == "material_label_interventions") & (label["regime"] == "I_XFY_trusted")].iloc[0]
        self.assertEqual(int(exact["n"]), int(exact["n_fire"]))
        self.assertEqual(int(exact["n"]), 2617)

    def test_decomposition_and_resplits_are_consistent(self) -> None:
        dec = pd.read_csv(self.ev / "family_excess_decomposition.csv").set_index("regime")
        for regime, r in dec.iterrows():
            self.assertAlmostEqual(r["rule_bias_v12_minus_conformal"] + r["design_effect_conformal_minus_nominal"], r["v12_excess_over_nominal"], places=12)
            self.assertLessEqual(r["resplit_conformal_rate"], r["conformal_exact_level"] + 0.005, regime)
        resplit = pd.read_csv(self.ev / "family_resplit_pooled.csv")
        self.assertEqual(int(resplit["n_resplits"].iloc[0]), 30)
        self.assertEqual(int(resplit["seed"].iloc[0]), 20260907)

    def test_policy_metrics_are_internally_consistent(self) -> None:
        m = pd.read_csv(self.ev / "policy_metrics.csv")
        self.assertEqual(set(m["policy"]), {"serve_always", "union_uncalibrated", "family_calibrated", "family_calibrated_strict"})
        self.assertEqual(set(m["regime"]), {"I_X", "I_XF", "I_Ym", "I_XFY", "I_XFY_trusted"})
        for _, r in m.iterrows():
            self.assertEqual(int(r["unsafe_allow"] + r["true_hold"] + r["true_block"]), int(r["n_material"]))
            self.assertEqual(int(r["n_material"] + r["n_immaterial"]), int(r["n_intervened"]))
            self.assertLessEqual(int(r["residual_blind_material"]), int(r["n_material"]))
            self.assertEqual(int(r["n_benign"]), 1200)
            self.assertAlmostEqual(float(r["benign_interruption_rate"]), (r["benign_hold"] + r["benign_block"]) / 1200.0, places=12)
            if r["policy"] == "serve_always":
                self.assertEqual(int(r["unsafe_allow"]), int(r["n_material"]))
                self.assertEqual(float(r["decision_fpr"]), 0.0)
            if r["regime"] == "I_XFY_trusted" and r["policy"] != "serve_always":
                self.assertEqual(int(r["unsafe_allow"]), 0)
                self.assertEqual(int(r["false_hold"] + r["false_block"]), 0)
                self.assertEqual(int(r["n_clean"]), 1200)
        primary = m[m["tau"] == 0.0].set_index(["regime", "policy"])
        for regime in ("I_X", "I_XF", "I_Ym"):
            self.assertEqual(int(primary.loc[(regime, "family_calibrated_strict"), "unsafe_allow"]), 0)
            self.assertEqual(float(primary.loc[(regime, "family_calibrated_strict"), "decision_fpr"]), 1.0)
        self.assertEqual(int(primary.loc[("I_X", "family_calibrated"), "residual_blind_material"]), 2617)
        # the trusted regime is not free: its benign interruption is comparable to P2's in the batch regimes
        self.assertGreater(float(primary.loc[("I_XFY_trusted", "family_calibrated"), "benign_interruption_rate"]), 0.4)
        comparison = pd.read_csv(self.ev / "policy_metrics_rule_comparison.csv")
        self.assertEqual(set(comparison["family_rule"]), {"conformal", "v12_asymmetric"})
        taxonomy = pd.read_csv(self.ev / "policy_taxonomy.csv").set_index("policy")
        self.assertIn("risk-tolerant", taxonomy.loc["family_calibrated", "policy_class"])
        self.assertIn("fail-closed", taxonomy.loc["family_calibrated_strict", "policy_class"])

    def test_witnesses_and_composition(self) -> None:
        w = pd.read_csv(self.ev / "counterexample_witnesses.csv").set_index("witness")
        self.assertEqual(int(w.loc["W8", "count"]), int(w.loc["W8", "denominator"]))
        self.assertEqual(int(w.loc["W2", "count"]), 2617)
        self.assertEqual(int(w.loc["W7", "count"]), 1534)
        comp = pd.read_csv(self.ev / "policy_contract_composition.csv")
        self.assertEqual(len(comp), 6)
        self.assertTrue(bool(comp["agreement"].all()))


class AdversarialEvidenceDesignTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ev = _evidence_dir("paper15_v13_adversarial", "adversarial_evidence_manifest.json")
        if self.ev is None:
            self.skipTest("adversarial evidence has not been built in this checkout")

    def test_design_and_replay(self) -> None:
        design = pd.read_csv(self.ev / "adversarial_gate_completeness.csv")
        self.assertEqual(len(design), 8)
        self.assertTrue(bool(design["complete"].all()))
        replay = pd.read_csv(self.ev / "adversarial_replay_consistency.csv")
        self.assertTrue(bool(replay["within_1e-9"].all()))
        self.assertEqual(int(replay["n_rows"].iloc[0]), 4200)

    def test_adaptive_variants_evade_and_keep_materiality(self) -> None:
        det = pd.read_csv(self.ev / "adversarial_detection_pooled.csv")
        fam = det[det["rule"] == "family"].set_index(["mechanism", "attack_class", "strength", "regime"])
        mat = pd.read_csv(self.ev / "adversarial_materiality.csv").set_index(["mechanism", "attack_class", "strength"])
        for mech in ("mean_shift", "scaling_drift"):
            for s in (0.02, 0.05, 0.10):
                for regime in ("I_X", "I_XF"):
                    self.assertLess(fam.loc[(mech, "adaptive", s, regime), "detection_rate"], fam.loc[(mech, "control", s, regime), "detection_rate"])
                self.assertGreater(mat.loc[(mech, "adaptive", s), "material_fraction_tau0"], 0.8 * mat.loc[(mech, "control", s), "material_fraction_tau0"])
                self.assertEqual(int(fam.loc[(mech, "adaptive", s, "I_X"), "n"]), 600)
        pol = pd.read_csv(self.ev / "adversarial_policy_metrics.csv")
        trusted = pol[(pol["regime"] == "I_XFY_trusted") & (pol["tau"] == 0.0)]
        self.assertEqual(int(trusted["unsafe_allow"].sum()), 0)
        p2 = pol[(pol["regime"] == "I_XF") & (pol["policy"] == "family_calibrated") & (pol["tau"] == 0.0)]
        self.assertGreater(int(p2[p2["attack_class"] == "adaptive"]["unsafe_allow"].sum()), int(p2[p2["attack_class"] == "control"]["unsafe_allow"].sum()))
        budget = pd.read_csv(self.ev / "adversarial_budget.csv")
        self.assertTrue(bool(((budget["perturbed_entry_fraction_mean"] > 0) & (budget["perturbed_entry_fraction_mean"] < 1)).all()))


if __name__ == "__main__":
    unittest.main()
