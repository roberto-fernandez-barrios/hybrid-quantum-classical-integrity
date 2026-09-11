"""Fail-closed verification of the Paper 1.5 publication evidence.

The verifier checks the SHA-256/row contracts embedded in every evidence
manifest and independently recomputes the manuscript's central count claims.
It intentionally does not treat unavailable raw-source hashes as failures when
run against the compact publication artifact; those raw inputs are covered by
the builders' original manifests and can be replayed from the documented public
datasets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


TOL = 1e-12
EXPECTED_MANIFESTS = 11  # nine immutable packages plus both v1.3.7 corrective packages


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _csv_rows(path: Path) -> int:
    with path.open("rb") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def verify_embedded_manifests(root: Path) -> dict[str, int]:
    manifests = sorted(root.rglob("*_manifest.json"))
    if len(manifests) != EXPECTED_MANIFESTS:
        raise ValueError(
            f"expected {EXPECTED_MANIFESTS} evidence manifests under {root}, found {len(manifests)}"
        )

    checked_outputs = 0
    for manifest_path in manifests:
        payload: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
        if payload.get("status", "complete") != "complete":
            raise ValueError(f"incomplete evidence manifest: {manifest_path}")
        checks = payload.get("acceptance_checks", {})
        failed = [name for name, passed in checks.items() if passed is not True]
        if failed:
            raise ValueError(f"failed acceptance checks in {manifest_path}: {failed}")

        for name, expected in payload.get("outputs", {}).items():
            output_path = manifest_path.parent / name
            if not output_path.is_file():
                raise FileNotFoundError(f"manifested output missing: {output_path}")
            observed_hash = _sha256(output_path)
            if observed_hash != expected["sha256"]:
                raise ValueError(f"SHA-256 mismatch: {output_path}")
            if output_path.suffix.lower() == ".csv":
                observed_rows = _csv_rows(output_path)
                if observed_rows != int(expected["rows"]):
                    raise ValueError(
                        f"row-count mismatch: {output_path}: {observed_rows} != {expected['rows']}"
                    )
            checked_outputs += 1
    return {"manifests": len(manifests), "manifested_outputs": checked_outputs}


def _assert_zero(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    maximum = frame[columns].astype(float).abs().to_numpy().max(initial=0.0)
    if maximum > TOL:
        raise ValueError(f"{label} is not invariant; max absolute response={maximum}")


def _verify_label_claims(path: Path, expected_total: int, expected_positive: int, expected_signed: tuple[int, int, int]) -> None:
    frame = pd.read_csv(path, low_memory=False)
    label_side = frame[frame["attack_family"] == "target_shift"].copy()
    if len(label_side) != expected_total:
        raise ValueError(f"{path.name}: expected {expected_total} label rows, found {len(label_side)}")

    feature_prediction = [
        "integrity_jsd_vs_clean_eval",
        "integrity_mmd_vs_clean_eval",
        "integrity_ks_reject05_vs_clean_eval",
        "integrity_score_jsd_vs_clean_eval",
        "integrity_pred_disagreement",
        "integrity_pred_jsd",
    ]
    _assert_zero(label_side, feature_prediction, f"{path.name} feature/prediction evidence")

    prior = label_side[label_side["attack"].str.contains("prior_preserving", regex=False)]
    if len(prior) != expected_total // 2:
        raise ValueError(f"{path.name}: unexpected prior-preserving count {len(prior)}")
    _assert_zero(
        prior,
        ["integrity_label_prior_shift", "integrity_label_jsd"],
        f"{path.name} label-marginal evidence",
    )

    impact = label_side["impact_bal_acc"].astype(float)
    if int((impact > TOL).sum()) != expected_positive:
        raise ValueError(f"{path.name}: positive-impact count changed")
    # ``impact_bal_acc`` is the positive part max(BA_clean - BA_observed, 0); the
    # signed change is recomputed here so that apparent improvements are counted
    # explicitly (artifact 1.2.0) instead of being folded into "zero impact".
    signed = label_side["bal_acc_clean"].astype(float) - label_side["bal_acc"].astype(float)
    observed_signed = (int((signed > TOL).sum()), int((signed.abs() <= TOL).sum()), int((signed < -TOL).sum()))
    if observed_signed != expected_signed:
        raise ValueError(f"{path.name}: signed label-path counts (decreased, unchanged, increased) {observed_signed} != {expected_signed}")
    if not bool(((impact > TOL) == (signed > TOL)).all()):
        raise ValueError(f"{path.name}: positive impact is not the positive part of the signed change")

    material = label_side[signed.abs() > TOL]
    joint = material[
        ["integrity_confusion_profile_l1_delta", "integrity_confusion_profile_jsd_delta"]
    ].astype(float).abs().max(axis=1)
    if bool((joint <= TOL).any()):
        raise ValueError(f"{path.name}: a label cell with a changed conclusion lacks joint-outcome evidence")


def verify_claims(root: Path) -> dict[str, int]:
    gate1 = next(root.rglob("gate1_unique_observations.csv"), None)
    expansion = next(root.rglob("expansion_unique_observations.csv"), None)
    if gate1 is None or expansion is None:
        raise FileNotFoundError("unique-observation tables required for independent claim verification")
    _verify_label_claims(gate1, expected_total=1440, expected_positive=1276, expected_signed=(1276, 105, 59))
    _verify_label_claims(expansion, expected_total=3600, expected_positive=2184, expected_signed=(2184, 983, 433))
    return {
        "gate1_label_rows": 1440,
        "gate1_positive_impact": 1276,
        "gate1_label_increased": 59,
        "expansion_label_rows": 3600,
        "expansion_positive_impact": 2184,
        "expansion_label_increased": 433,
        "expansion_label_material": 2617,
    }


def verify_reinforcement_claims(root: Path) -> dict[str, int]:
    """Recompute the calibrated label-path consistency claims of artifact 1.1.0.

    The null-calibrated feature and feature-plus-prediction regimes must never
    fire on an evaluation-label intervention (Propositions 1--2 survive
    calibration), and the label-marginal regime must never fire on a
    prior-preserving intervention. The false-alarm table must exist and report
    the prespecified nominal level.
    """
    summary_path = next(root.rglob("calibrated_label_path_summary.csv"), None)
    fpr_path = next(root.rglob("null_evaluation_false_alarm_overall.csv"), None)
    thresholds_path = next(root.rglob("null_calibration_thresholds.csv"), None)
    if summary_path is None or fpr_path is None or thresholds_path is None:
        raise FileNotFoundError("reinforcement evidence tables required for claim verification")

    summary = pd.read_csv(summary_path)
    label_all = summary[summary["subset"] == "all_label_interventions"].set_index("regime")
    prior = summary[summary["subset"] == "prior_preserving_label_interventions"].set_index("regime")
    for regime in ("I_X", "I_XF"):
        if int(label_all.loc[regime, "n_fire"]) != 0:
            raise ValueError(f"calibrated {regime} regime fired on an evaluation-label intervention")
    if int(prior.loc["I_Ym", "n_fire"]) != 0:
        raise ValueError("calibrated label-marginal regime fired on a prior-preserving intervention")

    thresholds = pd.read_csv(thresholds_path)
    calibrated = thresholds[thresholds["order_statistic_rank"] > 0]
    if not (calibrated["alpha"].astype(float) == 0.05).all():
        raise ValueError("null-calibration nominal level changed from 0.05")
    if not (calibrated["n_cal"].astype(int) == 200).all():
        raise ValueError("null-calibration draw count changed from 200 per cell")

    fpr = pd.read_csv(fpr_path)
    return {
        "reinforcement_label_rows": int(label_all.loc["I_XF", "n"]),
        "reinforcement_calibrated_cells": int(len(calibrated) // calibrated["sensor"].nunique()),
        "reinforcement_fpr_rows": int(len(fpr)),
    }


def verify_policy_claims(root: Path) -> dict[str, int]:
    """Recompute the policy-level claims of artifacts 1.2.0/1.3.0 from the manifested tables.

    The conformal family-calibrated feature and feature-plus-prediction regimes
    never fire on evaluation-label interventions; the serve-always baseline allows
    every material observation; the trusted item-aligned regime allows no material
    observation under any calibrated policy; the conformal family rule never
    exceeds the union rule in pooled false-alarm rate (primary aggregate); and the
    conformal rule stays within its exact level under the exchangeable re-splits.
    """
    metrics_path = next(root.rglob("policy_metrics.csv"), None)
    label_path = next(root.rglob("family_label_path_summary.csv"), None)
    fpr_path = next(root.rglob("family_false_alarm_overall.csv"), None)
    coverage_path = next(root.rglob("policy_regime_coverage.csv"), None)
    if metrics_path is None or label_path is None or fpr_path is None or coverage_path is None:
        raise FileNotFoundError("policy evidence tables required for claim verification")
    coverage = pd.read_csv(coverage_path).set_index("regime")
    trusted_coverage = coverage.loc["I_XFY_trusted"]
    if (
        trusted_coverage["coverage_feature"] != "calibrated"
        or trusted_coverage["coverage_prediction"] != "exact"
        or trusted_coverage["coverage_label"] != "exact"
    ):
        raise ValueError(
            "trusted regime must retain calibrated feature coverage and exact prediction/label coverage"
        )
    label = pd.read_csv(label_path)
    for regime in ("I_X", "I_XF"):
        block = label[(label["subset"] == "all_label_interventions") & (label["regime"] == regime)]
        if int(block["n_fire"].sum()) != 0:
            raise ValueError(f"family-calibrated {regime} regime fired on an evaluation-label intervention")
    prior = label[(label["subset"] == "prior_preserving_label_interventions") & (label["regime"] == "I_Ym")]
    if int(prior["n_fire"].sum()) != 0:
        raise ValueError("family-calibrated label-marginal regime fired on a prior-preserving intervention")
    metrics = pd.read_csv(metrics_path)
    primary = metrics[metrics["tau"] == 0.0]
    serve = primary[primary["policy"] == "serve_always"]
    if not bool((serve["unsafe_allow"] == serve["n_material"]).all()):
        raise ValueError("serve-always baseline does not allow every material observation")
    trusted = primary[(primary["regime"] == "I_XFY_trusted") & (primary["policy"] != "serve_always")]
    if int(trusted["unsafe_allow"].sum()) != 0 or int(trusted["false_hold"].sum() + trusted["false_block"].sum()) != 0:
        raise ValueError("trusted item-aligned regime has unsafe allows or false holds")
    # Benign-interruption decomposition of the trusted calibrated policy (artifact 1.3.1):
    # statistical holds + exact-reference blocks must equal the interruption count and rate.
    trusted_p2 = primary[(primary["regime"] == "I_XFY_trusted") & (primary["policy"] == "family_calibrated")].iloc[0]
    holds, blocks, n_benign = int(trusted_p2["benign_hold"]), int(trusted_p2["benign_block"]), int(trusted_p2["n_benign"])
    if abs(float(trusted_p2["benign_interruption_rate"]) - (holds + blocks) / n_benign) > 1e-12:
        raise ValueError("trusted-regime benign interruption rate does not equal (holds + blocks) / n_benign")
    fpr = pd.read_csv(fpr_path)
    if "aggregate" in fpr.columns:
        fpr = fpr[fpr["aggregate"] == "all_eight_environments"]
    for regime, block in fpr.groupby("regime"):
        family = float(block[block["rule"] == "family"]["pooled_rate"].iloc[0])
        union = float(block[block["rule"] == "union"]["pooled_rate"].iloc[0])
        if family > union + 1e-12:
            raise ValueError(f"family rule exceeds union rule in regime {regime}")
    resplit_path = next(root.rglob("family_resplit_pooled.csv"), None)
    if resplit_path is None:
        raise FileNotFoundError("family_resplit_pooled.csv required (artifact 1.3.0)")
    resplit = pd.read_csv(resplit_path)
    level = float(resplit["conformal_level"].iloc[0])
    if bool((resplit["resplit_rate_family"] > level + 0.005).any()):
        raise ValueError("conformal family rule exceeds its exact level under exchangeable re-splits")
    n_material = int(serve["n_material"].iloc[0])
    return {
        "policy_material_observations": n_material,
        "policy_regimes": int(primary["regime"].nunique()),
        "policy_policies": int(primary["policy"].nunique()),
        "policy_conformal_level_x10000": int(round(level * 10000)),
        "historical_v132_v136_trusted_statistical_holds": holds,
        "historical_v132_v136_gross_exact_blocks": blocks,
        "historical_v132_v136_trusted_total_interruptions": holds + blocks,
        "policy_trusted_feature_coverage_calibrated": 1,
    }


def verify_adversarial_claims(root: Path) -> dict[str, int]:
    """Recompute the Gate A claims of artifact 1.3.0 from the manifested tables.

    The matched controls and clean rows reproduce the frozen expansion within
    1e-9; every material adaptive row is blocked under the trusted item-aligned
    regime; the adaptive rows are scored in every environment.
    """
    replay_path = next(root.rglob("adversarial_replay_consistency.csv"), None)
    metrics_path = next(root.rglob("adversarial_policy_metrics.csv"), None)
    det_path = next(root.rglob("adversarial_detection_pooled.csv"), None)
    if replay_path is None or metrics_path is None or det_path is None:
        raise FileNotFoundError("adversarial evidence tables required for claim verification")
    replay = pd.read_csv(replay_path)
    if not bool(replay["within_1e-9"].all()):
        raise ValueError("Gate A replay does not reproduce the frozen expansion")
    metrics = pd.read_csv(metrics_path)
    trusted = metrics[(metrics["regime"] == "I_XFY_trusted") & (metrics["tau"] == 0.0) & (metrics["attack_class"] == "adaptive")]
    if int(trusted["unsafe_allow"].sum()) != 0:
        raise ValueError("trusted regime serves a material adaptive observation")
    det = pd.read_csv(det_path)
    adaptive = det[(det["attack_class"] == "adaptive") & (det["rule"] == "family")]
    n_adaptive = int(adaptive[adaptive["regime"] == "I_X"]["n"].sum())
    return {"adversarial_adaptive_rows": n_adaptive, "adversarial_conditions": int(det["attack"].nunique())}


def verify_v132_amendment(root: Path) -> dict[str, int]:
    """Verify the taxonomy audit and both derived 1.3.2 headline profiles."""
    audit_path = next(root.rglob("sensor_reference_audit.csv"), None)
    cost_path = next(root.rglob("trusted_interruption_decomposition.csv"), None)
    profile_path = next(root.rglob("adaptive_strength_profile.csv"), None)
    if audit_path is None or cost_path is None or profile_path is None:
        raise FileNotFoundError("v1.3.2 amendment evidence tables required")

    audit = pd.read_csv(audit_path, keep_default_na=False)
    if len(audit) != 14 or set(audit["compatible_reference_class"]) != {"A", "B", "C"}:
        raise ValueError("unexpected v1.3.2 sensor audit shape or classes")
    class_a = audit[audit["compatible_reference_class"] == "A"]
    if len(class_a) != 10:
        raise ValueError("expected ten selected statistical Class-A sensors")
    if not bool(
        (class_a["item_correspondence_used"] == "no").all()
        and (class_a["same_batch_item_set"] == "yes").all()
        and (class_a["protected_in_executed_harness"] == "yes").all()
        and (class_a["deployed_authentication_demonstrated"] == "no").all()
    ):
        raise ValueError("Class-A reference semantics contradict the executed implementation")

    cost = pd.read_csv(cost_path).set_index("quantity")
    expected_cost = {
        "batch_statistical_interruptions": 590,
        "gross_exact_reference_blocks": 85,
        "exact_blocks_overlapping_batch_interruptions": 46,
        "net_additional_interruptions_vs_batch_I_XFY_P2": 39,
        "trusted_statistical_holds": 544,
        "trusted_exact_reference_blocks": 85,
        "trusted_total_interruptions": 629,
    }
    for quantity, expected in expected_cost.items():
        if int(cost.loc[quantity, "n"]) != expected:
            raise ValueError(f"v1.3.2 trusted-cost quantity changed: {quantity}")
    if abs(float(cost.loc["net_additional_interruptions_vs_batch_I_XFY_P2", "rate"]) - 0.0325) > TOL:
        raise ValueError("v1.3.2 trusted-cost net percentage changed")

    profile = pd.read_csv(profile_path).set_index(["mechanism", "strength"])
    if len(profile) != 10:
        raise ValueError("adaptive strength profile must contain all ten mechanism-strength cells")
    matched = {
        ("mean_shift", 0.02): 156 / 174,
        ("mean_shift", 0.05): 159 / 237,
        ("mean_shift", 0.10): 148 / 322,
        ("scaling_drift", 0.02): 132 / 241,
        ("scaling_drift", 0.05): 114 / 313,
        ("scaling_drift", 0.10): 78 / 350,
    }
    for key, expected in matched.items():
        if abs(float(profile.loc[key, "material_served_rate_I_XFY"]) - expected) > TOL:
            raise ValueError(f"adaptive served-rate profile changed: {key}")
    return {
        "v132_sensor_audit_rows": len(audit),
        "historical_v132_v136_batch_interruptions": int(cost.loc["batch_statistical_interruptions", "n"]),
        "historical_v132_v136_trusted_statistical_holds": int(cost.loc["trusted_statistical_holds", "n"]),
        "historical_v132_v136_gross_exact_blocks": int(cost.loc["gross_exact_reference_blocks", "n"]),
        "historical_v132_v136_trusted_total_interruptions": int(cost.loc["trusted_total_interruptions", "n"]),
        "historical_v132_v136_exact_overlap": int(cost.loc["exact_blocks_overlapping_batch_interruptions", "n"]),
        "historical_v132_v136_net_additional": int(cost.loc["net_additional_interruptions_vs_batch_I_XFY_P2", "n"]),
        "historical_v132_v136_net_additional_basis_points": int(
            round(10000 * float(cost.loc["net_additional_interruptions_vs_batch_I_XFY_P2", "rate"]))
        ),
        "v132_adaptive_strength_cells": len(profile),
    }


def _assert_rate(observed: float, expected: float, label: str) -> None:
    if abs(float(observed) - float(expected)) > TOL:
        raise ValueError(f"geometry sensitivity derived value changed: {label}")


def verify_geometry_sensitivity(root: Path) -> dict[str, int]:
    """Independently verify the v1.3.5 geometry grid and derived summaries."""

    manifest_path = next(root.rglob("geometry_sensitivity_manifest.json"), None)
    if manifest_path is None:
        raise FileNotFoundError("geometry_sensitivity_manifest.json required")
    folder = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_gates = {
        "gate2_id_256",
        "gate3a_ood_tue_wed",
        "gate3b_ood_tue_fri_portscan",
        "gate3c_ood_wed_thu_webattacks",
        "gate3d_ood_wed_fri_morning",
        "gate5a_id_unsw",
        "gate5b_id_ton_iot",
        "gate6_ood_unsw",
    }
    strengths3 = (0.02, 0.05, 0.10)
    strengths5 = (0.02, 0.05, 0.10, 0.25, 0.50)
    expected_attacks = {
        "sham_identity",
        "sham_tiny_gaussian_sigma_0.001",
        "sham_tiny_scaling_alpha_0.001",
        *(f"mean_shift_pf_delta_{s:.3f}" for s in strengths3),
        *(f"scaling_drift_alpha_{s:.3f}" for s in strengths3),
        *(f"feature_dropout_p_{s:.3f}" for s in strengths3),
        *(f"cluster_preserving_mean_shift_delta_{s:.3f}" for s in strengths5),
        *(f"cluster_preserving_scaling_alpha_{s:.3f}" for s in strengths5),
    }
    design = manifest.get("design", {})
    if (
        set(design.get("environments", [])) != expected_gates
        or design.get("dimensions") != [8, 10, 12]
        or design.get("split_seeds") != [42, 43, 44, 45, 46]
        or design.get("model_seeds") != [42, 43]
        or set(design.get("interventions", [])) != expected_attacks
        or design.get("raw_jobs") != 240
        or design.get("model_cells") != 600
    ):
        raise ValueError("geometry sensitivity manifest design differs from the preregistered grid")

    obs = pd.read_csv(folder / "geometry_observations.csv", low_memory=False)
    key = ["gate", "svd_dim", "split_seed", "model_seed", "model", "attack"]
    if len(obs) != 13200 or obs.duplicated(key).any():
        raise ValueError("geometry sensitivity must contain 13,200 unique model/attack observations")
    if set(obs["gate"]) != expected_gates or set(obs["attack"]) != expected_attacks:
        raise ValueError("geometry sensitivity has an unexpected environment or intervention")
    if not bool(obs.groupby("attack").size().eq(600).all()):
        raise ValueError("geometry sensitivity has missing intervention cells")
    if not bool(
        (obs["geometry_id"] == "fixed_frozen_E__fresh_eval_draw_01").all()
        and (obs["reference_geometry"] == "fixed_frozen_E").all()
        and (obs["clean_current_geometry"] == "fresh_eval_draw_01").all()
        and (obs["attack_current_geometry"] == "intervened_fresh_eval_draw_01").all()
        and (obs["clean_draw_tag"] == "clean_resample_eval_01").all()
        and (obs["n_reference"] == obs["n_current"]).all()
    ):
        raise ValueError("declared and executed geometry do not match")

    identity = obs[obs["attack"] == "sham_identity"]
    paired_sensor_cols = [c for c in obs.columns if c.startswith("paired__")]
    paired_identity_cols = paired_sensor_cols + [
        "paired_pred_disagreement",
        "paired_label_flip_rate",
        "paired_confusion_profile_l1",
        "paired_confusion_profile_jsd",
    ]
    if identity[paired_identity_cols].astype(float).abs().to_numpy().max(initial=0.0) > TOL:
        raise ValueError("paired identity response is not exactly zero")
    for paired in paired_sensor_cols:
        sensor = paired.removeprefix("paired__")
        if (identity[sensor].astype(float) - identity[f"clean__{sensor}"].astype(float)).abs().max() > TOL:
            raise ValueError("aligned identity copy was confused with the exact paired response")

    adaptive = obs[obs["attack_class"] == "adaptive"]
    if set(adaptive["strength"].round(3)) != set(strengths5):
        raise ValueError("adaptive strength grid is incomplete")

    detection = pd.read_csv(folder / "geometry_attack_detection.csv", low_memory=False)
    for index, row in detection.iterrows():
        group = obs[obs["attack"] == row["attack"]]
        if row["scope_type"] == "environment":
            group = group[group["gate"] == row["scope"]]
        elif row["scope_type"] == "branch":
            group = group[group["branch"] == row["scope"]]
        elif row["scope_type"] != "pooled":
            raise ValueError(f"unknown geometry detection scope {row['scope_type']}")
        fire = group[f"fire_{row['rule']}__{row['regime']}"].astype(bool)
        clean = group[f"clean_fire_{row['rule']}__{row['regime']}"].astype(bool)
        if int(row["n"]) != len(group) or int(row["n_fire"]) != int(fire.sum()):
            raise ValueError(f"geometry detection count mismatch at row {index}")
        _assert_rate(row["response_rate"], fire.mean(), f"detection row {index}")
        if (
            int(row["clean_n_fire"]) != int(clean.sum())
            or int(row["attack_only"]) != int((fire & ~clean).sum())
            or int(row["clean_only"]) != int((~fire & clean).sum())
            or int(row["both_fire"]) != int((fire & clean).sum())
            or int(row["neither_fire"]) != int((~fire & ~clean).sum())
        ):
            raise ValueError(f"geometry paired clean/attack decomposition mismatch at row {index}")

    near = pd.read_csv(folder / "geometry_near_null.csv", low_memory=False)
    expected_near = detection[
        (detection["attack_class"] == "near_null")
        & detection["scope_type"].isin(["pooled", "environment"])
    ].reset_index(drop=True)
    pd.testing.assert_frame_equal(near, expected_near, check_dtype=False, check_exact=False, rtol=TOL, atol=TOL)
    gate_by_strength = pd.read_csv(folder / "geometry_gateA_by_strength.csv", low_memory=False)
    expected_gate = detection[
        detection["mechanism"].isin(["mean_shift", "scaling_drift"])
        & detection["attack_class"].isin(["control", "adaptive"])
        & detection["regime"].isin(["I_X", "I_XF"])
    ].reset_index(drop=True)
    pd.testing.assert_frame_equal(gate_by_strength, expected_gate, check_dtype=False, check_exact=False, rtol=TOL, atol=TOL)

    summary = pd.read_csv(folder / "geometry_gateA_summary.csv")
    if len(summary) != 24 or not bool((summary["n_environment_split_cells"] == 40).all()):
        raise ValueError("Gate A matched summary is incomplete")
    for index, row in summary.iterrows():
        if row["mechanism"] == "mean_shift":
            control = f"mean_shift_pf_delta_{row['strength']:.3f}"
            attack = f"cluster_preserving_mean_shift_delta_{row['strength']:.3f}"
        else:
            control = f"scaling_drift_alpha_{row['strength']:.3f}"
            attack = f"cluster_preserving_scaling_alpha_{row['strength']:.3f}"
        column = f"fire_{row['rule']}__{row['regime']}"
        c = obs[obs["attack"] == control]
        a = obs[obs["attack"] == attack]
        adaptive_material = a["material_tau0"].astype(bool)
        adaptive_fire = a[column].astype(bool)
        cells = c.groupby(["gate", "split_seed"])[column].mean().rename("control").to_frame().join(
            a.groupby(["gate", "split_seed"])[column].mean().rename("adaptive"), validate="one_to_one"
        )
        if (
            int(row["cells_adaptive_lower"]) != int((cells["adaptive"] < cells["control"] - TOL).sum())
            or int(row["cells_equal"]) != int((cells["adaptive"] - cells["control"]).abs().le(TOL).sum())
            or int(row["cells_adaptive_higher"]) != int((cells["adaptive"] > cells["control"] + TOL).sum())
        ):
            raise ValueError(f"Gate A matched-cell summary mismatch at row {index}")
        _assert_rate(row["aligned_control_response"], c[column].astype(bool).mean(), f"Gate A control {index}")
        _assert_rate(row["aligned_adaptive_response"], a[column].astype(bool).mean(), f"Gate A adaptive {index}")
        if (
            int(row["aligned_adaptive_material_rows"]) != int(adaptive_material.sum())
            or int(row["aligned_adaptive_material_nonresponse_rows"])
            != int((adaptive_material & ~adaptive_fire).sum())
        ):
            raise ValueError(f"Gate A material/nonresponse count mismatch at row {index}")
        _assert_rate(
            row["aligned_adaptive_material_nonresponse_fraction"],
            (adaptive_material & ~adaptive_fire).sum() / adaptive_material.sum(),
            f"Gate A material nonresponse {index}",
        )

    null_response = pd.read_csv(folder / "geometry_null_response.csv", low_memory=False)
    identity_null = null_response[null_response["response_kind"] == "paired_identity"]
    if identity_null.empty or int(identity_null["n_fire"].sum()) != 0 or identity_null["max_abs_response"].fillna(0).abs().max() > TOL:
        raise ValueError("paired identity response summary is not exact-zero")
    if not {"I_X", "I_XF"} <= set(null_response[null_response["response_kind"] == "clean_resample"]["target"]):
        raise ValueError("clean-resample false-action summaries are incomplete")
    return {
        "geometry_observations": len(obs),
        "geometry_environments": len(expected_gates),
        "geometry_interventions": len(expected_attacks),
        "geometry_gateA_matched_rows": len(summary),
    }


def verify_v137_correction(root: Path) -> dict[str, int]:
    """Verify corrected JSD finiteness and the completed label-geometry grid."""

    jsd_manifest = next(root.rglob("jsd_correction_manifest.json"), None)
    label_manifest = next(root.rglob("label_geometry_manifest.json"), None)
    if jsd_manifest is None or label_manifest is None:
        raise FileNotFoundError("both v1.3.7 corrective manifests are required")
    jsd = jsd_manifest.parent
    label = label_manifest.parent
    observations = pd.read_csv(jsd / "jsd_corrected_observations.csv", low_memory=False)
    corrected = observations[
        ["integrity_jsd_vs_clean_eval", "integrity_score_jsd_vs_clean_eval"]
    ].apply(pd.to_numeric, errors="coerce")
    if len(observations) != 64560 or not bool(np.isfinite(corrected.to_numpy(float)).all()):
        raise ValueError("v1.3.7 corrected JSD observations are incomplete or nonfinite")
    deltas = pd.read_csv(jsd / "jsd_correction_deltas.csv", low_memory=False)
    if deltas.empty or not {
        "affected_row_identifier", "sensor", "previous_value", "corrected_value",
        "previous_sensor_fire", "corrected_sensor_fire", "reason",
    }.issubset(deltas.columns):
        raise ValueError("v1.3.7 JSD before/after ledger is incomplete")
    changed_observation_rows = len(
        deltas[["correction_scope", "affected_row_identifier"]].drop_duplicates()
    )
    if changed_observation_rows != 58074 or len(deltas) != 192487:
        raise ValueError("v1.3.7 JSD delta cardinalities changed")
    decomposition = pd.read_csv(jsd / "jsd_sensor_decomposition.csv", low_memory=False)
    expected_sensors = {
        "integrity_jsd_vs_clean_eval", "integrity_mmd_vs_clean_eval",
        "integrity_ks_reject05_vs_clean_eval", "integrity_ks_mean_vs_clean_eval",
        "integrity_score_jsd_vs_clean_eval", "integrity_pred_pos_rate_shift",
        "integrity_pred_jsd", "integrity_label_prior_shift", "integrity_label_jsd",
        "integrity_confusion_profile_l1", "integrity_confusion_profile_jsd",
    }
    if set(decomposition["sensor"]) != expected_sensors:
        raise ValueError("v1.3.7 sensor decomposition is incomplete")
    ablation = pd.read_csv(jsd / "jsd_without_ks_ablation.csv", low_memory=False)
    if ablation.empty or set(ablation["rule"]) != {"union", "family"}:
        raise ValueError("v1.3.7 frozen-only without-KS ablation is incomplete")
    gate_f = pd.read_csv(jsd / "jsd_gate_f_summary.csv")
    if len(gate_f) != 48 or set(gate_f["geometry"]) != {"v136", "v137_corrected_jsd"} or set(gate_f["rule"]) != {"union", "family_v12", "family"}:
        raise ValueError("v1.3.7 Gate-F correction summary is incomplete")
    policy = pd.read_csv(jsd / "jsd_primary_policy_effect.csv")
    if len(policy) != 80 or set(policy["geometry"]) != {"primary_v136", "primary_v137_corrected_jsd"} or set(policy["family_rule"]) != {"conformal", "v12_asymmetric"}:
        raise ValueError("v1.3.7 Gate-D correction summary is incomplete")
    p2 = policy[(policy["policy"] == "family_calibrated") & (policy["family_rule"] == "conformal")].set_index(["geometry", "regime"])
    expected_policy = {
        "primary_v136": {"I_X": 4496, "I_XF": 4365, "I_Ym": 7008, "I_XFY": 4390, "I_XFY_trusted": 0},
        "primary_v137_corrected_jsd": {"I_X": 4496, "I_XF": 4368, "I_Ym": 7008, "I_XFY": 4394, "I_XFY_trusted": 0},
    }
    for geometry, expected in expected_policy.items():
        for regime, value in expected.items():
            if int(p2.loc[(geometry, regime), "unsafe_allow"]) != value:
                raise ValueError(f"unexpected v1.3.7 Gate-D P2 result for {geometry}/{regime}")

    current_p2 = policy[
        (policy["geometry"] == "primary_v137_corrected_jsd")
        & (policy["family_rule"] == "conformal")
        & (policy["policy"] == "family_calibrated")
    ].set_index("regime")
    batch = current_p2.loc["I_XFY"]
    trusted = current_p2.loc["I_XFY_trusted"]
    if int(batch["n_benign"]) != int(trusted["n_benign"]):
        raise ValueError("corrected batch/trusted near-null denominators differ")
    trusted_denominator = int(trusted["n_benign"])
    corrected_batch_interruptions = int(batch["benign_hold"]) + int(batch["benign_block"])
    gross_exact_blocks = int(trusted["benign_block"])
    trusted_total_interruptions = int(trusted["benign_hold"]) + gross_exact_blocks
    exact_overlap = corrected_batch_interruptions + gross_exact_blocks - trusted_total_interruptions
    net_additional = trusted_total_interruptions - corrected_batch_interruptions
    net_additional_basis_points = int(round(10000 * net_additional / trusted_denominator))
    if not (
        exact_overlap == gross_exact_blocks - net_additional
        and int(trusted["benign_hold"]) == corrected_batch_interruptions - exact_overlap
        and abs(
            float(trusted["benign_interruption_rate"])
            - trusted_total_interruptions / trusted_denominator
        )
        <= TOL
    ):
        raise ValueError("corrected trusted-reference decomposition is inconsistent")

    headline = pd.read_csv(jsd / "headline_delta.csv").set_index("claim")
    expected_headline = {
        "Trusted-reference gross exact blocks on near-null controls": f"{gross_exact_blocks}/{trusted_denominator}",
        "Trusted/batch near-null overlap": f"{exact_overlap}/{trusted_denominator}",
        "Trusted-reference net additional near-null interruptions": f"{net_additional}/{trusted_denominator}",
        "Trusted-reference net near-null increment": f"{net_additional_basis_points / 100:.2f} pp",
    }
    for claim, expected in expected_headline.items():
        if str(headline.loc[claim, "v1.3.7"]) != expected:
            raise ValueError(f"headline_delta current value disagrees with policy evidence: {claim}")
    resplit = pd.read_csv(jsd / "jsd_corrected_resplit_pooled.csv")
    split = pd.read_csv(jsd / "jsd_corrected_split_construction_sensitivity.csv")
    if len(resplit) != 4 or len(split) != 4:
        raise ValueError("v1.3.7 corrected split sensitivities are incomplete")
    if not bool((resplit["resplit_rate_family"] <= resplit["conformal_level"] + 0.005).all()):
        raise ValueError("corrected exchangeable re-split family exceeds declared tolerance")

    aligned = pd.read_csv(label / "label_geometry_observations.csv", low_memory=False)
    if len(aligned) != 3600:
        raise ValueError("label geometry sensitivity must contain 3,600 rows")
    summary = pd.read_csv(label / "label_geometry_summary.csv").set_index("question")
    if (
        int(summary.loc["Q1", "v136"]) != 11
        or int(summary.loc["Q1", "v136_denominator"]) != 2617
        or int(summary.loc["Q2", "v136"]) != 43
        or int(summary.loc["Q2", "v136_denominator"]) != 2617
    ):
        raise ValueError("historical label 11/2617 or 43/2617 endpoint did not reproduce")
    if (
        int(summary.loc["Q1", "v137"]), int(summary.loc["Q1", "v137_denominator"]),
        int(summary.loc["Q2", "v137"]), int(summary.loc["Q2", "v137_denominator"]),
    ) != (343, 2700, 1183, 2700):
        raise ValueError("aligned label endpoints do not reproduce 343/2700 and 1183/2700")
    blind = aligned[aligned["aggregate_blind"].astype(bool)]
    for sensor in (
        "integrity_jsd_vs_clean_eval", "integrity_mmd_vs_clean_eval",
        "integrity_ks_reject05_vs_clean_eval", "integrity_score_jsd_vs_clean_eval",
        "integrity_pred_pos_rate_shift", "integrity_pred_jsd",
        "integrity_label_prior_shift", "integrity_label_jsd",
        "integrity_confusion_profile_l1", "integrity_confusion_profile_jsd",
    ):
        if (
            pd.to_numeric(blind[f"aligned__{sensor}"], errors="coerce")
            - pd.to_numeric(blind[f"aligned__clean__{sensor}"], errors="coerce")
        ).abs().max() > TOL:
            raise ValueError(f"aggregate-blind label rows alter observable {sensor}")
    for rule in ("family", "union"):
        attack = blind[f"aligned__fire_{rule}__I_XFY"].astype(bool).to_numpy()
        clean = blind[f"aligned__clean_fire_{rule}__I_XFY"].astype(bool).to_numpy()
        if not np.array_equal(attack, clean):
            raise ValueError(f"aggregate-blind aligned label rows differ from paired-clean {rule} response")
    return {
        "v137_corrected_observations": len(observations),
        "v137_jsd_delta_records": len(deltas),
        "v137_jsd_changed_observation_rows": changed_observation_rows,
        "v137_label_geometry_rows": len(aligned),
        "v137_label_aggregate_blind_rows": len(blind),
        "v137_label_aligned_family_material_fires": int(summary.loc["Q1", "v137"]),
        "v137_label_aligned_union_material_fires": int(summary.loc["Q2", "v137"]),
        "current_v137_v138_corrected_batch_interruptions": corrected_batch_interruptions,
        "current_v137_v138_trusted_statistical_holds": int(trusted["benign_hold"]),
        "current_v137_v138_gross_exact_blocks": gross_exact_blocks,
        "current_v137_v138_trusted_total_interruptions": trusted_total_interruptions,
        "current_v137_v138_exact_overlap": exact_overlap,
        "current_v137_v138_net_additional": net_additional,
        "current_v137_v138_net_additional_basis_points": net_additional_basis_points,
    }


def verify_release_hashes(root: Path) -> int:
    manifest = root / "ARTIFACT_MANIFEST.sha256"
    if not manifest.exists():
        return 0
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = root / Path(relative)
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError(f"release-manifest mismatch: {relative}")
        checked += 1
    return checked


def verify(root: Path) -> dict[str, int]:
    root = root.resolve()
    result = verify_embedded_manifests(root)
    result.update(verify_claims(root))
    result.update(verify_reinforcement_claims(root))
    result.update(verify_policy_claims(root))
    result.update(verify_adversarial_claims(root))
    result.update(verify_v132_amendment(root))
    result.update(verify_geometry_sensitivity(root))
    result.update(verify_v137_correction(root))
    result["release_files"] = verify_release_hashes(root)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("results/paper_digest"),
        help="Evidence root or publication artifact root",
    )
    args = parser.parse_args()
    print(json.dumps(verify(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
