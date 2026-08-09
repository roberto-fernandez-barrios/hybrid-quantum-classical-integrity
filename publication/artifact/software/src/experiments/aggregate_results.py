# src/experiments/aggregate_results.py
#
# MAX-LEVEL auditability-aware aggregation for run__*.csv files produced by
# src.experiments.run_benchmark.
#
# Main goals:
#   - join each attacked row with its clean baseline
#   - aggregate across seeds into a paper-friendly table
#   - preserve per-model granularity (do NOT collapse all QSVC under one family)
#   - remain compatible with BOTH:
#       * legacy/current runner outputs
#       * richer future runner outputs
#   - derive auditability-oriented scores:
#       * impact_bal_acc_mean
#       * detectability_score_mean
#       * stealth_score_mean
#   - export companion tables useful for the paper narrative
#
# Usage:
#   python -m src.experiments.aggregate_results \
#       --raw-dir results/raw/hais_cicids_runs \
#       --out results/aggregated/agg.csv \
#       --recursive
#
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Iterable

import numpy as np
import pandas as pd

from src.utils.io import ensure_dir


# ----------------------------
# Helpers
# ----------------------------
def _to_float(df: pd.DataFrame, cols: Sequence[str]) -> None:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)


def _to_int(df: pd.DataFrame, cols: Sequence[str]) -> None:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")


def _strip_string_cols(df: pd.DataFrame, cols: Sequence[str]) -> None:
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()


def _safe_stat_mtime(p: Path) -> float:
    try:
        return float(p.stat().st_mtime)
    except Exception:
        return -1.0


def _find_run_files(raw_dir: Path, recursive: bool, pattern: str) -> List[Path]:
    """
    Return run files ordered by modification time, then path.

    This matters because later de-duplication keeps the LAST occurrence.
    With this ordering, keep='last' tends to preserve the newest file
    instead of whichever filename sorts last lexicographically.
    """
    files = sorted(raw_dir.rglob(pattern)) if recursive else sorted(raw_dir.glob(pattern))
    return sorted(files, key=lambda p: (_safe_stat_mtime(p), str(p)))


def _require_cols(df: pd.DataFrame, cols: Sequence[str], ctx: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise SystemExit(f"[ERROR] Missing required columns in {ctx}: {missing}")


def _attack_name_clean_series(df: pd.DataFrame) -> pd.Series:
    if "attack" not in df.columns:
        return pd.Series(False, index=df.index, dtype=bool)
    return df["attack"].astype(str).str.strip().str.lower().eq("clean")


def _detect_is_clean(df: pd.DataFrame) -> pd.Series:
    """
    Primary policy:
      attack_is_clean = 1 for clean, 0 for attacked

    Fallback:
      attack == 'clean' if attack_is_clean is missing / NaN.
    """
    attack_name_clean = _attack_name_clean_series(df)

    if "attack_is_clean" not in df.columns:
        return attack_name_clean.astype(bool)

    ais = pd.to_numeric(df["attack_is_clean"], errors="coerce").astype("Int64")
    col_clean = ais.eq(1)

    mask = ais.notna()
    conflicts = (attack_name_clean != col_clean) & mask
    if conflicts.any():
        print(
            f"[WARN] Detected {int(conflicts.sum())} rows where attack_is_clean disagrees with "
            f"attack=='clean'. Using attack_is_clean as primary."
        )

    return col_clean.where(mask, attack_name_clean).fillna(attack_name_clean).astype(bool)


_ID_RE = re.compile(r"__id([0-9a-fA-F]{8})")
_OOD_RE = re.compile(r"__tr([0-9a-fA-F]{8})__te([0-9a-fA-F]{8})")


def _dataset_tag_from_path(csv_path: Path, protocol: str) -> str:
    """
    Parse dataset tags from runner filenames.

      ID : __id<8hex>
      OOD: __tr<8hex>__te<8hex>
    """
    name = csv_path.name
    if str(protocol).lower() == "ood":
        m = _OOD_RE.search(name)
        if m:
            return f"tr{m.group(1).lower()}__te{m.group(2).lower()}"
        return "trNA__teNA"

    m = _ID_RE.search(name)
    if m:
        return f"id{m.group(1).lower()}"
    return "idNA"


def _safe_mean(s: pd.Series) -> float:
    return float(s.mean(skipna=True))


def _safe_std(s: pd.Series) -> float:
    return float(s.std(skipna=True))


def _safe_min(s: pd.Series) -> float:
    return float(s.min(skipna=True))


def _safe_max(s: pd.Series) -> float:
    return float(s.max(skipna=True))


def _safe_count_notna(s: pd.Series) -> int:
    return int(s.notna().sum())


def _as_attacked_mask(df: pd.DataFrame) -> pd.Series:
    """
    Consistent attacked-mask policy, aligned with _detect_is_clean().

    Priority:
      1) aggregated clean flags
      2) row-level is_clean
      3) attack_is_clean with fallback to attack == 'clean'
      4) attack == 'clean'
    """
    if "is_clean_all" in df.columns:
        return ~df["is_clean_all"].astype(bool)

    if "is_clean" in df.columns:
        return ~df["is_clean"].astype(bool)

    attack_name_clean = _attack_name_clean_series(df)

    if "attack_is_clean" in df.columns:
        ais = pd.to_numeric(df["attack_is_clean"], errors="coerce").astype("Int64")
        col_clean = ais.eq(1)
        mask = ais.notna()
        clean = col_clean.where(mask, attack_name_clean).fillna(attack_name_clean).astype(bool)
        return ~clean

    if "attack" in df.columns:
        return ~attack_name_clean

    return pd.Series(True, index=df.index, dtype=bool)


def _parse_csv_list(raw: str) -> List[str]:
    s = (raw or "").strip()
    if not s:
        return []
    s = s.replace(";", ",")
    return [p.strip() for p in s.split(",") if p.strip()]


def _weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    v = pd.to_numeric(values, errors="coerce").astype(float)
    w = pd.to_numeric(weights, errors="coerce").astype(float)

    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if not mask.any():
        return float("nan")

    vv = v[mask].to_numpy(dtype=float)
    ww = w[mask].to_numpy(dtype=float)
    return float(np.average(vv, weights=ww))


def _group_weighted_means(
    df: pd.DataFrame,
    *,
    group_cols: List[str],
    metrics: List[str],
    weight_col: str = "n_seed_units",
) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []

    for key, sub in df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)

        row: Dict[str, object] = {c: v for c, v in zip(group_cols, key)}
        row["n_groups"] = int(len(sub))

        if weight_col in sub.columns:
            w = pd.to_numeric(sub[weight_col], errors="coerce").astype(float)
            row["weight_sum"] = float(np.nansum(np.clip(w.to_numpy(dtype=float), a_min=0.0, a_max=None)))
        else:
            w = pd.Series(1.0, index=sub.index, dtype=float)
            row["weight_sum"] = float(len(sub))

        for m in metrics:
            row[m] = _weighted_mean(sub[m], w) if m in sub.columns else float("nan")

        rows.append(row)

    return pd.DataFrame(rows)


def _ensure_numeric_round(df: pd.DataFrame, cols: Iterable[str], ndigits: int = 12) -> None:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").round(ndigits)


def _coalesce_columns(df: pd.DataFrame, target: str, candidates: Sequence[str]) -> None:
    """
    Fill/create `target` by taking the first non-null value across candidates.
    Existing `target` is respected first if already present.
    """
    ordered = [c for c in [target, *candidates] if c in df.columns]
    if not ordered:
        return

    s = pd.Series(np.nan, index=df.index, dtype=object)
    for c in ordered:
        s = s.where(s.notna(), df[c])
    df[target] = s


def _maybe_bool_series(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(False, index=df.index, dtype=bool)
    x = df[col]
    if pd.api.types.is_bool_dtype(x):
        return x.fillna(False).astype(bool)
    return x.astype(str).str.strip().str.lower().isin({"1", "true", "t", "yes", "y"})


def _safe_positive_harm_from_drop(drop_series: pd.Series) -> pd.Series:
    s = pd.to_numeric(drop_series, errors="coerce").astype(float)
    return (-s).clip(lower=0.0)


def _safe_positive_harm_error_from_drop(drop_series: pd.Series) -> pd.Series:
    s = pd.to_numeric(drop_series, errors="coerce").astype(float)
    return s.clip(lower=0.0)


def _first_existing(df: pd.DataFrame, cols: Sequence[str]) -> Optional[str]:
    for c in cols:
        if c in df.columns:
            return c
    return None


# ----------------------------
# Schema normalization
# ----------------------------
def normalize_runner_schema(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Normalize legacy/current/future runner schemas into a canonical dataframe
    that the rest of the pipeline can rely on.
    """
    out = df.copy()

    # Prefer dataset_tag already written by richer runners. Fall back to filename parsing later.
    if "dataset_tag" in out.columns:
        out["dataset_tag"] = out["dataset_tag"].astype(str).str.strip()

    # Canonical clean-reference columns:
    # target = clean_<metric>
    clean_aliases = {
        "clean_bal_acc": ["bal_acc_clean"],
        "clean_f1_pos": ["f1_pos_clean"],
        "clean_roc_auc": ["roc_auc_clean"],
        "clean_pred_error_rate": ["pred_error_rate_clean"],
        "clean_pos_rate_eval": ["pos_rate_eval_clean"],
        "clean_label_pos_rate_eval": ["label_pos_rate_clean"],
        "clean_pred_pos_rate_eval": ["pred_pos_rate_clean"],
        "clean_integrity_jsd": ["integrity_jsd_clean"],
        "clean_integrity_mmd": ["integrity_mmd_clean"],
        "clean_integrity_ks_mean": ["integrity_ks_mean_clean"],
        "clean_integrity_ks_reject05": ["integrity_ks_reject05_clean"],
        "clean_integrity_score_jsd": ["integrity_score_jsd_clean"],
        "clean_integrity_confusion_profile_l1": ["integrity_confusion_profile_l1_clean"],
        "clean_integrity_confusion_profile_jsd": ["integrity_confusion_profile_jsd_clean"],
    }
    for target, aliases in clean_aliases.items():
        _coalesce_columns(out, target, aliases)

    # Canonical impacts if the runner already provided them.
    impact_aliases = {
        "impact_bal_acc": [],
        "impact_f1": [],
        "impact_roc_auc": [],
        "impact_pred_error": [],
    }
    for target, aliases in impact_aliases.items():
        _coalesce_columns(out, target, aliases)

    # Numeric conversions, including richer schema fields.
    _to_int(
        out,
        [
            "svd_dim",
            "seed",
            "split_seed",
            "model_seed",
            "attack_seed",
            "clean_ref_attack_seed",
            "attack_is_clean",
            "n_features",
            "max_train",
            "max_test",
        ],
    )

    _to_float(
        out,
        [
            # attack/meta
            "attack_strength",
            "attack_strength_nominal",
            "attack_strength_eff",
            "label_flip_rate",
            # performance
            "bal_acc",
            "f1_pos",
            "roc_auc",
            "pos_rate_eval",
            "pred_error_rate",
            "label_pos_rate_eval",
            "pred_pos_rate_eval",
            # clean performance
            "clean_bal_acc",
            "clean_f1_pos",
            "clean_roc_auc",
            "clean_pred_error_rate",
            "clean_pos_rate_eval",
            "clean_label_pos_rate_eval",
            "clean_pred_pos_rate_eval",
            # current base signals
            "integrity_jsd",
            "integrity_mmd",
            "integrity_ks_mean",
            "integrity_ks_reject05",
            "integrity_score_jsd",
            # clean base signals
            "clean_integrity_jsd",
            "clean_integrity_mmd",
            "clean_integrity_ks_mean",
            "clean_integrity_ks_reject05",
            "clean_integrity_score_jsd",
            "clean_integrity_confusion_profile_l1",
            "clean_integrity_confusion_profile_jsd",
            # existing runner deltas
            "integrity_jsd_delta",
            "integrity_mmd_delta",
            "integrity_ks_mean_delta",
            "integrity_ks_reject05_delta",
            "integrity_score_jsd_delta",
            "integrity_confusion_profile_l1_delta",
            "integrity_confusion_profile_jsd_delta",
            # attack-vs-clean eval / label-aware / pred-aware
            "integrity_jsd_vs_clean_eval",
            "integrity_mmd_vs_clean_eval",
            "integrity_ks_mean_vs_clean_eval",
            "integrity_ks_reject05_vs_clean_eval",
            "integrity_score_jsd_vs_clean_eval",
            "integrity_label_prior_shift",
            "integrity_label_jsd",
            "integrity_pred_pos_rate_shift",
            "integrity_pred_disagreement",
            "integrity_pred_jsd",
            "integrity_confusion_profile_l1",
            "integrity_confusion_profile_jsd",
            # already-computed drops if present in newer runner
            "bal_acc_drop",
            "f1_pos_drop",
            "roc_auc_drop",
            "pred_error_rate_drop",
            "pos_rate_eval_drop",
            "label_pos_rate_eval_drop",
            "pred_pos_rate_eval_drop",
            # already-computed impacts if present in newer runner
            "impact_bal_acc",
            "impact_f1",
            "impact_roc_auc",
            "impact_pred_error",
            # timing
            "signals_time_s",
            "train_time_s",
            "attack_prep_time_s",
            "predict_time_s",
            "scores_time_s",
            "ref_scores_time_s",
            "ref_predict_time_s",
        ],
    )

    _ensure_numeric_round(out, ["attack_strength_nominal", "attack_strength_eff"], ndigits=12)

    # attack_priority_group / attack_suite may exist in richer runner
    if "attack_priority_group" in out.columns:
        out["attack_priority_group"] = out["attack_priority_group"].astype(str).str.strip()
    if "attack_suite" in out.columns:
        out["attack_suite"] = out["attack_suite"].astype(str).str.strip()

    # is_clean
    out["is_clean"] = _detect_is_clean(out)

    # If richer runner provided direct clean refs for all rows, keep them.
    # Otherwise later clean-join will fill them.

    if verbose:
        direct_clean_cols = [c for c in ["clean_bal_acc", "clean_f1_pos", "clean_roc_auc"] if c in out.columns]
        if direct_clean_cols:
            n_nonnull = {
                c: int(pd.to_numeric(out[c], errors="coerce").notna().sum()) for c in direct_clean_cols
            }
            print(f"[INFO] Detected direct clean-reference columns from runner: {n_nonnull}")

    return out


# ----------------------------
# Loading + normalization
# ----------------------------
def load_runs(run_files: List[Path], verbose: bool = True) -> pd.DataFrame:
    if not run_files:
        raise SystemExit("[ERROR] No run files found.")

    dfs: List[pd.DataFrame] = []
    for p in run_files:
        df = pd.read_csv(p)
        df["__source_file"] = str(p)
        df["__source_mtime"] = _safe_stat_mtime(p)
        dfs.append(df)

    out = pd.concat(dfs, axis=0, ignore_index=True)

    _require_cols(
        out,
        [
            "protocol",
            "svd_dim",
            "model_family",
            "model",
            "scale",
            "attack",
            "attack_family",
            "attack_strength_nominal",
            "attack_strength_eff",
            "attack_seed",
            "run_id",
            "clean_ref_run_id",
            "clean_ref_attack_seed",
        ],
        ctx="loaded CSVs",
    )

    _strip_string_cols(
        out,
        [
            "protocol",
            "model_family",
            "model",
            "scale",
            "attack",
            "attack_family",
            "run_id",
            "clean_ref_run_id",
        ],
    )
    if "protocol" in out.columns:
        out["protocol"] = out["protocol"].astype(str).str.lower()

    out = normalize_runner_schema(out, verbose=verbose)

    # dataset_tag:
    # 1) prefer existing non-empty dataset_tag from runner
    # 2) fallback to parsing from source filename
    src = out["__source_file"].astype(str)
    file_to_proto = (
        out.drop_duplicates("__source_file")[["__source_file", "protocol"]]
        .set_index("__source_file")["protocol"]
    )

    unique_files = pd.DataFrame({"__source_file": src.unique()})
    unique_files["protocol"] = unique_files["__source_file"].map(file_to_proto).fillna("id").astype(str)
    unique_files["dataset_tag_from_file"] = unique_files.apply(
        lambda row: _dataset_tag_from_path(Path(row["__source_file"]), str(row["protocol"])),
        axis=1,
    )
    file_to_tag = unique_files.set_index("__source_file")["dataset_tag_from_file"].to_dict()

    if "dataset_tag" not in out.columns:
        out["dataset_tag"] = src.map(file_to_tag).fillna("idNA").astype(str).str.strip()
    else:
        missing = out["dataset_tag"].astype(str).str.strip().isin({"", "nan", "None"})
        out.loc[missing, "dataset_tag"] = src[missing].map(file_to_tag).fillna("idNA")
        out["dataset_tag"] = out["dataset_tag"].astype(str).str.strip()

    if verbose:
        n_bad = int(((out["protocol"] == "ood") & (~out["dataset_tag"].astype(str).str.startswith("tr"))).sum())
        if n_bad:
            print(f"[WARN] {n_bad} OOD rows have dataset_tag not starting with 'tr' (filename tags missing?).")

    return out


# ----------------------------
# Clean join
# ----------------------------
def attach_clean_baselines(df: pd.DataFrame) -> pd.DataFrame:
    """
    Join each row with its clean baseline.

    IMPORTANT:
    We scope the clean join by (protocol, dataset_tag, run_id, attack_seed),
    not just (run_id, attack_seed). This prevents cross-dataset contamination
    when different datasets / OOD pairs share the same logical run_id.

    This function is schema-aware:
      - respects direct clean_* columns already written by richer runners
      - fills missing clean_* via baseline join
      - computes missing *_drop and impact_* columns when absent
    """
    out = df.copy()

    current_metric_cols = [
        # performance
        "bal_acc",
        "f1_pos",
        "roc_auc",
        "pred_error_rate",
        "pos_rate_eval",
        "label_pos_rate_eval",
        "pred_pos_rate_eval",
        # signals
        "integrity_jsd",
        "integrity_mmd",
        "integrity_ks_mean",
        "integrity_ks_reject05",
        "integrity_score_jsd",
        "integrity_jsd_vs_clean_eval",
        "integrity_mmd_vs_clean_eval",
        "integrity_ks_mean_vs_clean_eval",
        "integrity_ks_reject05_vs_clean_eval",
        "integrity_score_jsd_vs_clean_eval",
        "integrity_label_prior_shift",
        "integrity_label_jsd",
        "integrity_pred_pos_rate_shift",
        "integrity_pred_disagreement",
        "integrity_pred_jsd",
        "integrity_confusion_profile_l1",
        "integrity_confusion_profile_jsd",
        # timing
        "signals_time_s",
        "attack_prep_time_s",
        "predict_time_s",
        "scores_time_s",
        "ref_scores_time_s",
        "ref_predict_time_s",
    ]
    current_metric_cols = [c for c in current_metric_cols if c in out.columns]

    scope_cols = [c for c in ["protocol", "dataset_tag"] if c in out.columns]

    baseline = out[out["is_clean"]][scope_cols + ["run_id", "attack_seed"] + current_metric_cols].copy()

    dup_subset = scope_cols + ["run_id", "attack_seed"]
    dup_mask = baseline.duplicated(subset=dup_subset, keep=False)
    if dup_mask.any():
        n_dup = int(dup_mask.sum())
        n_keys = int(baseline.loc[dup_mask, dup_subset].drop_duplicates().shape[0])
        print(
            f"[WARN] Baseline has {n_dup} rows across {n_keys} duplicated keys {dup_subset}. "
            f"Keeping the LAST occurrence per key for joining."
        )
        baseline = baseline.drop_duplicates(subset=dup_subset, keep="last")

    rename_map = {"run_id": "clean_key_run_id", "attack_seed": "clean_key_attack_seed"}
    for c in current_metric_cols:
        rename_map[c] = f"joined_clean_{c}"
    baseline = baseline.rename(columns=rename_map)

    out = out.merge(
        baseline,
        how="left",
        left_on=scope_cols + ["clean_ref_run_id", "clean_ref_attack_seed"],
        right_on=scope_cols + ["clean_key_run_id", "clean_key_attack_seed"],
    ).drop(columns=["clean_key_run_id", "clean_key_attack_seed"], errors="ignore")

    # Coalesce canonical clean_<metric>
    for c in current_metric_cols:
        canonical_clean = f"clean_{c}"
        joined_clean = f"joined_clean_{c}"

        if canonical_clean not in out.columns:
            out[canonical_clean] = np.nan

        if joined_clean in out.columns:
            out[canonical_clean] = pd.to_numeric(out[canonical_clean], errors="coerce").where(
                pd.to_numeric(out[canonical_clean], errors="coerce").notna(),
                pd.to_numeric(out[joined_clean], errors="coerce"),
            )

    # For clean rows, clean_<metric> == self when still missing
    for c in current_metric_cols:
        canonical_clean = f"clean_{c}"
        if c in out.columns and canonical_clean in out.columns:
            idx = out["is_clean"] & pd.to_numeric(out[canonical_clean], errors="coerce").isna()
            if idx.any():
                out.loc[idx, canonical_clean] = pd.to_numeric(out.loc[idx, c], errors="coerce")

    # Warn only for attacked rows still missing a clean baseline
    if "clean_bal_acc" in out.columns:
        attacked_missing = (~out["is_clean"]) & pd.to_numeric(out["clean_bal_acc"], errors="coerce").isna()
        n_miss = int(attacked_missing.sum())
        if n_miss:
            print(
                f"[WARN] Missing clean baseline for {n_miss} attacked rows. "
                f"Ensure corresponding clean runs are present in the aggregation scope."
            )

    # Compute missing drops:
    # convention = current - clean
    drop_metric_cols = [
        "bal_acc",
        "f1_pos",
        "roc_auc",
        "pred_error_rate",
        "pos_rate_eval",
        "label_pos_rate_eval",
        "pred_pos_rate_eval",
        "integrity_jsd",
        "integrity_mmd",
        "integrity_ks_mean",
        "integrity_ks_reject05",
        "integrity_score_jsd",
        "integrity_jsd_vs_clean_eval",
        "integrity_mmd_vs_clean_eval",
        "integrity_ks_mean_vs_clean_eval",
        "integrity_ks_reject05_vs_clean_eval",
        "integrity_score_jsd_vs_clean_eval",
        "integrity_label_prior_shift",
        "integrity_label_jsd",
        "integrity_pred_pos_rate_shift",
        "integrity_pred_disagreement",
        "integrity_pred_jsd",
        "integrity_confusion_profile_l1",
        "integrity_confusion_profile_jsd",
    ]
    for m in drop_metric_cols:
        clean_m = f"clean_{m}"
        drop_m = f"{m}_drop"
        if m in out.columns and clean_m in out.columns:
            cur = pd.to_numeric(out[m], errors="coerce")
            ref = pd.to_numeric(out[clean_m], errors="coerce")
            calc = cur - ref

            if drop_m not in out.columns:
                out[drop_m] = calc
            else:
                existing = pd.to_numeric(out[drop_m], errors="coerce")
                out[drop_m] = existing.where(existing.notna(), calc)

    # Compute missing impact_* if absent
    if "bal_acc_drop" in out.columns:
        calc = _safe_positive_harm_from_drop(out["bal_acc_drop"])
        if "impact_bal_acc" not in out.columns:
            out["impact_bal_acc"] = calc
        else:
            ex = pd.to_numeric(out["impact_bal_acc"], errors="coerce")
            out["impact_bal_acc"] = ex.where(ex.notna(), calc)

    if "f1_pos_drop" in out.columns:
        calc = _safe_positive_harm_from_drop(out["f1_pos_drop"])
        if "impact_f1" not in out.columns:
            out["impact_f1"] = calc
        else:
            ex = pd.to_numeric(out["impact_f1"], errors="coerce")
            out["impact_f1"] = ex.where(ex.notna(), calc)

    if "roc_auc_drop" in out.columns:
        calc = _safe_positive_harm_from_drop(out["roc_auc_drop"])
        if "impact_roc_auc" not in out.columns:
            out["impact_roc_auc"] = calc
        else:
            ex = pd.to_numeric(out["impact_roc_auc"], errors="coerce")
            out["impact_roc_auc"] = ex.where(ex.notna(), calc)

    if "pred_error_rate_drop" in out.columns:
        calc = _safe_positive_harm_error_from_drop(out["pred_error_rate_drop"])
        if "impact_pred_error" not in out.columns:
            out["impact_pred_error"] = calc
        else:
            ex = pd.to_numeric(out["impact_pred_error"], errors="coerce")
            out["impact_pred_error"] = ex.where(ex.notna(), calc)

    # Cleanup joined columns
    out = out.drop(columns=[c for c in out.columns if c.startswith("joined_clean_")], errors="ignore")

    return out


# ----------------------------
# De-duplication
# ----------------------------
def dedupe_runs(df: pd.DataFrame, prefer_run_id: bool = True) -> pd.DataFrame:
    """
    De-duplicate with dataset-aware scope.

    IMPORTANT:
    We must include protocol + dataset_tag when using run_id-based de-duplication.
    Otherwise, identical logical run_ids across different datasets / OOD pairs
    can incorrectly collapse into a single row.
    """
    if prefer_run_id and "run_id" in df.columns:
        subset = [c for c in ["protocol", "dataset_tag", "run_id", "attack_seed"] if c in df.columns]
        before = int(len(df))
        df2 = df.drop_duplicates(subset=subset, keep="last").copy()
        after = int(len(df2))
        if after != before:
            print(f"[INFO] De-duplicated by {subset}: {before} -> {after}")
        return df2

    key: List[str] = []
    for c in [
        "protocol",
        "dataset_tag",
        "split_seed",
        "model_seed",
        "svd_dim",
        "model_family",
        "model",
        "scale",
        "attack_suite",
        "attack_priority_group",
        "attack",
        "attack_seed",
    ]:
        if c in df.columns:
            key.append(c)

    before = int(len(df))
    df2 = df.drop_duplicates(subset=key, keep="last").copy()
    after = int(len(df2))
    if after != before:
        print(f"[INFO] De-duplicated by composite key: {before} -> {after}")
    return df2


# ----------------------------
# Aggregation
# ----------------------------
def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    _ensure_numeric_round(out, ["attack_strength_nominal", "attack_strength_eff"], ndigits=12)

    group_cols = [
        "protocol",
        "dataset_tag",
        "svd_dim",
        "model_family",
        "model",
        "scale",
    ]
    optional_group_cols = [
        "attack_suite",
        "attack_priority_group",
    ]
    for c in optional_group_cols:
        if c in out.columns:
            group_cols.append(c)

    group_cols += [
        "attack_family",
        "attack_strength_nominal",
        "attack",
    ]

    for c in group_cols:
        if c not in out.columns:
            raise SystemExit(f"[ERROR] Missing grouping column: {c}")

    metrics = [
        # current performance
        "bal_acc",
        "f1_pos",
        "roc_auc",
        "pred_error_rate",
        "pos_rate_eval",
        "label_pos_rate_eval",
        "pred_pos_rate_eval",
        # clean references
        "clean_bal_acc",
        "clean_f1_pos",
        "clean_roc_auc",
        "clean_pred_error_rate",
        "clean_pos_rate_eval",
        "clean_label_pos_rate_eval",
        "clean_pred_pos_rate_eval",
        # bookkeeping
        "label_flip_rate",
        "attack_strength_eff",
        # impact
        "impact_bal_acc",
        "impact_f1",
        "impact_roc_auc",
        "impact_pred_error",
        # signals
        "integrity_jsd",
        "integrity_mmd",
        "integrity_ks_mean",
        "integrity_ks_reject05",
        "integrity_score_jsd",
        "integrity_jsd_delta",
        "integrity_mmd_delta",
        "integrity_ks_mean_delta",
        "integrity_ks_reject05_delta",
        "integrity_score_jsd_delta",
        # richer / future signals
        "integrity_jsd_vs_clean_eval",
        "integrity_mmd_vs_clean_eval",
        "integrity_ks_mean_vs_clean_eval",
        "integrity_ks_reject05_vs_clean_eval",
        "integrity_score_jsd_vs_clean_eval",
        "integrity_label_prior_shift",
        "integrity_label_jsd",
        "integrity_pred_pos_rate_shift",
        "integrity_pred_disagreement",
        "integrity_pred_jsd",
        "integrity_confusion_profile_l1",
        "integrity_confusion_profile_jsd",
        "integrity_confusion_profile_l1_delta",
        "integrity_confusion_profile_jsd_delta",
        # drops vs clean
        "bal_acc_drop",
        "f1_pos_drop",
        "roc_auc_drop",
        "pred_error_rate_drop",
        "pos_rate_eval_drop",
        "label_pos_rate_eval_drop",
        "pred_pos_rate_eval_drop",
        "integrity_jsd_drop",
        "integrity_mmd_drop",
        "integrity_ks_mean_drop",
        "integrity_ks_reject05_drop",
        "integrity_score_jsd_drop",
        "integrity_jsd_vs_clean_eval_drop",
        "integrity_mmd_vs_clean_eval_drop",
        "integrity_ks_mean_vs_clean_eval_drop",
        "integrity_ks_reject05_vs_clean_eval_drop",
        "integrity_score_jsd_vs_clean_eval_drop",
        "integrity_label_prior_shift_drop",
        "integrity_label_jsd_drop",
        "integrity_pred_pos_rate_shift_drop",
        "integrity_pred_disagreement_drop",
        "integrity_pred_jsd_drop",
        "integrity_confusion_profile_l1_drop",
        "integrity_confusion_profile_jsd_drop",
        # costs
        "signals_time_s",
        "attack_prep_time_s",
        "train_time_s",
        "predict_time_s",
        "scores_time_s",
        "ref_scores_time_s",
        "ref_predict_time_s",
    ]
    metrics = [m for m in metrics if m in out.columns]

    g = out.groupby(group_cols, dropna=False)
    out_rows: List[Dict[str, object]] = []

    for key, sub in g:
        row: Dict[str, object] = {c: v for c, v in zip(group_cols, key)}
        row["n_runs"] = int(len(sub))

        seed_unit_cols = [c for c in ["split_seed", "model_seed"] if c in sub.columns]
        if seed_unit_cols:
            row["n_seed_units"] = int(sub[seed_unit_cols].drop_duplicates().shape[0])
        else:
            row["n_seed_units"] = int(sub["seed"].nunique()) if "seed" in sub.columns else int(len(sub))

        row["is_clean_any"] = bool(sub["is_clean"].any())
        row["is_clean_all"] = bool(sub["is_clean"].all())
        row["is_clean_mixed"] = bool(row["is_clean_any"] and (not row["is_clean_all"]))

        for m in metrics:
            s = pd.to_numeric(sub[m], errors="coerce").astype(float)
            row[f"{m}_mean"] = _safe_mean(s)
            row[f"{m}_std"] = _safe_std(s)
            row[f"{m}_min"] = _safe_min(s)
            row[f"{m}_max"] = _safe_max(s)
            row[f"{m}_n"] = _safe_count_notna(s)

        out_rows.append(row)

    agg = pd.DataFrame(out_rows)

    agg["__sort_clean"] = agg["attack"].astype(str).str.strip().str.lower().eq("clean").astype(int)
    sort_cols = [
        "protocol",
        "dataset_tag",
        "model_family",
        "model",
        "scale",
        "svd_dim",
    ]
    for c in ["attack_suite", "attack_priority_group"]:
        if c in agg.columns:
            sort_cols.append(c)
    sort_cols += [
        "__sort_clean",
        "attack_family",
        "attack_strength_nominal",
        "attack",
    ]
    sort_cols = [c for c in sort_cols if c in agg.columns]

    asc = [True] * len(sort_cols)
    if "__sort_clean" in sort_cols:
        asc[sort_cols.index("__sort_clean")] = False

    agg = agg.sort_values(sort_cols, ascending=asc).reset_index(drop=True)
    return agg.drop(columns=["__sort_clean"], errors="ignore")


# ----------------------------
# Auditability scoring
# ----------------------------
def _robust_minmax(
    s: pd.Series,
    *,
    q_lo: float = 0.05,
    q_hi: float = 0.95,
) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    out = pd.Series(np.nan, index=x.index, dtype=float)

    valid = x[np.isfinite(x)]
    if valid.size < 2:
        return out

    lo = float(valid.quantile(q_lo))
    hi = float(valid.quantile(q_hi))
    if not np.isfinite(lo) or not np.isfinite(hi):
        return out

    if hi <= lo:
        const_val = float(valid.iloc[0])
        fill = 0.0 if abs(const_val) < 1e-12 else 1.0
        out.loc[valid.index] = fill
        return out

    clipped = x.clip(lower=lo, upper=hi)
    out = (clipped - lo) / (hi - lo)
    return out.clip(lower=0.0, upper=1.0)


def add_auditability_scores(
    agg: pd.DataFrame,
    *,
    norm_group_cols: Optional[List[str]] = None,
    q_lo: float = 0.05,
    q_hi: float = 0.95,
) -> pd.DataFrame:
    out = agg.copy()
    attacked_mask = _as_attacked_mask(out)
    clean_mask = ~attacked_mask
    attacked_idx = out.index[attacked_mask]

    # Impact:
    # prefer direct impact_* means from richer runner;
    # fallback to deriving from drops when impact columns are absent.
    if "impact_bal_acc_mean" not in out.columns:
        if "impact_bal_acc_mean" in out.columns:
            pass
    # The aggregate step already produces *_mean for any present metric.
    impact_direct = _first_existing(out, ["impact_bal_acc_mean"])
    if impact_direct is not None:
        out["impact_bal_acc_mean"] = pd.to_numeric(out[impact_direct], errors="coerce")
        impact_source = "direct_runner_impact_bal_acc"
    elif "bal_acc_drop_mean" in out.columns:
        out["impact_bal_acc_mean"] = (-pd.to_numeric(out["bal_acc_drop_mean"], errors="coerce")).clip(lower=0.0)
        impact_source = "derived_from_bal_acc_drop_mean"
    else:
        out["impact_bal_acc_mean"] = np.nan
        impact_source = "missing"

    impact_f1_direct = _first_existing(out, ["impact_f1_mean"])
    if impact_f1_direct is not None:
        out["impact_f1_mean"] = pd.to_numeric(out[impact_f1_direct], errors="coerce")
    elif "f1_pos_drop_mean" in out.columns:
        out["impact_f1_mean"] = (-pd.to_numeric(out["f1_pos_drop_mean"], errors="coerce")).clip(lower=0.0)
    else:
        out["impact_f1_mean"] = np.nan

    impact_roc_direct = _first_existing(out, ["impact_roc_auc_mean"])
    if impact_roc_direct is not None:
        out["impact_roc_auc_mean"] = pd.to_numeric(out[impact_roc_direct], errors="coerce")
    elif "roc_auc_drop_mean" in out.columns:
        out["impact_roc_auc_mean"] = (-pd.to_numeric(out["roc_auc_drop_mean"], errors="coerce")).clip(lower=0.0)
    else:
        out["impact_roc_auc_mean"] = np.nan

    impact_err_direct = _first_existing(out, ["impact_pred_error_mean"])
    if impact_err_direct is not None:
        out["impact_pred_error_mean"] = pd.to_numeric(out[impact_err_direct], errors="coerce")
    elif "pred_error_rate_drop_mean" in out.columns:
        out["impact_pred_error_mean"] = pd.to_numeric(out["pred_error_rate_drop_mean"], errors="coerce").clip(lower=0.0)
    else:
        out["impact_pred_error_mean"] = np.nan

    out["impact_source"] = impact_source

    # Preferred detectability signals:
    # prefer attack-vs-clean-eval + label-aware + prediction-aware + confusion-profile.
    preferred_signal_pairs = [
        ("integrity_jsd_vs_clean_eval_mean", "integrity_jsd_mean"),
        ("integrity_mmd_vs_clean_eval_mean", "integrity_mmd_mean"),
        ("integrity_ks_reject05_vs_clean_eval_mean", "integrity_ks_reject05_mean"),
        ("integrity_score_jsd_vs_clean_eval_mean", "integrity_score_jsd_mean"),
        ("integrity_label_prior_shift_mean", None),
        ("integrity_label_jsd_mean", None),
        ("integrity_pred_pos_rate_shift_mean", None),
        ("integrity_pred_disagreement_mean", None),
        ("integrity_pred_jsd_mean", None),
        ("integrity_confusion_profile_l1_mean", None),
        ("integrity_confusion_profile_jsd_mean", None),
    ]

    signal_cols: List[str] = []
    signal_sources: List[str] = []
    for preferred, fallback in preferred_signal_pairs:
        if preferred in out.columns:
            signal_cols.append(preferred)
            signal_sources.append(f"{preferred}=preferred")
        elif fallback is not None and fallback in out.columns:
            signal_cols.append(fallback)
            signal_sources.append(f"{fallback}=fallback_for:{preferred}")

    if norm_group_cols is None:
        norm_group_cols = [c for c in ["protocol", "dataset_tag", "model", "svd_dim"] if c in out.columns]
    else:
        norm_group_cols = [c for c in norm_group_cols if c in out.columns]

    norm_cols: List[str] = []
    if signal_cols:
        if norm_group_cols:
            attacked_sub = out.loc[attacked_idx, norm_group_cols + signal_cols].copy()
            group_map = attacked_sub.groupby(norm_group_cols, dropna=False).groups

            for sig in signal_cols:
                new_col = f"{sig}__norm"
                out[new_col] = np.nan
                for _, idx in group_map.items():
                    idx = list(idx)
                    out.loc[idx, new_col] = _robust_minmax(out.loc[idx, sig], q_lo=q_lo, q_hi=q_hi)
                norm_cols.append(new_col)
        else:
            for sig in signal_cols:
                new_col = f"{sig}__norm"
                out[new_col] = np.nan
                out.loc[attacked_idx, new_col] = _robust_minmax(out.loc[attacked_idx, sig], q_lo=q_lo, q_hi=q_hi)
                norm_cols.append(new_col)

    # Transparency / provenance
    out["detectability_signal_cols_used"] = ",".join(signal_cols) if signal_cols else ""
    out["detectability_signal_sources"] = ";".join(signal_sources) if signal_sources else ""
    out["detectability_signal_count"] = int(len(signal_cols))
    out["detectability_norm_group_cols"] = ",".join(norm_group_cols) if norm_group_cols else ""
    out["detectability_norm_q_lo"] = float(q_lo)
    out["detectability_norm_q_hi"] = float(q_hi)

    if signal_cols:
        raw_matrix = out[signal_cols].apply(pd.to_numeric, errors="coerce")
        out["detectability_raw_mean"] = raw_matrix.mean(axis=1, skipna=True)
        out["detectability_raw_std"] = raw_matrix.std(axis=1, skipna=True)
    else:
        out["detectability_raw_mean"] = np.nan
        out["detectability_raw_std"] = np.nan

    if norm_cols:
        norm_matrix = out[norm_cols].apply(pd.to_numeric, errors="coerce")
        out["detectability_components_n"] = norm_matrix.notna().sum(axis=1).astype(int)
        out["detectability_score_mean"] = norm_matrix.mean(axis=1, skipna=True)
        out["detectability_score_std"] = norm_matrix.std(axis=1, skipna=True)
        out["detectability_score_min"] = norm_matrix.min(axis=1, skipna=True)
        out["detectability_score_max"] = norm_matrix.max(axis=1, skipna=True)
    else:
        out["detectability_components_n"] = 0
        out["detectability_score_mean"] = np.nan
        out["detectability_score_std"] = np.nan
        out["detectability_score_min"] = np.nan
        out["detectability_score_max"] = np.nan

    # Clean rows
    out.loc[clean_mask, "impact_bal_acc_mean"] = 0.0
    out.loc[clean_mask, "impact_f1_mean"] = 0.0
    out.loc[clean_mask, "impact_roc_auc_mean"] = 0.0
    out.loc[clean_mask, "impact_pred_error_mean"] = 0.0
    out.loc[clean_mask, "detectability_score_mean"] = 0.0
    out.loc[clean_mask, "detectability_score_std"] = 0.0
    out.loc[clean_mask, "detectability_score_min"] = 0.0
    out.loc[clean_mask, "detectability_score_max"] = 0.0
    out.loc[clean_mask, "detectability_components_n"] = 0

    # Availability / missingness
    det_score = pd.to_numeric(out["detectability_score_mean"], errors="coerce")
    out["detectability_available"] = ((attacked_mask & det_score.notna()) | clean_mask).astype(bool)
    out["detectability_missing"] = (attacked_mask & det_score.isna()).astype(bool)

    # Stealth:
    # keep detectability_score_mean as-is (NaN if unsupported),
    # but for stealth ranking treat missing detectability as 0 evidence.
    det_for_stealth = det_score.fillna(0.0).clip(lower=0.0, upper=1.0)
    out["detectability_score_for_stealth"] = det_for_stealth

    out["stealth_score_mean"] = pd.to_numeric(out["impact_bal_acc_mean"], errors="coerce") * (1.0 - det_for_stealth)
    out.loc[clean_mask, "stealth_score_mean"] = 0.0

    out["stealth_missing_detectability_assumed_zero"] = (
        attacked_mask & pd.to_numeric(out["detectability_score_mean"], errors="coerce").isna()
    ).astype(bool)

    out["stealth_rank_overall"] = np.nan
    out["stealth_rank_within_model"] = np.nan
    out["stealth_rank_within_protocol_dataset"] = np.nan
    out["stealth_rank_within_protocol_dataset_model"] = np.nan

    if len(attacked_idx) > 0:
        out.loc[attacked_idx, "stealth_rank_overall"] = (
            out.loc[attacked_idx, "stealth_score_mean"].rank(method="dense", ascending=False)
        )

        if "model" in out.columns:
            out.loc[attacked_idx, "stealth_rank_within_model"] = (
                out.loc[attacked_idx]
                .groupby("model", dropna=False)["stealth_score_mean"]
                .rank(method="dense", ascending=False)
            )

        rank_group = [c for c in ["protocol", "dataset_tag"] if c in out.columns]
        if rank_group:
            out.loc[attacked_idx, "stealth_rank_within_protocol_dataset"] = (
                out.loc[attacked_idx]
                .groupby(rank_group, dropna=False)["stealth_score_mean"]
                .rank(method="dense", ascending=False)
            )

        rank_group_model = [c for c in ["protocol", "dataset_tag", "model"] if c in out.columns]
        if rank_group_model:
            out.loc[attacked_idx, "stealth_rank_within_protocol_dataset_model"] = (
                out.loc[attacked_idx]
                .groupby(rank_group_model, dropna=False)["stealth_score_mean"]
                .rank(method="dense", ascending=False)
            )

    return out


# ----------------------------
# Convenience exports
# ----------------------------
def export_companion_tables(agg: pd.DataFrame, out_path: Path, quiet: bool = False) -> None:
    outdir = out_path.parent
    stem = out_path.stem

    attacked = agg[_as_attacked_mask(agg)].copy()
    clean = agg[~_as_attacked_mask(agg)].copy()

    # Numeric helper cols for weighted availability summaries
    if not attacked.empty:
        if "detectability_available" in attacked.columns:
            attacked["detectability_available_num"] = attacked["detectability_available"].astype(float)
        if "detectability_missing" in attacked.columns:
            attacked["detectability_missing_num"] = attacked["detectability_missing"].astype(float)
        if "stealth_missing_detectability_assumed_zero" in attacked.columns:
            attacked["stealth_missing_detectability_assumed_zero_num"] = (
                attacked["stealth_missing_detectability_assumed_zero"].astype(float)
            )

    written: List[Path] = []

    # 1) Clean summary by model/dim
    if not clean.empty:
        group_cols = [c for c in ["protocol", "dataset_tag", "model_family", "model", "svd_dim"] if c in clean.columns]
        metrics = [
            c for c in [
                "bal_acc_mean",
                "roc_auc_mean",
                "f1_pos_mean",
                "pred_error_rate_mean",
                "train_time_s_mean",
                "ref_scores_time_s_mean",
                "ref_predict_time_s_mean",
                "n_seed_units",
            ]
            if c in clean.columns
        ]
        if group_cols and metrics:
            clean_summary = clean[group_cols + metrics].copy()
            clean_summary = clean_summary.sort_values(
                [c for c in ["protocol", "dataset_tag", "model", "svd_dim"] if c in clean_summary.columns],
                ascending=True,
                na_position="last",
            )
            p = outdir / f"{stem}__clean_by_model_dim.csv"
            clean_summary.to_csv(p, index=False)
            written.append(p)

    # 2) Attacked summary by model/dim/family/severity
    if not attacked.empty:
        group_cols = [c for c in ["protocol", "dataset_tag", "model_family", "model", "svd_dim", "attack_family", "attack_strength_nominal"] if c in attacked.columns]
        if "attack_priority_group" in attacked.columns:
            group_cols.append("attack_priority_group")

        metrics = [
            c for c in [
                "bal_acc_drop_mean",
                "roc_auc_drop_mean",
                "f1_pos_drop_mean",
                "impact_bal_acc_mean",
                "detectability_score_mean",
                "stealth_score_mean",
                "n_seed_units",
            ]
            if c in attacked.columns
        ]
        if group_cols and metrics:
            attacked_summary = _group_weighted_means(
                attacked,
                group_cols=group_cols,
                metrics=[m for m in metrics if m != "n_seed_units"],
                weight_col="n_seed_units",
            )
            attacked_summary = attacked_summary.sort_values(
                [c for c in ["protocol", "dataset_tag", "model", "svd_dim", "attack_family", "attack_strength_nominal"] if c in attacked_summary.columns],
                ascending=True,
                na_position="last",
            )
            p = outdir / f"{stem}__attacked_by_model_dim_family_severity.csv"
            attacked_summary.to_csv(p, index=False)
            written.append(p)

    # 3) Top stealth overall
    if not attacked.empty:
        overall_cols = [
            c for c in [
                "protocol",
                "dataset_tag",
                "svd_dim",
                "model_family",
                "model",
                "scale",
                "attack_suite",
                "attack_priority_group",
                "attack_family",
                "attack_strength_nominal",
                "attack",
                "bal_acc_drop_mean",
                "roc_auc_drop_mean",
                "f1_pos_drop_mean",
                "impact_bal_acc_mean",
                "detectability_score_mean",
                "detectability_score_std",
                "detectability_components_n",
                "detectability_signal_cols_used",
                "detectability_signal_sources",
                "detectability_available",
                "detectability_missing",
                "detectability_score_for_stealth",
                "stealth_missing_detectability_assumed_zero",
                "stealth_score_mean",
                "stealth_rank_overall",
                "n_seed_units",
            ]
            if c in attacked.columns
        ]

        top_overall = attacked.sort_values(
            ["stealth_score_mean", "impact_bal_acc_mean"],
            ascending=[False, False],
            na_position="last",
        )[overall_cols]
        p = outdir / f"{stem}__top_stealth_overall.csv"
        top_overall.to_csv(p, index=False)
        written.append(p)

    # 4) Stealth by model
    if not attacked.empty and "model" in attacked.columns:
        group_cols = [c for c in ["protocol", "dataset_tag", "model_family", "model", "svd_dim"] if c in attacked.columns]
        metrics = [
            c for c in [
                "impact_bal_acc_mean",
                "detectability_score_mean",
                "stealth_score_mean",
                "detectability_available_num",
                "detectability_missing_num",
                "stealth_missing_detectability_assumed_zero_num",
            ]
            if c in attacked.columns
        ]
        if group_cols and metrics:
            by_model = _group_weighted_means(
                attacked,
                group_cols=group_cols,
                metrics=metrics,
                weight_col="n_seed_units",
            ).rename(
                columns={
                    "detectability_available_num": "detectability_available_rate",
                    "detectability_missing_num": "detectability_missing_rate",
                    "stealth_missing_detectability_assumed_zero_num": "stealth_missing_detectability_assumed_zero_rate",
                }
            )

            sort_cols = [c for c in ["protocol", "dataset_tag", "model", "svd_dim"] if c in by_model.columns] + ["stealth_score_mean"]
            ascending = [True] * (len(sort_cols) - 1) + [False]
            by_model = by_model.sort_values(sort_cols, ascending=ascending, na_position="last")
            p = outdir / f"{stem}__stealth_by_model.csv"
            by_model.to_csv(p, index=False)
            written.append(p)

    # 5) Stealth by attack family
    if not attacked.empty and "attack_family" in attacked.columns:
        group_cols = [c for c in ["protocol", "dataset_tag", "attack_family"] if c in attacked.columns]
        if "attack_priority_group" in attacked.columns:
            group_cols.append("attack_priority_group")

        metrics = [
            c for c in [
                "impact_bal_acc_mean",
                "detectability_score_mean",
                "stealth_score_mean",
                "detectability_available_num",
                "detectability_missing_num",
                "stealth_missing_detectability_assumed_zero_num",
            ]
            if c in attacked.columns
        ]
        if group_cols and metrics:
            by_family = _group_weighted_means(
                attacked,
                group_cols=group_cols,
                metrics=metrics,
                weight_col="n_seed_units",
            ).rename(
                columns={
                    "detectability_available_num": "detectability_available_rate",
                    "detectability_missing_num": "detectability_missing_rate",
                    "stealth_missing_detectability_assumed_zero_num": "stealth_missing_detectability_assumed_zero_rate",
                }
            )

            sort_cols = [c for c in ["protocol", "dataset_tag"] if c in by_family.columns] + ["stealth_score_mean"]
            ascending = [True] * (len(sort_cols) - 1) + [False]
            by_family = by_family.sort_values(sort_cols, ascending=ascending, na_position="last")
            p = outdir / f"{stem}__stealth_by_attack_family.csv"
            by_family.to_csv(p, index=False)
            written.append(p)

    if not quiet:
        for p in written:
            print(f"[OK] Wrote {p}")


# ----------------------------
# CLI
# ----------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", type=str, required=True, help="Directory containing run__*.csv files.")
    ap.add_argument("--pattern", type=str, default="run__*.csv", help="Glob pattern for run files.")
    ap.add_argument("--recursive", action="store_true", help="Search recursively under raw-dir.")
    ap.add_argument("--out", type=str, required=True, help="Output aggregated CSV path.")
    ap.add_argument("--no-dedupe", action="store_true", help="Disable de-duplication (not recommended).")
    ap.add_argument("--no-auditability", action="store_true", help="Disable auditability score derivation.")
    ap.add_argument("--no-companions", action="store_true", help="Do not write companion ranking tables.")
    ap.add_argument(
        "--norm-group-cols",
        type=str,
        default="protocol,dataset_tag,model,svd_dim",
        help="Comma-separated grouping columns for detectability normalization.",
    )
    ap.add_argument("--norm-q-lo", type=float, default=0.05, help="Lower quantile for robust min-max normalization.")
    ap.add_argument("--norm-q-hi", type=float, default=0.95, help="Upper quantile for robust min-max normalization.")
    ap.add_argument("--quiet", action="store_true", help="Reduce logging.")
    args = ap.parse_args()

    raw_dir = Path(args.raw_dir)
    if not raw_dir.exists():
        raise SystemExit(f"[ERROR] raw-dir not found: {raw_dir}")

    if not (0.0 <= float(args.norm_q_lo) < float(args.norm_q_hi) <= 1.0):
        raise SystemExit("[ERROR] Need 0 <= --norm-q-lo < --norm-q-hi <= 1.")

    run_files = _find_run_files(raw_dir, recursive=bool(args.recursive), pattern=str(args.pattern))
    if not args.quiet:
        print(
            f"[INFO] Found {len(run_files)} run files under {raw_dir} "
            f"(pattern={args.pattern}, recursive={args.recursive})"
        )

    df = load_runs(run_files, verbose=not bool(args.quiet))

    if not bool(args.no_dedupe):
        df = dedupe_runs(df, prefer_run_id=True)

    df = attach_clean_baselines(df)
    agg = aggregate(df)

    if not bool(args.no_auditability):
        norm_group_cols = _parse_csv_list(str(args.norm_group_cols))
        norm_group_cols = [c for c in norm_group_cols if c in agg.columns]
        agg = add_auditability_scores(
            agg,
            norm_group_cols=norm_group_cols,
            q_lo=float(args.norm_q_lo),
            q_hi=float(args.norm_q_hi),
        )

    out_path = Path(args.out)
    ensure_dir(out_path.parent)
    agg.to_csv(out_path, index=False)

    if not bool(args.no_companions):
        export_companion_tables(agg, out_path, quiet=bool(args.quiet))

    if not args.quiet:
        print(f"[OK] Wrote {out_path}")
        print(f"[INFO] Aggregated rows: {len(agg)}")
        with pd.option_context("display.max_columns", 400, "display.width", 240):
            print(agg.head(10))
        if "is_clean_mixed" in agg.columns:
            n_mixed = int(agg["is_clean_mixed"].sum())
            if n_mixed:
                print(
                    f"[WARN] Found {n_mixed} aggregated groups with mixed clean/attacked rows. "
                    f"Check grouping keys / runner output."
                )


if __name__ == "__main__":
    main()