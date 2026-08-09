"""Build reviewer-facing evidence tables for the Paper 1.5 Q1 Gate 1 run.

This script deliberately separates three issues that the generic aggregation
pipeline cannot resolve on its own:

1. The classical baseline is repeated in the qnone, ZZ, Z, and PauliXYZ CSVs.
   Those rows are computational duplicates, not additional observations.
2. Model seeds are nested within split seeds.  The primary uncertainty unit is
   therefore the split seed (five clusters), while the 20 seed-unit analysis is
   retained only as a sensitivity analysis.
3. An auditability gap is conditional on the auditor's information set.  The
   exported sensor-regime table keeps feature-only, feature-plus-prediction,
   label-marginal, and joint-outcome signals separate instead of hiding their
   coverage behind one scalar average.

The inputs are immutable raw CSVs.  All outputs are derived tables and a JSON
manifest written below ``results/paper_digest`` by default.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t


KEY_COLS = [
    "protocol",
    "dataset_tag",
    "svd_dim",
    "split_seed",
    "model_seed",
    "model",
    "attack",
]

FEATURE_SIGNAL_COLS = [
    "integrity_jsd_vs_clean_eval",
    "integrity_mmd_vs_clean_eval",
    "integrity_ks_reject05_vs_clean_eval",
]

PREDICTION_SIGNAL_COLS = ["integrity_score_jsd_vs_clean_eval"]

LABEL_MARGINAL_SIGNAL_COLS = [
    "integrity_label_prior_shift",
    "integrity_label_jsd",
]

JOINT_OUTCOME_SIGNAL_COLS = [
    "integrity_pred_pos_rate_shift",
    "integrity_pred_disagreement",
    "integrity_pred_jsd",
    "integrity_confusion_profile_l1",
    "integrity_confusion_profile_jsd",
]

STANDARD_SIGNAL_COLS = FEATURE_SIGNAL_COLS + PREDICTION_SIGNAL_COLS
FULL_SIGNAL_COLS = (
    STANDARD_SIGNAL_COLS
    + LABEL_MARGINAL_SIGNAL_COLS
    + JOINT_OUTCOME_SIGNAL_COLS
)

EXPECTED_MODELS = {
    "svc_rbf",
    "qsvc_zz_r1",
    "qsvc_z_r1",
    "qsvc_pauli_xyz_r1",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_columns(frame: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _load_raw(raw_dir: Path) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    paths = sorted(raw_dir.glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"No CSV files found under {raw_dir}")

    frames: list[pd.DataFrame] = []
    inputs: list[dict[str, object]] = []
    for path in paths:
        frame = pd.read_csv(path)
        frame["_source_file"] = path.name
        frames.append(frame)
        inputs.append(
            {
                "path": path.as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )

    raw = pd.concat(frames, ignore_index=True, sort=False)
    _require_columns(raw, KEY_COLS + ["impact_bal_acc"] + FULL_SIGNAL_COLS)
    return raw, inputs


def _deduplicate(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Collapse repeated SVC rows only after verifying numerical identity."""

    evidence_cols = [
        "bal_acc",
        "f1_pos",
        "roc_auc",
        "impact_bal_acc",
        *FULL_SIGNAL_COLS,
    ]
    evidence_cols = [column for column in evidence_cols if column in raw.columns]

    conflicts: list[tuple[object, ...]] = []
    duplicated = raw[raw.duplicated(KEY_COLS, keep=False)]
    for key, group in duplicated.groupby(KEY_COLS, dropna=False, sort=False):
        numeric = group[evidence_cols].apply(pd.to_numeric, errors="coerce")
        spread = numeric.max(axis=0, skipna=True) - numeric.min(axis=0, skipna=True)
        if bool((spread.fillna(0.0).abs() > 1e-12).any()):
            conflicts.append(key if isinstance(key, tuple) else (key,))

    if conflicts:
        preview = conflicts[:5]
        raise ValueError(
            "Repeated observation keys contain conflicting numerical evidence; "
            f"first conflicts: {preview}"
        )

    dedup = (
        raw.sort_values(KEY_COLS + ["_source_file"])
        .drop_duplicates(KEY_COLS, keep="first")
        .reset_index(drop=True)
    )
    if dedup.duplicated(KEY_COLS).any():
        raise AssertionError("Observation keys are not unique after deduplication")

    counts = {
        "raw_rows": int(len(raw)),
        "unique_rows": int(len(dedup)),
        "duplicate_rows_removed": int(len(raw) - len(dedup)),
        "raw_svc_rows": int((raw["model"] == "svc_rbf").sum()),
        "unique_svc_rows": int((dedup["model"] == "svc_rbf").sum()),
    }
    return dedup, counts


def _shared_minmax(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize across models within the same realized benchmark cell."""

    out = frame.copy()
    group_cols = [
        "protocol",
        "dataset_tag",
        "svd_dim",
        "split_seed",
        "model_seed",
    ]
    normalized: list[str] = []
    for column in FULL_SIGNAL_COLS:
        values = pd.to_numeric(out[column], errors="coerce")
        low = values.groupby([out[c] for c in group_cols], dropna=False).transform("min")
        high = values.groupby([out[c] for c in group_cols], dropna=False).transform("max")
        denominator = high - low
        norm_col = f"{column}__sharednorm"
        out[norm_col] = ((values - low) / denominator.replace(0.0, np.nan)).fillna(0.0)
        normalized.append(norm_col)

    feature_norm = [f"{c}__sharednorm" for c in FEATURE_SIGNAL_COLS]
    prediction_norm = [f"{c}__sharednorm" for c in PREDICTION_SIGNAL_COLS]
    label_norm = [f"{c}__sharednorm" for c in LABEL_MARGINAL_SIGNAL_COLS]
    outcome_norm = [f"{c}__sharednorm" for c in JOINT_OUTCOME_SIGNAL_COLS]
    standard_norm = feature_norm + prediction_norm

    out["detectability_feature_sharednorm"] = out[feature_norm].mean(axis=1)
    out["detectability_prediction_sharednorm"] = out[prediction_norm].mean(axis=1)
    out["detectability_standard_sharednorm"] = out[standard_norm].mean(axis=1)
    out["detectability_label_marginal_sharednorm"] = out[label_norm].mean(axis=1)
    out["detectability_joint_outcome_sharednorm"] = out[outcome_norm].mean(axis=1)
    out["detectability_full_sharednorm"] = out[normalized].mean(axis=1)
    out["stealth_standard_sharednorm"] = pd.to_numeric(
        out["impact_bal_acc"], errors="coerce"
    ) * (1.0 - out["detectability_standard_sharednorm"])
    out["stealth_full_sharednorm"] = pd.to_numeric(
        out["impact_bal_acc"], errors="coerce"
    ) * (1.0 - out["detectability_full_sharednorm"])
    return out


def _mean_ci(values: pd.Series) -> dict[str, float | int]:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    n = int(len(clean))
    if n == 0:
        return {"mean": math.nan, "std": math.nan, "ci95_low": math.nan, "ci95_high": math.nan, "n": 0}
    mean = float(clean.mean())
    if n == 1:
        return {"mean": mean, "std": math.nan, "ci95_low": math.nan, "ci95_high": math.nan, "n": 1}
    std = float(clean.std(ddof=1))
    half = float(student_t.ppf(0.975, df=n - 1) * std / math.sqrt(n))
    return {
        "mean": mean,
        "std": std,
        "ci95_low": mean - half,
        "ci95_high": mean + half,
        "n": n,
    }


def _per_seed_summary(attacked: pd.DataFrame) -> pd.DataFrame:
    group_cols = [
        "protocol",
        "dataset_tag",
        "model",
        "svd_dim",
        "split_seed",
        "model_seed",
    ]
    summary = (
        attacked.groupby(group_cols, dropna=False)
        .agg(
            impact_mean=("impact_bal_acc", "mean"),
            detectability_feature_sharednorm_mean=("detectability_feature_sharednorm", "mean"),
            detectability_standard_sharednorm_mean=("detectability_standard_sharednorm", "mean"),
            detectability_label_marginal_sharednorm_mean=("detectability_label_marginal_sharednorm", "mean"),
            detectability_joint_outcome_sharednorm_mean=("detectability_joint_outcome_sharednorm", "mean"),
            detectability_full_sharednorm_mean=("detectability_full_sharednorm", "mean"),
            stealth_standard_sharednorm_mean=("stealth_standard_sharednorm", "mean"),
            stealth_full_sharednorm_mean=("stealth_full_sharednorm", "mean"),
            n_attacks=("attack", "nunique"),
        )
        .reset_index()
    )
    summary["seed_unit"] = (
        summary["split_seed"].astype(str) + "|" + summary["model_seed"].astype(str)
    )
    return summary


def _cluster_summary(per_seed: pd.DataFrame) -> pd.DataFrame:
    """Primary summaries: average model seeds, then infer over split clusters."""

    metric_cols = [
        "impact_mean",
        "detectability_standard_sharednorm_mean",
        "detectability_full_sharednorm_mean",
        "stealth_standard_sharednorm_mean",
        "stealth_full_sharednorm_mean",
    ]
    cluster = (
        per_seed.groupby(
            ["protocol", "dataset_tag", "model", "svd_dim", "split_seed"],
            dropna=False,
        )[metric_cols]
        .mean()
        .reset_index()
    )

    records: list[dict[str, object]] = []
    group_cols = ["protocol", "dataset_tag", "model", "svd_dim"]
    for key, group in cluster.groupby(group_cols, dropna=False, sort=True):
        base = dict(zip(group_cols, key, strict=True))
        for metric in metric_cols:
            records.append({**base, "metric": metric, **_mean_ci(group[metric])})
    return cluster, pd.DataFrame.from_records(records)


def _paired_zz_svc(
    per_seed: pd.DataFrame, cluster: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    metrics = ["impact_mean", "stealth_full_sharednorm_mean"]
    sensitivity_records: list[dict[str, object]] = []
    cluster_records: list[dict[str, object]] = []

    for dim in sorted(per_seed["svd_dim"].unique()):
        unit = per_seed[per_seed["svd_dim"] == dim]
        wide = unit.pivot_table(
            index=["protocol", "dataset_tag", "svd_dim", "split_seed", "model_seed"],
            columns="model",
            values=metrics,
            aggfunc="first",
        )
        for metric in metrics:
            diff = wide[(metric, "qsvc_zz_r1")] - wide[(metric, "svc_rbf")]
            sensitivity_records.append(
                {
                    "svd_dim": int(dim),
                    "metric": metric,
                    "analysis_unit": "split_model_seed_sensitivity",
                    **_mean_ci(diff),
                    "all_positive": bool((diff > 0).all()),
                }
            )

        clustered = cluster[cluster["svd_dim"] == dim]
        wide_cluster = clustered.pivot_table(
            index=["protocol", "dataset_tag", "svd_dim", "split_seed"],
            columns="model",
            values=metrics,
            aggfunc="first",
        )
        for metric in metrics:
            diff = wide_cluster[(metric, "qsvc_zz_r1")] - wide_cluster[(metric, "svc_rbf")]
            cluster_records.append(
                {
                    "svd_dim": int(dim),
                    "metric": metric,
                    "analysis_unit": "split_seed_cluster_primary",
                    **_mean_ci(diff),
                    "all_positive": bool((diff > 0).all()),
                }
            )

    return (
        pd.DataFrame.from_records(cluster_records),
        pd.DataFrame.from_records(sensitivity_records),
    )


def _ratios(per_seed: pd.DataFrame) -> pd.DataFrame:
    summary = (
        per_seed.groupby(["protocol", "dataset_tag", "model", "svd_dim"], dropna=False)
        .agg(
            impact_mean=("impact_mean", "mean"),
            stealth_full_sharednorm_mean=("stealth_full_sharednorm_mean", "mean"),
            n_seed_units=("seed_unit", "nunique"),
            n_split_clusters=("split_seed", "nunique"),
        )
        .reset_index()
    )
    svc = summary[summary["model"] == "svc_rbf"].rename(
        columns={
            "impact_mean": "svc_impact_mean",
            "stealth_full_sharednorm_mean": "svc_stealth_full_sharednorm_mean",
        }
    )
    out = summary.merge(
        svc[
            [
                "protocol",
                "dataset_tag",
                "svd_dim",
                "svc_impact_mean",
                "svc_stealth_full_sharednorm_mean",
            ]
        ],
        on=["protocol", "dataset_tag", "svd_dim"],
        how="left",
    )
    out["impact_ratio_vs_svc"] = out["impact_mean"] / out["svc_impact_mean"]
    out["stealth_full_sharednorm_ratio_vs_svc"] = (
        out["stealth_full_sharednorm_mean"] / out["svc_stealth_full_sharednorm_mean"]
    )
    return out


def _sensor_regime_table(attacked: pd.DataFrame) -> pd.DataFrame:
    """Keep the observation regimes visible at attack/model/dimension level."""

    group_cols = [
        "protocol",
        "dataset_tag",
        "model",
        "svd_dim",
        "attack_family",
        "attack",
    ]
    aggregations: dict[str, tuple[str, str]] = {
        "impact_mean": ("impact_bal_acc", "mean"),
        "prediction_change_mean": ("integrity_pred_disagreement", "mean"),
        "feature_detectability_mean": ("detectability_feature_sharednorm", "mean"),
        "feature_prediction_detectability_mean": ("detectability_standard_sharednorm", "mean"),
        "label_marginal_detectability_mean": ("detectability_label_marginal_sharednorm", "mean"),
        "joint_outcome_detectability_mean": ("detectability_joint_outcome_sharednorm", "mean"),
        "full_detectability_mean": ("detectability_full_sharednorm", "mean"),
        "n_split_clusters": ("split_seed", "nunique"),
        "n_model_seeds": ("model_seed", "nunique"),
    }
    for column in STANDARD_SIGNAL_COLS + LABEL_MARGINAL_SIGNAL_COLS:
        aggregations[f"raw_{column}_max"] = (column, "max")

    out = attacked.groupby(group_cols, dropna=False).agg(**aggregations).reset_index()
    tolerance = 1e-12
    out["feature_prediction_structurally_blind"] = (
        out[[f"raw_{c}_max" for c in STANDARD_SIGNAL_COLS]].abs().max(axis=1)
        <= tolerance
    )
    out["label_marginal_structurally_blind"] = (
        out[[f"raw_{c}_max" for c in LABEL_MARGINAL_SIGNAL_COLS]].abs().max(axis=1)
        <= tolerance
    )
    out["impact_locus"] = np.where(
        out["prediction_change_mean"].abs() <= tolerance,
        "evaluation_or_label_path",
        "model_output_path",
    )
    return out.sort_values(
        ["feature_prediction_structurally_blind", "impact_mean"],
        ascending=[False, False],
    )


def _validate_design(dedup: pd.DataFrame) -> dict[str, object]:
    models = set(dedup["model"].dropna().astype(str))
    missing_models = sorted(EXPECTED_MODELS - models)
    if missing_models:
        raise ValueError(f"Expected models missing from Gate 1: {missing_models}")

    attacked = dedup[dedup["attack"] != "clean"]
    attacks_per_cell = attacked.groupby(
        ["model", "svd_dim", "split_seed", "model_seed"], dropna=False
    )["attack"].nunique()
    if attacks_per_cell.nunique() != 1:
        raise ValueError(
            "Inconsistent attack coverage across model/dimension/seed cells: "
            f"{sorted(attacks_per_cell.unique())}"
        )

    return {
        "models": sorted(models),
        "dimensions": sorted(int(v) for v in dedup["svd_dim"].unique()),
        "split_seeds": sorted(int(v) for v in dedup["split_seed"].unique()),
        "model_seeds": sorted(int(v) for v in dedup["model_seed"].unique()),
        "attacks_per_model_dimension_seed_cell": int(attacks_per_cell.iloc[0]),
    }


def build(raw_dir: Path, out_dir: Path) -> None:
    raw, inputs = _load_raw(raw_dir)
    dedup, duplicate_counts = _deduplicate(raw)
    design = _validate_design(dedup)
    normalized = _shared_minmax(dedup)
    attacked = normalized[normalized["attack"] != "clean"].copy()

    per_seed = _per_seed_summary(attacked)
    cluster, cluster_summary = _cluster_summary(per_seed)
    paired_primary, paired_sensitivity = _paired_zz_svc(per_seed, cluster)
    ratios = _ratios(per_seed)
    sensor_regimes = _sensor_regime_table(attacked)
    blind_cases = sensor_regimes[
        sensor_regimes["feature_prediction_structurally_blind"]
        & (sensor_regimes["impact_mean"] > 0)
    ].copy()

    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "gate1_unique_observations.csv": dedup.drop(columns=["_source_file"]),
        "gate1_per_seed_unit_summary.csv": per_seed,
        "gate1_per_split_cluster_summary.csv": cluster,
        "gate1_cluster_model_summary_ci95.csv": cluster_summary,
        "gate1_paired_zz_minus_svc_primary_clustered.csv": paired_primary,
        "gate1_paired_zz_minus_svc_seedunit_sensitivity.csv": paired_sensitivity,
        "gate1_ratios_vs_svc.csv": ratios,
        "gate1_sensor_regime_table.csv": sensor_regimes,
        "gate1_structurally_blind_positive_impact_cases.csv": blind_cases,
    }
    for name, frame in outputs.items():
        frame.to_csv(out_dir / name, index=False)

    manifest = {
        "analysis": "paper15_q1_gate1",
        "raw_directory": raw_dir.as_posix(),
        "normalization_group": [
            "protocol",
            "dataset_tag",
            "svd_dim",
            "split_seed",
            "model_seed",
        ],
        "primary_inference_unit": "split_seed after averaging nested model seeds",
        "sensitivity_inference_unit": "split_seed x model_seed",
        "duplicate_audit": duplicate_counts,
        "design": design,
        "input_files": inputs,
        "outputs": {
            name: {"rows": int(len(frame)), "sha256": _sha256(out_dir / name)}
            for name, frame in outputs.items()
        },
    }
    manifest_path = out_dir / "gate1_evidence_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(json.dumps({"duplicate_audit": duplicate_counts, "design": design}, indent=2))
    print(f"Wrote {len(outputs)} tables and manifest to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("results/raw/paper15_q1_gate1_id_seeds_20"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/paper_digest/paper15_q1_gate1_id_seeds_20_q1"),
    )
    args = parser.parse_args()
    build(args.raw_dir, args.out_dir)


if __name__ == "__main__":
    main()
