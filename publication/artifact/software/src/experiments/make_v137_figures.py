"""Regenerate the two manuscript figures affected by the corrected JSD values.

The plotting functions and visual conventions are unchanged.  Only the data
frames are rebuilt from the separately manifested v1.3.7 corrective evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd

from .make_q1_adversarial_figures import _draw as draw_adversarial
from .make_q1_policy_figures import BATCH, REGIME_ORDER, _draw as draw_policy


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _policy_frames(jsd_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    observations = pd.read_csv(jsd_dir / "jsd_corrected_observations.csv", low_memory=False)
    clean = observations[
        (observations["correction_scope"] == "null_draw")
        & (observations["attack_priority_group"] == "null_evaluation")
    ].copy()
    records: list[dict[str, object]] = []
    for regime in BATCH:
        for rule in ("union", "family_v12", "family"):
            column = f"fire_{rule}__{regime}"
            by_environment = clean.groupby("gate")[column].mean()
            records.append(
                {
                    "regime": regime,
                    "rule": rule,
                    "n_draws": len(clean),
                    "n_fire": int(clean[column].astype(bool).sum()),
                    "pooled_rate": float(clean[column].mean()),
                    "environment_cluster_mean_min": float(by_environment.min()),
                    "environment_cluster_mean_max": float(by_environment.max()),
                    "nominal_alpha": 0.05,
                    "conformal_exact_level": 10 / 201,
                }
            )
    panel_a = pd.DataFrame.from_records(records)

    policy = pd.read_csv(jsd_dir / "jsd_primary_policy_effect.csv")
    panel_b = policy[
        (policy["geometry"] == "primary_v137_corrected_jsd")
        & (policy["family_rule"] == "conformal")
    ].copy()
    panel_b["clean_denominator"] = panel_b["n_clean"]
    panel_b["nonmaterial_interruption_rate"] = (
        panel_b["integrity_only_hold_block"] / panel_b["n_immaterial"]
    )
    panel_b["unsafe_allow_rate"] = panel_b["unsafe_allow"] / panel_b["n_material"]
    panel_b["unsafe_allow_label_path"] = pd.NA
    panel_b["containment"] = panel_b["material_held_or_blocked"] / panel_b["n_material"]
    panel_b["residual_blind_material"] = panel_b["regime"].map(
        {"I_X": 2617, "I_XF": 2617, "I_Ym": 5450, "I_XFY": 0, "I_XFY_trusted": 0}
    )
    panel_b["order"] = panel_b["regime"].map({r: i for i, r in enumerate(REGIME_ORDER)})
    columns = [
        "regime", "policy", "n_clean", "clean_denominator", "decision_fpr",
        "n_benign", "benign_hold", "benign_block", "benign_interruption_rate",
        "nonmaterial_interruption_rate", "n_material", "unsafe_allow",
        "unsafe_allow_rate", "unsafe_allow_label_path", "containment",
        "residual_blind_material",
    ]
    return panel_a.sort_values(["regime", "rule"]), panel_b.sort_values(["order", "policy"])[columns]


def _adversarial_frames(jsd_dir: Path, frozen_adversarial: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    observations = pd.read_csv(jsd_dir / "jsd_corrected_observations.csv", low_memory=False)
    gate_a = observations[
        (observations["correction_scope"] == "gateA_original")
        & observations["regime_placeholder"].isna()
    ].copy() if "regime_placeholder" in observations else observations[
        observations["correction_scope"] == "gateA_original"
    ].copy()
    records: list[dict[str, object]] = []
    for (mechanism, attack_class, strength), group in gate_a.groupby(
        ["mechanism", "attack_class", "strength"], sort=True
    ):
        for regime in ("I_X", "I_XF"):
            fire = group[f"fire_family__{regime}"].astype(bool)
            records.append(
                {
                    "mechanism": mechanism,
                    "attack_class": attack_class,
                    "strength": float(strength),
                    "regime": regime,
                    "n": len(group),
                    "n_fire": int(fire.sum()),
                    "detection_rate": float(fire.mean()),
                }
            )
    detection = pd.DataFrame.from_records(records).sort_values(
        ["mechanism", "attack_class", "regime", "strength"]
    )
    # Materiality and predictions do not depend on JSD; retain their frozen values.
    materiality = pd.read_csv(frozen_adversarial / "adversarial_materiality.csv")[[
        "mechanism", "attack_class", "strength", "n", "material_fraction_tau0",
        "material_fraction_tau002", "material_fraction_tau005",
        "prediction_change_rate", "mean_perturbed_entry_fraction",
    ]].sort_values(["mechanism", "attack_class", "strength"])
    return detection, materiality


def _publish(
    stem: str,
    out_dir: Path,
    manuscript_figures: Path,
    manuscript_tables: Path,
    tdsc_figures: Path,
    left: pd.DataFrame,
    right: pd.DataFrame,
    draw,
    sources: list[str],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf, png = out_dir / f"{stem}.pdf", out_dir / f"{stem}.png"
    draw(left, right, [pdf, png])
    values_a = out_dir / f"{stem}_panel_a_values.csv"
    values_b = out_dir / f"{stem}_panel_b_values.csv"
    left.to_csv(values_a, index=False)
    right.to_csv(values_b, index=False)
    manifest = {
        "figure": stem,
        "release": "1.3.7",
        "source_evidence": sources,
        "outputs": {p.name: {"sha256": _sha256(p)} for p in (pdf, png, values_a, values_b)},
    }
    (out_dir / "figure_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for target in (manuscript_figures, tdsc_figures):
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, target / pdf.name)
        if target == manuscript_figures:
            shutil.copy2(png, target / png.name)
    manuscript_tables.mkdir(parents=True, exist_ok=True)
    shutil.copy2(values_a, manuscript_tables / values_a.name)
    shutil.copy2(values_b, manuscript_tables / values_b.name)
    print(json.dumps(manifest, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsd-dir", type=Path, default=Path("results/paper_digest/paper15_v137_jsd_correction"))
    parser.add_argument("--frozen-adversarial", type=Path, default=Path("publication/artifact/evidence/adversarial"))
    parser.add_argument("--out-root", type=Path, default=Path("results/figures/paper15_v137"))
    parser.add_argument("--manuscript-figures", type=Path, default=Path("manuscript/figures"))
    parser.add_argument("--manuscript-tables", type=Path, default=Path("manuscript/tables"))
    parser.add_argument("--tdsc-figures", type=Path, default=Path("publication/tdsc/figures"))
    args = parser.parse_args()

    policy_a, policy_b = _policy_frames(args.jsd_dir)
    _publish(
        "fig_q1_policy_decisions", args.out_root / "policy", args.manuscript_figures,
        args.manuscript_tables, args.tdsc_figures, policy_a, policy_b, draw_policy,
        ["jsd_gate_f_summary.csv", "jsd_primary_policy_effect.csv"],
    )
    adversarial_a, adversarial_b = _adversarial_frames(args.jsd_dir, args.frozen_adversarial)
    _publish(
        "fig_q1_adversarial_cluster_preserving", args.out_root / "adversarial",
        args.manuscript_figures, args.manuscript_tables, args.tdsc_figures,
        adversarial_a, adversarial_b, draw_adversarial,
        ["jsd_corrected_observations.csv", "adversarial_materiality.csv"],
    )


if __name__ == "__main__":
    main()
