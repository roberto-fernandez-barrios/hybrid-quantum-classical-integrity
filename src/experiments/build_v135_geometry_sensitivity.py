"""Build the fail-closed v1.3.5 geometry-aligned sensitivity evidence package."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.experiments.build_q1_policy_evidence import BATCH_REGIME_NAMES, score_frame
from src.experiments.build_q1_reinforcement_evidence import (
    CALIBRATED_SENSORS,
    DIMS,
    MODEL_SEEDS,
    NULL_GATES,
    SPLIT_SEEDS,
)
from src.experiments.run_v135_geometry_sensitivity import (
    ALL_BATCH_SENSOR_COLUMNS,
    ATTACK_CURRENT_GEOMETRY,
    CALIBRATION_DRAW_TAG,
    CLEAN_CURRENT_GEOMETRY,
    GEOMETRY_ID,
    IDENTITY_TOL,
    PREREGISTRATION,
    REFERENCE_GEOMETRY,
    geometry_attack_specs,
)


ALPHA = 0.05
TOL = 1e-12
OLD_EVIDENCE_FILES = 96
OLD_EVIDENCE_TREE_SHA256 = "0c3b001eae6a25c76566a1ca03c49332027e6edc49dc684e1552f972fe21a9d7"
RULES_REPORTED = ("union", "family")
REGIMES_REPORTED = tuple(BATCH_REGIME_NAMES)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def old_evidence_tree(repo: Path) -> tuple[int, str]:
    root = repo / "publication/artifact/evidence"
    files = sorted(p for p in root.rglob("*") if p.is_file() and "geometry_sensitivity" not in p.parts)
    lines = [f"{_sha256(p)}  {p.relative_to(repo).as_posix()}\n" for p in files]
    return len(files), hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def _prereg_commit(repo: Path) -> str:
    return subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", PREREGISTRATION], cwd=repo, text=True
    ).strip()


def geometry_audit_frame() -> pd.DataFrame:
    rows = [
        ("integrity_jsd_vs_clean_eval", "fixed E", "clean resample C", "fixed E", "T(fresh B)", "unpaired fixed-reference in both", "yes", "aligned distributional feature response"),
        ("integrity_mmd_vs_clean_eval", "fixed E", "clean resample C", "fixed E", "T(fresh B)", "unpaired fixed-reference in both", "yes", "aligned distributional feature response"),
        ("integrity_ks_reject05_vs_clean_eval", "fixed E", "clean resample C", "fixed E", "T(fresh B)", "unpaired fixed-reference in both", "yes", "aligned feature-CDF response"),
        ("integrity_score_jsd_vs_clean_eval", "scores f(E)", "scores f(C)", "scores f(E)", "scores f(T(B))", "unpaired fixed-reference in both", "yes", "aligned score-distribution response"),
        ("integrity_pred_pos_rate_shift", "prediction rate f(E)", "prediction rate f(C)", "prediction rate f(E)", "prediction rate f(T(B))", "unpaired fixed-reference in both", "yes", "aligned prediction-marginal response"),
        ("integrity_pred_jsd", "prediction distribution f(E)", "prediction distribution f(C)", "prediction distribution f(E)", "prediction distribution f(T(B))", "unpaired fixed-reference in both", "yes", "aligned prediction-distribution response"),
        ("integrity_label_prior_shift", "label rate y(E)", "label rate y(C)", "label rate y(E)", "label rate y(B)", "unpaired fixed-reference in both", "yes", "unchanged by feature edit; may reflect clean composition"),
        ("integrity_label_jsd", "label distribution y(E)", "label distribution y(C)", "label distribution y(E)", "label distribution y(B)", "unpaired fixed-reference in both", "yes", "unchanged by feature edit; may reflect clean composition"),
        ("integrity_confusion_profile_l1", "confusion PMF on E", "confusion PMF on C", "confusion PMF on E", "confusion PMF on T(B)", "unpaired fixed-reference in both", "yes", "aligned aggregate outcome response"),
        ("integrity_confusion_profile_jsd", "confusion PMF on E", "confusion PMF on C", "confusion PMF on E", "confusion PMF on T(B)", "unpaired fixed-reference in both", "yes", "aligned aggregate outcome response"),
        ("paired identity response", "fresh B", "fresh B", "fresh B", "identity(B)", "exact same-item", "yes", "reported separately; all meaningful scores zero"),
        ("paired prediction disagreement", "predictions f(B)", "predictions f(B)", "predictions f(B)", "predictions f(T(B))", "exact same-item", "yes", "not inserted into clean-resample calibration"),
        ("paired label mismatch", "labels y(B)", "labels y(B)", "labels y(B)", "labels y(B)", "exact same-item", "yes", "zero for every authorized feature intervention"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "sensor",
            "calibration_reference",
            "calibration_current",
            "attack_reference",
            "attack_current",
            "paired_unpaired",
            "geometry_matched",
            "consequence",
        ],
    )


def _expected_models(gate: str) -> set[str]:
    spec = next(s for s in NULL_GATES if str(s["gate"]) == gate)
    return set(spec["models"])


def load_raw(repo: Path, raw_dir: Path) -> tuple[pd.DataFrame, list[dict[str, Any]], dict[str, bool]]:
    frames: list[pd.DataFrame] = []
    inputs: list[dict[str, Any]] = []
    checks: dict[str, bool] = {}
    paths = sorted((repo / raw_dir).glob("geometry__*.csv"))
    checks["G0_all_240_raw_jobs_present"] = len(paths) == 240
    if not checks["G0_all_240_raw_jobs_present"]:
        raise RuntimeError(f"Observed {len(paths)} raw geometry jobs, expected 240")
    for path in paths:
        meta_path = path.with_suffix(".json")
        if not meta_path.is_file():
            raise FileNotFoundError(meta_path)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("csv_sha256") != _sha256(path):
            raise RuntimeError(f"Raw CSV hash mismatch: {path}")
        frame = pd.read_csv(path, low_memory=False)
        if len(frame) != int(meta["n_rows"]):
            raise RuntimeError(f"Raw row count mismatch: {path}")
        frames.append(frame)
        inputs.append(
            {
                "csv": path.relative_to(repo).as_posix(),
                "csv_sha256": _sha256(path),
                "json": meta_path.relative_to(repo).as_posix(),
                "json_sha256": _sha256(meta_path),
            }
        )
    obs = pd.concat(frames, ignore_index=True, sort=False)
    attacks = [s.tag for s in geometry_attack_specs()]
    checks["G1_expected_13200_unique_observations"] = len(obs) == 600 * len(attacks) and not obs.duplicated(
        ["gate", "svd_dim", "split_seed", "model_seed", "model", "attack"]
    ).any()
    checks["G2_exact_attack_set"] = set(obs["attack"]) == set(attacks)
    checks["G3_exact_environment_seed_dimension_grid"] = (
        set(obs["gate"]) == {str(s["gate"]) for s in NULL_GATES}
        and set(obs["svd_dim"].astype(int)) == set(DIMS)
        and set(obs["split_seed"].astype(int)) == set(SPLIT_SEEDS)
        and set(obs["model_seed"].astype(int)) == set(MODEL_SEEDS)
    )
    model_ok = all(set(group["model"]) == _expected_models(str(gate)) for gate, group in obs.groupby("gate"))
    checks["G4_exact_model_map_membership"] = bool(model_ok)
    geometry_ok = (
        (obs["geometry_id"] == GEOMETRY_ID).all()
        and (obs["reference_geometry"] == REFERENCE_GEOMETRY).all()
        and (obs["clean_current_geometry"] == CLEAN_CURRENT_GEOMETRY).all()
        and (obs["attack_current_geometry"] == ATTACK_CURRENT_GEOMETRY).all()
        and (obs["clean_draw_tag"] == CALIBRATION_DRAW_TAG).all()
        and (obs["n_reference"] == obs["n_current"]).all()
    )
    checks["G5_declared_geometry_matches_implementation"] = bool(geometry_ok)
    checks["G6_replay_matches_frozen_outputs"] = bool((pd.to_numeric(obs["replay_max_abs_difference"]) <= 1e-9).all())
    identity = obs[obs["attack"] == "sham_identity"]
    paired_identity_cols = [f"paired__{s}" for s in ALL_BATCH_SENSOR_COLUMNS] + [
        "paired_pred_disagreement",
        "paired_label_flip_rate",
        "paired_confusion_profile_l1",
        "paired_confusion_profile_jsd",
    ]
    identity_max = identity[paired_identity_cols].apply(pd.to_numeric, errors="coerce").abs().to_numpy().max()
    identity_copy_max = max(
        float((pd.to_numeric(identity[s]) - pd.to_numeric(identity[f"clean__{s}"])).abs().max())
        for s in ALL_BATCH_SENSOR_COLUMNS
    )
    checks["G7_paired_identity_exactly_zero"] = bool(identity_max <= IDENTITY_TOL)
    checks["G8_aligned_identity_copy_equals_clean"] = bool(identity_copy_max <= IDENTITY_TOL)
    feature = obs[obs["attack"] != "sham_identity"]
    paired_label_cols = ["paired__integrity_label_prior_shift", "paired__integrity_label_jsd", "paired_label_flip_rate"]
    checks["G9_feature_interventions_preserve_labels"] = bool(
        feature["labels_preserved"].astype(bool).all()
        and feature[paired_label_cols].apply(pd.to_numeric, errors="coerce").abs().to_numpy().max() <= TOL
    )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError(f"Raw geometry checks failed: {failed}")
    return obs, inputs, checks


def score_observations(obs: pd.DataFrame, null: pd.DataFrame, thresholds: pd.DataFrame) -> pd.DataFrame:
    calibration = null[null["attack_priority_group"] == "null_calibration"]
    thr = thresholds[thresholds["order_statistic_rank"] > 0].pivot_table(
        index=["gate", "svd_dim", "model"], columns="sensor", values="threshold", aggfunc="first"
    )
    parts: list[pd.DataFrame] = []
    for key, cal in calibration.groupby(["gate", "svd_dim", "model"], sort=True):
        if len(cal) != 200:
            raise ValueError(f"{key}: expected 200 calibration draws, got {len(cal)}")
        rows = obs[(obs["gate"] == key[0]) & (obs["svd_dim"] == key[1]) & (obs["model"] == key[2])]
        if len(rows) == 0:
            raise ValueError(f"No geometry rows for {key}")
        cal_values = {s: pd.to_numeric(cal[s], errors="coerce").to_numpy(dtype=float) for s in CALIBRATED_SENSORS}
        cell_thr = {s: float(thr.loc[key, s]) for s in CALIBRATED_SENSORS}
        attack_scored = score_frame(rows, cal_values, cell_thr)
        clean_rows = rows.copy()
        for sensor in CALIBRATED_SENSORS:
            clean_rows[sensor] = clean_rows[f"clean__{sensor}"]
        clean_scored = score_frame(clean_rows, cal_values, cell_thr)
        for regime in REGIMES_REPORTED:
            for rule in RULES_REPORTED:
                attack_scored[f"clean_fire_{rule}__{regime}"] = clean_scored[f"fire_{rule}__{regime}"].to_numpy()
        parts.append(attack_scored)
    scored = pd.concat(parts, ignore_index=True).sort_values(
        ["gate", "svd_dim", "split_seed", "model_seed", "model", "attack"]
    ).reset_index(drop=True)
    paired_exact_cols = ["paired_pred_disagreement", "paired_label_flip_rate", "paired_confusion_profile_l1", "paired_confusion_profile_jsd"]
    scored["fire_exact_paired"] = scored[paired_exact_cols].apply(pd.to_numeric, errors="coerce").fillna(0).abs().max(axis=1) > TOL
    d = pd.to_numeric(scored["delta_bal_acc"], errors="coerce").abs()
    scored["material_tau0"] = d > TOL
    scored["material_tau002"] = d > 0.02
    scored["material_tau005"] = d > 0.05
    return scored


def _detection_rows(scored: pd.DataFrame) -> pd.DataFrame:
    scopes: list[tuple[str, list[str], pd.DataFrame]] = [
        ("pooled", [], scored),
        ("environment", ["gate"], scored),
        ("branch", ["branch"], scored),
    ]
    records: list[dict[str, Any]] = []
    for scope_type, scope_cols, frame in scopes:
        group_cols = scope_cols + ["attack", "attack_class", "mechanism", "strength"]
        for key, group in frame.groupby(group_cols, sort=True, dropna=False):
            key_tuple = key if isinstance(key, tuple) else (key,)
            base = dict(zip(group_cols, key_tuple, strict=True))
            scope_value = "all_environments" if not scope_cols else str(base[scope_cols[0]])
            for regime in REGIMES_REPORTED:
                for rule in RULES_REPORTED:
                    attack_fire = group[f"fire_{rule}__{regime}"].astype(bool).to_numpy()
                    clean_fire = group[f"clean_fire_{rule}__{regime}"].astype(bool).to_numpy()
                    n = len(group)
                    records.append(
                        {
                            "scope_type": scope_type,
                            "scope": scope_value,
                            "attack": base["attack"],
                            "attack_class": base["attack_class"],
                            "mechanism": base["mechanism"],
                            "strength": float(base["strength"]),
                            "regime": regime,
                            "rule": rule,
                            "n": n,
                            "n_fire": int(attack_fire.sum()),
                            "response_rate": float(attack_fire.mean()),
                            "clean_n_fire": int(clean_fire.sum()),
                            "paired_clean_false_action_rate": float(clean_fire.mean()),
                            "attack_only": int((attack_fire & ~clean_fire).sum()),
                            "clean_only": int((~attack_fire & clean_fire).sum()),
                            "both_fire": int((attack_fire & clean_fire).sum()),
                            "neither_fire": int((~attack_fire & ~clean_fire).sum()),
                            "n_material_tau0": int(group["material_tau0"].sum()),
                            "material_fraction_tau0": float(group["material_tau0"].mean()),
                            "material_fraction_tau002": float(group["material_tau002"].mean()),
                            "material_fraction_tau005": float(group["material_tau005"].mean()),
                            "mean_signed_delta_bal_acc": float(pd.to_numeric(group["delta_bal_acc"]).mean()),
                            "prediction_change_rate": float((pd.to_numeric(group["paired_pred_disagreement"]) > TOL).mean()),
                        }
                    )
    return pd.DataFrame.from_records(records)


def _null_response(repo: Path, scored: pd.DataFrame) -> pd.DataFrame:
    per_sensor_all = pd.read_csv(
        repo / "publication/artifact/evidence/reinforcement/null_evaluation_false_alarm_overall.csv"
    )
    per_sensor_env = pd.read_csv(
        repo / "publication/artifact/evidence/reinforcement/null_evaluation_false_alarm_by_environment.csv"
    )
    family_all = pd.read_csv(repo / "publication/artifact/evidence/policy/family_false_alarm_overall.csv")
    family_env = pd.read_csv(repo / "publication/artifact/evidence/policy/family_false_alarm_by_environment.csv")
    records: list[dict[str, Any]] = []
    for _, row in per_sensor_all.iterrows():
        records.append({"response_kind": "clean_resample", "scope_type": "pooled", "scope": "all_environments", "target": row["target"], "target_kind": row["target_kind"], "rule": "per_sensor_or_union", "n": int(row["n"]), "n_fire": int(row["n_fire"]), "false_action_rate": float(row["false_alarm_rate"]), "max_abs_response": math.nan})
    for _, row in per_sensor_env.iterrows():
        records.append({"response_kind": "clean_resample", "scope_type": "environment", "scope": row["gate"], "target": row["target"], "target_kind": row["target_kind"], "rule": "per_sensor_or_union", "n": int(row["n"]), "n_fire": int(row["n_fire"]), "false_action_rate": float(row["false_alarm_rate"]), "max_abs_response": math.nan})
    for _, row in family_all[(family_all["aggregate"] == "all_eight_environments") & (family_all["rule"].isin(RULES_REPORTED))].iterrows():
        records.append({"response_kind": "clean_resample", "scope_type": "pooled", "scope": "all_environments", "target": row["regime"], "target_kind": "regime", "rule": row["rule"], "n": int(row["n_draws"]), "n_fire": int(row["n_fire"]), "false_action_rate": float(row["pooled_rate"]), "max_abs_response": math.nan})
    for _, row in family_env[family_env["rule"].isin(RULES_REPORTED)].iterrows():
        records.append({"response_kind": "clean_resample", "scope_type": "environment", "scope": row["gate"], "target": row["regime"], "target_kind": "regime", "rule": row["rule"], "n": int(row["n_draws"]), "n_fire": int(row["n_fire"]), "false_action_rate": float(row["pooled_rate"]), "max_abs_response": math.nan})
    identity = scored[scored["attack"] == "sham_identity"]
    identity_targets = [f"paired__{s}" for s in ALL_BATCH_SENSOR_COLUMNS] + ["paired_pred_disagreement", "paired_label_flip_rate", "paired_confusion_profile_l1", "paired_confusion_profile_jsd"]
    for target in identity_targets:
        vals = pd.to_numeric(identity[target], errors="coerce").abs()
        records.append({"response_kind": "paired_identity", "scope_type": "pooled", "scope": "all_environments", "target": target, "target_kind": "exact_same_item", "rule": "exact_zero", "n": int(len(vals)), "n_fire": int((vals > IDENTITY_TOL).sum()), "false_action_rate": math.nan, "max_abs_response": float(vals.max())})
    return pd.DataFrame.from_records(records)


def _gate_a_summary(scored: pd.DataFrame, repo: Path) -> pd.DataFrame:
    matched = {
        "mean_shift": ("mean_shift_pf_delta_{s:.3f}", "cluster_preserving_mean_shift_delta_{s:.3f}"),
        "scaling_drift": ("scaling_drift_alpha_{s:.3f}", "cluster_preserving_scaling_alpha_{s:.3f}"),
    }
    original_det = pd.read_csv(repo / "publication/artifact/evidence/adversarial/adversarial_detection_pooled.csv")
    original_mat = pd.read_csv(repo / "publication/artifact/evidence/adversarial/adversarial_materiality.csv").set_index("attack")
    records: list[dict[str, Any]] = []
    for mechanism, (control_fmt, adaptive_fmt) in matched.items():
        for strength in (0.02, 0.05, 0.10):
            control = control_fmt.format(s=strength)
            adaptive = adaptive_fmt.format(s=strength)
            for regime in ("I_X", "I_XF"):
                for rule in RULES_REPORTED:
                    cell_rates: dict[str, pd.DataFrame] = {}
                    for label, attack in (("control", control), ("adaptive", adaptive)):
                        sub = scored[scored["attack"] == attack]
                        cell_rates[label] = sub.groupby(["gate", "split_seed"], sort=True)[f"fire_{rule}__{regime}"].mean().reset_index(name=label)
                    cells = cell_rates["control"].merge(cell_rates["adaptive"], on=["gate", "split_seed"], validate="one_to_one")
                    control_rows = scored[scored["attack"] == control]
                    adaptive_rows = scored[scored["attack"] == adaptive]
                    control_material = control_rows["material_tau0"].astype(bool)
                    adaptive_material = adaptive_rows["material_tau0"].astype(bool)
                    adaptive_fire = adaptive_rows[f"fire_{rule}__{regime}"].astype(bool)
                    od = original_det[(original_det["attack"] == control) & (original_det["regime"] == regime) & (original_det["rule"] == rule)]
                    oa = original_det[(original_det["attack"] == adaptive) & (original_det["regime"] == regime) & (original_det["rule"] == rule)]
                    if len(od) != 1 or len(oa) != 1:
                        raise RuntimeError(f"Original Gate A comparison missing for {control}/{adaptive}/{regime}/{rule}")
                    records.append(
                        {
                            "mechanism": mechanism,
                            "strength": strength,
                            "regime": regime,
                            "rule": rule,
                            "n_environment_split_cells": int(len(cells)),
                            "cells_adaptive_lower": int((cells["adaptive"] < cells["control"] - TOL).sum()),
                            "cells_equal": int((np.abs(cells["adaptive"] - cells["control"]) <= TOL).sum()),
                            "cells_adaptive_higher": int((cells["adaptive"] > cells["control"] + TOL).sum()),
                            "fraction_cells_adaptive_lower": float((cells["adaptive"] < cells["control"] - TOL).mean()),
                            "aligned_control_response": float(control_rows[f"fire_{rule}__{regime}"].mean()),
                            "aligned_adaptive_response": float(adaptive_rows[f"fire_{rule}__{regime}"].mean()),
                            "aligned_response_difference_adaptive_minus_control": float(adaptive_rows[f"fire_{rule}__{regime}"].mean() - control_rows[f"fire_{rule}__{regime}"].mean()),
                            "aligned_control_material_fraction_tau0": float(control_rows["material_tau0"].mean()),
                            "aligned_adaptive_material_fraction_tau0": float(adaptive_rows["material_tau0"].mean()),
                            "aligned_control_material_rows": int(control_material.sum()),
                            "aligned_adaptive_material_rows": int(adaptive_rows["material_tau0"].sum()),
                            "aligned_adaptive_material_nonresponse_rows": int((adaptive_material & ~adaptive_fire).sum()),
                            "aligned_adaptive_material_nonresponse_fraction": float(
                                (adaptive_material & ~adaptive_fire).sum() / adaptive_material.sum()
                            ),
                            "aligned_adaptive_response_among_material": float(
                                (adaptive_material & adaptive_fire).sum() / adaptive_material.sum()
                            ),
                            "original_control_response": float(od.iloc[0]["detection_rate"]),
                            "original_adaptive_response": float(oa.iloc[0]["detection_rate"]),
                            "original_control_material_fraction_tau0": float(original_mat.loc[control, "material_fraction_tau0"]),
                            "original_adaptive_material_fraction_tau0": float(original_mat.loc[adaptive, "material_fraction_tau0"]),
                        }
                    )
    return pd.DataFrame.from_records(records)


def derive_outputs(repo: Path, scored: pd.DataFrame) -> dict[str, pd.DataFrame]:
    detection = _detection_rows(scored)
    null_response = _null_response(repo, scored)
    near_null = detection[(detection["attack_class"] == "near_null") & (detection["scope_type"].isin(["pooled", "environment"]))].reset_index(drop=True)
    gate_a = detection[
        detection["mechanism"].isin(["mean_shift", "scaling_drift"])
        & detection["attack_class"].isin(["control", "adaptive"])
        & detection["regime"].isin(["I_X", "I_XF"])
    ].reset_index(drop=True)
    gate_a_summary = _gate_a_summary(scored, repo)
    keep = [
        "gate", "svd_dim", "split_seed", "model_seed", "model", "model_family", "branch", "attack", "attack_class", "mechanism", "strength", "attack_seed",
        "geometry_id", "reference_geometry", "clean_current_geometry", "attack_current_geometry", "clean_draw_tag", "n_reference", "n_current", "labels_preserved",
        "clean_bal_acc", "attack_bal_acc", "delta_bal_acc", "material_tau0", "material_tau002", "material_tau005", "paired_pred_disagreement", "paired_label_flip_rate", "paired_confusion_profile_l1", "paired_confusion_profile_jsd", "fire_exact_paired", "replay_max_abs_difference",
    ]
    keep += ALL_BATCH_SENSOR_COLUMNS
    keep += [f"clean__{s}" for s in ALL_BATCH_SENSOR_COLUMNS]
    keep += [f"paired__{s}" for s in ALL_BATCH_SENSOR_COLUMNS]
    keep += [f"delta__{s}" for s in ALL_BATCH_SENSOR_COLUMNS]
    for regime in REGIMES_REPORTED:
        for rule in RULES_REPORTED:
            keep += [f"fire_{rule}__{regime}", f"clean_fire_{rule}__{regime}"]
        keep += [f"pvalue_family__{regime}"]
    keep += [c for c in scored.columns if c.startswith("atk_")]
    observations = scored[[c for c in dict.fromkeys(keep) if c in scored.columns]].reset_index(drop=True)
    return {
        "geometry_audit.csv": geometry_audit_frame(),
        "geometry_observations.csv": observations,
        "geometry_null_response.csv": null_response,
        "geometry_attack_detection.csv": detection,
        "geometry_near_null.csv": near_null,
        "geometry_gateA_by_strength.csv": gate_a,
        "geometry_gateA_summary.csv": gate_a_summary,
    }


def _fmt_rate(value: float) -> str:
    return f"{value:.3f}"


def write_macros(path: Path, outputs: dict[str, pd.DataFrame]) -> None:
    det = outputs["geometry_attack_detection.csv"]
    pooled = det[(det["scope_type"] == "pooled") & (det["rule"] == "family")]
    null = outputs["geometry_null_response.csv"]
    gate = outputs["geometry_gateA_summary.csv"]
    def rate(attack: str, regime: str) -> float:
        row = pooled[(pooled["attack"] == attack) & (pooled["regime"] == regime)]
        if len(row) != 1:
            raise RuntimeError(f"Macro row missing: {attack}/{regime}")
        return float(row.iloc[0]["response_rate"])
    clean_ix = null[(null["response_kind"] == "clean_resample") & (null["scope_type"] == "pooled") & (null["target"] == "I_X") & (null["rule"] == "family")]
    clean_ixf = null[(null["response_kind"] == "clean_resample") & (null["scope_type"] == "pooled") & (null["target"] == "I_XF") & (null["rule"] == "family")]
    identity_max = float(null[null["response_kind"] == "paired_identity"]["max_abs_response"].max())
    family_gate = gate[gate["rule"] == "family"]
    lines = [
        "% Generated by build_v135_geometry_sensitivity.py; do not edit.\n",
        f"\\newcommand{{\\GeoIdentityMax}}{{{identity_max:.1g}}}\n",
        f"\\newcommand{{\\GeoCleanFamilyIX}}{{{_fmt_rate(float(clean_ix.iloc[0]['false_action_rate']))}}}\n",
        f"\\newcommand{{\\GeoCleanFamilyIXF}}{{{_fmt_rate(float(clean_ixf.iloc[0]['false_action_rate']))}}}\n",
        f"\\newcommand{{\\GeoTinyGaussianIX}}{{{_fmt_rate(rate('sham_tiny_gaussian_sigma_0.001', 'I_X'))}}}\n",
        f"\\newcommand{{\\GeoTinyGaussianIXF}}{{{_fmt_rate(rate('sham_tiny_gaussian_sigma_0.001', 'I_XF'))}}}\n",
        f"\\newcommand{{\\GeoTinyScalingIX}}{{{_fmt_rate(rate('sham_tiny_scaling_alpha_0.001', 'I_X'))}}}\n",
        f"\\newcommand{{\\GeoTinyScalingIXF}}{{{_fmt_rate(rate('sham_tiny_scaling_alpha_0.001', 'I_XF'))}}}\n",
        f"\\newcommand{{\\GeoMeanShiftFamilyMin}}{{{_fmt_rate(min(rate(f'mean_shift_pf_delta_{s:.3f}', 'I_XF') for s in (0.02,0.05,0.10)))}}}\n",
        f"\\newcommand{{\\GeoMeanShiftFamilyMax}}{{{_fmt_rate(max(rate(f'mean_shift_pf_delta_{s:.3f}', 'I_XF') for s in (0.02,0.05,0.10)))}}}\n",
        f"\\newcommand{{\\GeoScalingFamilyMin}}{{{_fmt_rate(min(rate(f'scaling_drift_alpha_{s:.3f}', 'I_XF') for s in (0.02,0.05,0.10)))}}}\n",
        f"\\newcommand{{\\GeoScalingFamilyMax}}{{{_fmt_rate(max(rate(f'scaling_drift_alpha_{s:.3f}', 'I_XF') for s in (0.02,0.05,0.10)))}}}\n",
        f"\\newcommand{{\\GeoDropoutFamilyMin}}{{{_fmt_rate(min(rate(f'feature_dropout_p_{s:.3f}', 'I_XF') for s in (0.02,0.05,0.10)))}}}\n",
        f"\\newcommand{{\\GeoDropoutFamilyMax}}{{{_fmt_rate(max(rate(f'feature_dropout_p_{s:.3f}', 'I_XF') for s in (0.02,0.05,0.10)))}}}\n",
        f"\\newcommand{{\\GeoGateLowerCellsMin}}{{{int(family_gate['cells_adaptive_lower'].min())}}}\n",
        f"\\newcommand{{\\GeoGateLowerCellsMax}}{{{int(family_gate['cells_adaptive_lower'].max())}}}\n",
        f"\\newcommand{{\\GeoGateCellTotal}}{{{int(family_gate['n_environment_split_cells'].max())}}}\n",
        f"\\newcommand{{\\GeoGateAdaptiveMaterialMin}}{{{_fmt_rate(float(family_gate['aligned_adaptive_material_fraction_tau0'].min()))}}}\n",
        f"\\newcommand{{\\GeoGateAdaptiveMaterialMax}}{{{_fmt_rate(float(family_gate['aligned_adaptive_material_fraction_tau0'].max()))}}}\n",
        f"\\newcommand{{\\GeoGateControlMatchedMin}}{{{_fmt_rate(float(family_gate['aligned_control_response'].min()))}}}\n",
        f"\\newcommand{{\\GeoGateControlMatchedMax}}{{{_fmt_rate(float(family_gate['aligned_control_response'].max()))}}}\n",
        f"\\newcommand{{\\GeoGateAdaptiveMatchedMin}}{{{_fmt_rate(float(family_gate['aligned_adaptive_response'].min()))}}}\n",
        f"\\newcommand{{\\GeoGateAdaptiveMatchedMax}}{{{_fmt_rate(float(family_gate['aligned_adaptive_response'].max()))}}}\n",
        f"\\newcommand{{\\GeoGateMaterialNonresponseMin}}{{{_fmt_rate(float(family_gate['aligned_adaptive_material_nonresponse_fraction'].min()))}}}\n",
        f"\\newcommand{{\\GeoGateMaterialNonresponseMax}}{{{_fmt_rate(float(family_gate['aligned_adaptive_material_nonresponse_fraction'].max()))}}}\n",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(lines), encoding="utf-8")


def write_supplement_table(path: Path, outputs: dict[str, pd.DataFrame]) -> None:
    detection = outputs["geometry_attack_detection.csv"]
    pooled = detection[
        (detection["scope_type"] == "pooled")
        & (detection["rule"] == "family")
        & detection["regime"].isin(["I_X", "I_XF"])
    ]
    attacks = [
        ("Tiny Gaussian", "sham_tiny_gaussian_sigma_0.001", "0.001"),
        ("Tiny scaling", "sham_tiny_scaling_alpha_0.001", "0.001"),
        *[("Mean shift", f"mean_shift_pf_delta_{s:.3f}", f"{s:.2f}") for s in (0.02, 0.05, 0.10)],
        *[("Scaling drift", f"scaling_drift_alpha_{s:.3f}", f"{s:.2f}") for s in (0.02, 0.05, 0.10)],
        *[("Feature dropout", f"feature_dropout_p_{s:.3f}", f"{s:.2f}") for s in (0.02, 0.05, 0.10)],
    ]
    lines = [
        "% Generated by build_v135_geometry_sensitivity.py; do not edit.\n",
        "\\begin{table*}[!tbp]\n",
        "\\caption{Geometry-aligned sensitivity under the adopted full-conformal family rule (600 observations per intervention). Material is $|\\Delta_R|>0$ and is common to both regimes.}\n",
        "\\label{tab:s-geometry-feature}\n",
        "\\centering\\footnotesize\n",
        "\\begin{tabular}{llrrr}\n",
        "\\toprule\n",
        "Intervention & Strength & $\\mathcal I_X$ response & $\\mathcal I_{XF}$ response & Material fraction \\\\\n",
        "\\midrule\n",
    ]
    for label, attack, strength in attacks:
        block = pooled[pooled["attack"] == attack].set_index("regime")
        lines.append(
            f"{label} & {strength} & {float(block.loc['I_X', 'response_rate']):.3f} & "
            f"{float(block.loc['I_XF', 'response_rate']):.3f} & "
            f"{float(block.loc['I_X', 'material_fraction_tau0']):.3f} \\\\\n"
        )
    lines += ["\\bottomrule\n", "\\end{tabular}\n", "\\end{table*}\n\n"]

    gate = outputs["geometry_gateA_summary.csv"]
    gate = gate[gate["rule"] == "family"]
    lines += [
        "\\begin{table*}[!tbp]\n",
        "\\caption{Matched geometry-aligned Gate A sensitivity. Lower cells count environment/split cells in which adaptive response is below its matched control; there are 40 cells per regime. Material nonresponse is conditional on an adaptive material row.}\n",
        "\\label{tab:s-geometry-gatea}\n",
        "\\centering\\scriptsize\n",
        "\\begin{tabular}{llrrrrrr}\n",
        "\\toprule\n",
        "Mechanism & Strength & $\\mathcal I_X$ ctrl./adapt. & $\\mathcal I_{XF}$ ctrl./adapt. & Lower $\\mathcal I_X$ & Lower $\\mathcal I_{XF}$ & Adaptive material & Material nonresponse range \\\\\n",
        "\\midrule\n",
    ]
    for mechanism in ("mean_shift", "scaling_drift"):
        label = "Mean shift" if mechanism == "mean_shift" else "Scaling drift"
        for strength in (0.02, 0.05, 0.10):
            block = gate[(gate["mechanism"] == mechanism) & (gate["strength"].sub(strength).abs() <= TOL)].set_index("regime")
            nonresponse = block["aligned_adaptive_material_nonresponse_fraction"]
            lines.append(
                f"{label} & {strength:.2f} & "
                f"{float(block.loc['I_X', 'aligned_control_response']):.3f}/{float(block.loc['I_X', 'aligned_adaptive_response']):.3f} & "
                f"{float(block.loc['I_XF', 'aligned_control_response']):.3f}/{float(block.loc['I_XF', 'aligned_adaptive_response']):.3f} & "
                f"{int(block.loc['I_X', 'cells_adaptive_lower'])}/40 & {int(block.loc['I_XF', 'cells_adaptive_lower'])}/40 & "
                f"{float(block.loc['I_X', 'aligned_adaptive_material_fraction_tau0']):.3f} & "
                f"{float(nonresponse.min()):.3f}--{float(nonresponse.max()):.3f} \\\\\n"
            )
    lines += ["\\bottomrule\n", "\\end{tabular}\n", "\\end{table*}\n"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(lines), encoding="utf-8")


def build(repo: Path, raw_dir: Path, out_dir: Path, macros_path: Path, table_path: Path) -> None:
    prereg = repo / PREREGISTRATION
    null_path = repo / "publication/artifact/evidence/reinforcement/null_unique_observations.csv"
    thresholds_path = repo / "publication/artifact/evidence/reinforcement/null_calibration_thresholds.csv"
    for path in (prereg, null_path, thresholds_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    old_count, old_tree = old_evidence_tree(repo)
    if old_count != OLD_EVIDENCE_FILES or old_tree != OLD_EVIDENCE_TREE_SHA256:
        raise RuntimeError(f"Frozen v1.3.4 evidence changed: files={old_count}, tree={old_tree}")
    obs, raw_inputs, checks = load_raw(repo, raw_dir)
    null = pd.read_csv(null_path, low_memory=False)
    thresholds = pd.read_csv(thresholds_path)
    scored = score_observations(obs, null, thresholds)
    outputs = derive_outputs(repo, scored)
    gate_summary = outputs["geometry_gateA_summary.csv"]
    checks["G10_matched_pairs_complete_in_40_environment_split_cells"] = bool(
        (gate_summary["n_environment_split_cells"] == 40).all()
    )
    adaptive = scored[scored["attack_class"] == "adaptive"]
    checks["G11_all_five_adaptive_strengths_present_every_cell"] = bool(
        set(adaptive["strength"].round(3)) == {0.02, 0.05, 0.10, 0.25, 0.50}
        and adaptive.groupby(["gate", "svd_dim", "split_seed", "model_seed", "model", "mechanism"]).size().eq(5).all()
    )
    old_count_after, old_tree_after = old_evidence_tree(repo)
    checks["G12_old_v134_evidence_byte_identical"] = bool(
        old_count_after == OLD_EVIDENCE_FILES and old_tree_after == OLD_EVIDENCE_TREE_SHA256
    )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError(f"Geometry sensitivity checks failed; no manifest written: {failed}")
    out_abs = repo / out_dir
    out_abs.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(out_abs / name, index=False)
    write_macros(repo / macros_path, outputs)
    write_supplement_table(repo / table_path, outputs)
    prereg_commit = _prereg_commit(repo)
    manifest = {
        "analysis": "paper15_v135_geometry_aligned_sensitivity",
        "artifact_version": "1.3.5",
        "status": "complete",
        "description": "targeted methodological sensitivity amendment",
        "geometry": {
            "calibration": "s(E, C_k): fixed frozen evaluation reference versus clean-resample calibration draw",
            "clean_evaluation": "s(E, B_k): fixed frozen evaluation reference versus clean-resample evaluation draw",
            "aligned_intervention": "s(E, T(B_1)): same fixed reference and fresh evaluation draw 01, changing only clean versus intervened current",
            "paired_identity": "s(B_1, B_1): exact same-item identity response, separate from clean resampling",
            "geometry_id": GEOMETRY_ID,
        },
        "preregistration": {
            "file": PREREGISTRATION,
            "sha256": _sha256(prereg),
            "commit": prereg_commit,
            "commit_timestamp": subprocess.check_output(["git", "show", "-s", "--format=%cI", prereg_commit], cwd=repo, text=True).strip(),
        },
        "design": {
            "environments": [str(s["gate"]) for s in NULL_GATES],
            "dimensions": list(DIMS),
            "split_seeds": list(SPLIT_SEEDS),
            "model_seeds": list(MODEL_SEEDS),
            "raw_jobs": 240,
            "model_cells": 600,
            "interventions": [s.tag for s in geometry_attack_specs()],
            "adaptive_strengths": [0.02, 0.05, 0.10, 0.25, 0.50],
            "matched_strengths": [0.02, 0.05, 0.10],
            "calibration_draws_per_environment_dimension_model": 200,
            "clean_evaluation_draws_per_environment_dimension_model": 200,
            "aligned_intervention_draw_index": 1,
            "alpha": ALPHA,
        },
        "frozen_old_evidence": {
            "files": old_count_after,
            "modified": 0,
            "tree_sha256": old_tree_after,
            "tag": "paper15-q1-v1.3.4",
        },
        "acceptance_checks": checks,
        "inputs": {
            "null_draws": {"path": null_path.relative_to(repo).as_posix(), "sha256": _sha256(null_path)},
            "thresholds": {"path": thresholds_path.relative_to(repo).as_posix(), "sha256": _sha256(thresholds_path)},
            "raw_jobs": raw_inputs,
        },
        "outputs": {
            name: {"rows": int(len(frame)), "sha256": _sha256(out_abs / name)} for name, frame in outputs.items()
        },
        "presentation_output": {
            "path": macros_path.as_posix(),
            "sha256": _sha256(repo / macros_path),
        },
        "presentation_table": {
            "path": table_path.as_posix(),
            "sha256": _sha256(repo / table_path),
        },
    }
    (out_abs / "geometry_sensitivity_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status": "complete", "checks": checks, "outputs": len(outputs) + 1}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--raw-dir", type=Path, default=Path("results/raw/paper15_v135_geometry"))
    parser.add_argument("--out-dir", type=Path, default=Path("publication/artifact/evidence/geometry_sensitivity"))
    parser.add_argument("--macros", type=Path, default=Path("publication/tdsc/tables/geometry_sensitivity_macros.tex"))
    parser.add_argument("--table", type=Path, default=Path("publication/tdsc/tables/s_geometry_sensitivity.tex"))
    args = parser.parse_args()
    build(args.repo_root.resolve(), args.raw_dir, args.out_dir, args.macros, args.table)


if __name__ == "__main__":
    main()
