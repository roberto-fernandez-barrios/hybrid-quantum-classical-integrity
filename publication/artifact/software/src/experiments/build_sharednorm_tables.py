"""
Build shared-normalized detectability and stealth tables for Paper 1.5.

This script reconstructs the shared-normalized auditability tables used in
the manuscript from the aggregate CSV.

Important details:

1. Shared normalization is fitted on the full table, including clean rows; clean rows are excluded only from attack summaries.
2. Shared normalization is performed across models within:
       protocol, dataset_tag, svd_dim
   Model is deliberately excluded.
3. The standard signal family uses four feature/score signals measured
   against the clean evaluation reference.
4. The label/prediction-aware signal family uses seven label/prediction
   signals.
5. Full detectability is the arithmetic mean over all available normalized
   signal components, not the mean of two block-level means.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


STANDARD_SIGNAL_COLS = [
    "integrity_jsd_vs_clean_eval_mean",
    "integrity_mmd_vs_clean_eval_mean",
    "integrity_ks_reject05_vs_clean_eval_mean",
    "integrity_score_jsd_vs_clean_eval_mean",
]

LABEL_PRED_SIGNAL_COLS = [
    "integrity_label_prior_shift_mean",
    "integrity_label_jsd_mean",
    "integrity_pred_pos_rate_shift_mean",
    "integrity_pred_disagreement_mean",
    "integrity_pred_jsd_mean",
    "integrity_confusion_profile_l1_mean",
    "integrity_confusion_profile_jsd_mean",
]


def _require_cols(df: pd.DataFrame, cols: list[str], label: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing {label} columns: {missing}")


def _find_impact_column(df: pd.DataFrame) -> str:
    candidates = [
        "impact_bal_acc_mean",
        "impact_bal_acc",
        "impact",
        "bal_acc_drop_mean",
        "bal_acc_drop",
    ]
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError("Could not find impact column. Tried: " + ", ".join(candidates))


def _drop_clean_rows(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    if "is_clean_any" in out.columns:
        out = out[~out["is_clean_any"].astype(bool)].copy()
    elif "is_clean_all" in out.columns:
        out = out[~out["is_clean_all"].astype(bool)].copy()
    elif "attack" in out.columns:
        out = out[~out["attack"].astype(str).str.lower().isin(["clean", "none", "baseline"])].copy()

    return out


def _shared_minmax(df: pd.DataFrame, cols: list[str], group_cols: list[str]) -> pd.DataFrame:
    out = df.copy()

    for col in cols:
        norm_col = f"{col}_sharednorm"

        def scale(s: pd.Series) -> pd.Series:
            s = pd.to_numeric(s, errors="coerce")
            lo = s.min()
            hi = s.max()
            if pd.isna(lo) or pd.isna(hi) or hi == lo:
                return pd.Series(np.zeros(len(s)), index=s.index)
            return (s - lo) / (hi - lo)

        out[norm_col] = out.groupby(group_cols, dropna=False)[col].transform(scale)

    return out


def build_sharednorm_tables(agg: pd.DataFrame) -> dict[str, pd.DataFrame]:
    df = agg.copy()

    required = ["protocol", "dataset_tag", "svd_dim", "model"]
    _require_cols(df, required, "required metadata")
    _require_cols(df, STANDARD_SIGNAL_COLS, "standard signal")
    _require_cols(df, LABEL_PRED_SIGNAL_COLS, "label/prediction signal")

    impact_col = _find_impact_column(df)
    df["impact"] = pd.to_numeric(df[impact_col], errors="coerce")

    group_cols = ["protocol", "dataset_tag", "svd_dim"]

    standard_norm_cols = [f"{c}_sharednorm" for c in STANDARD_SIGNAL_COLS]
    label_pred_norm_cols = [f"{c}_sharednorm" for c in LABEL_PRED_SIGNAL_COLS]
    all_norm_cols = standard_norm_cols + label_pred_norm_cols

    df = _shared_minmax(df, STANDARD_SIGNAL_COLS + LABEL_PRED_SIGNAL_COLS, group_cols)

    df["detectability_old_sharednorm"] = df[standard_norm_cols].mean(axis=1)
    df["detectability_new_sharednorm"] = df[label_pred_norm_cols].mean(axis=1)
    df["detectability_sharednorm"] = df[all_norm_cols].mean(axis=1)

    df["stealth_old_sharednorm"] = df["impact"] * (1.0 - df["detectability_old_sharednorm"])
    df["stealth_new_sharednorm"] = df["impact"] * (1.0 - df["detectability_new_sharednorm"])
    df["stealth_sharednorm"] = df["impact"] * (1.0 - df["detectability_sharednorm"])

    # Normalization is computed on the full table, including clean rows.
    # Clean rows are excluded only from attack summaries and ratios.
    df = _drop_clean_rows(df)

    summary = (
        df.groupby(["protocol", "model", "svd_dim"], dropna=False)
        .agg(
            impact_bal_acc_mean=("impact", "mean"),
            detectability_sharednorm_mean=("detectability_sharednorm", "mean"),
            stealth_sharednorm_mean=("stealth_sharednorm", "mean"),
            detectability_old_sharednorm_mean=("detectability_old_sharednorm", "mean"),
            detectability_new_sharednorm_mean=("detectability_new_sharednorm", "mean"),
            stealth_old_sharednorm_mean=("stealth_old_sharednorm", "mean"),
            stealth_new_sharednorm_mean=("stealth_new_sharednorm", "mean"),
            n_attacks=("impact", "size"),
        )
        .reset_index()
    )

    svc = summary[summary["model"] == "svc_rbf"].copy()
    svc = svc.rename(
        columns={
            "impact_bal_acc_mean": "svc_impact",
            "stealth_sharednorm_mean": "svc_stealth_sharednorm",
        }
    )

    ratios = summary.merge(
        svc[["protocol", "svd_dim", "svc_impact", "svc_stealth_sharednorm"]],
        on=["protocol", "svd_dim"],
        how="left",
    )

    ratios = ratios[ratios["model"] != "svc_rbf"].copy()

    ratios["impact_ratio_vs_svc"] = (
        ratios["impact_bal_acc_mean"] / ratios["svc_impact"].replace(0, np.nan)
    )
    ratios["stealth_sharednorm_ratio_vs_svc"] = (
        ratios["stealth_sharednorm_mean"] / ratios["svc_stealth_sharednorm"].replace(0, np.nan)
    )

    signal_manifest = pd.DataFrame(
        [{"family": "standard", "csv_column_used": c} for c in STANDARD_SIGNAL_COLS]
        + [{"family": "label_prediction", "csv_column_used": c} for c in LABEL_PRED_SIGNAL_COLS]
    )

    return {
        "row_level_sharednorm.csv": df,
        "summary_by_model_dim_protocol_sharednorm.csv": summary,
        "table_model_vs_svc_ratios_sharednorm.csv": ratios,
        "signal_columns_used.csv": signal_manifest,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agg", required=True, help="Path to aggregated CSV.")
    parser.add_argument("--outdir", required=True, help="Output directory.")
    args = parser.parse_args()

    agg = pd.read_csv(args.agg)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    tables = build_sharednorm_tables(agg)

    print("[INFO] Signal columns used:")
    for _, row in tables["signal_columns_used.csv"].iterrows():
        print(f"  - {row['family']}: {row['csv_column_used']}")

    for name, table in tables.items():
        table.to_csv(outdir / name, index=False)
        print(f"[OK] Written: {outdir / name} rows={len(table)}")


if __name__ == "__main__":
    main()
