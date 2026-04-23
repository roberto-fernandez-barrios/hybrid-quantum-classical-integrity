# DONE
# src/experiments/aggregate_results.py
#
# Aggregates multiple run__*.csv files produced by src/experiments/run_benchmark.py
# into a single paper-friendly table.
#
# Works with the CURRENT runner in this chat:
#   - attack_is_clean semantics: CLEAN=1, ATTACKED=0
#   - clean_ref_run_id + clean_ref_attack_seed columns exist (used for joins)
#   - protocol is "id" or "ood"
#   - dataset hashes are in filename tags (e.g., __idXXXXXXXX or __trXXXXXXXX__teXXXXXXXX),
#     but NOT necessarily in CSV columns -> we parse them from filename for safety.
#
# Key design choices:
#   - Clean baseline is joined using (clean_ref_run_id, clean_ref_attack_seed).
#     This is robust even if you change naming conventions.
#   - Aggregation groups by a stable attack key:
#       (protocol, dataset_tag, svd_dim, model_family, model, scale,
#        attack_family, attack_strength_nominal, attack)
#     so plots/tables are deterministic even if effective strength varies by seed.
#   - Includes both nominal + effective strength stats, plus drops vs clean.
#   - De-duplicates by (run_id, attack_seed) (preferred) or a fallback composite key.
#
# Usage examples:
#   python -m src.experiments.aggregate_results --raw-dir results/raw/hais_cicids_runs --out results/tables/agg.csv
#   python -m src.experiments.aggregate_results --raw-dir results/raw/hais_cicids_runs --pattern "run__*.csv" --recursive
#
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

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


def _find_run_files(raw_dir: Path, recursive: bool, pattern: str) -> List[Path]:
    return sorted(raw_dir.rglob(pattern)) if recursive else sorted(raw_dir.glob(pattern))


def _require_cols(df: pd.DataFrame, cols: Sequence[str], ctx: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise SystemExit(f"[ERROR] Missing required columns in {ctx}: {missing}")


def _detect_is_clean(df: pd.DataFrame) -> pd.Series:
    """
    Runner policy (CURRENT):
      attack_is_clean = 1 for clean, 0 for attacked

    Fallback:
      attack == "clean" (case-insensitive) if attack_is_clean is missing.
    """
    attack_name_clean = df["attack"].astype(str).str.lower().eq("clean")

    if "attack_is_clean" not in df.columns:
        return attack_name_clean.astype(bool)

    ais = pd.to_numeric(df["attack_is_clean"], errors="coerce").astype("Int64")
    col_clean = ais.eq(1)

    mask = ais.notna()
    conflicts = (attack_name_clean != col_clean) & mask
    if conflicts.any():
        n = int(conflicts.sum())
        print(
            f"[WARN] Detected {n} rows where attack_is_clean (1=clean) disagrees with attack=='clean'. "
            f"Using attack_is_clean as primary."
        )

    return col_clean.where(mask, attack_name_clean).fillna(attack_name_clean).astype(bool)


_ID_RE = re.compile(r"__id([0-9a-fA-F]{8})")
_OOD_RE = re.compile(r"__tr([0-9a-fA-F]{8})__te([0-9a-fA-F]{8})")


def _dataset_tag_from_path(csv_path: Path, protocol: str) -> str:
    """
    In run_benchmark.py you tag filenames with:
      - ID:  __id<8hex>
      - OOD: __tr<8hex>__te<8hex>

    We parse that, because the CSV may not include hashes.
    """
    name = csv_path.name
    if protocol == "ood":
        m = _OOD_RE.search(name)
        if m:
            return f"tr{m.group(1).lower()}__te{m.group(2).lower()}"
        return "trNA__teNA"
    m = _ID_RE.search(name)
    if m:
        return f"id{m.group(1).lower()}"
    return "idNA"


def _safe_std(s: pd.Series) -> float:
    # pandas std defaults to ddof=1; keep it (paper-friendly).
    return float(s.std(skipna=True))


def _safe_mean(s: pd.Series) -> float:
    return float(s.mean(skipna=True))


def _maybe(df: pd.DataFrame, col: str) -> Optional[pd.Series]:
    return df[col] if col in df.columns else None


# ----------------------------
# Loading + normalization
# ----------------------------
def load_runs(
    run_files: List[Path],
    verbose: bool = True,
) -> pd.DataFrame:
    if not run_files:
        raise SystemExit("[ERROR] No run files found.")

    dfs: List[pd.DataFrame] = []
    for p in run_files:
        df = pd.read_csv(p)
        df["__source_file"] = str(p)
        dfs.append(df)

    out = pd.concat(dfs, axis=0, ignore_index=True)

    # Required core columns from runner
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

    # Types
    _to_int(out, ["svd_dim", "seed", "split_seed", "model_seed", "attack_seed", "clean_ref_attack_seed"])
    _to_float(
        out,
        [
            # legacy / optional numeric fields
            "attack_strength",
            "attack_strength_nominal",
            "attack_strength_eff",
            "bal_acc",
            "f1_pos",
            "roc_auc",
            "pos_rate_eval",
            "label_flip_rate",
            "pred_error_rate",
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
            "signals_time_s",
            "train_time_s",
            "attack_prep_time_s",
        ],
    )

    # Clean flag (semantics fixed)
    out["is_clean"] = _detect_is_clean(out)

    # Dataset tag (vectorized-ish): compute per unique source file + protocol, then map back
    # (avoids slow row-wise apply on large concatenations)
    src = out["__source_file"].astype(str)
    proto = out["protocol"].astype(str)

    unique_pairs = pd.DataFrame({"__source_file": src.unique()})
    # For each unique file, protocol is constant within file in your runner outputs;
    # but we still compute via mapping from any row matching that file:
    file_to_proto = out.drop_duplicates("__source_file")[["__source_file", "protocol"]].set_index("__source_file")[
        "protocol"
    ]
    unique_pairs["protocol"] = unique_pairs["__source_file"].map(file_to_proto).fillna("id").astype(str)

    def _compute_tag(row) -> str:
        return _dataset_tag_from_path(Path(row["__source_file"]), str(row["protocol"]))

    unique_pairs["dataset_tag"] = unique_pairs.apply(_compute_tag, axis=1)
    file_to_tag = unique_pairs.set_index("__source_file")["dataset_tag"].to_dict()
    out["dataset_tag"] = src.map(file_to_tag).fillna("idNA")

    # Guard: if protocol is ood, dataset_tag should be tr..te.. (warn only)
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
    Joins clean baseline metrics per row using runner-provided pointers:
      (clean_ref_run_id, clean_ref_attack_seed)

    Hardening:
      - Baseline lookup is built ONLY from clean rows.
      - Rename baseline key cols to avoid pandas merge duplicate columns (run_id/attack_seed).
      - Warn if baseline contains duplicated keys (shouldn't happen; indicates collisions / reruns).
    """
    # Base columns to attach from the clean row
    base_cols = [
        "bal_acc",
        "f1_pos",
        "roc_auc",
        "pred_error_rate",
        "pos_rate_eval",
        "integrity_jsd",
        "integrity_mmd",
        "integrity_ks_mean",
        "integrity_ks_reject05",
        "integrity_score_jsd",
        # time columns too, sometimes useful
        "signals_time_s",
        "attack_prep_time_s",
    ]
    base_cols = [c for c in base_cols if c in df.columns]

    # Build baseline table ONLY from clean rows
    baseline = df[df["is_clean"]][["run_id", "attack_seed"] + base_cols].copy()

    # Warn on duplicated baseline keys (should be 0 in normal operation)
    dup_mask = baseline.duplicated(subset=["run_id", "attack_seed"], keep=False)
    if dup_mask.any():
        n_dup = int(dup_mask.sum())
        n_keys = int(baseline[dup_mask][["run_id", "attack_seed"]].drop_duplicates().shape[0])
        print(
            f"[WARN] Baseline has {n_dup} rows across {n_keys} duplicated (run_id, attack_seed) keys. "
            f"Keeping the LAST occurrence per key for joining."
        )
        baseline = baseline.drop_duplicates(subset=["run_id", "attack_seed"], keep="last")

    # Rename baseline key cols to avoid duplicate columns after merge
    baseline = baseline.rename(
        columns={
            "run_id": "clean_key_run_id",
            "attack_seed": "clean_key_attack_seed",
            **{c: f"clean_{c}" for c in base_cols},
        }
    )

    merged = df.merge(
        baseline,
        how="left",
        left_on=["clean_ref_run_id", "clean_ref_attack_seed"],
        right_on=["clean_key_run_id", "clean_key_attack_seed"],
    )

    # Drop helper join keys from baseline side
    merged = merged.drop(columns=["clean_key_run_id", "clean_key_attack_seed"], errors="ignore")

    # Baseline coverage check
    miss = merged["clean_bal_acc"].isna() if "clean_bal_acc" in merged.columns else pd.Series(False, index=merged.index)
    n_miss = int(miss.sum())
    if n_miss:
        # This can happen if you aggregate across folders but didn't include the corresponding clean rows.
        print(
            f"[WARN] Missing clean baseline for {n_miss} rows. "
            f"Make sure you included the clean runs (same outdir / same cfg_fingerprint)."
        )

    # For clean rows, baseline == itself. If missing (shouldn't), enforce.
    if "clean_bal_acc" in merged.columns and "bal_acc" in merged.columns:
        idx = merged["is_clean"] & merged["clean_bal_acc"].isna()
        if idx.any():
            merged.loc[idx, "clean_bal_acc"] = merged.loc[idx, "bal_acc"]

    # Drops vs clean
    def _drop(col: str) -> None:
        c_clean = f"clean_{col}"
        c_drop = f"{col}_drop"
        if col in merged.columns and c_clean in merged.columns:
            merged[c_drop] = merged[col].astype(float) - merged[c_clean].astype(float)

    for m in ["bal_acc", "f1_pos", "roc_auc", "pred_error_rate"]:
        _drop(m)

    return merged


# ----------------------------
# De-duplication
# ----------------------------
def dedupe_runs(df: pd.DataFrame, prefer_run_id: bool = True) -> pd.DataFrame:
    """
    Prevent double-counting when you pass multiple folders / reruns.

    IMPORTANT hardening:
      - If run_id does NOT include attack_seed, deduping on run_id alone can drop distinct attacks.
      - We therefore dedupe on (run_id, attack_seed) when attack_seed exists.

    Fallback: composite key based on core config columns.
    """
    if prefer_run_id and "run_id" in df.columns:
        subset = ["run_id"]
        if "attack_seed" in df.columns:
            subset.append("attack_seed")

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
    """
    Produces a table with mean/std across seeds for each attack key + model key.
    """
    group_cols = [
        "protocol",
        "dataset_tag",
        "svd_dim",
        "model_family",
        "model",
        "scale",
        "attack_family",
        "attack_strength_nominal",
        "attack",
    ]
    for c in group_cols:
        if c not in df.columns:
            raise SystemExit(f"[ERROR] Missing grouping column: {c}")

    metrics = [
        "bal_acc",
        "f1_pos",
        "roc_auc",
        "pred_error_rate",
        "label_flip_rate",
        "integrity_jsd",
        "integrity_mmd",
        "integrity_ks_mean",
        "integrity_ks_reject05",
        "integrity_score_jsd",
        # drops
        "bal_acc_drop",
        "f1_pos_drop",
        "roc_auc_drop",
        "pred_error_rate_drop",
        # strength eff
        "attack_strength_eff",
        # costs
        "signals_time_s",
        "attack_prep_time_s",
        "train_time_s",
    ]
    metrics = [m for m in metrics if m in df.columns]

    g = df.groupby(group_cols, dropna=False)

    out_rows: List[Dict[str, object]] = []
    for key, sub in g:
        row: Dict[str, object] = {c: v for c, v in zip(group_cols, key)}
        row["n_runs"] = int(len(sub))

        # how many unique seed units
        seed_unit_cols = [c for c in ["split_seed", "model_seed"] if c in sub.columns]
        if seed_unit_cols:
            row["n_seed_units"] = int(sub[seed_unit_cols].drop_duplicates().shape[0])
        else:
            row["n_seed_units"] = int(sub["seed"].nunique()) if "seed" in sub.columns else int(len(sub))

        # clean flags (helps detect mixed/buggy grouping)
        row["is_clean_any"] = bool(sub["is_clean"].any())
        row["is_clean_all"] = bool(sub["is_clean"].all())
        row["is_clean_mixed"] = bool(row["is_clean_any"] and (not row["is_clean_all"]))

        # nominal strength is in key; keep eff stats too
        if "attack_strength_eff" in sub.columns:
            row["attack_strength_eff_mean"] = _safe_mean(sub["attack_strength_eff"])
            row["attack_strength_eff_std"] = _safe_std(sub["attack_strength_eff"])

        for m in metrics:
            if m == "attack_strength_eff":
                continue
            s = sub[m].astype(float)
            row[f"{m}_mean"] = _safe_mean(s)
            row[f"{m}_std"] = _safe_std(s)

        out_rows.append(row)

    out = pd.DataFrame(out_rows)

    # Nice sorting: protocol, model, then clean first, then by family+nominal
    out["__sort_clean"] = out["attack"].astype(str).str.lower().eq("clean").astype(int)

    sort_cols = [
        "protocol",
        "dataset_tag",
        "model_family",
        "model",
        "scale",
        "svd_dim",
        "__sort_clean",
        "attack_family",
        "attack_strength_nominal",
        "attack",
    ]
    sort_cols = [c for c in sort_cols if c in out.columns]
    asc = [True] * len(sort_cols)
    if "__sort_clean" in sort_cols:
        asc[sort_cols.index("__sort_clean")] = False  # clean first

    out = out.sort_values(sort_cols, ascending=asc).reset_index(drop=True)
    out = out.drop(columns=["__sort_clean"], errors="ignore")
    return out


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
    ap.add_argument("--quiet", action="store_true", help="Reduce logging.")
    args = ap.parse_args()

    raw_dir = Path(args.raw_dir)
    if not raw_dir.exists():
        raise SystemExit(f"[ERROR] raw-dir not found: {raw_dir}")

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

    out_path = Path(args.out)
    ensure_dir(out_path.parent)
    agg.to_csv(out_path, index=False)

    if not args.quiet:
        print(f"[OK] Wrote {out_path}")
        print(f"[INFO] Aggregated rows: {len(agg)}")

        # quick sanity: show first few
        with pd.option_context("display.max_columns", 200, "display.width", 140):
            print(agg.head(10))

        # optional sanity: detect mixed groups (should be 0)
        if "is_clean_mixed" in agg.columns:
            n_mixed = int(agg["is_clean_mixed"].sum())
            if n_mixed:
                print(
                    f"[WARN] Found {n_mixed} aggregated groups with mixed clean/attacked rows. "
                    f"Check grouping keys / runner output."
                )


if __name__ == "__main__":
    main()
