# src/datasets/cicids_subset.py
#
# Loader for prepared CICIDS subsets.
#
# Supports:
#   - ID mode: a single CSV (features + label [+ optional _source_file]) and we split inside.
#   - OOD mode: explicit train_csv + test_csv produced by prepare_cicids_subset.py (no internal split).
#
# Notes:
#   - No scaling here (scaling happens in run_benchmark).
#   - Median imputation fit on train only.
#   - Optional SVD fit on train only.
#     Guard is deterministic: 0 < n_components < min(n_features, n_samples) to avoid unstable / invalid cases.
#   - In OOD mode we validate schema consistency (feature columns must match as sets) if strict_schema=True.
#   - We avoid false positives on "all-NaN feature" in OOD: we only hard-fail if TRAIN has all-NaN features.
#   - When strict_schema=False:
#       * if schemas differ -> restrict to intersection (train order)
#       * if schemas match as sets but order differs -> reorder test to match train (important!)
#
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split


@dataclass(frozen=True)
class CicidsConfig:
    # -------------------------
    # Paths
    # -------------------------
    # ID mode
    path: Optional[Path] = None

    # OOD mode (explicit split)
    train_path: Optional[Path] = None
    test_path: Optional[Path] = None

    # -------------------------
    # Columns / split
    # -------------------------
    label_col: str = "label"
    test_size: float = 0.3
    stratify: bool = True

    # Meta column produced by prepare_cicids_subset (optional)
    source_file_col: str = "_source_file"

    # -------------------------
    # Feature prep
    # -------------------------
    svd_dim: int = 8

    # Robustness knobs
    strict_schema: bool = True  # OOD: feature columns must match (set). Order aligned to train.
    strict_numeric: bool = True  # Raise if non-numeric feature cols remain after coercion
    allow_empty_after_drop: bool = False  # If True, don't error when 0 feature cols remain (not recommended)

    # Optional extra checks
    error_if_all_nan_feature: bool = True  # ID/OOD: fail if TRAIN has any feature becomes all-NaN after coercion
    error_if_nan_after_impute: bool = False  # If True, fail if NaNs remain after imputation (strong)
    validate_label_binary: bool = True  # Fail if labels are not in {0,1}

    # OOD: after alignment/intersection, require at least this many features (prevents garbage runs)
    min_features_after_alignment: int = 2

    # If True, when svd_dim is too large, clip to max allowed (min(n_feat,n_samp)-1) instead of skipping
    svd_clip_instead_of_skip: bool = False

    # Debug
    verbose: bool = False  # Print small debug stats


# -------------------------
# Helpers
# -------------------------
def _coerce_features_numeric(X_df: pd.DataFrame, *, strict_numeric: bool) -> pd.DataFrame:
    """
    Coerce feature columns to numeric best-effort.

    IMPORTANT:
      We convert *all* columns with pd.to_numeric(errors="coerce") so we also handle
      pandas StringDtype (string[python]/string[pyarrow]) and other non-object dtypes.
    """
    X_df = X_df.copy()
    X_df = X_df.apply(pd.to_numeric, errors="coerce")

    if strict_numeric:
        still_bad = [c for c in X_df.columns if not np.issubdtype(X_df[c].dtype, np.number)]
        if still_bad:
            raise ValueError(
                f"Non-numeric feature columns remain after coercion: {still_bad[:10]}"
                f"{' (more...)' if len(still_bad) > 10 else ''}"
            )

    return X_df


def _validate_label_binary(y: np.ndarray, *, path: Path) -> None:
    u = np.unique(y)
    if not np.all(np.isin(u, [0, 1])):
        raise ValueError(f"Label column in {path} is not binary {{0,1}}. Unique values: {u[:20]}")


def _read_xy(
    path: Path,
    *,
    label_col: str,
    source_file_col: str,
    strict_numeric: bool,
    validate_label_binary: bool,
) -> Tuple[np.ndarray, np.ndarray, List[str], Dict[str, Any]]:
    """
    Read a prepared subset CSV into (X, y, feature_cols, stats).

    - Drops label column and optional meta column(s) from features.
    - Drops common pandas index artifacts (Unnamed:*) if present.
    - Coerces remaining feature columns to numeric (best effort).
    - Replaces inf/-inf with NaN.
    - Reports columns that became all-NaN (does NOT raise here; caller decides).
    """
    df = pd.read_csv(path)

    # Drop common pandas index column artifacts if present
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed:")]
    if unnamed:
        df = df.drop(columns=unnamed, errors="ignore")

    if label_col not in df.columns:
        raise ValueError(
            f"Missing label column '{label_col}' in {path}. "
            f"Available columns (first 30): {list(df.columns)[:30]}"
        )

    y = df[label_col].astype(int).to_numpy()
    if validate_label_binary:
        _validate_label_binary(y, path=path)

    drop_cols = [label_col]
    if source_file_col and source_file_col in df.columns:
        drop_cols.append(source_file_col)

    X_df = df.drop(columns=drop_cols, errors="ignore").copy()
    feature_cols = list(X_df.columns)

    # Detect duplicate feature names early (painful downstream)
    dups = pd.Index(feature_cols)[pd.Index(feature_cols).duplicated()].unique().tolist()
    if dups:
        raise ValueError(
            f"Duplicate feature columns in {path}: {dups[:10]}"
            f"{' (more...)' if len(dups) > 10 else ''}"
        )

    if not feature_cols:
        stats = {
            "n_rows": int(len(y)),
            "n_features": 0,
            "nan_frac_mean_per_feature": float("nan"),
            "nan_frac_max_per_feature": float("nan"),
            "pos_rate": float(np.mean(y)) if len(y) > 0 else float("nan"),
            "all_nan_feature_cols": [],
        }
        return np.empty((len(y), 0), dtype=float), y, feature_cols, stats

    # Coerce to numeric + clean infinities
    X_df = _coerce_features_numeric(X_df, strict_numeric=strict_numeric)
    X_df = X_df.replace([np.inf, -np.inf], np.nan)

    all_nan_cols = X_df.columns[X_df.isna().all()].tolist()

    # Useful stats
    nan_per_feat = X_df.isna().mean(axis=0) if X_df.shape[1] > 0 else None
    nan_frac_mean = float(np.mean(nan_per_feat)) if nan_per_feat is not None else float("nan")
    nan_frac_max = float(np.max(nan_per_feat)) if nan_per_feat is not None else float("nan")

    stats = {
        "n_rows": int(len(y)),
        "n_features": int(X_df.shape[1]),
        "nan_frac_mean_per_feature": nan_frac_mean,
        "nan_frac_max_per_feature": nan_frac_max,
        "pos_rate": float(np.mean(y)) if len(y) > 0 else float("nan"),
        "all_nan_feature_cols": all_nan_cols,
    }

    X = X_df.to_numpy(dtype=float)
    return X, y, feature_cols, stats


def _fit_transform_impute_svd(
    X_tr: np.ndarray,
    X_te: np.ndarray,
    *,
    seed: int,
    svd_dim: int,
    error_if_nan_after_impute: bool,
    svd_clip_instead_of_skip: bool,
    verbose: bool,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Fit median imputer on train only and transform both.
    Optionally fit SVD on train only and transform both.

    Deterministic SVD guard:
      0 < n_components < min(n_features, n_samples)

    Returns:
      X_tr2, X_te2, info dict (svd_applied + effective n_components)
    """
    imputer = SimpleImputer(strategy="median")
    X_tr2 = imputer.fit_transform(X_tr)
    X_te2 = imputer.transform(X_te)

    if error_if_nan_after_impute:
        if np.isnan(X_tr2).any():
            raise ValueError("NaNs remain in TRAIN after median imputation (likely all-NaN feature in train).")
        if np.isnan(X_te2).any():
            raise ValueError("NaNs remain in TEST after median imputation (check schema/imputation).")

    n_features = int(X_tr2.shape[1])
    n_samples = int(X_tr2.shape[0])
    n_comp_req = int(svd_dim)

    info = {
        "svd_requested": int(n_comp_req),
        "svd_applied": int(0),
        "svd_n_components": int(0),
        "svd_policy": "clip" if svd_clip_instead_of_skip else "skip",
    }

    if not n_comp_req or n_comp_req <= 0:
        return np.asarray(X_tr2), np.asarray(X_te2), info

    if n_features == 0:
        return np.asarray(X_tr2), np.asarray(X_te2), info

    max_allowed = int(min(n_features, n_samples) - 1)
    if max_allowed <= 0:
        if verbose:
            print(
                f"[CICIDS][WARN] Skipping SVD: max_allowed={max_allowed} "
                f"(n_features={n_features}, n_samples={n_samples})."
            )
        return np.asarray(X_tr2), np.asarray(X_te2), info

    n_comp_eff = n_comp_req
    if n_comp_req > max_allowed:
        if svd_clip_instead_of_skip:
            n_comp_eff = max_allowed
            if verbose:
                print(
                    f"[CICIDS][WARN] Clipping SVD: svd_dim={n_comp_req} -> {n_comp_eff} "
                    f"(max_allowed={max_allowed})."
                )
        else:
            if verbose:
                print(
                    f"[CICIDS][WARN] Skipping SVD: svd_dim={n_comp_req} not <= max_allowed={max_allowed} "
                    f"(need n_comp < min(n_features={n_features}, n_samples={n_samples}))."
                )
            return np.asarray(X_tr2), np.asarray(X_te2), info

    svd = TruncatedSVD(n_components=int(n_comp_eff), random_state=int(seed))
    X_tr2 = svd.fit_transform(X_tr2)
    X_te2 = svd.transform(X_te2)

    info["svd_applied"] = int(1)
    info["svd_n_components"] = int(n_comp_eff)
    return np.asarray(X_tr2), np.asarray(X_te2), info


def _align_test_to_train_order(X_te: np.ndarray, cols_te: List[str], cols_tr: List[str]) -> Tuple[np.ndarray, List[str]]:
    """
    Reorder test features to match train feature order.
    Assumes set(cols_tr) == set(cols_te).
    """
    if cols_te == cols_tr:
        return X_te, cols_te
    pos = {c: i for i, c in enumerate(cols_te)}
    idx = [pos[c] for c in cols_tr]
    return X_te[:, idx], list(cols_tr)


def _restrict_to_intersection(
    X_tr: np.ndarray,
    cols_tr: List[str],
    X_te: np.ndarray,
    cols_te: List[str],
) -> Tuple[np.ndarray, List[str], np.ndarray, List[str], Dict[str, Any]]:
    """
    If strict_schema=False and schemas differ, restrict both to intersection (train order).
    """
    set_tr, set_te = set(cols_tr), set(cols_te)
    inter = [c for c in cols_tr if c in set_te]  # keep train order

    pos_tr = {c: i for i, c in enumerate(cols_tr)}
    pos_te = {c: i for i, c in enumerate(cols_te)}

    idx_tr = [pos_tr[c] for c in inter]
    idx_te = [pos_te[c] for c in inter]

    rep = {
        "policy": "intersection",
        "n_train_before": int(len(cols_tr)),
        "n_test_before": int(len(cols_te)),
        "n_after": int(len(inter)),
        "dropped_from_train": sorted(list(set_tr - set(inter)))[:50],
        "dropped_from_test": sorted(list(set_te - set(inter)))[:50],
    }

    return X_tr[:, idx_tr], inter, X_te[:, idx_te], inter, rep


def _read_header_cols(path: Path) -> List[str]:
    try:
        df_head = pd.read_csv(path, nrows=1)
        return list(df_head.columns)
    except Exception:
        return []


def _raise_no_features(path: Path, *, label_col: str, source_file_col: str, columns_preview: List[str]) -> None:
    raise ValueError(
        "No feature columns found after dropping label/meta columns. "
        f"path={path} label_col={label_col!r} source_file_col={source_file_col!r} "
        f"columns(first30)={columns_preview[:30]}"
    )


# -------------------------
# Public API
# -------------------------
def load_cicids_subset(cfg: CicidsConfig, seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns:
      X_train, y_train, X_test, y_test

    Modes:
      - ID mode: cfg.path is set (single CSV). We do train_test_split with random_state=seed.
      - OOD mode: cfg.train_path and cfg.test_path set. No internal split.

    IMPORTANT:
      - NO scaling here.
      - Median imputation fit on train only.
      - Optional SVD fit on train only.
    """
    # -------------------------
    # OOD explicit split mode
    # -------------------------
    if cfg.train_path is not None or cfg.test_path is not None:
        if cfg.train_path is None or cfg.test_path is None:
            raise ValueError("For OOD mode you must provide BOTH train_path and test_path.")

        train_path = Path(cfg.train_path)
        test_path = Path(cfg.test_path)

        X_tr, y_tr, cols_tr, st_tr = _read_xy(
            train_path,
            label_col=cfg.label_col,
            source_file_col=cfg.source_file_col,
            strict_numeric=cfg.strict_numeric,
            validate_label_binary=cfg.validate_label_binary,
        )
        X_te, y_te, cols_te, st_te = _read_xy(
            test_path,
            label_col=cfg.label_col,
            source_file_col=cfg.source_file_col,
            strict_numeric=cfg.strict_numeric,
            validate_label_binary=cfg.validate_label_binary,
        )

        # All-NaN feature handling (OOD):
        # - hard fail if TRAIN has all-NaN features
        # - allow TEST all-NaN features (optional warn) since train-impute may cover it
        if cfg.error_if_all_nan_feature:
            tr_all_nan = list(st_tr.get("all_nan_feature_cols", []))
            if tr_all_nan:
                raise ValueError(
                    f"OOD: TRAIN has feature columns that are all-NaN after coercion in {train_path}: "
                    f"{tr_all_nan[:10]}{' (more...)' if len(tr_all_nan) > 10 else ''}"
                )
            te_all_nan = list(st_te.get("all_nan_feature_cols", []))
            if te_all_nan and cfg.verbose:
                print(
                    f"[CICIDS][WARN] OOD: TEST has all-NaN features after coercion "
                    f"(will be imputed from train if possible): {te_all_nan[:10]}"
                    f"{' (more...)' if len(te_all_nan) > 10 else ''}"
                )

        # Schema policy
        if cfg.strict_schema:
            set_tr, set_te = set(cols_tr), set(cols_te)
            if set_tr != set_te:
                only_tr = sorted(list(set_tr - set_te))[:20]
                only_te = sorted(list(set_te - set_tr))[:20]
                raise ValueError(
                    "OOD schema mismatch: feature columns differ between train and test.\n"
                    f"- n_train_cols={len(cols_tr)} n_test_cols={len(cols_te)}\n"
                    f"- only_in_train(first20)={only_tr}\n"
                    f"- only_in_test(first20)={only_te}\n"
                    "Tip: ensure prepare_cicids_subset.py ran in OOD mode with schema alignment "
                    "(or set strict_schema=False to use intersection)."
                )
            # Even in strict mode, align order to train
            X_te, cols_te = _align_test_to_train_order(X_te, cols_te, cols_tr)
        else:
            # Non-strict: if sets differ -> intersection; else align order
            if set(cols_tr) != set(cols_te):
                X_tr, cols_tr, X_te, cols_te, rep = _restrict_to_intersection(X_tr, cols_tr, X_te, cols_te)
                if cfg.verbose:
                    print(f"[CICIDS][WARN] OOD: schema mismatch -> using intersection. {rep}")
            else:
                X_te, cols_te = _align_test_to_train_order(X_te, cols_te, cols_tr)

        if X_tr.shape[1] != X_te.shape[1]:
            raise RuntimeError(
                f"Internal schema alignment error: train_feat={X_tr.shape[1]} test_feat={X_te.shape[1]}."
            )

        # Prevent garbage runs after intersection/alignment
        if int(X_tr.shape[1]) < int(cfg.min_features_after_alignment):
            raise ValueError(
                f"OOD: too few features after schema alignment: {int(X_tr.shape[1])} "
                f"(<{int(cfg.min_features_after_alignment)}). "
                f"train={train_path} test={test_path}"
            )

        if (X_tr.shape[1] == 0 or X_te.shape[1] == 0) and not cfg.allow_empty_after_drop:
            _raise_no_features(
                train_path,
                label_col=cfg.label_col,
                source_file_col=cfg.source_file_col,
                columns_preview=_read_header_cols(train_path),
            )

        if cfg.verbose:
            print("[CICIDS] OOD mode")
            print(
                f"[CICIDS] train: rows={st_tr.get('n_rows')} feat={X_tr.shape[1]} pos_rate={st_tr.get('pos_rate'):.4f} "
                f"nan_mean={st_tr.get('nan_frac_mean_per_feature'):.4f} nan_max={st_tr.get('nan_frac_max_per_feature'):.4f}"
            )
            print(
                f"[CICIDS] test : rows={st_te.get('n_rows')} feat={X_te.shape[1]} pos_rate={st_te.get('pos_rate'):.4f} "
                f"nan_mean={st_te.get('nan_frac_mean_per_feature'):.4f} nan_max={st_te.get('nan_frac_max_per_feature'):.4f}"
            )

        X_tr2, X_te2, svd_info = _fit_transform_impute_svd(
            X_tr,
            X_te,
            seed=int(seed),
            svd_dim=int(cfg.svd_dim),
            error_if_nan_after_impute=bool(cfg.error_if_nan_after_impute),
            svd_clip_instead_of_skip=bool(cfg.svd_clip_instead_of_skip),
            verbose=bool(cfg.verbose),
        )
        if cfg.verbose:
            print(f"[CICIDS] SVD: {svd_info}")

        return X_tr2, np.asarray(y_tr), X_te2, np.asarray(y_te)

    # -------------------------
    # ID split-inside mode
    # -------------------------
    if cfg.path is None:
        raise ValueError("For ID mode you must provide cfg.path (single CSV).")

    path = Path(cfg.path)

    X, y, _cols, st = _read_xy(
        path,
        label_col=cfg.label_col,
        source_file_col=cfg.source_file_col,
        strict_numeric=cfg.strict_numeric,
        validate_label_binary=cfg.validate_label_binary,
    )

    if cfg.error_if_all_nan_feature:
        all_nan = list(st.get("all_nan_feature_cols", []))
        if all_nan:
            raise ValueError(
                f"ID: feature columns became all-NaN after coercion in {path}: "
                f"{all_nan[:10]}{' (more...)' if len(all_nan) > 10 else ''}"
            )

    if X.shape[1] == 0 and not cfg.allow_empty_after_drop:
        _raise_no_features(
            path,
            label_col=cfg.label_col,
            source_file_col=cfg.source_file_col,
            columns_preview=_read_header_cols(path),
        )

    strat = y if cfg.stratify else None
    X_tr, X_te, y_tr, y_te = train_test_split(
        X,
        y,
        test_size=float(cfg.test_size),
        random_state=int(seed),
        stratify=strat,
    )

    if cfg.verbose:
        print("[CICIDS] ID mode")
        print(
            f"[CICIDS] pool: rows={st.get('n_rows')} feat={st.get('n_features')} pos_rate={st.get('pos_rate'):.4f} "
            f"nan_mean={st.get('nan_frac_mean_per_feature'):.4f} nan_max={st.get('nan_frac_max_per_feature'):.4f}"
        )
        print(f"[CICIDS] split: test_size={cfg.test_size} stratify={cfg.stratify} seed={seed}")

    X_tr2, X_te2, svd_info = _fit_transform_impute_svd(
        X_tr,
        X_te,
        seed=int(seed),
        svd_dim=int(cfg.svd_dim),
        error_if_nan_after_impute=bool(cfg.error_if_nan_after_impute),
        svd_clip_instead_of_skip=bool(cfg.svd_clip_instead_of_skip),
        verbose=bool(cfg.verbose),
    )
    if cfg.verbose:
        print(f"[CICIDS] SVD: {svd_info}")

    return X_tr2, np.asarray(y_tr), X_te2, np.asarray(y_te)
