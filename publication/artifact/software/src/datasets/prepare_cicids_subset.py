# src/datasets/prepare_cicids_subset.py
#
# Prepare CICIDS CSV subset(s) for reproducible experiments.
#
# Supports:
#   1) ID (in-distribution) subsets:
#        - sample a balanced subset from a pool of CSV files
#        - optionally generate multiple subsets for multiple prep seeds in one call
#
#   2) OOD (out-of-distribution) split by files:
#        - build train and test subsets from *different* file groups (e.g., Monday* vs Tuesday*)
#        - useful for distribution shift that is not just random splitting
#
# Output:
#   - CSV with numeric features + label column "label" (0=benign, 1=attack)
#   - optional metadata column "_source_file" (kept as string, NOT coerced to numeric)
#   - JSON report with hashes + cleaning stats + files used + schema info (+ feature list)
#
# Notes:
#   - We do NOT scale here. Scaling happens in run_benchmark.
#   - We do NOT impute here. Imputation happens in cicids_subset/run_benchmark (fit on train only).
#   - In OOD mode we GUARANTEE a consistent feature schema between train/test (configurable).
#
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


# ----------------------------
# Utils
# ----------------------------
def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    return df


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _parse_int_list(s: str) -> List[int]:
    s = (s or "").strip()
    if not s:
        return []
    parts = [p.strip() for p in (s.split(",") if "," in s else s.split()) if p.strip()]
    return [int(p) for p in parts]


def _match_files(files: Sequence[Path], patterns: Sequence[str]) -> List[Path]:
    pats = [str(p).strip() for p in patterns if str(p).strip()]
    matched: List[Path] = []
    for f in files:
        for p in pats:
            if fnmatch.fnmatch(f.name, p):
                matched.append(f)
                break
    return matched


def _resolve_template(path_or_template: str, seed: int) -> Path:
    """
    Supports:
      --out-template "data/cicids_subset__prep{seed}.csv"
      --out "data/cicids_subset.csv" (legacy)
    """
    s = str(path_or_template)
    if "{seed}" in s:
        s = s.format(seed=int(seed))
    return Path(s)


def _stable_rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(int(seed))


def _dataset_id(payload: Dict[str, Any]) -> str:
    """
    Stable ID for dataset generation settings.
    Useful to link run_grid outputs to an exact prepared dataset config.
    """
    b = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha1(b).hexdigest()[:12]


# ----------------------------
# Config
# ----------------------------
@dataclass(frozen=True)
class PrepCfg:
    label_col: str
    n_total: int
    n_per_class: int
    seed: int
    drop_non_numeric: bool
    max_nan_frac: float
    keep_source_file: bool
    benign_token: str  # default "benign"


# Common CICIDS-style identifiers / timestamps / endpoints (leakage-ish)
_LEAKAGE_COLS = [
    "Flow_ID",
    "Timestamp",
    "Src_IP",
    "Dst_IP",
    "Src_Port",
    "Dst_Port",
    "Source_IP",
    "Destination_IP",
    "Source_Port",
    "Destination_Port",
    "FlowID",
]

# Meta columns we treat as "non-feature"
_META_COLS = {"_source_file"}

# Label columns we always exclude from features
_LABEL_COLS = {"label"}


# ----------------------------
# Loading / labels
# ----------------------------
def _load_concat_csv(files: Sequence[Path], keep_source_file: bool) -> Tuple[pd.DataFrame, Dict[str, str]]:
    if not files:
        raise RuntimeError("No CSV files provided to load.")

    dfs: List[pd.DataFrame] = []
    file_hashes: Dict[str, str] = {}

    for f in files:
        file_hashes[f.name] = _sha256_file(f)
        df = pd.read_csv(f, low_memory=False)
        df = _clean_columns(df)
        if keep_source_file:
            df["_source_file"] = f.name
        dfs.append(df)

    out = pd.concat(dfs, ignore_index=True)
    out = _clean_columns(out)
    return out, file_hashes


def _binarize_labels(df: pd.DataFrame, label_col: str, benign_token: str) -> Tuple[pd.Series, pd.Series]:
    """
    Returns:
      y_raw: original string-normalized labels
      y: binarized (0 benign, 1 attack)
    """
    if label_col not in df.columns:
        raise RuntimeError(f"Label column '{label_col}' not found. Available: {list(df.columns)[:20]}...")

    y_raw = df[label_col].astype(str).str.strip().str.lower()
    benign_token = str(benign_token).strip().lower()
    y = (y_raw != benign_token).astype(int)
    return y_raw, y


# ----------------------------
# Cleaning / schema
# ----------------------------
def _coerce_numeric_best_effort(X: pd.DataFrame, protected_cols: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """
    Convert non-numeric columns to numeric when possible (best effort).
    Protected columns (e.g. '_source_file') are left untouched.
    """
    prot = set(protected_cols or [])
    X = X.copy()
    for c in X.columns:
        if c in prot:
            continue
        if not is_numeric_dtype(X[c]):
            X[c] = pd.to_numeric(X[c], errors="coerce")
    return X


def _feature_cols(df: pd.DataFrame) -> List[str]:
    """
    Feature columns: everything except meta cols and label.
    """
    return [c for c in df.columns if c not in _META_COLS and c not in _LABEL_COLS]


def _assert_numeric_features(df: pd.DataFrame) -> None:
    """
    Enforce: all feature columns are numeric after cleaning.
    Meta/label columns are ignored.
    """
    feat = _feature_cols(df)
    bad = [c for c in feat if not is_numeric_dtype(df[c])]
    if bad:
        raise RuntimeError(
            f"Non-numeric feature columns remain after cleaning: {bad[:10]} "
            f"{'(more...)' if len(bad) > 10 else ''}. "
            f"Tip: use --drop-non-numeric or inspect coercion."
        )


def _nan_stats(df: pd.DataFrame) -> Dict[str, Any]:
    feat = _feature_cols(df)
    if not feat:
        return {"n_features": 0, "nan_frac_mean": None, "nan_frac_p95": None, "nan_frac_max": None}
    row_nan = df[feat].isna().mean(axis=1)
    return {
        "n_features": int(len(feat)),
        "nan_frac_mean": float(row_nan.mean()),
        "nan_frac_p95": float(np.quantile(row_nan.to_numpy(), 0.95)),
        "nan_frac_max": float(row_nan.max()),
    }


def _clean_features(
    X: pd.DataFrame,
    drop_non_numeric: bool,
    max_nan_frac: float,
    keep_source_file: bool,
) -> Tuple[pd.DataFrame, Dict[str, Any], np.ndarray]:
    """
    Cleaning pipeline (deterministic and reportable):

      1) drop leakage columns if present
      2) coerce numeric best-effort (but keep meta columns as-is)
      3) optionally drop non-numeric columns (meta preserved if keep_source_file)
      4) replace inf/-inf -> NaN
      5) drop all-NaN columns
      6) compute keep_mask based on row NaN fraction (FEATURES ONLY; meta excluded)
      7) filter rows (keep_mask)
      8) reset index
      9) assert numeric features (meta ignored)

    NOTE: NO IMPUTATION HERE.

    Returns:
      X_clean: cleaned + filtered + reset_index(drop=True)
      rep: report dict
      kept_idx: indices (np.ndarray) of kept rows w.r.t. the input X (after step 5 schema)
               This is what you must use to filter y with iloc to keep alignment robust.
    """
    rep: Dict[str, Any] = {}

    X0 = X.copy()

    # Drop leakage columns
    drop_cols = [c for c in _LEAKAGE_COLS if c in X0.columns]
    if drop_cols:
        X0 = X0.drop(columns=drop_cols)

    # Protect meta columns
    protected = set()
    if keep_source_file and "_source_file" in X0.columns:
        protected.add("_source_file")

    rep["nan_stats_before"] = _nan_stats(X0)

    # Coerce numeric FIRST (meta untouched)
    X0 = _coerce_numeric_best_effort(X0, protected_cols=list(protected))

    # Optionally drop non-numeric columns (but preserve meta if requested)
    if drop_non_numeric:
        meta_df = None
        meta_cols_present = [c for c in protected if c in X0.columns]
        if meta_cols_present:
            meta_df = X0[meta_cols_present].copy()
            X0 = X0.drop(columns=meta_cols_present, errors="ignore")

        X0 = X0.select_dtypes(include=[np.number]).copy()

        if meta_df is not None and not meta_df.empty:
            X0 = pd.concat([X0, meta_df], axis=1)

    # Clean infinities (meta unaffected because it's non-numeric)
    X0 = X0.replace([np.inf, -np.inf], np.nan)

    n_rows_raw = int(X0.shape[0])
    n_cols_raw = int(X0.shape[1])

    # Drop columns all NaN (including meta if it happens to be all-NaN; ok)
    all_nan_cols = X0.columns[X0.isna().all()].tolist()
    X0 = X0.dropna(axis=1, how="all")

    # Compute keep_mask based on NaN fraction over FEATURES ONLY
    feat_cols = _feature_cols(X0)
    if not feat_cols:
        raise RuntimeError("After cleaning, no feature columns remain.")

    row_nan_frac = X0[feat_cols].isna().mean(axis=1)
    keep_mask = (row_nan_frac <= float(max_nan_frac)).to_numpy()
    kept_idx = np.where(keep_mask)[0]

    # Filter rows + reset index
    X1 = X0.iloc[kept_idx].copy().reset_index(drop=True)

    # Enforce numeric features now.
    _assert_numeric_features(X1)

    rep.update(
        {
            "rows_raw": n_rows_raw,
            "cols_raw": n_cols_raw,
            "cols_dropped_leakage": drop_cols,
            "cols_dropped_all_nan": all_nan_cols,
            "rows_after_nan_filter": int(X1.shape[0]),
            "cols_after_cleaning": int(X1.shape[1]),
            "max_nan_frac": float(max_nan_frac),
            "imputed": False,
            "kept_meta_cols": sorted(list(protected)),
            "n_feature_cols_after": int(len(_feature_cols(X1))),
            "nan_stats_after": _nan_stats(X1),
        }
    )

    return X1, rep, kept_idx


def _balanced_subset_indices(
    y: np.ndarray, n_total: int, n_per_class: int, seed: int
) -> Tuple[np.ndarray, Dict[str, Any]]:
    y = np.asarray(y).astype(int)
    idx0 = np.where(y == 0)[0]
    idx1 = np.where(y == 1)[0]
    if idx0.size == 0 or idx1.size == 0:
        raise RuntimeError("One class disappeared after cleaning (need both benign and attack).")

    if int(n_per_class) > 0:
        npc = int(n_per_class)
    else:
        npc = int(n_total) // 2

    npc = min(npc, int(idx0.size), int(idx1.size))
    if npc <= 0:
        raise RuntimeError("n_per_class resolved to 0; check n_total / class sizes.")

    rng = _stable_rng(seed)
    sel = np.concatenate(
        [
            rng.choice(idx0, size=npc, replace=False),
            rng.choice(idx1, size=npc, replace=False),
        ]
    )
    rng.shuffle(sel)

    info = {
        "prep_seed": int(seed),
        "n_per_class": int(npc),
        "n_total": int(2 * npc),
        "class0_available": int(idx0.size),
        "class1_available": int(idx1.size),
    }
    return sel, info


def _align_schema(
    X_tr: pd.DataFrame,
    X_te: pd.DataFrame,
    schema_from: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Align feature schemas between train and test.

    schema_from:
      - "train": keep train feature cols; test is reindexed to train cols (missing -> NaN)
      - "intersection": keep only common feature cols
      - "union": union of feature cols (both reindexed; missing -> NaN)
    """
    schema_from = (schema_from or "train").strip().lower()

    tr_feat = _feature_cols(X_tr)
    te_feat = _feature_cols(X_te)

    tr_set = set(tr_feat)
    te_set = set(te_feat)

    if schema_from == "train":
        cols = tr_feat
    elif schema_from == "intersection":
        cols = [c for c in tr_feat if c in te_set]
    elif schema_from == "union":
        cols = sorted(list(tr_set.union(te_set)))
    else:
        raise ValueError("schema_from must be one of: train|intersection|union")

    # Reindex features; keep meta columns as-is (if present)
    tr_meta = [c for c in X_tr.columns if c in _META_COLS]
    te_meta = [c for c in X_te.columns if c in _META_COLS]

    X_tr_al = X_tr.reindex(columns=cols + tr_meta)
    X_te_al = X_te.reindex(columns=cols + te_meta)

    missing_in_test = [c for c in cols if c not in te_set]
    missing_in_train = [c for c in cols if c not in tr_set]

    rep = {
        "schema_from": schema_from,
        "n_features_train_before": int(len(tr_feat)),
        "n_features_test_before": int(len(te_feat)),
        "n_features_final": int(len(cols)),
        "dropped_from_train": sorted(list(set(tr_feat) - set(cols))),
        "dropped_from_test": sorted(list(set(te_feat) - set(cols))),
        "added_to_test_missing": sorted(missing_in_test),
        "added_to_train_missing": sorted(missing_in_train),
        "n_missing_in_test_after_align": int(len(missing_in_test)),
        "n_missing_in_train_after_align": int(len(missing_in_train)),
        "feature_cols_final": list(cols),
        "meta_cols_train": tr_meta,
        "meta_cols_test": te_meta,
    }
    return X_tr_al, X_te_al, rep


# ----------------------------
# Output helpers
# ----------------------------
def _n_features_in_output(out_df: pd.DataFrame) -> int:
    """
    Output columns include:
      - feature cols
      - optional meta cols (e.g. _source_file)
      - label
    """
    cols = list(out_df.columns)
    cols = [c for c in cols if c not in _META_COLS and c != "label"]
    return int(len(cols))


def _write_one_output(out_csv: Path, out_report: Path, out_df: pd.DataFrame, report: Dict[str, Any]) -> None:
    _ensure_parent(out_csv)
    out_df.to_csv(out_csv, index=False)
    report["output"] = {
        "path": str(out_csv),
        "shape": list(out_df.shape),
        "n_features": _n_features_in_output(out_df),
        "sha256": _sha256_file(out_csv),
        "columns": list(out_df.columns),
        "feature_cols": [c for c in out_df.columns if (c != "label" and c not in _META_COLS)],
        "meta_cols": [c for c in out_df.columns if c in _META_COLS],
        "label_col": "label" if "label" in out_df.columns else None,
    }
    _write_json(out_report, report)
    print(f"[OK] Saved {out_csv} shape={tuple(out_df.shape)}")
    print(f"[OK] Report {out_report}")


# ----------------------------
# Modes
# ----------------------------
def _run_id_mode(
    indir: Path,
    files: List[Path],
    seeds: List[int],
    out_template: str,
    report_template: str,
    cfg_base: PrepCfg,
) -> None:
    print(f"[INFO] ID mode: loading {len(files)} CSV files from {indir}")
    df, file_hashes = _load_concat_csv(files, keep_source_file=cfg_base.keep_source_file)

    # Normalize label col same way we normalize df columns
    label_col = str(cfg_base.label_col).strip().replace(" ", "_")
    y_raw, y = _binarize_labels(df, label_col=label_col, benign_token=cfg_base.benign_token)

    X = df.drop(columns=[label_col], errors="ignore")

    # Clean pool (NO IMPUTE)
    X_clean, rep_clean, kept_idx = _clean_features(
        X=X,
        drop_non_numeric=cfg_base.drop_non_numeric,
        max_nan_frac=cfg_base.max_nan_frac,
        keep_source_file=cfg_base.keep_source_file,
    )

    # Align labels with kept rows (ROBUST: use iloc with kept_idx)
    y_raw2 = y_raw.iloc[kept_idx].reset_index(drop=True)
    y2 = y.iloc[kept_idx].reset_index(drop=True)

    base_payload = {
        "mode": "id",
        "files_used": [f.name for f in files],
        "label_col_clean": label_col,
        "benign_token": cfg_base.benign_token,
        "drop_non_numeric": cfg_base.drop_non_numeric,
        "max_nan_frac": cfg_base.max_nan_frac,
        "keep_source_file": cfg_base.keep_source_file,
        "n_total": cfg_base.n_total,
        "n_per_class": cfg_base.n_per_class,
        "feature_cols_pool": _feature_cols(X_clean),
        "imputed": False,
    }

    for s in seeds:
        cfg = PrepCfg(**{**cfg_base.__dict__, "seed": int(s)})

        sel, subset_info = _balanced_subset_indices(
            y=y2.to_numpy(),
            n_total=cfg.n_total,
            n_per_class=cfg.n_per_class,
            seed=cfg.seed,
        )

        out_df = X_clean.iloc[sel].copy()
        out_df["label"] = y2.iloc[sel].to_numpy().astype(int)

        out_csv = _resolve_template(out_template, seed=cfg.seed)
        out_rep = _resolve_template(report_template, seed=cfg.seed)

        payload = dict(base_payload)
        payload["prep_seed"] = int(cfg.seed)
        payload["subset_n_total"] = int(subset_info["n_total"])
        payload["subset_n_per_class"] = int(subset_info["n_per_class"])
        data_id = _dataset_id(payload)

        rep: Dict[str, Any] = {
            "dataset_id": data_id,
            "dataset_id_payload": payload,
            "mode": "id",
            "source": {
                "indir": str(indir),
                "files_used": [f.name for f in files],
                "file_sha256": file_hashes,
            },
            "labels": {
                "label_col_raw": str(cfg_base.label_col),
                "label_col_clean": str(label_col),
                "benign_token": str(cfg_base.benign_token),
                "raw_distribution_pool": y_raw2.value_counts().to_dict(),
                "binarized_pos_rate_pool": float(y2.mean()),
                "pos_rate_subset": float(out_df["label"].mean()),
            },
            "cleaning": rep_clean,
            "subset": subset_info,
            "schema": {
                "feature_cols_pool": _feature_cols(X_clean),
                "meta_cols_pool": [c for c in X_clean.columns if c in _META_COLS],
                "n_features_pool": int(len(_feature_cols(X_clean))),
                "kept_meta_cols": rep_clean.get("kept_meta_cols", []),
            },
        }

        _write_one_output(out_csv, out_rep, out_df, rep)
        print(out_df["label"].value_counts().to_dict())


def _run_ood_mode(
    indir: Path,
    all_files: List[Path],
    train_patterns: List[str],
    test_patterns: List[str],
    seeds: List[int],
    out_train_template: str,
    out_test_template: str,
    report_template: str,
    cfg_base: PrepCfg,
    schema_from: str,
) -> None:
    train_files = _match_files(all_files, train_patterns)
    test_files = _match_files(all_files, test_patterns)

    if not train_files:
        raise RuntimeError("OOD mode: no files matched --train-files patterns.")
    if not test_files:
        raise RuntimeError("OOD mode: no files matched --test-files patterns.")

    # Ensure disjointness (strongly recommended)
    train_set = set([f.name for f in train_files])
    test_set = set([f.name for f in test_files])
    inter = sorted(train_set.intersection(test_set))
    if inter:
        raise RuntimeError(f"OOD mode requires disjoint train/test file sets. Overlap: {inter[:10]}")

    print(f"[INFO] OOD mode: train_files={len(train_files)} test_files={len(test_files)}")
    print(f"[INFO] OOD mode: schema_from={schema_from} (NO IMPUTE here)")

    df_tr, hashes_tr = _load_concat_csv(train_files, keep_source_file=cfg_base.keep_source_file)
    df_te, hashes_te = _load_concat_csv(test_files, keep_source_file=cfg_base.keep_source_file)

    label_col = str(cfg_base.label_col).strip().replace(" ", "_")

    y_raw_tr, y_tr = _binarize_labels(df_tr, label_col=label_col, benign_token=cfg_base.benign_token)
    y_raw_te, y_te = _binarize_labels(df_te, label_col=label_col, benign_token=cfg_base.benign_token)

    X_tr = df_tr.drop(columns=[label_col], errors="ignore")
    X_te = df_te.drop(columns=[label_col], errors="ignore")

    # Clean pools (NO IMPUTE)
    X_tr_clean, rep_tr, kept_tr_idx = _clean_features(
        X=X_tr,
        drop_non_numeric=cfg_base.drop_non_numeric,
        max_nan_frac=cfg_base.max_nan_frac,
        keep_source_file=cfg_base.keep_source_file,
    )
    X_te_clean, rep_te, kept_te_idx = _clean_features(
        X=X_te,
        drop_non_numeric=cfg_base.drop_non_numeric,
        max_nan_frac=cfg_base.max_nan_frac,
        keep_source_file=cfg_base.keep_source_file,
    )

    # Align labels with kept rows (ROBUST)
    y_raw_tr2 = y_raw_tr.iloc[kept_tr_idx].reset_index(drop=True)
    y_tr2 = y_tr.iloc[kept_tr_idx].reset_index(drop=True)
    y_raw_te2 = y_raw_te.iloc[kept_te_idx].reset_index(drop=True)
    y_te2 = y_te.iloc[kept_te_idx].reset_index(drop=True)

    # Align schema (CRITICAL). Still no impute.
    X_tr_al, X_te_al, rep_schema = _align_schema(X_tr_clean, X_te_clean, schema_from=schema_from)

    # Keep indices aligned (paranoia)
    X_tr_al2 = X_tr_al.reset_index(drop=True)
    X_te_al2 = X_te_al.reset_index(drop=True)

    base_payload = {
        "mode": "ood_by_files",
        "train_files_used": [f.name for f in train_files],
        "test_files_used": [f.name for f in test_files],
        "label_col_clean": label_col,
        "benign_token": cfg_base.benign_token,
        "drop_non_numeric": cfg_base.drop_non_numeric,
        "max_nan_frac": cfg_base.max_nan_frac,
        "keep_source_file": cfg_base.keep_source_file,
        "schema_from": schema_from,
        "n_total": cfg_base.n_total,
        "n_per_class": cfg_base.n_per_class,
        "feature_cols_final": rep_schema.get("feature_cols_final", []),
        "imputed": False,
    }

    for s in seeds:
        cfg = PrepCfg(**{**cfg_base.__dict__, "seed": int(s)})

        sel_tr, info_tr = _balanced_subset_indices(
            y=y_tr2.to_numpy(),
            n_total=cfg.n_total,
            n_per_class=cfg.n_per_class,
            seed=cfg.seed,
        )
        sel_te, info_te = _balanced_subset_indices(
            y=y_te2.to_numpy(),
            n_total=cfg.n_total,
            n_per_class=cfg.n_per_class,
            seed=cfg.seed,
        )

        out_tr = X_tr_al2.iloc[sel_tr].copy()
        out_tr["label"] = y_tr2.iloc[sel_tr].to_numpy().astype(int)

        out_te = X_te_al2.iloc[sel_te].copy()
        out_te["label"] = y_te2.iloc[sel_te].to_numpy().astype(int)

        out_train = _resolve_template(out_train_template, seed=cfg.seed)
        out_test = _resolve_template(out_test_template, seed=cfg.seed)
        out_rep = _resolve_template(report_template, seed=cfg.seed)

        _ensure_parent(out_train)
        _ensure_parent(out_test)

        out_tr.to_csv(out_train, index=False)
        out_te.to_csv(out_test, index=False)

        payload = dict(base_payload)
        payload["prep_seed"] = int(cfg.seed)
        payload["train_subset_n_total"] = int(info_tr["n_total"])
        payload["test_subset_n_total"] = int(info_te["n_total"])
        data_id = _dataset_id(payload)

        rep: Dict[str, Any] = {
            "dataset_id": data_id,
            "dataset_id_payload": payload,
            "mode": "ood_by_files",
            "source": {
                "indir": str(indir),
                "train_files_used": [f.name for f in train_files],
                "test_files_used": [f.name for f in test_files],
                "train_file_sha256": hashes_tr,
                "test_file_sha256": hashes_te,
            },
            "labels": {
                "label_col_raw": str(cfg_base.label_col),
                "label_col_clean": str(label_col),
                "benign_token": str(cfg_base.benign_token),
                "train_raw_distribution_pool": y_raw_tr2.value_counts().to_dict(),
                "test_raw_distribution_pool": y_raw_te2.value_counts().to_dict(),
                "train_pos_rate_subset": float(out_tr["label"].mean()),
                "test_pos_rate_subset": float(out_te["label"].mean()),
            },
            "cleaning": {"train": rep_tr, "test": rep_te},
            "schema": rep_schema,
            "subset": {"prep_seed": int(cfg.seed), "train": info_tr, "test": info_te},
            "outputs": {"train_csv": str(out_train), "test_csv": str(out_test)},
            "hashes": {"train_sha256": _sha256_file(out_train), "test_sha256": _sha256_file(out_test)},
            "nan_stats_outputs": {
                "train": _nan_stats(out_tr.drop(columns=["label"], errors="ignore")),
                "test": _nan_stats(out_te.drop(columns=["label"], errors="ignore")),
            },
        }

        _write_json(out_rep, rep)

        print(f"[OK] Saved train {out_train} shape={tuple(out_tr.shape)}")
        print(f"[OK] Saved test  {out_test}  shape={tuple(out_te.shape)}")
        print(f"[OK] Report     {out_rep}")
        print(
            {
                "train_counts": out_tr["label"].value_counts().to_dict(),
                "test_counts": out_te["label"].value_counts().to_dict(),
            }
        )


# ----------------------------
# CLI
# ----------------------------
def main() -> None:
    ap = argparse.ArgumentParser()

    ap.add_argument("--indir", type=str, required=True, help="Directory containing CICIDS CSV files")
    ap.add_argument("--label-col", type=str, default="Label", help="Label column name (raw)")
    ap.add_argument("--benign-token", type=str, default="benign", help="Token that means benign in label column")

    # Subset control
    ap.add_argument("--n-total", type=int, default=3000, help="Total rows per subset (balanced 50/50 by default)")
    ap.add_argument("--n-per-class", type=int, default=0, help="If >0, overrides n_total/2")
    ap.add_argument("--seed", type=int, default=42, help="Legacy single seed (used if --seeds not provided)")
    ap.add_argument(
        "--seeds",
        type=str,
        default="",
        help="Comma/space list to generate multiple subsets (e.g. 42,123,999)",
    )

    # Cleaning
    ap.add_argument("--drop-non-numeric", action="store_true", help="Drop non-numeric columns after coercion")
    ap.add_argument("--max-nan-frac", type=float, default=0.2, help="Drop rows with NaN fraction above this")

    # File selection (ID mode)
    ap.add_argument(
        "--use-only-files",
        nargs="*",
        default=[],
        help="Glob patterns of CSV files to include for ID mode (e.g. Monday*,Tuesday*)",
    )

    # OOD by files mode (train/test from disjoint file groups)
    ap.add_argument("--ood", action="store_true", help="Enable OOD-by-files mode")
    ap.add_argument("--train-files", nargs="*", default=[], help="Glob patterns for TRAIN files (OOD mode).")
    ap.add_argument("--test-files", nargs="*", default=[], help="Glob patterns for TEST files (OOD mode).")

    # OOD schema policy
    ap.add_argument(
        "--schema-from",
        type=str,
        default="train",
        help="OOD schema alignment: train|intersection|union (default: train)",
    )

    # Output (ID)
    ap.add_argument("--out", type=str, default="data/cicids_subset.csv", help="Legacy single output path (ID)")
    ap.add_argument(
        "--out-template",
        type=str,
        default="",
        help='Template for multiple outputs, must include "{seed}". Example: data/cicids_subset__prep{seed}.csv',
    )

    # Output (OOD)
    ap.add_argument("--out-train", type=str, default="data/cicids_train.csv", help="Legacy single train output (OOD)")
    ap.add_argument("--out-test", type=str, default="data/cicids_test.csv", help="Legacy single test output (OOD)")
    ap.add_argument(
        "--out-train-template",
        type=str,
        default="",
        help='Template must include "{seed}". Example: data/cicids_train__prep{seed}.csv',
    )
    ap.add_argument(
        "--out-test-template",
        type=str,
        default="",
        help='Template must include "{seed}". Example: data/cicids_test__prep{seed}.csv',
    )

    # Reporting
    ap.add_argument("--report", type=str, default="", help="Legacy single report path")
    ap.add_argument(
        "--report-template",
        type=str,
        default="",
        help='Template must include "{seed}". Example: data/cicids_subset__prep{seed}.prep_report.json',
    )

    # Extra
    ap.add_argument("--keep-source-file", action="store_true", help="Add _source_file column for analysis by file/day")
    ap.add_argument("--dry-run", action="store_true", help="Print matched files/outputs and exit")

    args = ap.parse_args()

    indir = Path(args.indir)
    all_files = sorted(indir.glob("*.csv"))
    if not all_files:
        raise RuntimeError(f"No CSV files found in {indir}")

    seeds = _parse_int_list(args.seeds) if str(args.seeds).strip() else [int(args.seed)]
    if not seeds:
        raise RuntimeError("No seeds provided (check --seeds / --seed).")

    cfg_base = PrepCfg(
        label_col=str(args.label_col),
        n_total=int(args.n_total),
        n_per_class=int(args.n_per_class),
        seed=int(seeds[0]),
        drop_non_numeric=bool(args.drop_non_numeric),
        max_nan_frac=float(args.max_nan_frac),
        keep_source_file=bool(args.keep_source_file),
        benign_token=str(args.benign_token),
    )

    if args.ood:
        if not args.train_files or not args.test_files:
            raise RuntimeError("OOD mode requires --train-files and --test-files patterns.")

        train_files = _match_files(all_files, list(args.train_files))
        test_files = _match_files(all_files, list(args.test_files))

        out_train_template = str(args.out_train_template).strip() or str(args.out_train).strip()
        out_test_template = str(args.out_test_template).strip() or str(args.out_test).strip()

        if len(seeds) > 1:
            if "{seed}" not in out_train_template or "{seed}" not in out_test_template:
                raise RuntimeError(
                    "With multiple --seeds in OOD mode you must use "
                    "--out-train-template/--out-test-template with {seed}."
                )

        report_template = str(args.report_template).strip()
        if not report_template:
            if str(args.report).strip():
                report_template = str(args.report).strip()
            else:
                rep_base = out_train_template
                if rep_base.endswith(".csv"):
                    rep_base = rep_base[:-4]
                report_template = rep_base + ".prep_report.json"

        if len(seeds) > 1 and "{seed}" not in report_template:
            raise RuntimeError(
                "With multiple --seeds you must use --report-template including {seed} "
                "(or pass --report-template explicitly)."
            )

        if bool(args.dry_run):
            print("[DRY-RUN] OOD mode")
            print(f"indir: {indir}")
            print(f"train_patterns: {list(args.train_files)} -> matched {len(train_files)} files")
            print(f"test_patterns:  {list(args.test_files)} -> matched {len(test_files)} files")
            print(f"schema_from: {args.schema_from}")
            print(f"seeds: {seeds}")
            print(f"out_train_template: {out_train_template}")
            print(f"out_test_template:  {out_test_template}")
            print(f"report_template:    {report_template}")
            print("train_files:", [f.name for f in train_files][:20], "..." if len(train_files) > 20 else "")
            print("test_files: ", [f.name for f in test_files][:20], "..." if len(test_files) > 20 else "")
            return

        _run_ood_mode(
            indir=indir,
            all_files=all_files,
            train_patterns=list(args.train_files),
            test_patterns=list(args.test_files),
            seeds=seeds,
            out_train_template=out_train_template,
            out_test_template=out_test_template,
            report_template=report_template,
            cfg_base=cfg_base,
            schema_from=str(args.schema_from),
        )
        return

    # ID mode
    if args.use_only_files:
        files = _match_files(all_files, args.use_only_files)
        if not files:
            raise RuntimeError("No files matched --use-only-files patterns")
    else:
        files = all_files

    out_template = str(args.out_template).strip() or str(args.out).strip()
    if len(seeds) > 1 and "{seed}" not in out_template:
        raise RuntimeError('With multiple --seeds you must use --out-template including "{seed}".')

    report_template = str(args.report_template).strip()
    if not report_template:
        if str(args.report).strip():
            report_template = str(args.report).strip()
        else:
            rep_base = out_template
            if rep_base.endswith(".csv"):
                rep_base = rep_base[:-4]
            report_template = rep_base + ".prep_report.json"

    if len(seeds) > 1 and "{seed}" not in report_template:
        raise RuntimeError('With multiple --seeds you must use --report-template including "{seed}".')

    if bool(args.dry_run):
        print("[DRY-RUN] ID mode")
        print(f"indir: {indir}")
        print(f"matched files: {len(files)}")
        print(f"seeds: {seeds}")
        print(f"out_template: {out_template}")
        print(f"report_template: {report_template}")
        print("files:", [f.name for f in files][:30], "..." if len(files) > 30 else "")
        return

    _run_id_mode(
        indir=indir,
        files=files,
        seeds=seeds,
        out_template=out_template,
        report_template=report_template,
        cfg_base=cfg_base,
    )


if __name__ == "__main__":
    main()
