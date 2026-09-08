"""Build the reinforcement evidence package for Paper 1.5 (artifact 1.1.0).

Three prespecified sensitivity gates (see
``manuscript/paper15_v11_reinforcement_prereg.md``):

Gate N  null calibration of the non-invariant sensors with disjoint
        calibration/evaluation clean pools, then calibrated detection rates on
        the frozen ``paper_core`` expansion observations;
Gate P  symmetric preprocessing ablation of the secondary ZZ-minus-SVC profile;
Gate T  cross-validated tuning of both learners on training rows only.

The builder fails closed: any missing job, design mismatch, or failed
acceptance check aborts without writing a manifest. Thresholds are computed
from calibration draws only and are never adjusted after attacked rows are
examined.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist

from src.datasets.cicids_subset import CicidsConfig, load_cicids_subset
from src.experiments.build_q1_gate1_evidence import (
    KEY_COLS,
    _deduplicate,
    _mean_ci,
    _require_columns,
    _sha256,
)
from src.experiments.run_benchmark import _packed_seed, _stratified_subsample_indices
from src.experiments.run_v11_reinforcement_queue import GATE_N_ENVIRONMENTS


ALPHA = 0.05
N_CAL_EXPECTED = 200
N_EVAL_EXPECTED = 200
TOL = 1e-12

SPLIT_SEEDS = (42, 43, 44, 45, 46)
MODEL_SEEDS = (42, 43)
DIMS = (8, 10, 12)

FEATURE_SENSORS = [
    "integrity_jsd_vs_clean_eval",
    "integrity_mmd_vs_clean_eval",
    "integrity_ks_reject05_vs_clean_eval",
]
PREDICTION_SENSORS = [
    "integrity_score_jsd_vs_clean_eval",
    "integrity_pred_pos_rate_shift",
    "integrity_pred_jsd",
]
LABEL_MARGINAL_SENSORS = ["integrity_label_prior_shift", "integrity_label_jsd"]
JOINT_OUTCOME_SENSORS = ["integrity_confusion_profile_l1", "integrity_confusion_profile_jsd"]

CALIBRATED_SENSORS = FEATURE_SENSORS + PREDICTION_SENSORS + LABEL_MARGINAL_SENSORS + JOINT_OUTCOME_SENSORS

# Batch-level statistical auditor.  The executed scores below are aggregate
# comparisons with a benchmark-held clean batch drawn from the same item set;
# they do not use item correspondence and are thresholded against clean-draw
# variability.  Version 1.3.2 records that reference semantics explicitly.
REGIMES: dict[str, list[str]] = {
    "I_X": FEATURE_SENSORS,
    "I_XF": FEATURE_SENSORS + PREDICTION_SENSORS,
    "I_Ym": LABEL_MARGINAL_SENSORS,
    "I_XFY": FEATURE_SENSORS + PREDICTION_SENSORS + LABEL_MARGINAL_SENSORS + JOINT_OUTCOME_SENSORS,
}
# Trusted-reference auditor: aggregate class-B and item-aligned class-C
# invariants have an exact-zero null.  Keep the two granularities separate;
# the combined I_XFY auditor holds both.
EXACT_AGGREGATE_SENSORS = [
    "integrity_confusion_profile_l1_delta",
    "integrity_confusion_profile_jsd_delta",
]
EXACT_ITEM_ALIGNED_SENSORS = [
    "integrity_pred_disagreement",
    "label_flip_rate",
]
EXACT_REFERENCE_SENSORS = EXACT_AGGREGATE_SENSORS + EXACT_ITEM_ALIGNED_SENSORS
EXACT_REGIMES: dict[str, list[str]] = {
    "I_XF_item_aligned": ["integrity_pred_disagreement"],
    "I_XFY_item_aligned": EXACT_REFERENCE_SENSORS,
}
SENSOR_REGIME = {
    **{s: "feature" for s in FEATURE_SENSORS},
    **{s: "prediction" for s in PREDICTION_SENSORS},
    **{s: "aggregate_exact" for s in EXACT_AGGREGATE_SENSORS},
    **{s: "item_aligned_exact" for s in EXACT_ITEM_ALIGNED_SENSORS},
    **{s: "label_marginal" for s in LABEL_MARGINAL_SENSORS},
    **{s: "joint_outcome" for s in JOINT_OUTCOME_SENSORS},
}

NULL_GATES = (
    {"gate": "gate2_id_256", "models": {"svc_rbf", "qsvc_zz_r1"}, "n": 256},
    {"gate": "gate3a_ood_tue_wed", "models": {"svc_rbf", "qsvc_zz_r1"}, "n": 128},
    {"gate": "gate3b_ood_tue_fri_portscan", "models": {"svc_rbf", "qsvc_zz_r1"}, "n": 128},
    {"gate": "gate3c_ood_wed_thu_webattacks", "models": {"svc_rbf", "qsvc_zz_r1"}, "n": 128},
    {"gate": "gate3d_ood_wed_fri_morning", "models": {"svc_rbf", "qsvc_zz_r1"}, "n": 128},
    {"gate": "gate5a_id_unsw", "models": {"svc_rbf", "qsvc_zz_r1", "qsvc_z_r1", "qsvc_pauli_xyz_r1"}, "n": 128},
    {"gate": "gate5b_id_ton_iot", "models": {"svc_rbf", "qsvc_zz_r1", "qsvc_z_r1", "qsvc_pauli_xyz_r1"}, "n": 128},
    {"gate": "gate6_ood_unsw", "models": {"svc_rbf", "qsvc_zz_r1"}, "n": 128},
)
PREP_CONFIGS = ("P0_reference", "PA_standard_standard", "PB_minmax2pi_minmax2pi")
TUNED_ENVS = ("gate1_id_cicids", "gate6_ood_unsw")
EXPECTED_FILES_PER_GATE = len(SPLIT_SEEDS) * len(MODEL_SEEDS) * len(DIMS)
N_NULL_ATTACKS = 20 + 20 + 3 + 1  # calibration + evaluation + shams + clean
N_CORE_ATTACKS = 18 + 1


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _relative_to_repo(path: Path, repo: Path | None) -> str:
    """Repository-relative POSIX path (artifact 1.2.0: no machine-specific paths in evidence)."""

    if repo is None:
        return path.as_posix()
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _load_dir(raw_dir: Path, gate_label: str, *, expected_files: int, expected_models: set[str],
              expected_attacks: int, repo: Path | None = None) -> tuple[pd.DataFrame, dict[str, object], list[dict[str, object]]]:
    paths = sorted(raw_dir.glob("*qbexact_statevector*.csv"))
    complete = len(paths) == expected_files
    frames: list[pd.DataFrame] = []
    inputs: list[dict[str, object]] = []
    pools: list[dict[str, object]] = []
    for path in paths:
        json_path = path.with_suffix(".json")
        if not json_path.is_file():
            raise FileNotFoundError(f"Missing metadata for {path}")
        frame = pd.read_csv(path, low_memory=False)
        frame["gate"] = gate_label
        frame["_source_file"] = path.name
        frames.append(frame)
        meta = json.loads(json_path.read_text(encoding="utf-8"))
        pool = dict(meta.get("split", {}).get("clean_pool", {}) or {})
        pool.update(
            {
                "gate": gate_label,
                "split_seed": int(meta["run_cfg"]["split_seed"]),
                "model_seed": int(meta["run_cfg"]["model_seed"]),
                "svd_dim": int(meta["run_cfg"]["svd_dim"]),
                "n_test": int(meta["split"]["n_test"]),
            }
        )
        pools.append(pool)
        inputs.append(
            {
                "gate": gate_label,
                "csv": _relative_to_repo(path, repo),
                "csv_sha256": _sha256(path),
                "json": _relative_to_repo(json_path, repo),
                "json_sha256": _sha256(json_path),
            }
        )
    if not complete:
        raise RuntimeError(f"{gate_label}: observed {len(paths)} of {expected_files} exact-statevector CSVs")
    raw = pd.concat(frames, ignore_index=True, sort=False)
    _require_columns(raw, KEY_COLS + ["gate", "attack_family", "attack_priority_group", "impact_bal_acc", "bal_acc_clean"] + CALIBRATED_SENSORS + EXACT_REFERENCE_SENSORS)
    dedup, dup_audit = _deduplicate(raw)

    models = set(dedup["model"].astype(str))
    if models != expected_models:
        raise ValueError(f"{gate_label}: models {sorted(models)} != expected {sorted(expected_models)}")
    cells = dedup.groupby(["model", "svd_dim", "split_seed", "model_seed"]).size()
    if int(cells.nunique()) != 1 or int(cells.iloc[0]) != expected_attacks:
        raise ValueError(f"{gate_label}: attack rows per cell {sorted(set(cells))} != {expected_attacks}")
    if set(dedup["split_seed"].astype(int)) != set(SPLIT_SEEDS) or set(dedup["model_seed"].astype(int)) != set(MODEL_SEEDS) or set(dedup["svd_dim"].astype(int)) != set(DIMS):
        raise ValueError(f"{gate_label}: seed/dimension design mismatch")

    design = {
        "gate": gate_label,
        "raw_directory": _relative_to_repo(raw_dir, repo),
        "observed_files": len(paths),
        "expected_files": expected_files,
        "complete": bool(complete),
        "models": ",".join(sorted(models)),
        "rows_raw": int(dup_audit["raw_rows"]),
        "rows_unique": int(dup_audit["unique_rows"]),
        "duplicate_svc_rows_removed": int(dup_audit["duplicate_rows_removed"]),
    }
    dedup.attrs["pools"] = pools
    return dedup, design, inputs


# ---------------------------------------------------------------------------
# Gate N: null calibration
# ---------------------------------------------------------------------------


def _order_statistic_rank(n: int, alpha: float) -> int:
    return int(math.ceil((n + 1) * (1.0 - alpha)))


def _clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    lo = 0.0 if k == 0 else float(beta_dist.ppf((1 - level) / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta_dist.ppf(1 - (1 - level) / 2, k + 1, n - k))
    return lo, hi


def _thresholds(null_frame: pd.DataFrame) -> pd.DataFrame:
    calib = null_frame[null_frame["attack_priority_group"] == "null_calibration"]
    records: list[dict[str, object]] = []
    for (gate, dim, model), group in calib.groupby(["gate", "svd_dim", "model"], sort=True):
        n_cal = int(len(group))
        if n_cal != N_CAL_EXPECTED:
            raise ValueError(f"{gate} d={dim} {model}: {n_cal} calibration draws, expected {N_CAL_EXPECTED}")
        rank = _order_statistic_rank(n_cal, ALPHA)
        for sensor in CALIBRATED_SENSORS:
            values = np.sort(pd.to_numeric(group[sensor], errors="coerce").to_numpy(dtype=float))
            if np.isnan(values).any():
                raise ValueError(f"{gate} d={dim} {model}: NaN calibration values for {sensor}")
            records.append(
                {
                    "gate": gate,
                    "svd_dim": int(dim),
                    "model": model,
                    "sensor": sensor,
                    "sensor_family": SENSOR_REGIME[sensor],
                    "n_cal": n_cal,
                    "alpha": ALPHA,
                    "order_statistic_rank": rank,
                    "threshold": float(values[rank - 1]),
                    "null_median": float(np.median(values)),
                    "null_max": float(values[-1]),
                    "rule": "fire if value > threshold",
                }
            )
        for sensor in EXACT_REFERENCE_SENSORS:
            records.append(
                {
                    "gate": gate,
                    "svd_dim": int(dim),
                    "model": model,
                    "sensor": sensor,
                    "sensor_family": SENSOR_REGIME[sensor],
                    "n_cal": n_cal,
                    "alpha": 0.0,
                    "order_statistic_rank": 0,
                    "threshold": 0.0,
                    "null_median": 0.0,
                    "null_max": 0.0,
                    "rule": "exact item-aligned invariance: fire if |value| > 0; undefined on unaligned null draws",
                }
            )
    return pd.DataFrame.from_records(records)


def _fire_matrix(frame: pd.DataFrame, thresholds: pd.DataFrame, *, item_aligned: bool) -> pd.DataFrame:
    """Return a copy of ``frame`` with boolean ``fire__<sensor>`` and ``fire__<regime>`` columns.

    ``item_aligned`` is True for interventions applied in place to the frozen
    batch (same items as the reference) and False for clean null draws, whose
    items differ; item-aligned sensors are computed only in the former case.
    """

    thr = thresholds[thresholds["order_statistic_rank"] > 0].pivot_table(index=["gate", "svd_dim", "model"], columns="sensor", values="threshold", aggfunc="first")
    out = frame.copy()
    keyed = out.set_index(["gate", "svd_dim", "model"]).index
    missing = [key for key in set(keyed) if key not in thr.index]
    if missing:
        raise ValueError(f"No thresholds for cells {sorted(missing)[:5]}")
    for sensor in CALIBRATED_SENSORS:
        t = thr[sensor].reindex(keyed).to_numpy(dtype=float)
        v = pd.to_numeric(out[sensor], errors="coerce").to_numpy(dtype=float)
        out[f"fire__{sensor}"] = v > t
    for regime, sensors in REGIMES.items():
        out[f"fire__{regime}"] = out[[f"fire__{s}" for s in sensors]].any(axis=1)
    if item_aligned:
        for sensor in EXACT_REFERENCE_SENSORS:
            v = pd.to_numeric(out[sensor], errors="coerce").fillna(0.0).to_numpy(dtype=float)
            out[f"fire__{sensor}"] = np.abs(v) > TOL
        for regime, sensors in EXACT_REGIMES.items():
            out[f"fire__{regime}"] = out[[f"fire__{s}" for s in sensors]].any(axis=1)
    return out


def _rate_records(frame: pd.DataFrame, group_cols: list[str], *, label: str, item_aligned: bool = False) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    targets = [(s, "sensor") for s in CALIBRATED_SENSORS] + [(r, "regime") for r in REGIMES]
    if item_aligned:
        targets += [(s, "sensor_exact") for s in EXACT_REFERENCE_SENSORS] + [(r, "regime_exact") for r in EXACT_REGIMES]
    for key, group in frame.groupby(group_cols, sort=True, dropna=False):
        key_tuple = key if isinstance(key, tuple) else (key,)
        base = dict(zip(group_cols, key_tuple, strict=True))
        n = int(len(group))
        for name, kind in targets:
            k = int(group[f"fire__{name}"].sum())
            lo, hi = _clopper_pearson(k, n)
            records.append({**base, "target": name, "target_kind": kind, "n": n, "n_fire": k, f"{label}": k / n if n else math.nan, "ci95_low": lo, "ci95_high": hi})
    return pd.DataFrame.from_records(records)


def _max_window_mass(values: np.ndarray, width: float) -> float:
    """Largest fraction of points contained in a closed window of the given width."""

    x = np.sort(np.asarray(values, dtype=float))
    n = len(x)
    if n == 0:
        return math.nan
    best = 1
    j = 0
    for i in range(n):
        while j < n and x[j] - x[i] <= width:
            j += 1
        best = max(best, j - i)
    return best / n


def _mass_point_profile(repo: Path) -> pd.DataFrame:
    """Cluster structure of the frozen evaluation batches.

    Several staged tables contain repeated flow patterns, so projected features
    carry tight clusters of rows (values equal to within roughly 1e-4 standard
    deviations). A fresh clean batch reproduces the cluster, whereas an in-place
    perturbation of the order of 1e-3 standard deviations or larger smears it;
    this is why the KS rejection sensor reacts to near-null shams and small
    mean shifts that lie far below its between-batch null. Features are
    standardized with the training-fitted scaler of the frozen classical branch
    before the window masses are computed.
    """

    from sklearn.preprocessing import StandardScaler

    records: list[dict[str, object]] = []
    for env in GATE_N_ENVIRONMENTS:
        n = int(env["n"])
        for dim in DIMS:
            for split in SPLIT_SEEDS:
                if env["protocol"] == "ood":
                    cfg = CicidsConfig(train_path=repo / str(env["data_train"]), test_path=repo / str(env["data_test"]), svd_dim=dim)
                else:
                    cfg = CicidsConfig(path=repo / str(env["data"]), svd_dim=dim)
                X_tr, y_tr, X_te, y_te = load_cicids_subset(cfg, seed=split)
                for mseed in MODEL_SEEDS:
                    base = _packed_seed(split, mseed)
                    tr_idx = _stratified_subsample_indices(np.asarray(y_tr), n, seed=base)
                    te_idx = _stratified_subsample_indices(np.asarray(y_te), n, seed=base + 1)
                    scaler = StandardScaler().fit(np.asarray(X_tr, dtype=float)[tr_idx])
                    X = scaler.transform(np.asarray(X_te, dtype=float)[te_idx])
                    w_001 = np.array([_max_window_mass(X[:, j], 0.01) for j in range(X.shape[1])])
                    w_0001 = np.array([_max_window_mass(X[:, j], 0.001) for j in range(X.shape[1])])
                    rounded = np.round(X, 6)
                    dup_rows = int(len(X) - len(np.unique(rounded, axis=0)))
                    records.append(
                        {
                            "gate": str(env["gate"]),
                            "svd_dim": int(dim),
                            "split_seed": int(split),
                            "model_seed": int(mseed),
                            "n_eval": int(len(X)),
                            "near_duplicate_rows_1e-6": dup_rows,
                            "near_duplicate_row_fraction_1e-6": dup_rows / len(X),
                            "max_cluster_mass_width_0.01sd": float(w_001.max()),
                            "mean_cluster_mass_width_0.01sd": float(w_001.mean()),
                            "max_cluster_mass_width_0.001sd": float(w_0001.max()),
                            "n_features_cluster_ge_0.20_width_0.01sd": int((w_001 >= 0.20).sum()),
                            "n_features": int(X.shape[1]),
                        }
                    )
    return pd.DataFrame.from_records(records)


def build_gate_n(repo: Path, expansion_path: Path) -> tuple[dict[str, pd.DataFrame], list[dict[str, object]], list[dict[str, object]], dict[str, bool]]:
    frames: list[pd.DataFrame] = []
    designs: list[dict[str, object]] = []
    inputs: list[dict[str, object]] = []
    pools: list[dict[str, object]] = []
    for spec in NULL_GATES:
        raw_dir = repo / f"results/raw/paper15_v11_null_{spec['gate']}"
        frame, design, files = _load_dir(raw_dir, str(spec["gate"]), expected_files=EXPECTED_FILES_PER_GATE, expected_models=set(spec["models"]), expected_attacks=N_NULL_ATTACKS, repo=repo)
        design["gate_family"] = "N_null_calibration"
        frames.append(frame)
        designs.append(design)
        inputs.extend(files)
        pools.extend(frame.attrs["pools"])
    null = pd.concat(frames, ignore_index=True, sort=False)

    checks: dict[str, bool] = {}
    identity = null[null["attack"] == "sham_identity"]
    checks["N_identity_control_exactly_invariant"] = bool(identity[CALIBRATED_SENSORS + ["integrity_pred_disagreement"]].astype(float).abs().to_numpy().max() <= TOL)

    thresholds = _thresholds(null)
    evaluation = null[null["attack_priority_group"] == "null_evaluation"]
    counts = evaluation.groupby(["gate", "svd_dim", "model"]).size()
    checks["N_evaluation_draw_count"] = bool((counts == N_EVAL_EXPECTED).all())

    eval_fire = _fire_matrix(evaluation, thresholds, item_aligned=False)
    fpr_cell = _rate_records(eval_fire, ["gate", "svd_dim", "model"], label="false_alarm_rate")
    fpr_pooled = _rate_records(eval_fire, ["gate"], label="false_alarm_rate")
    fpr_overall = _rate_records(eval_fire.assign(all="all_environments"), ["all"], label="false_alarm_rate")

    benign = null[null["attack_priority_group"] == "sham"]
    benign_fire = _fire_matrix(benign, thresholds, item_aligned=True)
    benign_rates = _rate_records(benign_fire, ["attack", "gate"], label="fire_rate", item_aligned=True)

    expansion = pd.read_csv(expansion_path, low_memory=False)
    attacked = expansion[expansion["attack"] != "clean"].copy()
    attacked = attacked[attacked["gate"].isin([str(s["gate"]) for s in NULL_GATES])]
    if len(attacked) == 0:
        raise ValueError("No attacked expansion rows matched the null gates")
    att_fire = _fire_matrix(attacked, thresholds, item_aligned=True)
    att_fire["attack_strength"] = att_fire["attack_strength_nominal"].astype(float).round(3)
    det_cell = _rate_records(att_fire, ["gate", "svd_dim", "model", "attack_family", "attack"], label="detection_rate", item_aligned=True)
    det_env = _rate_records(att_fire, ["gate", "attack_family", "attack"], label="detection_rate", item_aligned=True)
    det_pooled = _rate_records(att_fire.assign(all="all_environments"), ["all", "attack_family", "attack"], label="detection_rate", item_aligned=True)
    det_family_regime = _rate_records(att_fire.assign(all="all_environments"), ["all", "attack_family"], label="detection_rate", item_aligned=True)

    label_side = att_fire[att_fire["attack_family"] == "target_shift"]
    prior = label_side[label_side["attack"].str.contains("prior_preserving", regex=False)]
    positive = label_side[pd.to_numeric(label_side["impact_bal_acc"], errors="coerce") > TOL]
    checks["N_label_path_I_X_calibrated_detection_zero"] = bool(label_side["fire__I_X"].sum() == 0)
    checks["N_label_path_I_XF_calibrated_detection_zero"] = bool(label_side["fire__I_XF"].sum() == 0)
    checks["N_label_path_I_XF_item_aligned_exact_detection_zero"] = bool(label_side["fire__I_XF_item_aligned"].sum() == 0)
    checks["N_prior_preserving_I_Ym_calibrated_detection_zero"] = bool(prior["fire__I_Ym"].sum() == 0)
    checks["N_positive_impact_label_rows_all_detected_item_aligned"] = bool(positive["fire__I_XFY_item_aligned"].all())
    all_regimes = list(REGIMES) + list(EXACT_REGIMES)

    def _summary_rows(subset: str, block: pd.DataFrame) -> list[dict[str, object]]:
        return [
            {
                "subset": subset,
                "regime": r,
                "auditor": "item_aligned_exact" if r in EXACT_REGIMES else "batch_level_calibrated",
                "n": int(len(block)),
                "n_fire": int(block[f"fire__{r}"].sum()),
                "detection_rate": float(block[f"fire__{r}"].mean()) if len(block) else math.nan,
            }
            for r in all_regimes
        ]

    label_summary = pd.DataFrame.from_records(
        _summary_rows("all_label_interventions", label_side)
        + _summary_rows("prior_preserving_label_interventions", prior)
        + _summary_rows("positive_impact_label_interventions", positive)
    )

    mass_profile = _mass_point_profile(repo)
    pool_frame = pd.DataFrame.from_records(pools).sort_values(["gate", "svd_dim", "split_seed", "model_seed"]).reset_index(drop=True)
    checks["N_pool_halves_disjoint_and_sufficient"] = bool(((pool_frame["n_calibration_half"] >= pool_frame["n_test"]) & (pool_frame["n_evaluation_half"] >= pool_frame["n_test"]) & (pool_frame["n_calibration_half"] + pool_frame["n_evaluation_half"] == pool_frame["n_pool"])).all())

    keep = ["gate", "protocol", "dataset_tag", "svd_dim", "split_seed", "model_seed", "model", "attack", "attack_family", "attack_priority_group", "impact_bal_acc", "bal_acc", "bal_acc_clean"] + CALIBRATED_SENSORS + EXACT_REFERENCE_SENSORS + [c for c in null.columns if c.startswith("atk_")]
    outputs = {
        "null_unique_observations.csv": null[[c for c in keep if c in null.columns]].reset_index(drop=True),
        "null_pool_design.csv": pool_frame,
        "null_mass_point_profile.csv": mass_profile,
        "null_calibration_thresholds.csv": thresholds,
        "null_evaluation_false_alarm_by_cell.csv": fpr_cell,
        "null_evaluation_false_alarm_by_environment.csv": fpr_pooled,
        "null_evaluation_false_alarm_overall.csv": fpr_overall,
        "null_benign_control_response.csv": benign_rates,
        "calibrated_detection_by_cell.csv": det_cell,
        "calibrated_detection_by_environment.csv": det_env,
        "calibrated_detection_pooled.csv": det_pooled,
        "calibrated_detection_by_family_pooled.csv": det_family_regime,
        "calibrated_label_path_summary.csv": label_summary,
    }
    return outputs, designs, inputs, checks


# ---------------------------------------------------------------------------
# Gates P and T: paired secondary profile and invariance
# ---------------------------------------------------------------------------


def _paired_profile(frame: pd.DataFrame, condition: str) -> pd.DataFrame:
    attacked = frame[frame["attack"] != "clean"]
    per_seed = attacked.groupby(["svd_dim", "split_seed", "model_seed", "model"], dropna=False)["impact_bal_acc"].mean().reset_index()
    per_split = per_seed.groupby(["svd_dim", "split_seed", "model"], dropna=False)["impact_bal_acc"].mean().reset_index()
    records: list[dict[str, object]] = []
    for dim in sorted(per_split["svd_dim"].unique()):
        wide = per_split[per_split["svd_dim"] == dim].pivot_table(index="split_seed", columns="model", values="impact_bal_acc", aggfunc="first")
        diff = wide["qsvc_zz_r1"] - wide["svc_rbf"]
        records.append({"condition": condition, "svd_dim": int(dim), "metric": "zz_minus_svc_impact_mean", **_mean_ci(diff), "clusters_positive": int((diff > 0).sum()), "n_clusters": int(len(diff)), "svc_impact_mean": float(wide["svc_rbf"].mean()), "zz_impact_mean": float(wide["qsvc_zz_r1"].mean())})
    return pd.DataFrame.from_records(records)


def _clean_performance(frame: pd.DataFrame, condition: str) -> pd.DataFrame:
    clean = frame[frame["attack"] == "clean"]
    per_split = clean.groupby(["svd_dim", "split_seed", "model"], dropna=False)["bal_acc_clean"].mean().reset_index()
    records: list[dict[str, object]] = []
    for (dim, model), group in per_split.groupby(["svd_dim", "model"], sort=True):
        records.append({"condition": condition, "svd_dim": int(dim), "model": model, "metric": "clean_balanced_accuracy", **_mean_ci(group["bal_acc_clean"])})
    return pd.DataFrame.from_records(records)


def _label_invariance(frame: pd.DataFrame, condition: str) -> dict[str, object]:
    label = frame[frame["attack_family"] == "target_shift"]
    xf = FEATURE_SENSORS + ["integrity_score_jsd_vs_clean_eval"] + ["integrity_pred_disagreement", "integrity_pred_jsd"]
    prior = label[label["attack"].str.contains("prior_preserving", regex=False)]
    impact = pd.to_numeric(label["impact_bal_acc"], errors="coerce")
    positive = label[impact > TOL]
    joint = positive[["integrity_confusion_profile_l1_delta", "integrity_confusion_profile_jsd_delta"]].astype(float).abs().max(axis=1)
    return {
        "condition": condition,
        "label_rows": int(len(label)),
        "feature_prediction_blind_rows": int((label[xf].astype(float).abs().max(axis=1) <= TOL).sum()),
        "prior_preserving_rows": int(len(prior)),
        "label_marginal_blind_rows": int((prior[LABEL_MARGINAL_SENSORS].astype(float).abs().max(axis=1) <= TOL).sum()),
        "positive_impact_rows": int(len(positive)),
        "positive_impact_with_joint_response": int((joint > TOL).sum()),
        "negative_impact_rows": int((impact < -TOL).sum()),
    }


def build_gate_p(repo: Path) -> tuple[dict[str, pd.DataFrame], list[dict[str, object]], list[dict[str, object]], dict[str, bool]]:
    paired, clean, invariance, designs, inputs = [], [], [], [], []
    for config in PREP_CONFIGS:
        raw_dir = repo / f"results/raw/paper15_v11_prep_{config}"
        frame, design, files = _load_dir(raw_dir, config, expected_files=EXPECTED_FILES_PER_GATE, expected_models={"svc_rbf", "qsvc_zz_r1"}, expected_attacks=N_CORE_ATTACKS, repo=repo)
        design["gate_family"] = "P_preprocessing_ablation"
        scales = frame[["model", "scale"]].drop_duplicates().set_index("model")["scale"].to_dict()
        design["scale_svc"] = scales.get("svc_rbf", "")
        design["scale_qsvc"] = scales.get("qsvc_zz_r1", "")
        designs.append(design)
        inputs.extend(files)
        paired.append(_paired_profile(frame, config))
        clean.append(_clean_performance(frame, config))
        invariance.append(_label_invariance(frame, config))
    inv = pd.DataFrame.from_records(invariance)
    checks = {
        "P_label_path_exact_invariance_every_config": bool(((inv["feature_prediction_blind_rows"] == inv["label_rows"]) & (inv["label_marginal_blind_rows"] == inv["prior_preserving_rows"]) & (inv["positive_impact_with_joint_response"] == inv["positive_impact_rows"]) & (inv["negative_impact_rows"] == 0)).all()),
        "P_scaler_configurations_as_prespecified": bool({(d["gate"], d["scale_svc"], d["scale_qsvc"]) for d in designs} == {("P0_reference", "standard", "minmax2pi"), ("PA_standard_standard", "standard", "standard"), ("PB_minmax2pi_minmax2pi", "minmax2pi", "minmax2pi")}),
    }
    outputs = {
        "prep_ablation_paired_zz_minus_svc.csv": pd.concat(paired, ignore_index=True),
        "prep_ablation_clean_performance.csv": pd.concat(clean, ignore_index=True),
        "prep_ablation_label_invariance.csv": inv,
    }
    return outputs, designs, inputs, checks


def build_gate_t(repo: Path, expansion_path: Path, prep_reference: pd.DataFrame | None) -> tuple[dict[str, pd.DataFrame], list[dict[str, object]], list[dict[str, object]], dict[str, bool]]:
    paired, clean, invariance, hyper, designs, inputs = [], [], [], [], [], []
    tuned_frames: dict[str, pd.DataFrame] = {}
    for env in TUNED_ENVS:
        raw_dir = repo / f"results/raw/paper15_v11_tuned_{env}"
        frame, design, files = _load_dir(raw_dir, env, expected_files=EXPECTED_FILES_PER_GATE, expected_models={"svc_rbf", "qsvc_zz_r1"}, expected_attacks=N_CORE_ATTACKS, repo=repo)
        design["gate_family"] = "T_tuned_baselines"
        designs.append(design)
        inputs.extend(files)
        tuned_frames[env] = frame
        paired.append(_paired_profile(frame, f"{env}__tuned_cv5"))
        clean.append(_clean_performance(frame, f"{env}__tuned_cv5"))
        invariance.append(_label_invariance(frame, f"{env}__tuned_cv5"))
        h = frame[["gate", "model", "svd_dim", "split_seed", "model_seed", "model_tuning", "model_C", "model_gamma", "model_cv_bal_acc"]].drop_duplicates().sort_values(["gate", "model", "svd_dim", "split_seed", "model_seed"])
        hyper.append(h)

    # Untuned references with identical seeds: Gate P P0 for CICIDS ID, frozen expansion E8 for UNSW OOD.
    if prep_reference is not None:
        paired.append(_paired_profile(prep_reference, "gate1_id_cicids__reference_untuned"))
        clean.append(_clean_performance(prep_reference, "gate1_id_cicids__reference_untuned"))
    expansion = pd.read_csv(expansion_path, low_memory=False)
    e8 = expansion[expansion["gate"] == "gate6_ood_unsw"]
    if len(e8):
        paired.append(_paired_profile(e8, "gate6_ood_unsw__reference_untuned"))
        clean.append(_clean_performance(e8, "gate6_ood_unsw__reference_untuned"))

    inv = pd.DataFrame.from_records(invariance)
    hyper_frame = pd.concat(hyper, ignore_index=True)
    checks = {
        "T_label_path_exact_invariance_every_environment": bool(((inv["feature_prediction_blind_rows"] == inv["label_rows"]) & (inv["label_marginal_blind_rows"] == inv["prior_preserving_rows"]) & (inv["positive_impact_with_joint_response"] == inv["positive_impact_rows"]) & (inv["negative_impact_rows"] == 0)).all()),
        "T_all_models_tuned_by_cv5": bool((hyper_frame["model_tuning"] == "cv5").all()),
        "T_cv_selected_from_prespecified_grids": bool(set(hyper_frame["model_C"].astype(float)) <= {0.1, 1.0, 10.0, 100.0}),
    }
    selected_summary = hyper_frame.groupby(["gate", "model", "model_C", "model_gamma"], dropna=False).size().reset_index(name="n_cells")
    outputs = {
        "tuned_paired_zz_minus_svc.csv": pd.concat(paired, ignore_index=True),
        "tuned_clean_performance.csv": pd.concat(clean, ignore_index=True),
        "tuned_label_invariance.csv": inv,
        "tuned_selected_hyperparameters.csv": hyper_frame,
        "tuned_selected_hyperparameters_summary.csv": selected_summary,
    }
    return outputs, designs, inputs, checks


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build(repo: Path, out_dir: Path) -> None:
    expansion_path = repo / "results/paper_digest/paper15_q1_expansion/expansion_unique_observations.csv"
    if not expansion_path.is_file():
        raise FileNotFoundError(expansion_path)
    prereg = repo / "manuscript/paper15_v11_reinforcement_prereg.md"

    outputs: dict[str, pd.DataFrame] = {}
    designs: list[dict[str, object]] = []
    inputs: list[dict[str, object]] = []
    checks: dict[str, bool] = {}

    n_out, n_design, n_inputs, n_checks = build_gate_n(repo, expansion_path)
    outputs.update(n_out); designs.extend(n_design); inputs.extend(n_inputs); checks.update(n_checks)

    p_out, p_design, p_inputs, p_checks = build_gate_p(repo)
    outputs.update(p_out); designs.extend(p_design); inputs.extend(p_inputs); checks.update(p_checks)

    p0_frame, _, _ = _load_dir(repo / "results/raw/paper15_v11_prep_P0_reference", "P0_reference", expected_files=EXPECTED_FILES_PER_GATE, expected_models={"svc_rbf", "qsvc_zz_r1"}, expected_attacks=N_CORE_ATTACKS, repo=repo)
    t_out, t_design, t_inputs, t_checks = build_gate_t(repo, expansion_path, p0_frame)
    outputs.update(t_out); designs.extend(t_design); inputs.extend(t_inputs); checks.update(t_checks)

    design_frame = pd.DataFrame.from_records(designs)
    checks["all_gates_complete"] = bool(design_frame["complete"].all())
    outputs = {"reinforcement_gate_completeness.csv": design_frame, **outputs}

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError(f"Acceptance checks failed; no manifest written: {failed}")

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(out_dir / name, index=False)

    manifest = {
        "analysis": "paper15_v11_reinforcement",
        "status": "complete",
        "backend_filter": "qbexact_statevector",
        "preregistration": {"file": prereg.relative_to(repo).as_posix(), "sha256": _sha256(prereg) if prereg.is_file() else None},
        "null_calibration": {
            "auditor_modes": {
                "batch_level_calibrated": "new batch without item correspondence; calibrated distributional sensors only; thresholds from the calibration half",
                "item_aligned_exact": "same items compared against trusted references; exact zero threshold on prediction disagreement, confusion-profile deltas and item-level label mismatch",
            },
            "amendment": "A1 (prereg): item-aligned sensors are undefined on unaligned null draws and are excluded from batch-level regime unions",
            "alpha": ALPHA,
            "n_calibration_draws_per_cell": N_CAL_EXPECTED,
            "n_evaluation_draws_per_cell": N_EVAL_EXPECTED,
            "order_statistic_rank": _order_statistic_rank(N_CAL_EXPECTED, ALPHA),
            "rule": "per (environment, dimension, model) cell; fire if value > threshold; thresholds from calibration half only",
            "regimes": REGIMES,
            "exact_regimes": EXACT_REGIMES,
            "exact_aggregate_sensors": EXACT_AGGREGATE_SENSORS,
            "exact_item_aligned_sensors": EXACT_ITEM_ALIGNED_SENSORS,
        },
        "acceptance_checks": checks,
        "gates": design_frame.to_dict(orient="records"),
        "input_files": inputs,
        "outputs": {name: {"rows": int(len(frame)), "sha256": _sha256(out_dir / name)} for name, frame in outputs.items()},
    }
    (out_dir / "reinforcement_evidence_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status": "complete", "acceptance_checks": checks, "outputs": len(outputs)}, indent=2))
    print(f"Wrote {len(outputs)} tables and manifest to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=Path("results/paper_digest/paper15_v11_reinforcement"))
    args = parser.parse_args()
    build(args.repo_root.resolve(), args.out_dir)


if __name__ == "__main__":
    main()
