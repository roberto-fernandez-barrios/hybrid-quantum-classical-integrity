"""Assemble the preregistered v1.3.7 corrective evidence.

This builder is deliberately downstream-only.  It reads the immutable v1.3.6
evidence and the isolated deterministic replay rows emitted by
``run_v137_correction.py``; it never writes to a historical evidence directory.
Every corrected historical observation retains its previous JSD coordinate and
the legacy/current decision comparison.  Label-geometry sensitivity is emitted
to a separate directory and is not substituted for the executed primary design.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from src.experiments.build_q1_policy_evidence import (
    ALPHA,
    BATCH_FOR_POLICY,
    BATCH_REGIME_NAMES,
    CELL,
    NEAR_NULL_SHAMS,
    POLICY_REGIME_NAMES,
    RULES,
    TOL,
    _exact_fire,
    score_frame,
)
from src.experiments.build_q1_adversarial_evidence import load_gate_a
from src.experiments.build_q1_reinforcement_evidence import (
    CALIBRATED_SENSORS,
    EXPECTED_FILES_PER_GATE,
    EXACT_REFERENCE_SENSORS,
    N_NULL_ATTACKS,
    NULL_GATES,
    REGIMES as BATCH_REGIMES,
    _load_dir,
    _thresholds,
)
from src.hsaas.policy import POLICIES, POLICY_CLASS, REGIMES as POLICY_REGIMES, Evidence, decide
from src.integrity.family_calibration import (
    conformal_family_pvalues,
    legacy_v12_family_scores,
    legacy_v12_family_threshold,
    legacy_v136_conformal_family_pvalues,
    rank_scores,
)


ANALYSIS = "paper15_v137_jsd_label_geometry_correction"
SCHEMA_VERSION = 1
PREREGISTRATION = "manuscript/v137_jsd_label_geometry_prereg.md"
PREREG_COMMIT = "711a46c5c9af567d6777dd3811f44ef3a7987224"
V136_TAG = "paper15-q1-v1.3.6"
V135_TAG = "paper15-q1-v1.3.5"
CORRECTED = (
    "integrity_jsd_vs_clean_eval",
    "integrity_score_jsd_vs_clean_eval",
)
ALL_DECOMPOSITION_SENSORS = tuple(CALIBRATED_SENSORS) + (
    "integrity_ks_mean_vs_clean_eval",
)
KEYS = ["gate", "svd_dim", "split_seed", "model_seed", "model", "attack"]
DECISION_COLUMNS = [
    f"fire_{rule}__{regime}" for rule in RULES for regime in BATCH_REGIME_NAMES
] + [f"pvalue_family__{regime}" for regime in BATCH_REGIME_NAMES]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, lineterminator="\n")


def _finite(frame: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    values = frame[list(columns)].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(values).all():
        bad = int((~np.isfinite(values)).sum())
        raise ValueError(f"{label}: {bad} nonfinite current scientific coordinates")


def _load_raw(repo: Path, raw_dir: Path) -> tuple[pd.DataFrame, list[dict[str, Any]], list[dict[str, str]]]:
    csvs = sorted(raw_dir.glob("v137__*.csv"))
    metas = sorted(raw_dir.glob("v137__*.json"))
    if len(csvs) != 300 or len(metas) != 300:
        raise ValueError(f"corrective queue incomplete: {len(csvs)} CSV and {len(metas)} JSON; expected 300 each")
    metadata: list[dict[str, Any]] = []
    inputs: list[dict[str, str]] = []
    expected_csv: set[str] = set()
    for path in metas:
        meta = json.loads(path.read_text(encoding="utf-8"))
        if meta.get("schema_version") != 2 or meta.get("analysis") != ANALYSIS:
            raise ValueError(f"unexpected metadata schema/analysis in {path}")
        csv_path = path.with_suffix(".csv")
        if not csv_path.is_file() or _sha256(csv_path) != meta["csv_sha256"]:
            raise ValueError(f"raw hash mismatch for {csv_path}")
        if not all(bool(m["all_corrected_jsd_finite"]) for m in meta["models"]):
            raise ValueError(f"nonfinite corrected JSD reported by {path}")
        if max(float(m["replay_max_abs_non_jsd_difference"]) for m in meta["models"]) > 1e-9:
            raise ValueError(f"frozen replay mismatch reported by {path}")
        metadata.append(meta)
        expected_csv.add(csv_path.name)
        inputs.extend(
            [
                {"role": "corrective_raw_csv", "path": csv_path.relative_to(repo).as_posix(), "sha256": _sha256(csv_path)},
                {"role": "corrective_raw_metadata", "path": path.relative_to(repo).as_posix(), "sha256": _sha256(path)},
            ]
        )
    if expected_csv != {p.name for p in csvs}:
        raise ValueError("raw CSV/metadata stems do not match exactly")
    raw = pd.concat((pd.read_csv(p, low_memory=False) for p in csvs), ignore_index=True, sort=False)
    counts = raw["scope"].value_counts().to_dict()
    expected = {
        "null_draw": 26400,
        "core_original": 15120,  # calibrated 10,800 plus Gate-1 4,320
        "gateA_original": 9600,
        "feature_aligned": 13200,
        "label_aligned": 3600,
    }
    if counts != expected or len(raw) != 67920:
        raise ValueError(f"unexpected raw scope counts: {counts}")
    if raw.duplicated(KEYS + ["scope"]).any():
        raise ValueError("duplicate corrective raw row identifier")
    _finite(raw, CORRECTED, "corrective raw")
    return raw, metadata, inputs


def _merge_correction(
    old: pd.DataFrame,
    raw: pd.DataFrame,
    scope: str,
    columns: Iterable[str],
) -> pd.DataFrame:
    cols = list(columns)
    rhs = raw[raw["scope"] == scope][KEYS + cols].copy()
    if len(rhs) != len(old):
        raise ValueError(f"{scope}: historical/raw row mismatch {len(old)} != {len(rhs)}")
    out = old.merge(rhs, on=KEYS, how="left", validate="one_to_one", suffixes=("", "__corrected"))
    for col in cols:
        new = f"{col}__corrected"
        if out[new].isna().any():
            raise ValueError(f"{scope}: missing corrected {col}")
        out[f"previous__{col}"] = out[col]
        out[col] = out.pop(new)
    out["correction_scope"] = scope
    return out


def _restore_descriptive_ks(
    repo: Path,
    null: pd.DataFrame,
    gate_a: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Restore the frozen KS statistic omitted from compact historical tables.

    No statistic is recomputed.  The exact per-job frozen rows are read and
    joined by the canonical row identifier; this supports the required sensor
    decomposition while leaving the prespecified ``ks_reject05`` component
    untouched.
    """

    null_parts: list[pd.DataFrame] = []
    for spec in NULL_GATES:
        full, _, _ = _load_dir(
            repo / f"results/raw/paper15_v11_null_{spec['gate']}",
            str(spec["gate"]),
            expected_files=EXPECTED_FILES_PER_GATE,
            expected_models=set(spec["models"]),
            expected_attacks=N_NULL_ATTACKS,
            repo=repo,
        )
        null_parts.append(full)
    null_full = pd.concat(null_parts, ignore_index=True, sort=False)
    gate_a_full, _, _ = load_gate_a(repo)
    gate_a_full = gate_a_full[gate_a_full["attack"] != "clean"]

    def attach(compact: pd.DataFrame, full: pd.DataFrame, label: str) -> pd.DataFrame:
        rhs = full[KEYS + ["integrity_ks_mean_vs_clean_eval"]]
        out = compact.merge(rhs, on=KEYS, how="left", validate="one_to_one")
        if out["integrity_ks_mean_vs_clean_eval"].isna().any():
            raise ValueError(f"{label}: frozen KS-statistic join is incomplete")
        return out

    return attach(null, null_full, "null"), attach(gate_a, gate_a_full, "Gate A")


def _score_frame_legacy(
    rows: pd.DataFrame,
    calibration: dict[str, np.ndarray],
    thresholds: dict[str, float],
) -> pd.DataFrame:
    """Exact v1.3.6 family semantics, isolated to before/after reproduction."""

    out = rows.copy()
    values = {s: pd.to_numeric(rows[s], errors="coerce").to_numpy(dtype=float) for s in CALIBRATED_SENSORS}
    for sensor in CALIBRATED_SENSORS:
        out[f"fire_sensor__{sensor}"] = values[sensor] > float(thresholds[sensor])
        out[f"rank__{sensor}"] = rank_scores(values[sensor], calibration[sensor])
    for regime, sensors in BATCH_REGIMES.items():
        out[f"fire_union__{regime}"] = out[[f"fire_sensor__{s}" for s in sensors]].any(axis=1)
        cal_score = legacy_v12_family_scores(calibration, calibration, sensors)
        q = legacy_v12_family_threshold(cal_score, ALPHA)
        v12 = legacy_v12_family_scores(values, calibration, sensors)
        out[f"score_family_v12__{regime}"] = v12
        out[f"fire_family_v12__{regime}"] = v12 > q
        p = legacy_v136_conformal_family_pvalues(calibration, values, sensors)
        out[f"pvalue_family__{regime}"] = p
        out[f"fire_family__{regime}"] = p <= ALPHA + TOL
    return out


def _score_cells(
    rows: pd.DataFrame,
    null: pd.DataFrame,
    thresholds: pd.DataFrame,
    *,
    legacy: bool,
) -> pd.DataFrame:
    calibration = null[null["attack_priority_group"] == "null_calibration"]
    thr = thresholds[thresholds["order_statistic_rank"] > 0].pivot_table(
        index=CELL, columns="sensor", values="threshold", aggfunc="first"
    )
    parts: list[pd.DataFrame] = []
    scorer = _score_frame_legacy if legacy else score_frame
    for key, cal in calibration.groupby(CELL, sort=True):
        if len(cal) != 200:
            raise ValueError(f"{key}: calibration count {len(cal)}, expected 200")
        target = rows[
            (rows["gate"] == key[0])
            & (rows["svd_dim"] == key[1])
            & (rows["model"] == key[2])
        ]
        if target.empty:
            continue
        cal_map = {s: pd.to_numeric(cal[s], errors="coerce").to_numpy(float) for s in CALIBRATED_SENSORS}
        cell_thr = {s: float(thr.loc[key, s]) for s in CALIBRATED_SENSORS}
        parts.append(scorer(target, cal_map, cell_thr))
    if not parts:
        return rows.iloc[0:0].copy()
    out = pd.concat(parts, ignore_index=True, sort=False)
    if len(out) != len(rows):
        raise ValueError(f"scoring lost rows: {len(out)} != {len(rows)}")
    return out.sort_values(KEYS).reset_index(drop=True)


def _add_exact(frame: pd.DataFrame, *, paired: bool = False) -> pd.DataFrame:
    out = frame.copy()
    if paired:
        cols = [
            "paired_pred_disagreement",
            "paired_label_flip_rate",
            "paired_confusion_profile_l1",
            "paired_confusion_profile_jsd",
        ]
        out["fire_exact"] = (
            out[cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).abs().max(axis=1) > TOL
        )
    else:
        out["fire_exact"] = _exact_fire(out).to_numpy()
    return out


def _ensure_delta(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    if "delta_bal_acc" not in out:
        out["delta_bal_acc"] = (
            pd.to_numeric(out["bal_acc_clean"], errors="coerce")
            - pd.to_numeric(out["bal_acc"], errors="coerce")
        )
    return out


def _score_aligned(
    rows: pd.DataFrame,
    null: pd.DataFrame,
    thresholds: pd.DataFrame,
    *,
    legacy: bool = False,
) -> pd.DataFrame:
    attack = _score_cells(rows, null, thresholds, legacy=legacy)
    clean = rows.copy()
    for sensor in CALIBRATED_SENSORS:
        clean[sensor] = clean[f"clean__{sensor}"]
    clean = _score_cells(clean, null, thresholds, legacy=legacy)
    for regime in BATCH_REGIME_NAMES:
        for rule in ("union", "family"):
            attack[f"clean_fire_{rule}__{regime}"] = clean[f"fire_{rule}__{regime}"].to_numpy()
    attack = _add_exact(attack, paired=True)
    delta = pd.to_numeric(attack["delta_bal_acc"], errors="coerce").abs()
    attack["material_tau0"] = delta > TOL
    attack["material_tau002"] = delta > 0.02
    attack["material_tau005"] = delta > 0.05
    return attack


def _with_previous(current: pd.DataFrame, previous: pd.DataFrame) -> pd.DataFrame:
    keep = KEYS + [f"fire_sensor__{s}" for s in CALIBRATED_SENSORS] + DECISION_COLUMNS
    rhs = previous[keep].rename(columns={c: f"previous__{c}" for c in keep if c not in KEYS})
    return current.merge(rhs, on=KEYS, how="left", validate="one_to_one")


def _actions(
    frame: pd.DataFrame,
    regime: str,
    policy: str,
    *,
    family_column: str = "fire_family",
) -> np.ndarray:
    batch = BATCH_FOR_POLICY[regime]
    spec = POLICY_REGIMES[regime]
    union = frame[f"fire_union__{batch}"].astype(bool).to_numpy()
    family = frame[f"{family_column}__{batch}"].astype(bool).to_numpy()
    exact = (
        frame["fire_exact"].astype(bool).to_numpy()
        if "fire_exact" in frame
        else np.zeros(len(frame), dtype=bool)
    )
    return np.asarray(
        [
            decide(
                policy,
                spec,
                Evidence(bool(union[i]), bool(family[i]), bool(exact[i]) if spec.trusted_reference else None),
            ).action
            for i in range(len(frame))
        ]
    )


def _policy_counts(frame: pd.DataFrame, geometry: str) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    delta = pd.to_numeric(frame["delta_bal_acc"], errors="coerce").abs().to_numpy()
    material = delta > TOL
    for regime in POLICY_REGIME_NAMES:
        for policy in POLICIES:
            action = _actions(frame, regime, policy)
            records.append(
                {
                    "geometry": geometry,
                    "regime": regime,
                    "policy": policy,
                    "policy_class": POLICY_CLASS[policy],
                    "n": len(frame),
                    "n_material": int(material.sum()),
                    "allow": int((action == "allow").sum()),
                    "hold": int((action == "hold").sum()),
                    "block": int((action == "block").sum()),
                    "unsafe_allow": int(((action == "allow") & material).sum()),
                    "material_held_or_blocked": int(((action != "allow") & material).sum()),
                }
            )
    return pd.DataFrame.from_records(records)


def _gate_f_summary(old_null: pd.DataFrame, new_null: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for geometry, frame in (("v136", old_null), ("v137_corrected_jsd", new_null)):
        for observation_class, mask in (
            ("clean_evaluation", frame["attack_priority_group"] == "null_evaluation"),
            ("near_null", frame["attack"].isin(NEAR_NULL_SHAMS)),
        ):
            rows = frame.loc[mask]
            for regime in BATCH_REGIME_NAMES:
                for rule in ("union", "family_v12", "family"):
                    fire = rows[f"fire_{rule}__{regime}"].astype(bool)
                    records.append(
                        {
                            "geometry": geometry,
                            "observation_class": observation_class,
                            "regime": regime,
                            "rule": rule,
                            "n": len(rows),
                            "n_fire": int(fire.sum()),
                            "fire_rate": float(fire.mean()),
                            "interpretation": "descriptive; the executed clean draws violate the exchangeability premise" if observation_class == "clean_evaluation" else "prespecified near-null stress-control response; not operational traffic",
                        }
                    )
    return pd.DataFrame.from_records(records)


def _primary_policy_metrics(
    frame: pd.DataFrame,
    null: pd.DataFrame,
    benign_exact: pd.DataFrame,
    geometry: str,
    family_rule: str,
) -> pd.DataFrame:
    evaluation = null[null["attack_priority_group"] == "null_evaluation"].copy()
    near_null = null[null["attack"].isin(NEAR_NULL_SHAMS)].copy()
    exact_rhs = benign_exact[KEYS + ["fire_exact"]]
    near_null = near_null.merge(exact_rhs, on=KEYS, how="left", validate="one_to_one")
    if near_null["fire_exact"].isna().any():
        raise ValueError("near-null exact-reference alignment is incomplete")
    exact_zero = null[null["attack"].isin(["clean", "sham_identity"])].copy()
    exact_zero["fire_exact"] = False
    if len(evaluation) != 12000 or len(near_null) != 1200 or len(exact_zero) != 1200:
        raise ValueError("Gate-D clean/near-null/exact-zero denominators changed")

    material = pd.to_numeric(frame["delta_bal_acc"], errors="coerce").abs().to_numpy() > TOL
    records: list[dict[str, Any]] = []
    family_column = "fire_family" if family_rule == "conformal" else "fire_family_v12"
    for regime in POLICY_REGIME_NAMES:
        clean = exact_zero if POLICY_REGIMES[regime].trusted_reference else evaluation
        for policy in POLICIES:
            attacked_actions = _actions(frame, regime, policy, family_column=family_column)
            clean_actions = _actions(clean, regime, policy, family_column=family_column)
            benign_actions = _actions(near_null, regime, policy, family_column=family_column)
            records.append(
                {
                    "geometry": geometry,
                    "family_rule": family_rule,
                    "regime": regime,
                    "policy": policy,
                    "policy_class": POLICY_CLASS[policy],
                    "n_clean": len(clean),
                    "false_hold": int((clean_actions == "hold").sum()),
                    "false_block": int((clean_actions == "block").sum()),
                    "decision_fpr": float((clean_actions != "allow").mean()),
                    "n_benign": len(near_null),
                    "benign_hold": int((benign_actions == "hold").sum()),
                    "benign_block": int((benign_actions == "block").sum()),
                    "benign_interruption_rate": float((benign_actions != "allow").mean()),
                    "n_intervened": len(frame),
                    "n_material": int(material.sum()),
                    "allow": int((attacked_actions == "allow").sum()),
                    "hold": int((attacked_actions == "hold").sum()),
                    "block": int((attacked_actions == "block").sum()),
                    "unsafe_allow": int(((attacked_actions == "allow") & material).sum()),
                    "material_held_or_blocked": int(((attacked_actions != "allow") & material).sum()),
                    "n_immaterial": int((~material).sum()),
                    "integrity_only_hold_block": int(((attacked_actions != "allow") & ~material).sum()),
                }
            )
    return pd.DataFrame.from_records(records)


def _without_ks(frame: pd.DataFrame, null: pd.DataFrame) -> pd.DataFrame:
    calibration = null[null["attack_priority_group"] == "null_calibration"]
    out_parts: list[pd.DataFrame] = []
    for key, cal in calibration.groupby(CELL, sort=True):
        rows = frame[(frame["gate"] == key[0]) & (frame["svd_dim"] == key[1]) & (frame["model"] == key[2])].copy()
        if rows.empty:
            continue
        for regime, sensors0 in BATCH_REGIMES.items():
            sensors = tuple(s for s in sensors0 if s != "integrity_ks_reject05_vs_clean_eval")
            fire_cols = [f"fire_sensor__{s}" for s in sensors]
            rows[f"fire_union_without_ks__{regime}"] = rows[fire_cols].any(axis=1)
            c = {s: pd.to_numeric(cal[s], errors="coerce").to_numpy(float) for s in sensors}
            v = {s: pd.to_numeric(rows[s], errors="coerce").to_numpy(float) for s in sensors}
            p = conformal_family_pvalues(c, v, sensors)
            rows[f"pvalue_family_without_ks__{regime}"] = p
            rows[f"fire_family_without_ks__{regime}"] = p <= ALPHA + TOL
        out_parts.append(rows)
    return pd.concat(out_parts, ignore_index=True).sort_values(KEYS).reset_index(drop=True)


def _mechanism_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    if "attack_class" not in out:
        out["attack_class"] = out.get("attack_family", "unknown")
    if "mechanism" not in out:
        attack = out["attack"].astype(str)
        choices = [
            attack.str.startswith("sham_tiny_gaussian"),
            attack.str.startswith("sham_tiny_scaling"),
            attack.str.startswith("feature_sign_flip"),
            attack.str.startswith("mean_shift"),
            attack.str.startswith("scaling_drift"),
            attack.str.startswith("feature_dropout"),
            attack.str.startswith("label_flip_prior_preserving"),
            attack.str.startswith("label_flip"),
            attack.str.startswith("cluster_preserving_mean_shift"),
            attack.str.startswith("cluster_preserving_scaling"),
            attack.str.startswith("clean_resample"),
            attack.eq("sham_identity"),
        ]
        values = [
            "tiny_gaussian", "tiny_scaling", "sign_flip", "mean_shift", "scaling_drift",
            "dropout", "label_flip_prior_preserving", "label_flip", "mean_shift", "scaling_drift",
            "clean_resample", "identity",
        ]
        out["mechanism"] = np.select(choices, values, default="unknown")
    if "strength" not in out:
        out["strength"] = pd.to_numeric(out.get("atk_strength_nominal", np.nan), errors="coerce")
    return out


def _decomposition(scopes: dict[str, pd.DataFrame]) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for scope, frame0 in scopes.items():
        frame = _mechanism_columns(frame0)
        group_cols = ["attack", "attack_class", "mechanism", "strength"]
        for key, group in frame.groupby(group_cols, sort=True, dropna=False):
            base = dict(zip(group_cols, key if isinstance(key, tuple) else (key,), strict=True))
            for sensor in ALL_DECOMPOSITION_SENSORS:
                values = pd.to_numeric(group[sensor], errors="coerce").to_numpy(float)
                member_regimes = [r for r, ss in BATCH_REGIMES.items() if sensor in ss]
                if not member_regimes:
                    member_regimes = ["descriptive_only"]
                for regime in member_regimes:
                    fire_col = f"fire_sensor__{sensor}"
                    has_fire = fire_col in group
                    fire = group[fire_col].astype(bool).to_numpy() if has_fire else np.zeros(len(group), dtype=bool)
                    only = np.zeros(len(group), dtype=bool)
                    family = np.zeros(len(group), dtype=bool)
                    if regime != "descriptive_only" and has_fire:
                        peers = [
                            f"fire_sensor__{s}"
                            for s in BATCH_REGIMES[regime]
                            if s != sensor and f"fire_sensor__{s}" in group
                        ]
                        other = group[peers].any(axis=1).to_numpy(bool) if peers else np.zeros(len(group), bool)
                        only = fire & ~other
                        family_col = f"fire_family__{regime}"
                        if family_col in group:
                            family = group[family_col].astype(bool).to_numpy()
                    records.append(
                        {
                            "scope": scope,
                            **base,
                            "regime": regime,
                            "sensor": sensor,
                            "n": len(group),
                            "n_finite": int(np.isfinite(values).sum()),
                            "mean_response": float(np.mean(values)),
                            "median_response": float(np.median(values)),
                            "min_response": float(np.min(values)),
                            "max_response": float(np.max(values)),
                            "n_sensor_fire": int(fire.sum()) if regime != "descriptive_only" and has_fire else math.nan,
                            "n_only_sensor_fire": int(only.sum()) if regime != "descriptive_only" and has_fire else math.nan,
                            "n_family_fire": int(family.sum()) if regime != "descriptive_only" and has_fire else math.nan,
                            "note": "KS mean is descriptive; ks_reject05 is the prespecified calibrated component" if sensor == "integrity_ks_mean_vs_clean_eval" else "frozen sensor component",
                        }
                    )
    return pd.DataFrame.from_records(records)


def _ablation(scopes: dict[str, pd.DataFrame], null: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for scope, frame0 in scopes.items():
        frame = _mechanism_columns(_without_ks(frame0, null))
        group_cols = ["attack", "attack_class", "mechanism", "strength"]
        for key, group in frame.groupby(group_cols, sort=True, dropna=False):
            base = dict(zip(group_cols, key if isinstance(key, tuple) else (key,), strict=True))
            for regime in BATCH_REGIME_NAMES:
                for rule in ("union", "family"):
                    primary = group[f"fire_{rule}__{regime}"].astype(bool)
                    ablated = group[f"fire_{rule}_without_ks__{regime}"].astype(bool)
                    records.append(
                        {
                            "scope": scope,
                            **base,
                            "regime": regime,
                            "rule": rule,
                            "n": len(group),
                            "primary_n_fire": int(primary.sum()),
                            "without_ks_n_fire": int(ablated.sum()),
                            "delta_n_fire": int(ablated.sum() - primary.sum()),
                            "surviving_primary_fires": int((primary & ablated).sum()),
                            "ablation_role": "descriptive frozen-only; never replaces the prespecified primary family",
                        }
                    )
    return pd.DataFrame.from_records(records)


def _mde(thresholds: pd.DataFrame) -> pd.DataFrame:
    rows = thresholds[thresholds["sensor"] == "integrity_confusion_profile_l1"].copy()
    rows["batch_size"] = np.where(rows["gate"] == "gate2_id_256", 256, 128)
    rows["lattice_step_l1"] = 2.0 / rows["batch_size"]
    rows["minimum_net_confusion_count_units_to_exceed_threshold"] = (
        np.floor(rows["threshold"] * rows["batch_size"] / 2.0).astype(int) + 1
    )
    rows["minimum_observable_l1_strictly_above_threshold"] = (
        2.0 * rows["minimum_net_confusion_count_units_to_exceed_threshold"] / rows["batch_size"]
    )
    rows["interpretation"] = (
        "exact 2/n L1 lattice implication for net confusion-cell count displacement; altered labels can cancel in aggregate; descriptive, not a statistical-power guarantee"
    )
    return rows


def _label_outputs(
    original_old: pd.DataFrame,
    original_new: pd.DataFrame,
    aligned: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    old = original_old[original_old["attack_family"] == "target_shift"].sort_values(KEYS).reset_index(drop=True)
    new = original_new[original_new["attack_family"] == "target_shift"].sort_values(KEYS).reset_index(drop=True)
    ali = aligned.sort_values(KEYS).reset_index(drop=True)
    if not (old[KEYS].equals(new[KEYS]) and old[KEYS].equals(ali[KEYS])):
        raise ValueError("label original/aligned row identifiers differ")
    observations = ali[KEYS + [
        "attack_class", "mechanism", "strength", "branch", "clean_bal_acc", "attack_bal_acc",
        "delta_bal_acc", "fire_exact", "paired_label_flip_rate", "paired_confusion_profile_l1",
        "paired_confusion_profile_jsd",
    ] + list(CALIBRATED_SENSORS) + [
        name
        for sensor in CALIBRATED_SENSORS
        for name in (f"clean__{sensor}", f"paired__{sensor}", f"delta__{sensor}")
    ] + DECISION_COLUMNS + [
        f"clean_fire_{rule}__{regime}"
        for rule in ("union", "family")
        for regime in BATCH_REGIME_NAMES
    ]].copy()
    observations = observations.rename(columns={
        c: f"aligned__{c}" for c in observations.columns if c not in KEYS + ["attack_class", "mechanism", "strength", "branch"]
    })
    prefix_cols = list(CALIBRATED_SENSORS) + DECISION_COLUMNS + ["delta_bal_acc", "fire_exact"]
    for label, frame in (("original", old), ("corrected_original", new)):
        for col in prefix_cols:
            observations[f"{label}__{col}"] = frame[col].to_numpy()
    observations["original_material"] = pd.to_numeric(old["delta_bal_acc"]).abs().to_numpy() > TOL
    observations["aligned_material"] = pd.to_numeric(ali["delta_bal_acc"]).abs().to_numpy() > TOL
    aggregate_cols = [
        "paired__integrity_label_prior_shift",
        "paired__integrity_label_jsd",
        "paired__integrity_confusion_profile_l1",
        "paired__integrity_confusion_profile_jsd",
    ]
    aggregate = ali[aggregate_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).abs().max(axis=1)
    observations["aggregate_separable"] = aggregate.to_numpy() > TOL
    observations["aggregate_blind"] = ~observations["aggregate_separable"]

    detection_records: list[dict[str, Any]] = []
    frames = {"original_v136": old, "corrected_original": new, "aligned": ali}
    for geometry, frame in frames.items():
        material = observations["original_material"] if geometry != "aligned" else observations["aligned_material"]
        for key, idx in observations.groupby(["attack", "attack_class", "mechanism", "strength"], sort=True).groups.items():
            positions = np.asarray(list(idx), dtype=int)
            for subset_name, subset_mask in (
                ("all", np.ones(len(positions), dtype=bool)),
                ("material", material.iloc[positions].to_numpy(bool)),
                ("aggregate_separable", observations["aggregate_separable"].iloc[positions].to_numpy(bool)),
                ("aggregate_blind", observations["aggregate_blind"].iloc[positions].to_numpy(bool)),
            ):
                pos = positions[subset_mask]
                for regime in BATCH_REGIME_NAMES:
                    for rule in ("union", "family"):
                        fire = frame.iloc[pos][f"fire_{rule}__{regime}"].astype(bool)
                        clean_fire = (
                            frame.iloc[pos][f"clean_fire_{rule}__{regime}"].astype(bool)
                            if geometry == "aligned"
                            else pd.Series(False, index=fire.index)
                        )
                        detection_records.append(
                            {
                                "geometry": geometry,
                                "attack": key[0],
                                "attack_class": key[1],
                                "mechanism": key[2],
                                "strength": key[3],
                                "subset": subset_name,
                                "regime": regime,
                                "rule": rule,
                                "n": len(pos),
                                "n_fire": int(fire.sum()),
                                "response_rate": float(fire.mean()) if len(pos) else math.nan,
                                "clean_n_fire": int(clean_fire.sum()),
                                "attack_only": int((fire & ~clean_fire).sum()),
                                "clean_only": int((~fire & clean_fire).sum()),
                                "both_fire": int((fire & clean_fire).sum()),
                            }
                        )
    detection = pd.DataFrame.from_records(detection_records)

    material_records: list[dict[str, Any]] = []
    for key, idx in observations.groupby(["attack", "attack_class", "mechanism", "strength"], sort=True).groups.items():
        group = observations.loc[idx]
        material_records.append(
            {
                "attack": key[0], "attack_class": key[1], "mechanism": key[2], "strength": key[3],
                "n": len(group),
                "original_n_material": int(group["original_material"].sum()),
                "aligned_n_material": int(group["aligned_material"].sum()),
                "n_aggregate_separable": int(group["aggregate_separable"].sum()),
                "n_aggregate_blind": int(group["aggregate_blind"].sum()),
                "aligned_family_detected_aggregate_separable": int((
                    group["aggregate_separable"] & group["aligned__fire_family__I_XFY"].astype(bool)
                ).sum()),
                "aligned_union_detected_aggregate_separable": int((
                    group["aggregate_separable"] & group["aligned__fire_union__I_XFY"].astype(bool)
                ).sum()),
            }
        )
    material_table = pd.DataFrame.from_records(material_records)
    for rule in ("family", "union"):
        material_table[f"aligned_{rule}_aggregate_separable_fraction"] = (
            material_table[f"aligned_{rule}_detected_aggregate_separable"] / material_table["n_aggregate_separable"]
        )

    policy = pd.concat(
        [
            _policy_counts(old, "original_v136"),
            _policy_counts(new, "corrected_original"),
            _policy_counts(ali, "aligned"),
        ],
        ignore_index=True,
    )

    def total(geometry: str, rule: str, subset: pd.Series) -> int:
        frame = frames[geometry]
        return int(frame.loc[subset.to_numpy(bool), f"fire_{rule}__I_XFY"].sum())

    old_mat = observations["original_material"]
    ali_mat = observations["aligned_material"]
    sep = observations["aggregate_separable"]
    blind = observations["aggregate_blind"]
    summary = pd.DataFrame.from_records(
        [
            {"question": "Q1", "metric": "conformal I_XFY on material label interventions", "v136": total("original_v136", "family", old_mat), "v137": total("aligned", "family", ali_mat), "v136_denominator": int(old_mat.sum()), "v137_denominator": int(ali_mat.sum())},
            {"question": "Q2", "metric": "union I_XFY on material label interventions", "v136": total("original_v136", "union", old_mat), "v137": total("aligned", "union", ali_mat), "v136_denominator": int(old_mat.sum()), "v137_denominator": int(ali_mat.sum())},
            {"question": "Q3", "metric": "direction family/union", "v136": "original", "v137": "computed directly; see numeric Q1-Q2", "v136_denominator": math.nan, "v137_denominator": math.nan},
            {"question": "Q4", "metric": "aggregate-blind rows: attack-only family/union beyond paired clean response", "v136": math.nan, "v137": f"family_attack_only={int((ali.loc[blind.to_numpy(bool), 'fire_family__I_XFY'].astype(bool).to_numpy() & ~ali.loc[blind.to_numpy(bool), 'clean_fire_family__I_XFY'].astype(bool).to_numpy()).sum())};union_attack_only={int((ali.loc[blind.to_numpy(bool), 'fire_union__I_XFY'].astype(bool).to_numpy() & ~ali.loc[blind.to_numpy(bool), 'clean_fire_union__I_XFY'].astype(bool).to_numpy()).sum())}", "v136_denominator": math.nan, "v137_denominator": int(blind.sum())},
            {"question": "Q5", "metric": "aggregate-separable aligned detection", "v136": math.nan, "v137": f"family={total('aligned', 'family', sep)}/{int(sep.sum())};union={total('aligned', 'union', sep)}/{int(sep.sum())}", "v136_denominator": math.nan, "v137_denominator": int(sep.sum())},
            {"question": "Q6", "metric": "policy F/D effect", "v136": "see policy table", "v137": "see policy table", "v136_denominator": len(old), "v137_denominator": len(ali)},
            {"question": "Q7", "metric": "material altered results served", "v136": int(old_mat.sum()), "v137": int(ali_mat.sum()), "v136_denominator": len(old), "v137_denominator": len(ali)},
            {"question": "Q8", "metric": "invariant conclusions", "v136": "structural blind regions; exact trusted-reference checks", "v137": "unchanged; sensitivity is finite-design statistical response only", "v136_denominator": math.nan, "v137_denominator": math.nan},
        ]
    )
    return {
        "label_geometry_observations.csv": observations,
        "label_geometry_detection.csv": detection,
        "label_geometry_material.csv": material_table,
        "label_geometry_policy_effect.csv": policy,
        "label_geometry_summary.csv": summary,
    }


def _delta_table(scopes: dict[str, pd.DataFrame]) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for scope, frame in scopes.items():
        coordinates = [
            coordinate
            for sensor in CORRECTED
            for coordinate in (sensor, f"clean__{sensor}", f"paired__{sensor}", f"delta__{sensor}")
            if f"previous__{coordinate}" in frame and coordinate in frame
        ]
        for coordinate in coordinates:
            sensor = next(sensor for sensor in CORRECTED if coordinate.endswith(sensor))
            previous = pd.to_numeric(frame[f"previous__{coordinate}"], errors="coerce").to_numpy(float)
            corrected = pd.to_numeric(frame[coordinate], errors="coerce").to_numpy(float)
            value_changed = ~(np.isclose(previous, corrected, rtol=0.0, atol=1e-15, equal_nan=True))
            fire_old_col = f"previous__fire_sensor__{sensor}"
            fire_new_col = f"fire_sensor__{sensor}"
            primary_coordinate = coordinate == sensor
            fire_old = frame[fire_old_col].astype(bool).to_numpy() if primary_coordinate and fire_old_col in frame else np.zeros(len(frame), bool)
            fire_new = frame[fire_new_col].astype(bool).to_numpy() if primary_coordinate and fire_new_col in frame else np.zeros(len(frame), bool)
            decision_change = np.zeros(len(frame), bool)
            if primary_coordinate:
                for regime in BATCH_REGIME_NAMES:
                    for rule in ("union", "family"):
                        old_col = f"previous__fire_{rule}__{regime}"
                        new_col = f"fire_{rule}__{regime}"
                        if old_col in frame and new_col in frame:
                            decision_change |= frame[old_col].astype(bool).to_numpy() != frame[new_col].astype(bool).to_numpy()
            keep = value_changed | (fire_old != fire_new) | decision_change
            for pos in np.flatnonzero(keep):
                row = frame.iloc[pos]
                rec: dict[str, Any] = {
                    "correction_scope": scope,
                    **{key: row[key] for key in KEYS},
                    "affected_row_identifier": "|".join(str(row[key]) for key in KEYS),
                    "sensor": sensor,
                    "coordinate": coordinate,
                    "previous_value": previous[pos],
                    "corrected_value": corrected[pos],
                    "previous_sensor_fire": bool(fire_old[pos]) if primary_coordinate and fire_old_col in frame else math.nan,
                    "corrected_sensor_fire": bool(fire_new[pos]) if primary_coordinate and fire_new_col in frame else math.nan,
                    "reason": "shared overflow-inclusive histogram edges; finite PMF normalization",
                }
                for regime in BATCH_REGIME_NAMES:
                    for rule in ("union", "family"):
                        old_col = f"previous__fire_{rule}__{regime}"
                        new_col = f"fire_{rule}__{regime}"
                        rec[f"previous_{rule}_fire__{regime}"] = bool(row[old_col]) if primary_coordinate and old_col in row.index else math.nan
                        rec[f"corrected_{rule}_fire__{regime}"] = bool(row[new_col]) if primary_coordinate and new_col in row.index else math.nan
                records.append(rec)
    return pd.DataFrame.from_records(records)


def _headline(
    old_core: pd.DataFrame,
    new_core: pd.DataFrame,
    old_ga: pd.DataFrame,
    new_ga: pd.DataFrame,
    old_geom: pd.DataFrame,
    new_geom: pd.DataFrame,
    old_null: pd.DataFrame,
    new_null: pd.DataFrame,
    benign: pd.DataFrame,
    label_summary: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    def add(claim: str, old: Any, new: Any, delta: Any, reason: str) -> None:
        rows.append({"claim": claim, "v1.3.6": old, "v1.3.7": new, "delta": delta, "reason": reason})

    def rate_range(frame: pd.DataFrame, mask: pd.Series, regimes: tuple[str, ...], rule: str = "family") -> str:
        rates: list[float] = []
        selected = frame.loc[mask].copy()
        for regime in regimes:
            rates.extend(
                selected.groupby("attack", sort=True)[f"fire_{rule}__{regime}"].mean().astype(float).tolist()
            )
        if not rates:
            raise ValueError("empty headline rate range")
        return f"{min(rates):.2f}--{max(rates):.2f}"

    def count_delta(old: int, new: int) -> str:
        return f"{new-old:+d}"

    label = label_summary.set_index("question")
    for q, claim in (("Q1", "Label conformal material response"), ("Q2", "Label union material response")):
        rec = label.loc[q]
        old = f"{rec['v136']}/{int(rec['v136_denominator'])}"
        new = f"{rec['v137']}/{int(rec['v137_denominator'])}"
        add(claim, old, new, f"{int(rec['v137'])-int(rec['v136']):+d} fires", "aligned label-geometry sensitivity; the executed original geometry remains separately reported")

    # Every policy served count reported in the primary Gate-D table.
    material = pd.to_numeric(new_core["delta_bal_acc"]).abs().to_numpy() > TOL
    if int(material.sum()) != 7008:
        raise ValueError(f"historical material denominator mismatch: {int(material.sum())} != 7008")
    expected_p2 = {"I_X": 4496, "I_XF": 4365, "I_Ym": 7008, "I_XFY": 4390, "I_XFY_trusted": 0}
    policy_labels = {
        "serve_always": "P0",
        "union_uncalibrated": "P1",
        "family_calibrated": "P2",
        "family_calibrated_strict": "P3",
    }
    for regime in POLICY_REGIME_NAMES:
        for policy in POLICIES:
            old_actions = _actions(old_core, regime, policy)
            new_actions = _actions(new_core, regime, policy)
            old_n = int(((old_actions == "allow") & material).sum())
            new_n = int(((new_actions == "allow") & material).sum())
            if policy == "family_calibrated" and old_n != expected_p2[regime]:
                raise ValueError(f"historical P2 headline mismatch for {regime}: {old_n} != {expected_p2[regime]}")
            add(
                f"{policy_labels[policy]} material altered results served ({regime})",
                f"{old_n}/7008",
                f"{new_n}/7008",
                count_delta(old_n, new_n),
                "corrected JSD coordinates and thresholds" if regime != "I_XFY_trusted" else "exact trusted-reference decisions; JSD correction cannot remove exact blocking",
            )

    expected_legacy = {"I_X": 4494, "I_XF": 4327, "I_Ym": 7008, "I_XFY": 4322, "I_XFY_trusted": 0}
    for regime in POLICY_REGIME_NAMES:
        old_actions = _actions(old_core, regime, "family_calibrated", family_column="fire_family_v12")
        new_actions = _actions(new_core, regime, "family_calibrated", family_column="fire_family_v12")
        old_n = int(((old_actions == "allow") & material).sum())
        new_n = int(((new_actions == "allow") & material).sum())
        if old_n != expected_legacy[regime]:
            raise ValueError(f"historical asymmetric-rule headline mismatch for {regime}")
        add(
            f"Superseded asymmetric-rule material results served ({regime})",
            f"{old_n}/7008",
            f"{new_n}/7008",
            count_delta(old_n, new_n),
            "descriptive comparison only; corrected JSD coordinates, no rule selection",
        )

    old_eval = old_null[old_null["attack_priority_group"] == "null_evaluation"]
    new_eval = new_null[new_null["attack_priority_group"] == "null_evaluation"]
    for regime in BATCH_REGIME_NAMES:
        for rule, label_name in (("union", "Union"), ("family_v12", "Superseded asymmetric family"), ("family", "Conformal family")):
            old_fire = int(old_eval[f"fire_{rule}__{regime}"].sum())
            new_fire = int(new_eval[f"fire_{rule}__{regime}"].sum())
            add(
                f"Gate F {label_name} clean response ({regime})",
                f"{old_fire}/12000 ({old_fire/12000:.3f})",
                f"{new_fire}/12000 ({new_fire/12000:.3f})",
                count_delta(old_fire, new_fire),
                "same disjoint clean-evaluation draws; descriptive because the executed design violates exchangeability",
            )
    old_sensor_rates = [float(old_eval[f"fire_sensor__{sensor}"].mean()) for sensor in CALIBRATED_SENSORS]
    new_sensor_rates = [float(new_eval[f"fire_sensor__{sensor}"].mean()) for sensor in CALIBRATED_SENSORS]
    add(
        "Gate F per-sensor clean-response range",
        f"{min(old_sensor_rates):.3f}--{max(old_sensor_rates):.3f}",
        f"{min(new_sensor_rates):.3f}--{max(new_sensor_rates):.3f}",
        "range recomputed",
        "same sensors, thresholds and frozen clean-evaluation rows; corrected JSD definition only",
    )

    old_core_m = _mechanism_columns(old_core)
    new_core_m = _mechanism_columns(new_core)
    core_regimes = ("I_X", "I_XF", "I_XFY")
    for mechanism, label_name in (
        ("mean_shift", "Mean-shift feature conformal response range"),
        ("scaling_drift", "Scaling-drift feature conformal response range"),
        ("sign_flip", "Sign-flip feature conformal response range"),
        ("dropout", "Feature-dropout conformal response range"),
    ):
        old_range = rate_range(old_core_m, old_core_m["mechanism"] == mechanism, core_regimes)
        new_range = rate_range(new_core_m, new_core_m["mechanism"] == mechanism, core_regimes)
        add(label_name, old_range, new_range, "range recomputed", "same frozen mechanisms, strengths and rows; corrected JSD only")
    old_dropout_rates = old_core_m.loc[old_core_m["mechanism"] == "dropout"].groupby("attack")["fire_exact"].mean()
    new_dropout_rates = new_core_m.loc[new_core_m["mechanism"] == "dropout"].groupby("attack")["fire_exact"].mean()
    add(
        "Feature-dropout exact prediction-change range",
        f"{old_dropout_rates.min():.2f}--{old_dropout_rates.max():.2f}",
        f"{new_dropout_rates.min():.2f}--{new_dropout_rates.max():.2f}",
        "none",
        "predictions and exact checks are unchanged",
    )

    # The near-null and Gate-A ranges are the actual manuscript headline ranges,
    # not newly selected subsets.
    old_sham = old_null["attack"].isin(NEAR_NULL_SHAMS)
    new_sham = new_null["attack"].isin(NEAR_NULL_SHAMS)
    add(
        "Near-null conformal response range",
        rate_range(old_null, old_sham, core_regimes),
        rate_range(new_null, new_sham, core_regimes),
        "range recomputed",
        "same 1,200 prespecified near-null controls; corrected JSD only",
    )
    for attack_class, label_name in (("control", "matched-control"), ("adaptive", "adaptive")):
        old_mask = (old_ga["attack_class"] == attack_class) & (pd.to_numeric(old_ga["strength"]) <= 0.10)
        new_mask = (new_ga["attack_class"] == attack_class) & (pd.to_numeric(new_ga["strength"]) <= 0.10)
        add(
            f"Gate A original-geometry {label_name} conformal response range",
            rate_range(old_ga, old_mask, core_regimes),
            rate_range(new_ga, new_mask, core_regimes),
            "range recomputed",
            "same Gate-A rows and original s(E,T(E)) geometry; corrected JSD only",
        )
        old_gmask = (
            (old_geom["attack_class"] == attack_class)
            & old_geom["mechanism"].isin(["mean_shift", "scaling_drift"])
            & (pd.to_numeric(old_geom["strength"]) <= 0.10)
        )
        new_gmask = (
            (new_geom["attack_class"] == attack_class)
            & new_geom["mechanism"].isin(["mean_shift", "scaling_drift"])
            & (pd.to_numeric(new_geom["strength"]) <= 0.10)
        )
        add(
            f"Gate A aligned-geometry {label_name} conformal response range",
            rate_range(old_geom, old_gmask, core_regimes),
            rate_range(new_geom, new_gmask, core_regimes),
            "range recomputed",
            "same v1.3.5 aligned feature geometry; corrected JSD only",
        )

    adapt_old = old_ga[old_ga["attack_class"] == "adaptive"]
    adapt_new = new_ga[new_ga["attack_class"] == "adaptive"]
    adapt_material = pd.to_numeric(adapt_new["delta_bal_acc"]).abs().to_numpy() > TOL
    if int(adapt_material.sum()) != 3418:
        raise ValueError("historical Gate-A adaptive material denominator did not reproduce 3418")
    for regime in core_regimes:
        o_fire = int(adapt_old[f"fire_family__{regime}"].sum())
        n_fire = int(adapt_new[f"fire_family__{regime}"].sum())
        add(f"Gate A original adaptive conformal response ({regime})", f"{o_fire}/{len(adapt_old)}", f"{n_fire}/{len(adapt_new)}", count_delta(o_fire, n_fire), "corrected JSD coordinates and thresholds")
        old_allow = _actions(adapt_old, regime, "family_calibrated")
        new_allow = _actions(adapt_new, regime, "family_calibrated")
        old_served = int(((old_allow == "allow") & adapt_material).sum())
        new_served = int(((new_allow == "allow") & adapt_material).sum())
        add(
            f"Gate A adaptive P2 material served ({regime})",
            f"{old_served}/3418 ({old_served/3418:.2f})",
            f"{new_served}/3418 ({new_served/3418:.2f})",
            count_delta(old_served, new_served),
            "same 6,000 Gate-A adaptive rows; corrected JSD only",
        )

    # The exact-reference gross blocks are frozen, but their overlap with the
    # corrected batch response must be recomputed to audit the 3.25 pp claim.
    benign_sorted = benign.sort_values(KEYS).reset_index(drop=True)
    old_sham_rows = old_null.loc[old_sham].sort_values(KEYS).reset_index(drop=True)
    new_sham_rows = new_null.loc[new_sham].sort_values(KEYS).reset_index(drop=True)
    if not (benign_sorted[KEYS].equals(old_sham_rows[KEYS]) and benign_sorted[KEYS].equals(new_sham_rows[KEYS])):
        raise ValueError("near-null rows do not align with frozen exact-reference decisions")
    exact = benign_sorted["fire_exact"].astype(bool).to_numpy()
    gross = int(exact.sum())
    old_overlap = int((exact & old_sham_rows["fire_family__I_XFY"].astype(bool).to_numpy()).sum())
    new_overlap = int((exact & new_sham_rows["fire_family__I_XFY"].astype(bool).to_numpy()).sum())
    old_net, new_net = gross - old_overlap, gross - new_overlap
    if (gross, old_overlap, old_net) != (85, 46, 39):
        raise ValueError(f"historical near-null exact audit mismatch: {(gross, old_overlap, old_net)}")
    add("Trusted-reference gross exact blocks on near-null controls", f"{gross}/1200", f"{gross}/1200", 0, "predictions and exact-reference comparison unchanged")
    add("Trusted/batch near-null overlap", f"{old_overlap}/1200", f"{new_overlap}/1200", count_delta(old_overlap, new_overlap), "overlap recomputed against corrected I_XFY batch response")
    add("Trusted-reference net additional near-null interruptions", f"{old_net}/1200", f"{new_net}/1200", count_delta(old_net, new_net), "gross exact blocks minus overlap with corrected batch response")
    add("Trusted-reference net near-null increment", f"{100*old_net/1200:.2f} pp", f"{100*new_net/1200:.2f} pp", f"{100*(new_net-old_net)/1200:+.2f} pp", "descriptive internal stress-control contrast")

    invariant = [
        ("Total material altered results", "7008/10800", "impact definition and predictions unchanged"),
        ("Exact trusted-reference label detection", "2617/2617", "item-aligned exact checks unchanged"),
        ("Exact trusted-reference all label interventions", "3600/3600", "item-aligned exact checks unchanged"),
        ("Exact trusted-reference clean false actions", "0/1200", "exact-zero clean invariant unchanged"),
        ("Structural propositions 1--7", "unchanged", "no structural statement depends on histogram support"),
        ("Quantum model cells", "165 model-environment configurations (descriptive, not independent experiments)", "models and predictions unchanged"),
        ("Quantum acceptance checks", "9/9", "no quantum experiment or output changed"),
        ("Re-split sensitivity construction", "unchanged historical sensitivity", "no new calibration campaign and no retroactive primary substitution"),
    ]
    for claim, value, reason in invariant:
        add(claim, value, value, 0, reason)
    return pd.DataFrame.from_records(rows)


def build(repo: Path, raw_dir: Path, jsd_dir: Path, label_dir: Path) -> None:
    raw, metadata, raw_inputs = _load_raw(repo, raw_dir)
    queue_status_path = repo / "results/paper_digest/paper15_v137_correction/queue_status.json"
    if not queue_status_path.is_file():
        raise FileNotFoundError(queue_status_path)
    queue_status = json.loads(queue_status_path.read_text(encoding="utf-8"))
    if queue_status.get("analysis") != ANALYSIS or queue_status.get("all_completed") is not True:
        raise ValueError("corrective queue status is absent or incomplete")
    evidence = repo / "publication/artifact/evidence"
    null_old = pd.read_csv(evidence / "reinforcement/null_unique_observations.csv", low_memory=False)
    core_all = pd.read_csv(evidence / "expansion/expansion_unique_observations.csv", low_memory=False)
    core_base = core_all[(core_all["attack"] != "clean") & (core_all["gate"] != "gate1_id_cicids")].copy()
    ga_all = pd.read_csv(evidence / "adversarial/adversarial_unique_observations.csv", low_memory=False)
    ga_base = ga_all[ga_all["attack"] != "clean"].copy()
    null_old, ga_base = _restore_descriptive_ks(repo, null_old, ga_base)
    geom_base = pd.read_csv(evidence / "geometry_sensitivity/geometry_observations.csv", low_memory=False)
    gate1_all = pd.read_csv(evidence / "gate1/gate1_unique_observations.csv", low_memory=False)
    gate1_all["gate"] = "gate1_id_cicids"
    benign = pd.read_csv(evidence / "policy/policy_benign_decisions.csv", low_memory=False)

    null_new = _merge_correction(null_old, raw, "null_draw", CORRECTED)
    core_new = _merge_correction(core_base, raw[raw["gate"] != "gate1_id_cicids"], "core_original", CORRECTED)
    ga_new = _merge_correction(ga_base, raw, "gateA_original", CORRECTED)
    geom_cols = [
        name
        for sensor in CORRECTED
        for name in (sensor, f"clean__{sensor}", f"paired__{sensor}", f"delta__{sensor}")
    ]
    geom_new = _merge_correction(geom_base, raw, "feature_aligned", geom_cols)
    gate1_attack = gate1_all[gate1_all["attack"] != "clean"].copy()
    gate1_new = _merge_correction(gate1_attack, raw[raw["gate"] == "gate1_id_cicids"], "core_original", CORRECTED)
    gate1_clean = gate1_all[gate1_all["attack"] == "clean"].copy()
    for sensor in CORRECTED:
        gate1_clean[f"previous__{sensor}"] = gate1_clean[sensor]
    gate1_clean["correction_scope"] = "gate1_clean_unchanged"
    gate1_new = pd.concat([gate1_new, gate1_clean], ignore_index=True, sort=False)
    gate1_new["correction_scope"] = "gate1_frozen_design"

    old_thresholds = pd.read_csv(evidence / "reinforcement/null_calibration_thresholds.csv")
    new_thresholds = _thresholds(null_new)
    _finite(null_new, CALIBRATED_SENSORS, "corrected null")
    threshold_cmp = old_thresholds.merge(
        new_thresholds,
        on=["gate", "svd_dim", "model", "sensor"],
        how="outer",
        validate="one_to_one",
        suffixes=("__previous", "__corrected"),
    )
    threshold_cmp["delta"] = threshold_cmp["threshold__corrected"] - threshold_cmp["threshold__previous"]

    null_old_s = _score_cells(null_old, null_old, old_thresholds, legacy=True)
    null_new_s = _score_cells(null_new, null_new, new_thresholds, legacy=False)
    null_new_s = _with_previous(null_new_s, null_old_s)
    core_old_s = _add_exact(_ensure_delta(_score_cells(core_base, null_old, old_thresholds, legacy=True)))
    core_new_s = _add_exact(_ensure_delta(_score_cells(core_new, null_new, new_thresholds, legacy=False)))
    core_new_s = _with_previous(core_new_s, core_old_s)
    ga_old_s = _add_exact(_score_cells(_mechanism_columns(ga_base), null_old, old_thresholds, legacy=True))
    ga_new_s = _add_exact(_score_cells(_mechanism_columns(ga_new), null_new, new_thresholds, legacy=False))
    ga_new_s = _with_previous(ga_new_s, ga_old_s)
    geom_old_s = _score_aligned(geom_base, null_old, old_thresholds, legacy=True)
    geom_new_s = _score_aligned(geom_new, null_new, new_thresholds)
    geom_new_s = _with_previous(geom_new_s, geom_old_s)

    label_raw = raw[raw["scope"] == "label_aligned"].copy()
    _finite(label_raw, CALIBRATED_SENSORS, "aligned label")
    label_new_s = _score_aligned(label_raw, null_new, new_thresholds)

    # Validate canonical historical endpoints before any output is accepted.
    old_label = core_old_s[core_old_s["attack_family"] == "target_shift"]
    old_material = pd.to_numeric(old_label["delta_bal_acc"]).abs() > TOL
    if (int(old_material.sum()), int(old_label.loc[old_material, "fire_family__I_XFY"].sum()), int(old_label.loc[old_material, "fire_union__I_XFY"].sum())) != (2617, 11, 43):
        raise ValueError("historical label endpoints did not reproduce 2617/11/43")

    label_outputs = _label_outputs(core_old_s, core_new_s, label_new_s)
    gate_f_summary = _gate_f_summary(null_old_s, null_new_s)
    policy_primary = pd.concat(
        [
            _primary_policy_metrics(core_old_s, null_old_s, benign, "primary_v136", "conformal"),
            _primary_policy_metrics(core_new_s, null_new_s, benign, "primary_v137_corrected_jsd", "conformal"),
            _primary_policy_metrics(core_old_s, null_old_s, benign, "primary_v136", "v12_asymmetric"),
            _primary_policy_metrics(core_new_s, null_new_s, benign, "primary_v137_corrected_jsd", "v12_asymmetric"),
        ],
        ignore_index=True,
    )

    scope_frames = {
        "null_draw": null_new_s,
        "core_original": core_new_s,
        "gateA_original": ga_new_s,
        "feature_aligned": geom_new_s,
    }
    deltas = _delta_table({**scope_frames, "gate1_frozen_design": gate1_new})
    observations = pd.concat(
        [frame.assign(correction_scope=scope) for scope, frame in scope_frames.items()] + [gate1_new],
        ignore_index=True,
        sort=False,
    )
    decomposition_scopes = {
        "near_null_original": null_new_s[null_new_s["attack"].isin(NEAR_NULL_SHAMS)],
        "core_original": core_new_s,
        "gateA_original": ga_new_s,
        "feature_aligned": geom_new_s,
        "label_aligned": label_new_s,
        "gate1_frozen_design": gate1_new,
    }
    decomposition = _decomposition(decomposition_scopes)
    ablation = _ablation(
        {name: frame for name, frame in decomposition_scopes.items() if name != "gate1_frozen_design"},
        null_new,
    )
    mde = _mde(new_thresholds)
    headline = _headline(
        core_old_s,
        core_new_s,
        ga_old_s,
        ga_new_s,
        geom_old_s,
        geom_new_s,
        null_old_s,
        null_new_s,
        benign,
        label_outputs["label_geometry_summary.csv"],
    )

    outputs = {
        "jsd_corrected_observations.csv": observations,
        "jsd_correction_deltas.csv": deltas,
        "jsd_corrected_thresholds.csv": new_thresholds,
        "jsd_threshold_deltas.csv": threshold_cmp,
        "jsd_sensor_decomposition.csv": decomposition,
        "jsd_without_ks_ablation.csv": ablation,
        "jsd_mde_description.csv": mde,
        "jsd_gate_f_summary.csv": gate_f_summary,
        "jsd_primary_policy_effect.csv": policy_primary,
        "headline_delta.csv": headline,
    }
    for name, frame in outputs.items():
        _write_csv(frame, jsd_dir / name)
    for name, frame in label_outputs.items():
        _write_csv(frame, label_dir / name)

    checks: dict[str, bool] = {
        "all_300_jobs_complete": len(metadata) == 300,
        "all_67920_raw_rows_present": len(raw) == 67920,
        "all_current_jsd_finite": bool(np.isfinite(observations[list(CORRECTED)].apply(pd.to_numeric, errors="coerce")).all().all()),
        "historical_label_11_of_2617_reproduced": int(old_label.loc[old_material, "fire_family__I_XFY"].sum()) == 11,
        "historical_label_43_of_2617_reproduced": int(old_label.loc[old_material, "fire_union__I_XFY"].sum()) == 43,
        "no_historical_evidence_output_target": all(
            p.parent.resolve() in (jsd_dir.resolve(), label_dir.resolve())
            for p in [*(jsd_dir / n for n in outputs), *(label_dir / n for n in label_outputs)]
        ),
        "structural_blind_aligned_rows_equal_their_paired_clean_sensor_vector": bool(
            max(
                (
                    pd.to_numeric(label_new_s.loc[label_outputs["label_geometry_observations.csv"]["aggregate_blind"].to_numpy(bool), sensor], errors="coerce")
                    - pd.to_numeric(label_new_s.loc[label_outputs["label_geometry_observations.csv"]["aggregate_blind"].to_numpy(bool), f"clean__{sensor}"], errors="coerce")
                ).abs().max()
                for sensor in CALIBRATED_SENSORS
            ) <= TOL
        ),
        "structural_blind_aligned_rows_add_no_family_or_union_fire_beyond_paired_clean": bool(
            all(
                label_outputs["label_geometry_observations.csv"].loc[
                    lambda f: f["aggregate_blind"], f"aligned__fire_{rule}__I_XFY"
                ].astype(bool).equals(
                    label_outputs["label_geometry_observations.csv"].loc[
                        lambda f: f["aggregate_blind"], f"aligned__clean_fire_{rule}__I_XFY"
                    ].astype(bool)
                )
                for rule in ("family", "union")
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError(f"v1.3.7 evidence checks failed: {failed}")

    immutable_tree = _git(repo, "rev-parse", f"{V136_TAG}:publication/artifact/evidence")
    geom_tree = _git(repo, "rev-parse", f"{V135_TAG}:publication/artifact/evidence/geometry_sensitivity")
    common = {
        "schema_version": SCHEMA_VERSION,
        "analysis": ANALYSIS,
        "release_classification": "sensor-correction and label-geometry closure release",
        "preregistration": PREREGISTRATION,
        "preregistration_commit": PREREG_COMMIT,
        "v136_tag": V136_TAG,
        "v136_evidence_tree": immutable_tree,
        "v135_geometry_tag": V135_TAG,
        "v135_geometry_evidence_tree": geom_tree,
        "historical_evidence_files_modified": 0,
        "historical_geometry_files_modified": 0,
        "checks": checks,
        "raw_inputs": raw_inputs,
    }
    audit_source = repo / "publication/artifact/evidence/jsd_correction/jsd_historical_nan_audit.csv"
    audit_target = jsd_dir / "jsd_historical_nan_audit.csv"
    if audit_source.resolve() != audit_target.resolve():
        if not audit_source.is_file():
            raise FileNotFoundError(audit_source)
        shutil.copy2(audit_source, audit_target)
    jsd_output_records = {
        name: {"sha256": _sha256(jsd_dir / name), "rows": len(frame)}
        for name, frame in outputs.items()
    }
    jsd_output_records[audit_target.name] = {
        "sha256": _sha256(audit_target),
        "rows": len(pd.read_csv(audit_target, low_memory=False)),
    }
    if queue_status_path.resolve() != (jsd_dir / "queue_status.json").resolve():
        shutil.copy2(queue_status_path, jsd_dir / "queue_status.json")
    jsd_output_records["queue_status.json"] = {
        "sha256": _sha256(jsd_dir / "queue_status.json"),
    }
    jsd_manifest = {
        **common,
        "status": "complete",
        "acceptance_checks": checks,
        "corrected_sensors": list(CORRECTED),
        "n_historical_observation_rows": int(len(observations)),
        "n_delta_records": int(len(deltas)),
        "outputs": jsd_output_records,
    }
    jsd_manifest_path = jsd_dir / "jsd_correction_manifest.json"
    jsd_manifest_path.write_text(json.dumps(jsd_manifest, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    label_manifest = {
        **common,
        "status": "complete",
        "acceptance_checks": checks,
        "geometry": {"original": "s(E,T_y(E))", "aligned": "s(E,T_y(B)) with clean comparator s(E,B)"},
        "outputs": {
            name: {"sha256": _sha256(label_dir / name), "rows": len(frame)}
            for name, frame in label_outputs.items()
        },
    }
    label_manifest_path = label_dir / "label_geometry_manifest.json"
    label_manifest_path.write_text(json.dumps(label_manifest, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "status": "complete",
                "jsd_evidence_files": len(jsd_output_records) + 1,
                "label_evidence_files": len(label_outputs) + 1,
                "total_v137_evidence_files": len(jsd_output_records) + len(label_outputs) + 2,
                "checks": checks,
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--raw-dir", type=Path, default=Path("results/raw/paper15_v137_correction"))
    parser.add_argument("--jsd-dir", type=Path, default=Path("results/paper_digest/paper15_v137_jsd_correction"))
    parser.add_argument("--label-dir", type=Path, default=Path("results/paper_digest/paper15_v137_label_geometry_sensitivity"))
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    build(repo, repo / args.raw_dir, repo / args.jsd_dir, repo / args.label_dir)


if __name__ == "__main__":
    main()
