from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ============================================================
# Helpers
# ============================================================

def _pick_col(df: pd.DataFrame, candidates: List[str], required: bool = False) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise KeyError(
            f"No se encontró ninguna de estas columnas: {candidates}\n"
            f"Columnas disponibles: {list(df.columns)}"
        )
    return None


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _safe_filename(s: object) -> str:
    s = str(s).strip()
    s = re.sub(r"\s+", "_", s)
    return re.sub(r"[^a-zA-Z0-9_\-\.]+", "_", s)


def _to_numeric_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def _extract_severity_from_name(name: str) -> float:
    """
    Fallback ONLY if no explicit attack strength column exists.
    Extracts trailing numeric token from attack name.
    """
    if not isinstance(name, str):
        return np.nan
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)$", name)
    if not m:
        return np.nan
    try:
        return float(m.group(1))
    except Exception:
        return np.nan


def _normalize_family(v: object) -> str:
    s = str(v).strip().lower()
    if any(k in s for k in ["qsvc", "quantum"]):
        return "quantum"
    if any(k in s for k in ["classical", "svc", "rbf", "linear", "svm"]):
        return "classical"
    return s or "unknown"


def _normalize_protocol(v: object) -> str:
    s = str(v).strip().lower()
    if s in {"id", "ood"}:
        return s
    return s or "unknown"


def _corr_safe(x: pd.Series, y: pd.Series) -> float:
    try:
        z = pd.DataFrame({"x": _to_numeric_series(x), "y": _to_numeric_series(y)}).dropna()
        if len(z) < 2:
            return float("nan")
        return float(z.corr().iloc[0, 1])
    except Exception:
        return float("nan")


def _weighted_corr_safe(x: pd.Series, y: pd.Series, w: Optional[pd.Series]) -> float:
    """
    Weighted Pearson correlation.
    Falls back to standard Pearson if weights are unavailable.
    """
    try:
        xx = _to_numeric_series(x).astype(float)
        yy = _to_numeric_series(y).astype(float)

        if w is None:
            return _corr_safe(xx, yy)

        ww = _to_numeric_series(w).astype(float)
        mask = np.isfinite(xx) & np.isfinite(yy) & np.isfinite(ww) & (ww > 0)
        if int(mask.sum()) < 2:
            return float("nan")

        xv = xx[mask].to_numpy(dtype=float)
        yv = yy[mask].to_numpy(dtype=float)
        wv = ww[mask].to_numpy(dtype=float)

        mx = np.average(xv, weights=wv)
        my = np.average(yv, weights=wv)

        xc = xv - mx
        yc = yv - my

        cov = np.average(xc * yc, weights=wv)
        vx = np.average(xc * xc, weights=wv)
        vy = np.average(yc * yc, weights=wv)

        if vx <= 0 or vy <= 0:
            return float("nan")

        return float(cov / np.sqrt(vx * vy))
    except Exception:
        return float("nan")


def _iter_protocol_dataset_groups(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
) -> Iterable[Tuple[Tuple[str, str], pd.DataFrame]]:
    proto_col = cols.get("protocol")
    dtag_col = cols.get("dataset_tag")

    if proto_col is None and dtag_col is None:
        yield ("all", "all"), df.copy()
        return

    tmp = df.copy()

    if proto_col is None:
        tmp["__proto_fallback"] = "all"
        proto_col = "__proto_fallback"

    if dtag_col is None:
        tmp["__dtag_fallback"] = "all"
        dtag_col = "__dtag_fallback"

    for (proto, dtag), g in tmp.groupby([proto_col, dtag_col], dropna=False):
        yield (str(proto), str(dtag)), g.copy()


def _group_suffix(proto: str, dtag: str) -> str:
    return f"proto_{_safe_filename(proto)}__dtag_{_safe_filename(dtag)}"


def _plot_save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {path}")


def _diverging_limits(arr: np.ndarray) -> Tuple[float, float]:
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return -1.0, 1.0
    m = float(np.max(np.abs(finite)))
    if m <= 0:
        m = 1.0
    return -m, m


def _sequential_limits(arr: np.ndarray) -> Tuple[float, float]:
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return 0.0, 1.0
    lo = float(np.min(finite))
    hi = float(np.max(finite))
    if not np.isfinite(lo) or not np.isfinite(hi):
        return 0.0, 1.0
    if hi <= lo:
        hi = lo + 1.0
    if lo > 0:
        lo = 0.0
    return lo, hi


def _bool_from_mixed_series(s: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(s):
        return s.fillna(False).astype(bool)

    out = s.astype(str).str.strip().str.lower().map(
        {
            "1": True,
            "0": False,
            "true": True,
            "false": False,
            "yes": True,
            "no": False,
            "y": True,
            "n": False,
            "clean": True,
            "attacked": False,
        }
    )

    mask_na = out.isna()
    if mask_na.any():
        try:
            out.loc[mask_na] = _to_numeric_series(s.loc[mask_na]) == 1.0
        except Exception:
            pass

    return out.fillna(False).astype(bool)


def _preferred_impact_key(cols: Dict[str, Optional[str]]) -> Optional[str]:
    for k in [
        "impact_bal_acc_mean",
        "bal_acc_drop_mean",
        "roc_auc_drop_mean",
        "f1_pos_drop_mean",
    ]:
        if cols.get(k) is not None:
            return k
    return None


def _preferred_detectability_key(cols: Dict[str, Optional[str]]) -> Optional[str]:
    for k in [
        "detectability_score_mean",
        "integrity_confusion_profile_jsd_mean",
        "integrity_confusion_profile_l1_mean",
        "integrity_pred_disagreement_mean",
        "integrity_pred_jsd_mean",
        "integrity_label_jsd_mean",
        "integrity_score_jsd_mean",
        "integrity_jsd_mean",
        "integrity_mmd_mean",
        "integrity_ks_reject05_mean",
    ]:
        if cols.get(k) is not None:
            return k
    return None


def _format_num(x: object, decimals: int = 3) -> str:
    try:
        v = float(x)
        if not np.isfinite(v):
            return "nan"
        return f"{v:.{decimals}f}"
    except Exception:
        return "nan"


def _build_attack_severity_labels(
    df: pd.DataFrame,
    attack_col: str,
    severity_col: Optional[str],
) -> pd.Series:
    attack = df[attack_col].astype(str)

    if severity_col is None or severity_col not in df.columns:
        return attack

    sev = _to_numeric_series(df[severity_col])
    sev_str = sev.map(lambda x: f"s={_format_num(x, 3)}" if pd.notna(x) else "s=nan")
    return attack + " | " + sev_str.astype(str)


def _build_attack_context_labels(
    df: pd.DataFrame,
    attack_col: str,
    svd_col: Optional[str],
    severity_col: Optional[str],
) -> pd.Series:
    attack = df[attack_col].astype(str)
    label = attack.copy()

    if svd_col is not None and svd_col in df.columns:
        d = _to_numeric_series(df[svd_col])
        d_str = d.map(lambda x: f"d={int(x)}" if pd.notna(x) else "d=nan")
        label = label + " | " + d_str.astype(str)

    if severity_col is not None and severity_col in df.columns:
        sev = _to_numeric_series(df[severity_col])
        sev_str = sev.map(lambda x: f"s={_format_num(x, 3)}" if pd.notna(x) else "s=nan")
        label = label + " | " + sev_str.astype(str)

    return label


def _annotate_top_points(
    ax,
    df: pd.DataFrame,
    xcol: str,
    ycol: str,
    labelcol: str,
    rankcol: Optional[str] = None,
    top_n: int = 8,
) -> None:
    if df.empty:
        return

    use_cols = [xcol, ycol, labelcol]
    if rankcol is not None and rankcol in df.columns:
        use_cols.append(rankcol)

    sub = df[use_cols].copy()
    sub[xcol] = _to_numeric_series(sub[xcol])
    sub[ycol] = _to_numeric_series(sub[ycol])
    sub = sub.dropna(subset=[xcol, ycol])

    if sub.empty:
        return

    if rankcol is not None and rankcol in sub.columns:
        sub["__rank"] = _to_numeric_series(sub[rankcol])
        sub = sub.sort_values("__rank", ascending=True).head(int(top_n))
    else:
        sub["__abs_y"] = sub[ycol].abs()
        sub = sub.sort_values("__abs_y", ascending=False).head(int(top_n))

    for _, r in sub.iterrows():
        ax.annotate(
            str(r[labelcol]),
            (float(r[xcol]), float(r[ycol])),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=7,
            alpha=0.9,
        )


def _weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    v = _to_numeric_series(values).astype(float)
    w = _to_numeric_series(weights).astype(float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if not mask.any():
        return float("nan")
    return float(np.average(v[mask].to_numpy(dtype=float), weights=w[mask].to_numpy(dtype=float)))


def _weighted_groupby_mean(
    df: pd.DataFrame,
    group_cols: List[str],
    value_cols: List[str],
    weight_col: Optional[str],
) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []

    for key, sub in df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)

        row: Dict[str, object] = {c: v for c, v in zip(group_cols, key)}
        row["n_rows"] = int(len(sub))

        if weight_col is not None and weight_col in sub.columns:
            w = _to_numeric_series(sub[weight_col]).fillna(0.0)
        else:
            w = pd.Series(1.0, index=sub.index, dtype=float)

        row["weight_sum"] = float(np.nansum(np.clip(w.to_numpy(dtype=float), a_min=0.0, a_max=None)))

        for c in value_cols:
            if c not in sub.columns:
                row[c] = float("nan")
            else:
                row[c] = _weighted_mean(sub[c], w)

        rows.append(row)

    return pd.DataFrame(rows)


def _weighted_abs_attack_order(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    weight_col: Optional[str],
    top_n: int,
) -> List[str]:
    rows = []
    for key, sub in df.groupby(group_col, dropna=False):
        if weight_col is not None and weight_col in sub.columns:
            w = _to_numeric_series(sub[weight_col]).fillna(0.0)
        else:
            w = pd.Series(1.0, index=sub.index, dtype=float)

        rows.append(
            {
                group_col: key,
                "__metric_abs": abs(_weighted_mean(sub[value_col], w)),
            }
        )

    rank_df = pd.DataFrame(rows)
    if rank_df.empty:
        return []

    return (
        rank_df.sort_values("__metric_abs", ascending=False)
        .head(int(top_n))[group_col]
        .astype(str)
        .tolist()
    )


def _heatmap_style(metric_key: str) -> Tuple[str, bool]:
    if metric_key.endswith("_drop_mean"):
        return "RdBu_r", True
    return "viridis", False


# ============================================================
# Column inference / preparation
# ============================================================

def _infer_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    cols: Dict[str, Optional[str]] = {}

    # IDs / grouping
    cols["protocol"] = _pick_col(df, ["protocol"])
    cols["dataset_tag"] = _pick_col(df, ["dataset_tag", "dataset", "dataset_id_tag"])
    cols["svd_dim"] = _pick_col(df, ["svd_dim", "dim", "d"])
    cols["model"] = _pick_col(df, ["model"])
    cols["model_family"] = _pick_col(df, ["model_family", "family"])
    cols["scale"] = _pick_col(df, ["scale"])
    cols["attack_name"] = _pick_col(df, ["attack", "attack_name", "attack_id"])
    cols["attack_family"] = _pick_col(df, ["attack_family", "attack_group", "family_attack"])
    cols["attack_priority_group"] = _pick_col(df, ["attack_priority_group"])
    cols["attack_suite"] = _pick_col(df, ["attack_suite"])
    cols["attack_is_clean"] = _pick_col(df, ["attack_is_clean", "is_clean", "clean", "is_clean_all"])
    cols["severity"] = _pick_col(
        df,
        [
            "attack_strength_nominal",
            "attack_strength_nominal_mean",
            "attack_strength_eff",
            "attack_strength_eff_mean",
            "attack_strength",
            "attack_severity",
            "severity",
            "strength",
        ],
    )

    # counts / robustness
    cols["n_seed_units"] = _pick_col(df, ["n_seed_units", "n_seeds", "n_runs", "weight_sum"])

    # metrics mean/std
    cols["bal_acc_mean"] = _pick_col(df, ["bal_acc_mean", "balanced_accuracy_mean", "balacc_mean"])
    cols["roc_auc_mean"] = _pick_col(df, ["roc_auc_mean", "auc_mean"])
    cols["f1_pos_mean"] = _pick_col(df, ["f1_pos_mean", "f1_mean"])
    cols["pred_error_rate_mean"] = _pick_col(df, ["pred_error_rate_mean"])

    cols["bal_acc_std"] = _pick_col(df, ["bal_acc_std", "balanced_accuracy_std", "balacc_std"])
    cols["roc_auc_std"] = _pick_col(df, ["roc_auc_std", "auc_std"])
    cols["f1_pos_std"] = _pick_col(df, ["f1_pos_std", "f1_std"])

    # drops
    cols["bal_acc_drop_mean"] = _pick_col(df, ["bal_acc_drop_mean", "balanced_accuracy_drop_mean", "balacc_drop_mean"])
    cols["roc_auc_drop_mean"] = _pick_col(df, ["roc_auc_drop_mean", "auc_drop_mean"])
    cols["f1_pos_drop_mean"] = _pick_col(df, ["f1_pos_drop_mean", "f1_drop_mean"])
    cols["pred_error_rate_drop_mean"] = _pick_col(df, ["pred_error_rate_drop_mean"])

    # impact / auditability
    cols["impact_bal_acc_mean"] = _pick_col(df, ["impact_bal_acc_mean"])
    cols["impact_f1_mean"] = _pick_col(df, ["impact_f1_mean"])
    cols["impact_roc_auc_mean"] = _pick_col(df, ["impact_roc_auc_mean"])
    cols["impact_pred_error_mean"] = _pick_col(df, ["impact_pred_error_mean"])

    cols["detectability_score_mean"] = _pick_col(df, ["detectability_score_mean"])
    cols["detectability_score_std"] = _pick_col(df, ["detectability_score_std"])
    cols["stealth_score_mean"] = _pick_col(df, ["stealth_score_mean"])
    cols["stealth_rank_overall"] = _pick_col(df, ["stealth_rank_overall"])
    cols["stealth_rank_within_model"] = _pick_col(df, ["stealth_rank_within_model"])
    cols["stealth_rank_within_protocol_dataset_model"] = _pick_col(df, ["stealth_rank_within_protocol_dataset_model"])

    # integrity / detectability raw or richer
    cols["integrity_jsd_mean"] = _pick_col(df, ["integrity_jsd_mean", "jsd_mean"])
    cols["integrity_mmd_mean"] = _pick_col(df, ["integrity_mmd_mean", "mmd_mean"])
    cols["integrity_score_jsd_mean"] = _pick_col(df, ["integrity_score_jsd_mean", "score_jsd_mean"])
    cols["integrity_ks_reject05_mean"] = _pick_col(df, ["integrity_ks_reject05_mean", "ks_reject05_mean"])

    cols["integrity_label_prior_shift_mean"] = _pick_col(df, ["integrity_label_prior_shift_mean"])
    cols["integrity_label_jsd_mean"] = _pick_col(df, ["integrity_label_jsd_mean"])
    cols["integrity_pred_pos_rate_shift_mean"] = _pick_col(df, ["integrity_pred_pos_rate_shift_mean"])
    cols["integrity_pred_disagreement_mean"] = _pick_col(df, ["integrity_pred_disagreement_mean"])
    cols["integrity_pred_jsd_mean"] = _pick_col(df, ["integrity_pred_jsd_mean"])
    cols["integrity_confusion_profile_l1_mean"] = _pick_col(df, ["integrity_confusion_profile_l1_mean"])
    cols["integrity_confusion_profile_jsd_mean"] = _pick_col(df, ["integrity_confusion_profile_jsd_mean"])

    # time
    cols["train_time_s_mean"] = _pick_col(df, ["train_time_s_mean", "fit_time_s_mean", "train_time_mean"])
    cols["predict_time_s_mean"] = _pick_col(df, ["predict_time_s_mean", "pred_time_s_mean", "inference_time_s_mean"])
    cols["scores_time_s_mean"] = _pick_col(df, ["scores_time_s_mean"])
    cols["signals_time_s_mean"] = _pick_col(df, ["signals_time_s_mean"])
    cols["ref_scores_time_s_mean"] = _pick_col(df, ["ref_scores_time_s_mean"])
    cols["ref_predict_time_s_mean"] = _pick_col(df, ["ref_predict_time_s_mean"])

    return cols


def _prepare_df(df: pd.DataFrame, cols: Dict[str, Optional[str]]) -> Tuple[pd.DataFrame, Dict[str, Optional[str]]]:
    out = df.copy()
    cols = dict(cols)

    # protocol normalized
    if cols["protocol"] is not None:
        out["__protocol_norm"] = out[cols["protocol"]].map(_normalize_protocol)
        cols["protocol"] = "__protocol_norm"

    # model family normalized
    if cols["model_family"] is not None:
        out["__model_family_norm"] = out[cols["model_family"]].map(_normalize_family)
        cols["model_family"] = "__model_family_norm"
    elif cols["model"] is not None:
        out["__model_family_norm"] = out[cols["model"]].map(_normalize_family)
        cols["model_family"] = "__model_family_norm"

    # exact model fallback
    if cols["model"] is None and cols["model_family"] is not None:
        out["__model_fallback"] = out[cols["model_family"]].astype(str)
        cols["model"] = "__model_fallback"

    # attack family fallback
    if cols["attack_family"] is None and cols["attack_name"] is not None:
        out["__attack_family_fallback"] = out[cols["attack_name"]].astype(str).str.replace(
            r"_[0-9]+(?:\.[0-9]+)?$", "", regex=True
        )
        cols["attack_family"] = "__attack_family_fallback"

    # attack priority fallback
    if cols["attack_priority_group"] is None and cols["attack_family"] is not None:
        out["__attack_priority_group_fallback"] = out[cols["attack_family"]].astype(str)
        cols["attack_priority_group"] = "__attack_priority_group_fallback"

    # severity fallback
    if cols["severity"] is None:
        if cols["attack_name"] is not None:
            out["__severity_inferred"] = out[cols["attack_name"]].map(_extract_severity_from_name)
            cols["severity"] = "__severity_inferred"
        else:
            out["__severity_inferred"] = np.nan
            cols["severity"] = "__severity_inferred"

    # clean flag
    if cols["attack_is_clean"] is not None:
        out["__is_clean_norm"] = _bool_from_mixed_series(out[cols["attack_is_clean"]])
        cols["attack_is_clean"] = "__is_clean_norm"
    elif cols["attack_name"] is not None:
        out["__is_clean_norm"] = out[cols["attack_name"]].astype(str).str.strip().str.lower().eq("clean")
        cols["attack_is_clean"] = "__is_clean_norm"

    numeric_keys = [
        "svd_dim",
        "severity",
        "n_seed_units",
        "bal_acc_mean", "roc_auc_mean", "f1_pos_mean", "pred_error_rate_mean",
        "bal_acc_std", "roc_auc_std", "f1_pos_std",
        "bal_acc_drop_mean", "roc_auc_drop_mean", "f1_pos_drop_mean", "pred_error_rate_drop_mean",
        "impact_bal_acc_mean", "impact_f1_mean", "impact_roc_auc_mean", "impact_pred_error_mean",
        "detectability_score_mean", "detectability_score_std",
        "stealth_score_mean", "stealth_rank_overall", "stealth_rank_within_model", "stealth_rank_within_protocol_dataset_model",
        "integrity_jsd_mean", "integrity_mmd_mean", "integrity_score_jsd_mean", "integrity_ks_reject05_mean",
        "integrity_label_prior_shift_mean", "integrity_label_jsd_mean",
        "integrity_pred_pos_rate_shift_mean", "integrity_pred_disagreement_mean", "integrity_pred_jsd_mean",
        "integrity_confusion_profile_l1_mean", "integrity_confusion_profile_jsd_mean",
        "train_time_s_mean", "predict_time_s_mean", "scores_time_s_mean", "signals_time_s_mean",
        "ref_scores_time_s_mean", "ref_predict_time_s_mean",
    ]
    for k in numeric_keys:
        c = cols.get(k)
        if c is not None and c in out.columns:
            out[c] = _to_numeric_series(out[c])

    # derive impact if missing
    if cols.get("impact_bal_acc_mean") is None and cols.get("bal_acc_drop_mean") is not None:
        out["__impact_bal_acc_derived"] = (-_to_numeric_series(out[cols["bal_acc_drop_mean"]])).clip(lower=0.0)
        cols["impact_bal_acc_mean"] = "__impact_bal_acc_derived"

    if cols.get("impact_f1_mean") is None and cols.get("f1_pos_drop_mean") is not None:
        out["__impact_f1_derived"] = (-_to_numeric_series(out[cols["f1_pos_drop_mean"]])).clip(lower=0.0)
        cols["impact_f1_mean"] = "__impact_f1_derived"

    if cols.get("impact_roc_auc_mean") is None and cols.get("roc_auc_drop_mean") is not None:
        out["__impact_roc_auc_derived"] = (-_to_numeric_series(out[cols["roc_auc_drop_mean"]])).clip(lower=0.0)
        cols["impact_roc_auc_mean"] = "__impact_roc_auc_derived"

    if cols.get("impact_pred_error_mean") is None and cols.get("pred_error_rate_drop_mean") is not None:
        out["__impact_pred_error_derived"] = _to_numeric_series(out[cols["pred_error_rate_drop_mean"]]).clip(lower=0.0)
        cols["impact_pred_error_mean"] = "__impact_pred_error_derived"

    # derive stealth if missing
    if (
        cols.get("stealth_score_mean") is None
        and cols.get("impact_bal_acc_mean") is not None
        and cols.get("detectability_score_mean") is not None
    ):
        det = _to_numeric_series(out[cols["detectability_score_mean"]]).clip(lower=0.0, upper=1.0)
        imp = _to_numeric_series(out[cols["impact_bal_acc_mean"]])
        out["__stealth_derived"] = imp * (1.0 - det)
        cols["stealth_score_mean"] = "__stealth_derived"

    # derived attack labels
    if cols.get("attack_name") is not None:
        out["__attack_severity_label"] = _build_attack_severity_labels(
            out,
            attack_col=cols["attack_name"],
            severity_col=cols.get("severity"),
        )
        cols["attack_severity_label"] = "__attack_severity_label"

        out["__attack_context_label"] = _build_attack_context_labels(
            out,
            attack_col=cols["attack_name"],
            svd_col=cols.get("svd_dim"),
            severity_col=cols.get("severity"),
        )
        cols["attack_context_label"] = "__attack_context_label"
    else:
        cols["attack_severity_label"] = None
        cols["attack_context_label"] = None

    return out, cols


def _filter_df(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
    only_model: Optional[str] = None,
    only_protocol: Optional[str] = None,
    only_dataset_tag: Optional[str] = None,
    only_family: Optional[str] = None,
) -> pd.DataFrame:
    d = df.copy()

    if only_model and cols["model"] is not None:
        d = d[d[cols["model"]].astype(str).str.contains(only_model, case=False, na=False)]

    if only_family and cols["model_family"] is not None:
        d = d[d[cols["model_family"]].astype(str).str.contains(only_family, case=False, na=False)]

    if only_protocol and cols["protocol"] is not None:
        d = d[d[cols["protocol"]].astype(str).str.lower() == only_protocol.strip().lower()]

    if only_dataset_tag and cols["dataset_tag"] is not None:
        d = d[d[cols["dataset_tag"]].astype(str).str.contains(only_dataset_tag, case=False, na=False)]

    return d


def _clean_rows_only(df: pd.DataFrame, cols: Dict[str, Optional[str]]) -> pd.DataFrame:
    d = df.copy()
    if cols["attack_is_clean"] is not None:
        return d[d[cols["attack_is_clean"]] == True].copy()
    if cols["attack_name"] is not None:
        return d[d[cols["attack_name"]].astype(str).str.lower() == "clean"].copy()
    return d.iloc[0:0].copy()


def _attacked_rows_only(df: pd.DataFrame, cols: Dict[str, Optional[str]]) -> pd.DataFrame:
    d = df.copy()
    if cols["attack_is_clean"] is not None:
        return d[d[cols["attack_is_clean"]] == False].copy()
    if cols["attack_name"] is not None:
        return d[~d[cols["attack_name"]].astype(str).str.lower().eq("clean")].copy()
    return d.iloc[0:0].copy()


# ============================================================
# Summary exports
# ============================================================

def export_summary_tables(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
    outdir: Path,
    top_n_summary_stealth: int = 50,
) -> None:
    weight_col = cols.get("n_seed_units")

    metric_keys = [
        "bal_acc_mean", "roc_auc_mean", "f1_pos_mean", "pred_error_rate_mean",
        "bal_acc_drop_mean", "roc_auc_drop_mean", "f1_pos_drop_mean", "pred_error_rate_drop_mean",
        "impact_bal_acc_mean", "impact_f1_mean", "impact_roc_auc_mean", "impact_pred_error_mean",
        "detectability_score_mean", "detectability_score_std", "stealth_score_mean",
        "integrity_jsd_mean", "integrity_mmd_mean", "integrity_score_jsd_mean", "integrity_ks_reject05_mean",
        "integrity_label_prior_shift_mean", "integrity_label_jsd_mean",
        "integrity_pred_pos_rate_shift_mean", "integrity_pred_disagreement_mean", "integrity_pred_jsd_mean",
        "integrity_confusion_profile_l1_mean", "integrity_confusion_profile_jsd_mean",
        "train_time_s_mean", "predict_time_s_mean", "scores_time_s_mean", "signals_time_s_mean",
        "ref_scores_time_s_mean", "ref_predict_time_s_mean",
    ]
    metric_cols = [cols[k] for k in metric_keys if cols.get(k) is not None]

    base_group = [c for c in [cols["protocol"], cols["dataset_tag"]] if c is not None]

    # clean summary
    d_clean = _clean_rows_only(df, cols)
    clean_keys = [c for c in [*base_group, cols["model"], cols["model_family"], cols["svd_dim"]] if c is not None]
    if clean_keys and metric_cols and not d_clean.empty:
        g = _weighted_groupby_mean(
            d_clean,
            group_cols=clean_keys,
            value_cols=metric_cols,
            weight_col=weight_col,
        )
        sort_cols = [c for c in [cols["protocol"], cols["dataset_tag"], cols["model"], cols["svd_dim"]] if c in g.columns]
        if sort_cols:
            g = g.sort_values(sort_cols, ascending=True, na_position="last")
        g.to_csv(outdir / "summary_clean_by_model_dim.csv", index=False)
        print(f"[OK] {outdir / 'summary_clean_by_model_dim.csv'}")

    # attacked detailed summary
    d_att = _attacked_rows_only(df, cols)
    att_keys = [
        c for c in [
            *base_group,
            cols["model"],
            cols["model_family"],
            cols["svd_dim"],
            cols["attack_priority_group"],
            cols["attack_family"],
            cols["severity"],
            cols["attack_name"],
            cols.get("attack_severity_label"),
            cols.get("attack_context_label"),
        ]
        if c is not None
    ]
    if att_keys and metric_cols and not d_att.empty:
        g2 = _weighted_groupby_mean(
            d_att,
            group_cols=att_keys,
            value_cols=metric_cols,
            weight_col=weight_col,
        )
        g2.to_csv(outdir / "summary_attacked_by_model_dim_family_severity.csv", index=False)
        print(f"[OK] {outdir / 'summary_attacked_by_model_dim_family_severity.csv'}")

    # compact stealth summary by model/dim
    if cols["model"] is not None and not d_att.empty:
        compact_metrics = [
            c for c in [
                cols["impact_bal_acc_mean"],
                cols["detectability_score_mean"],
                cols["stealth_score_mean"],
                cols["bal_acc_drop_mean"],
                cols["roc_auc_drop_mean"],
                cols["f1_pos_drop_mean"],
            ]
            if c is not None
        ]
        compact_keys = [c for c in [*base_group, cols["model"], cols["model_family"], cols["svd_dim"]] if c is not None]
        if compact_metrics and compact_keys:
            g3 = _weighted_groupby_mean(
                d_att,
                group_cols=compact_keys,
                value_cols=compact_metrics,
                weight_col=weight_col,
            )
            stealth_col = cols.get("stealth_score_mean")
            if stealth_col is not None and stealth_col in g3.columns:
                sort_cols = [c for c in [cols["protocol"], cols["dataset_tag"], cols["model"], cols["svd_dim"]] if c is not None]
                g3 = g3.sort_values(sort_cols + [stealth_col], ascending=[True] * len(sort_cols) + [False], na_position="last")
            g3.to_csv(outdir / "summary_stealth_by_model.csv", index=False)
            print(f"[OK] {outdir / 'summary_stealth_by_model.csv'}")

    # top stealth overall
    if not d_att.empty and cols.get("stealth_score_mean") is not None:
        top_cols = [
            c for c in [
                cols["protocol"], cols["dataset_tag"], cols["model"], cols["model_family"], cols["svd_dim"],
                cols["attack_priority_group"], cols["attack_family"], cols["severity"], cols["attack_name"],
                cols.get("attack_severity_label"), cols.get("attack_context_label"),
                cols["impact_bal_acc_mean"], cols["detectability_score_mean"], cols["stealth_score_mean"],
                cols["bal_acc_drop_mean"], cols["roc_auc_drop_mean"], cols["f1_pos_drop_mean"],
                cols["n_seed_units"],
            ]
            if c is not None
        ]

        g4 = d_att[top_cols].copy()
        g4 = g4.sort_values(cols["stealth_score_mean"], ascending=False, na_position="last").head(int(top_n_summary_stealth))
        g4.to_csv(outdir / "summary_top_stealth_overall.csv", index=False)
        print(f"[OK] {outdir / 'summary_top_stealth_overall.csv'}")

        g4_full = d_att[top_cols].copy()
        g4_full = g4_full.sort_values(cols["stealth_score_mean"], ascending=False, na_position="last")
        g4_full.to_csv(outdir / "summary_stealth_overall_ranked.csv", index=False)
        print(f"[OK] {outdir / 'summary_stealth_overall_ranked.csv'}")


# ============================================================
# Plotters
# ============================================================

def plot_clean_metric_by_svd(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
    outdir: Path,
    metric_key: str,
    std_key: Optional[str],
    outname_prefix: str,
) -> None:
    if cols["svd_dim"] is None or cols["model"] is None:
        print(f"[WARN] No se puede hacer {outname_prefix} (faltan svd_dim/model).")
        return

    metric_col = cols.get(metric_key)
    std_col = cols.get(std_key) if std_key else None

    if metric_col is None:
        print(f"[WARN] No se puede hacer {outname_prefix} (falta {metric_key}).")
        return

    d = _clean_rows_only(df, cols).copy()
    if d.empty:
        print(f"[WARN] No hay filas clean para {outname_prefix}.")
        return

    for (proto, dtag), dg in _iter_protocol_dataset_groups(d, cols):
        dg = dg.dropna(subset=[cols["svd_dim"]]).copy()
        if dg.empty:
            continue

        fig = plt.figure(figsize=(11, 6))
        ax = plt.gca()

        for model, gm in dg.groupby(cols["model"], dropna=False):
            gm = gm.sort_values(cols["svd_dim"])
            x = _to_numeric_series(gm[cols["svd_dim"]]).values
            y = _to_numeric_series(gm[metric_col]).values
            if np.isfinite(y).sum() == 0:
                continue

            if std_col is not None and std_col in gm.columns:
                yerr = _to_numeric_series(gm[std_col]).values
                if np.isfinite(yerr).sum() > 0:
                    ax.errorbar(x, y, yerr=yerr, marker="o", capsize=3, label=str(model))
                else:
                    ax.plot(x, y, marker="o", label=str(model))
            else:
                ax.plot(x, y, marker="o", label=str(model))

        ax.set_xlabel("SVD dim")
        ax.set_ylabel(metric_col)
        ax.set_title(f"{outname_prefix} | {proto} | {dtag}")
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=8, ncol=2)

        fname = outdir / f"{outname_prefix}__metric_{_safe_filename(metric_col)}__{_group_suffix(proto, dtag)}.png"
        _plot_save(fig, fname)


def plot_attack_strength_vs_metric_by_family(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
    outdir: Path,
    metric_key: str,
    outname_prefix: str,
    top_n_attacks_per_family: int = 6,
) -> None:
    if cols["model"] is None or cols["attack_name"] is None or cols["severity"] is None or cols["attack_family"] is None:
        print(f"[WARN] No se puede hacer {outname_prefix} (faltan model/attack_name/severity/attack_family).")
        return

    metric_col = cols.get(metric_key)
    if metric_col is None:
        print(f"[WARN] No se puede hacer {outname_prefix} (falta {metric_key}).")
        return

    d = _attacked_rows_only(df, cols).copy()
    if d.empty:
        print(f"[WARN] No hay filas attacked para {outname_prefix}.")
        return

    d["__sev"] = _to_numeric_series(d[cols["severity"]])
    d["__metric"] = _to_numeric_series(d[metric_col])
    d = d.dropna(subset=["__sev", "__metric"])
    if d.empty:
        print(f"[WARN] Sin datos válidos para {outname_prefix}.")
        return

    weight_col = cols.get("n_seed_units")

    for (proto, dtag), dg in _iter_protocol_dataset_groups(d, cols):
        for model, gm in dg.groupby(cols["model"], dropna=False):
            for fam, gmf in gm.groupby(cols["attack_family"], dropna=False):
                if gmf.empty:
                    continue

                attack_order = _weighted_abs_attack_order(
                    gmf,
                    group_col=cols["attack_name"],
                    value_col="__metric",
                    weight_col=weight_col,
                    top_n=top_n_attacks_per_family,
                )
                if not attack_order:
                    continue

                sub = gmf[gmf[cols["attack_name"]].astype(str).isin(attack_order)].copy()
                if sub.empty:
                    continue
                if sub["__sev"].nunique(dropna=True) < 2:
                    continue

                grp = _weighted_groupby_mean(
                    sub,
                    group_cols=[cols["attack_name"], "__sev"],
                    value_cols=["__metric"],
                    weight_col=weight_col,
                ).sort_values([cols["attack_name"], "__sev"])

                fig = plt.figure(figsize=(10.5, 6))
                ax = plt.gca()

                for attack_name, gf in grp.groupby(cols["attack_name"], dropna=False):
                    x = _to_numeric_series(gf["__sev"]).astype(float).values
                    y = _to_numeric_series(gf["__metric"]).astype(float).values
                    order = np.argsort(x)
                    ax.plot(x[order], y[order], marker="o", label=str(attack_name))

                ax.set_xlabel("Attack strength (explicit nominal/effective preferred)")
                ax.set_ylabel(metric_col)
                ax.set_title(f"{model} | {fam} | {outname_prefix} | {proto} | {dtag}")
                ax.grid(True, alpha=0.25)
                ax.legend(fontsize=7, ncol=2)

                fname = outdir / (
                    f"{outname_prefix}__metric_{_safe_filename(metric_col)}"
                    f"__{_safe_filename(model)}__fam_{_safe_filename(fam)}"
                    f"__{_group_suffix(proto, dtag)}.png"
                )
                _plot_save(fig, fname)


def plot_detectability_vs_impact_scatter(df: pd.DataFrame, cols: Dict[str, Optional[str]], outdir: Path) -> None:
    if cols["model"] is None or cols["attack_family"] is None or cols["attack_name"] is None:
        print("[WARN] No se puede hacer detectability_vs_impact_scatter (faltan model/attack_family/attack_name).")
        return

    impact_key = _preferred_impact_key(cols)
    det_key = _preferred_detectability_key(cols)
    if impact_key is None or det_key is None:
        print("[WARN] No se puede hacer detectability_vs_impact_scatter (faltan columnas de impacto/detectabilidad).")
        return

    impact_col = cols[impact_key]
    signal_col = cols[det_key]

    d = _attacked_rows_only(df, cols).copy()
    if d.empty:
        print("[WARN] No hay filas attacked para detectability_vs_impact_scatter.")
        return

    d["__impact"] = _to_numeric_series(d[impact_col])
    d["__sig"] = _to_numeric_series(d[signal_col])
    d = d.dropna(subset=["__impact", "__sig"])
    if d.empty:
        print("[WARN] Sin datos válidos para detectability_vs_impact_scatter.")
        return

    label_col = cols.get("attack_context_label") or cols.get("attack_name")
    weight_col = cols.get("n_seed_units")

    corr_rows = []
    for (proto, dtag), dg in _iter_protocol_dataset_groups(d, cols):
        for model, gm in dg.groupby(cols["model"], dropna=False):
            fig = plt.figure(figsize=(9, 6))
            ax = plt.gca()

            for fam, gf in gm.groupby(cols["attack_family"], dropna=False):
                if gf.empty:
                    continue

                if weight_col is not None and weight_col in gf.columns:
                    weights = _to_numeric_series(gf[weight_col]).fillna(1.0).clip(lower=1.0)
                    sizes = 25.0 + 12.0 * np.sqrt(weights.to_numpy(dtype=float))
                else:
                    weights = None
                    sizes = 35.0

                ax.scatter(gf["__sig"].values, gf["__impact"].values, s=sizes, label=str(fam), alpha=0.8)

                corr_rows.append(
                    {
                        "protocol": proto,
                        "dataset_tag": dtag,
                        "model": model,
                        "attack_family": fam,
                        "n_points": int(len(gf)),
                        "signal_col": signal_col,
                        "impact_col": impact_col,
                        "corr_pearson": _corr_safe(gf["__sig"], gf["__impact"]),
                        "corr_weighted": _weighted_corr_safe(
                            gf["__sig"],
                            gf["__impact"],
                            gf[weight_col] if (weight_col is not None and weight_col in gf.columns) else None,
                        ),
                    }
                )

            rank_col = (
                cols.get("stealth_rank_within_protocol_dataset_model")
                or cols.get("stealth_rank_within_model")
                or cols.get("stealth_rank_overall")
            )
            _annotate_top_points(
                ax=ax,
                df=gm,
                xcol="__sig",
                ycol="__impact",
                labelcol=label_col,
                rankcol=rank_col,
                top_n=8,
            )

            corr_plain = _corr_safe(gm["__sig"], gm["__impact"])
            corr_weighted = _weighted_corr_safe(
                gm["__sig"],
                gm["__impact"],
                gm[weight_col] if (weight_col is not None and weight_col in gm.columns) else None,
            )

            title = f"{model} | detectability vs impact | {proto} | {dtag}"
            if np.isfinite(corr_weighted):
                title += f" (w-corr={corr_weighted:.3f})"
            elif np.isfinite(corr_plain):
                title += f" (corr={corr_plain:.3f})"

            ax.set_xlabel(signal_col)
            ax.set_ylabel(impact_col)
            ax.set_title(title)
            ax.grid(True, alpha=0.25)
            ax.legend(fontsize=8, ncol=2)

            fname = outdir / (
                f"detectability_vs_impact_scatter"
                f"__impact_{_safe_filename(impact_col)}"
                f"__det_{_safe_filename(signal_col)}"
                f"__{_safe_filename(model)}__{_group_suffix(proto, dtag)}.png"
            )
            _plot_save(fig, fname)

    if corr_rows:
        pd.DataFrame(corr_rows).to_csv(outdir / "detectability_vs_impact_correlations.csv", index=False)
        print(f"[OK] {outdir / 'detectability_vs_impact_correlations.csv'}")


def plot_time_cost_by_model_dim_train_infer(df: pd.DataFrame, cols: Dict[str, Optional[str]], outdir: Path) -> None:
    if cols["svd_dim"] is None or cols["model"] is None:
        print("[WARN] No se puede hacer time_cost_by_model_dim_train_infer (faltan svd_dim/model).")
        return

    d = _clean_rows_only(df, cols).copy()
    if d.empty:
        d = df.copy()

    time_keys = [
        ("train_time_s_mean", "train"),
        ("predict_time_s_mean", "predict"),
        ("scores_time_s_mean", "scores"),
        ("ref_scores_time_s_mean", "ref_scores"),
        ("ref_predict_time_s_mean", "ref_predict"),
    ]

    for (proto, dtag), dg in _iter_protocol_dataset_groups(d, cols):
        dg = dg.dropna(subset=[cols["svd_dim"]]).copy()
        if dg.empty:
            continue

        fig = plt.figure(figsize=(11, 6))
        ax = plt.gca()

        for model, gm in dg.groupby(cols["model"], dropna=False):
            gm = gm.sort_values(cols["svd_dim"])
            x = _to_numeric_series(gm[cols["svd_dim"]]).values

            for key, lab in time_keys:
                c = cols.get(key)
                if c is None:
                    continue
                y = _to_numeric_series(gm[c]).values
                if np.isfinite(y).sum() == 0:
                    continue
                ax.plot(x, y, marker="o", label=f"{model} | {lab}")

        ax.set_xlabel("SVD dim")
        ax.set_ylabel("Time (s)")
        ax.set_title(f"Training / inference time by exact model and SVD | {proto} | {dtag}")
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=8, ncol=2)

        fname = outdir / f"time_cost_train_infer_by_model_dim__{_group_suffix(proto, dtag)}.png"
        _plot_save(fig, fname)


def plot_time_cost_by_model_dim_audit(df: pd.DataFrame, cols: Dict[str, Optional[str]], outdir: Path) -> None:
    if cols["svd_dim"] is None or cols["model"] is None:
        print("[WARN] No se puede hacer time_cost_by_model_dim_audit (faltan svd_dim/model).")
        return

    d = _clean_rows_only(df, cols).copy()
    if d.empty:
        d = df.copy()

    time_keys = [
        ("signals_time_s_mean", "signals"),
    ]

    for (proto, dtag), dg in _iter_protocol_dataset_groups(d, cols):
        dg = dg.dropna(subset=[cols["svd_dim"]]).copy()
        if dg.empty:
            continue

        fig = plt.figure(figsize=(11, 6))
        ax = plt.gca()

        for model, gm in dg.groupby(cols["model"], dropna=False):
            gm = gm.sort_values(cols["svd_dim"])
            x = _to_numeric_series(gm[cols["svd_dim"]]).values

            for key, lab in time_keys:
                c = cols.get(key)
                if c is None:
                    continue
                y = _to_numeric_series(gm[c]).values
                if np.isfinite(y).sum() == 0:
                    continue
                ax.plot(x, y, marker="o", label=f"{model} | {lab}")

        ax.set_xlabel("SVD dim")
        ax.set_ylabel("Time (s)")
        ax.set_title(f"Audit overhead by exact model and SVD | {proto} | {dtag}")
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=8, ncol=2)

        fname = outdir / f"time_cost_audit_by_model_dim__{_group_suffix(proto, dtag)}.png"
        _plot_save(fig, fname)


def plot_attack_family_boxplot(df: pd.DataFrame, cols: Dict[str, Optional[str]], outdir: Path) -> None:
    if cols["attack_family"] is None or cols["model"] is None:
        print("[WARN] No se puede hacer attack_family_boxplot (faltan attack_family/model).")
        return

    metric_key = "stealth_score_mean" if cols.get("stealth_score_mean") is not None else _preferred_impact_key(cols)
    metric_col = cols.get(metric_key) if metric_key is not None else None

    if metric_col is None:
        print("[WARN] No se puede hacer attack_family_boxplot (falta métrica).")
        return

    d = _attacked_rows_only(df, cols).copy()
    if d.empty:
        print("[WARN] No hay filas attacked para attack_family_boxplot.")
        return

    d["__metric"] = _to_numeric_series(d[metric_col])

    for (proto, dtag), dg in _iter_protocol_dataset_groups(d, cols):
        for model, gm in dg.groupby(cols["model"], dropna=False):
            fams, vals = [], []
            for fam, gf in gm.groupby(cols["attack_family"], dropna=False):
                x = _to_numeric_series(gf["__metric"]).dropna().values
                if len(x) == 0:
                    continue
                fams.append(str(fam))
                vals.append(x)

            if not vals:
                continue

            fig = plt.figure(figsize=(11, 6))
            ax = plt.gca()
            try:
                ax.boxplot(vals, tick_labels=fams, showfliers=True)
            except TypeError:
                ax.boxplot(vals, labels=fams, showfliers=True)
            ax.set_xticklabels(fams, rotation=45, ha="right")
            ax.set_ylabel(metric_col)
            ax.set_title(f"{model} | attack family distribution | {proto} | {dtag}")
            ax.grid(True, alpha=0.25)

            fname = outdir / (
                f"attack_family_boxplot__metric_{_safe_filename(metric_col)}"
                f"__{_safe_filename(model)}__{_group_suffix(proto, dtag)}.png"
            )
            _plot_save(fig, fname)


def plot_metric_heatmap_by_model(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
    outdir: Path,
    metric_key: str,
    outname_prefix: str,
    top_n_attacks: int = 18,
) -> None:
    """
    IMPORTANT:
    Main heatmap uses attack + severity rows, NOT raw attack name only.
    This avoids collapsing multiple severities into a single average row.
    """
    if cols["model"] is None or cols["svd_dim"] is None or cols.get("attack_severity_label") is None:
        print(f"[WARN] No se puede hacer {outname_prefix} (faltan model/svd_dim/attack_severity_label).")
        return

    metric_col = cols.get(metric_key)
    if metric_col is None:
        print(f"[WARN] No se puede hacer {outname_prefix} (falta {metric_key}).")
        return

    d = _attacked_rows_only(df, cols).copy()
    if d.empty:
        print(f"[WARN] No hay filas attacked para {outname_prefix}.")
        return

    d["__metric"] = _to_numeric_series(d[metric_col])
    d["__svd"] = _to_numeric_series(d[cols["svd_dim"]])
    d = d.dropna(subset=["__metric", "__svd"])
    if d.empty:
        print(f"[WARN] Sin datos válidos para {outname_prefix}.")
        return

    weight_col = cols.get("n_seed_units")
    row_label_col = cols["attack_severity_label"]

    cmap, use_diverging = _heatmap_style(metric_key)

    for (proto, dtag), dg in _iter_protocol_dataset_groups(d, cols):
        for model, gm in dg.groupby(cols["model"], dropna=False):
            attack_order = _weighted_abs_attack_order(
                gm,
                group_col=row_label_col,
                value_col="__metric",
                weight_col=weight_col,
                top_n=top_n_attacks,
            )
            if not attack_order:
                continue

            grp = _weighted_groupby_mean(
                gm[gm[row_label_col].astype(str).isin(attack_order)].copy(),
                group_cols=[row_label_col, "__svd"],
                value_cols=["__metric"],
                weight_col=weight_col,
            )

            if grp.empty:
                continue

            piv = grp.pivot_table(index=row_label_col, columns="__svd", values="__metric", aggfunc="mean")
            piv = piv.reindex(index=attack_order)
            piv = piv.sort_index(axis=1)
            if piv.empty:
                continue

            fig = plt.figure(figsize=(10, max(5, 0.35 * len(piv) + 2)))
            ax = plt.gca()
            arr = piv.to_numpy(dtype=float)

            if use_diverging:
                vmin, vmax = _diverging_limits(arr)
                im = ax.imshow(arr, aspect="auto", interpolation="nearest", cmap=cmap, vmin=vmin, vmax=vmax)
            else:
                vmin, vmax = _sequential_limits(arr)
                im = ax.imshow(arr, aspect="auto", interpolation="nearest", cmap=cmap, vmin=vmin, vmax=vmax)

            plt.colorbar(im, label=metric_col)
            ax.set_yticks(np.arange(len(piv.index)))
            ax.set_yticklabels([str(x) for x in piv.index])
            ax.set_xticks(np.arange(len(piv.columns)))
            ax.set_xticklabels([str(int(x)) if np.isfinite(x) else "nan" for x in piv.columns])
            ax.set_xlabel("SVD dim")
            ax.set_ylabel("Attack | severity")
            ax.set_title(f"{model} | {outname_prefix} | {proto} | {dtag}")

            fname = outdir / (
                f"{outname_prefix}__metric_{_safe_filename(metric_col)}"
                f"__{_safe_filename(model)}__{_group_suffix(proto, dtag)}.png"
            )
            _plot_save(fig, fname)


def plot_top_stealth_bar_by_model(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
    outdir: Path,
    top_n: int = 12,
) -> None:
    if cols["stealth_score_mean"] is None or cols["model"] is None:
        print("[WARN] No se puede hacer top_stealth_bar_by_model (faltan stealth/model).")
        return

    d = _attacked_rows_only(df, cols).copy()
    if d.empty:
        print("[WARN] No hay filas attacked para top_stealth_bar_by_model.")
        return

    d["__stealth"] = _to_numeric_series(d[cols["stealth_score_mean"]])
    d = d.dropna(subset=["__stealth"])
    if d.empty:
        print("[WARN] Sin datos válidos para top_stealth_bar_by_model.")
        return

    label_col = cols.get("attack_context_label") or cols.get("attack_name")
    weight_col = cols.get("n_seed_units")

    for (proto, dtag), dg in _iter_protocol_dataset_groups(d, cols):
        for model, gm in dg.groupby(cols["model"], dropna=False):
            # rank contexts by weighted stealth if possible
            if label_col is not None:
                order = _weighted_abs_attack_order(
                    gm,
                    group_col=label_col,
                    value_col="__stealth",
                    weight_col=weight_col,
                    top_n=top_n,
                )
                if not order:
                    continue

                grp = _weighted_groupby_mean(
                    gm[gm[label_col].astype(str).isin(order)].copy(),
                    group_cols=[label_col],
                    value_cols=["__stealth"],
                    weight_col=weight_col,
                )
                grp = grp.sort_values("__stealth", ascending=False, na_position="last")
            else:
                grp = gm.sort_values("__stealth", ascending=False, na_position="last").head(int(top_n)).copy()
                grp[label_col] = grp.index.astype(str)

            if grp.empty:
                continue

            labels = grp[label_col].astype(str).tolist()
            y = grp["__stealth"].astype(float).values

            fig = plt.figure(figsize=(11, max(4.5, 0.35 * len(grp) + 1.5)))
            ax = plt.gca()
            ax.barh(np.arange(len(grp)), y)
            ax.set_yticks(np.arange(len(grp)))
            ax.set_yticklabels(labels)
            ax.invert_yaxis()
            ax.set_xlabel(cols["stealth_score_mean"])
            ax.set_title(f"{model} | top stealth attacks | {proto} | {dtag}")
            ax.grid(True, axis="x", alpha=0.25)

            fname = outdir / (
                f"top_stealth_bar_by_model__metric_{_safe_filename(cols['stealth_score_mean'])}"
                f"__{_safe_filename(model)}__{_group_suffix(proto, dtag)}.png"
            )
            _plot_save(fig, fname)


def plot_family_delta_heatmap(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
    outdir: Path,
    metric_key: Optional[str] = None,
) -> None:
    """
    Secondary view only:
    compare family-aggregated classical vs quantum deltas across (attack_family, svd_dim),
    split by protocol/dataset_tag to avoid hidden mixing.

    Aggregation is weighted by n_seed_units when available.
    """
    if cols["model_family"] is None or cols["attack_family"] is None or cols["svd_dim"] is None:
        print("[WARN] No se puede hacer family_delta_heatmap (faltan model_family/attack_family/svd_dim).")
        return

    if metric_key is None:
        metric_key = "impact_bal_acc_mean" if cols.get("impact_bal_acc_mean") is not None else _preferred_impact_key(cols)
    if metric_key is None:
        print("[WARN] No se puede hacer family_delta_heatmap (falta impacto/drop).")
        return

    metric_col = cols[metric_key]
    if metric_col is None:
        print("[WARN] No se puede hacer family_delta_heatmap (columna nula).")
        return

    d = _attacked_rows_only(df, cols).copy()
    if d.empty:
        print("[WARN] No hay filas attacked para family_delta_heatmap.")
        return

    d["__family_norm"] = d[cols["model_family"]].map(_normalize_family)
    d["__metric"] = _to_numeric_series(d[metric_col])
    d["__svd"] = _to_numeric_series(d[cols["svd_dim"]])
    d = d.dropna(subset=["__metric", "__svd"])
    if d.empty:
        print("[WARN] Sin datos válidos para family_delta_heatmap.")
        return

    weight_col = cols.get("n_seed_units")

    for (proto, dtag), dg in _iter_protocol_dataset_groups(d, cols):
        models_present = set(dg["__family_norm"].astype(str).unique().tolist())
        if not {"classical", "quantum"}.issubset(models_present):
            print(f"[INFO] No hay ambos modelos para family_delta_heatmap en {proto}/{dtag}.")
            continue

        grp = _weighted_groupby_mean(
            dg,
            group_cols=[cols["attack_family"], "__svd", "__family_norm"],
            value_cols=["__metric"],
            weight_col=weight_col,
        )

        piv = grp.pivot_table(
            index=cols["attack_family"],
            columns=["__svd", "__family_norm"],
            values="__metric",
            aggfunc="mean",
        )

        svd_vals = sorted({c[0] for c in piv.columns})
        delta = pd.DataFrame(index=piv.index)

        for s in svd_vals:
            q = piv[(s, "quantum")] if (s, "quantum") in piv.columns else np.nan
            c = piv[(s, "classical")] if (s, "classical") in piv.columns else np.nan
            delta[s] = q - c

        if delta.empty:
            continue

        fig = plt.figure(figsize=(10, max(5, 0.45 * len(delta.index) + 2)))
        ax = plt.gca()
        arr = delta.to_numpy(dtype=float)
        vmin, vmax = _diverging_limits(arr)
        im = ax.imshow(arr, aspect="auto", interpolation="nearest", cmap="RdBu_r", vmin=vmin, vmax=vmax)
        plt.colorbar(im, label=f"quantum - classical ({metric_col})")
        ax.set_yticks(np.arange(len(delta.index)))
        ax.set_yticklabels([str(x) for x in delta.index])
        ax.set_xticks(np.arange(len(delta.columns)))
        ax.set_xticklabels([str(int(x)) if np.isfinite(x) else "nan" for x in delta.columns])
        ax.set_xlabel("SVD dim")
        ax.set_ylabel("Attack family")
        ax.set_title(f"Family-level delta heatmap | {proto} | {dtag}")

        fname = outdir / (
            f"family_delta_heatmap__metric_{_safe_filename(metric_col)}"
            f"__{_group_suffix(proto, dtag)}.png"
        )
        _plot_save(fig, fname)


def plot_id_vs_ood_by_model(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
    outdir: Path,
    metric_key: str,
    outname_prefix: str,
) -> None:
    """
    Compare ID vs OOD for the same exact model and SVD WITHOUT collapsing
    all OOD dataset_tag values into a single line.

    Each line is:
      <protocol>:<dataset_tag>

    The plotted value is the weighted mean across attacked rows for that
    exact (protocol, dataset_tag, model, svd_dim) slice.
    """
    if cols["protocol"] is None or cols["model"] is None or cols["svd_dim"] is None or cols["dataset_tag"] is None:
        print(f"[WARN] No se puede hacer {outname_prefix} (faltan protocol/model/svd_dim/dataset_tag).")
        return

    metric_col = cols.get(metric_key)
    if metric_col is None:
        print(f"[WARN] No se puede hacer {outname_prefix} (falta {metric_key}).")
        return

    d = _attacked_rows_only(df, cols).copy()
    if d.empty:
        print(f"[WARN] No hay filas attacked para {outname_prefix}.")
        return

    d["__metric"] = _to_numeric_series(d[metric_col])
    d["__svd"] = _to_numeric_series(d[cols["svd_dim"]])
    d = d.dropna(subset=["__metric", "__svd"])
    if d.empty:
        print(f"[WARN] Sin datos válidos para {outname_prefix}.")
        return

    proto_values = set(d[cols["protocol"]].astype(str).str.lower().unique().tolist())
    if not {"id", "ood"}.issubset(proto_values):
        print(f"[INFO] No hay ambos protocolos para {outname_prefix}.")
        return

    weight_col = cols.get("n_seed_units")

    group_cols = [cols["protocol"], cols["dataset_tag"], cols["model"], "__svd"]
    agg_rows = []
    for key, sub in d.groupby(group_cols, dropna=False):
        proto, dtag, model, svd = key
        if weight_col is not None and weight_col in sub.columns:
            w = _to_numeric_series(sub[weight_col]).fillna(0.0)
        else:
            w = pd.Series(1.0, index=sub.index, dtype=float)

        agg_rows.append(
            {
                "protocol": str(proto),
                "dataset_tag": str(dtag),
                "model": str(model),
                "__svd": float(svd),
                "__metric": _weighted_mean(sub["__metric"], w),
            }
        )

    agg_df = pd.DataFrame(agg_rows)
    if agg_df.empty:
        return

    for model, gm in agg_df.groupby("model", dropna=False):
        proto_values_model = set(gm["protocol"].astype(str).str.lower().unique().tolist())
        if not {"id", "ood"}.issubset(proto_values_model):
            continue

        fig = plt.figure(figsize=(10.5, 6))
        ax = plt.gca()

        line_count = 0
        for (proto, dtag), gl in gm.groupby(["protocol", "dataset_tag"], dropna=False):
            gl = gl.sort_values("__svd")
            x = gl["__svd"].astype(float).values
            y = gl["__metric"].astype(float).values
            if np.isfinite(y).sum() == 0:
                continue

            label = f"{str(proto).upper()}:{str(dtag)}"
            ax.plot(x, y, marker="o", label=label)
            line_count += 1

        if line_count == 0:
            plt.close(fig)
            continue

        ax.set_xlabel("SVD dim")
        ax.set_ylabel(metric_col)
        ax.set_title(f"{model} | ID vs OOD by dataset_tag | attacked-mean {metric_col}")
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=8, ncol=2)

        fname = outdir / (
            f"{outname_prefix}__metric_{_safe_filename(metric_col)}"
            f"__{_safe_filename(model)}.png"
        )
        _plot_save(fig, fname)


def plot_id_vs_ood_by_model_attack_family(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
    outdir: Path,
    metric_key: str,
    outname_prefix: str,
) -> None:
    """
    More controlled ID vs OOD comparison:
    one plot per (model, attack_family), keeping dataset_tag separated.
    """
    if (
        cols["protocol"] is None
        or cols["model"] is None
        or cols["svd_dim"] is None
        or cols["dataset_tag"] is None
        or cols["attack_family"] is None
    ):
        print(f"[WARN] No se puede hacer {outname_prefix} (faltan protocol/model/svd_dim/dataset_tag/attack_family).")
        return

    metric_col = cols.get(metric_key)
    if metric_col is None:
        print(f"[WARN] No se puede hacer {outname_prefix} (falta {metric_key}).")
        return

    d = _attacked_rows_only(df, cols).copy()
    if d.empty:
        print(f"[WARN] No hay filas attacked para {outname_prefix}.")
        return

    d["__metric"] = _to_numeric_series(d[metric_col])
    d["__svd"] = _to_numeric_series(d[cols["svd_dim"]])
    d = d.dropna(subset=["__metric", "__svd"])
    if d.empty:
        print(f"[WARN] Sin datos válidos para {outname_prefix}.")
        return

    proto_values = set(d[cols["protocol"]].astype(str).str.lower().unique().tolist())
    if not {"id", "ood"}.issubset(proto_values):
        print(f"[INFO] No hay ambos protocolos para {outname_prefix}.")
        return

    weight_col = cols.get("n_seed_units")

    group_cols = [cols["protocol"], cols["dataset_tag"], cols["model"], cols["attack_family"], "__svd"]
    agg_rows = []
    for key, sub in d.groupby(group_cols, dropna=False):
        proto, dtag, model, attack_family, svd = key
        if weight_col is not None and weight_col in sub.columns:
            w = _to_numeric_series(sub[weight_col]).fillna(0.0)
        else:
            w = pd.Series(1.0, index=sub.index, dtype=float)

        agg_rows.append(
            {
                "protocol": str(proto),
                "dataset_tag": str(dtag),
                "model": str(model),
                "attack_family": str(attack_family),
                "__svd": float(svd),
                "__metric": _weighted_mean(sub["__metric"], w),
            }
        )

    agg_df = pd.DataFrame(agg_rows)
    if agg_df.empty:
        return

    for (model, attack_family), gm in agg_df.groupby(["model", "attack_family"], dropna=False):
        proto_values_slice = set(gm["protocol"].astype(str).str.lower().unique().tolist())
        if not {"id", "ood"}.issubset(proto_values_slice):
            continue

        fig = plt.figure(figsize=(10.5, 6))
        ax = plt.gca()

        line_count = 0
        for (proto, dtag), gl in gm.groupby(["protocol", "dataset_tag"], dropna=False):
            gl = gl.sort_values("__svd")
            x = gl["__svd"].astype(float).values
            y = gl["__metric"].astype(float).values
            if np.isfinite(y).sum() == 0:
                continue

            label = f"{str(proto).upper()}:{str(dtag)}"
            ax.plot(x, y, marker="o", label=label)
            line_count += 1

        if line_count == 0:
            plt.close(fig)
            continue

        ax.set_xlabel("SVD dim")
        ax.set_ylabel(metric_col)
        ax.set_title(f"{model} | {attack_family} | ID vs OOD by dataset_tag")
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=8, ncol=2)

        fname = outdir / (
            f"{outname_prefix}__metric_{_safe_filename(metric_col)}"
            f"__{_safe_filename(model)}__fam_{_safe_filename(attack_family)}.png"
        )
        _plot_save(fig, fname)


# ============================================================
# Main
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Make auditability-aware, paper-friendly plots from aggregate CSV")
    parser.add_argument("--csv", type=str, required=True, help="Ruta al CSV agregado")
    parser.add_argument("--outdir", type=str, default="results/plots", help="Directorio de salida")
    parser.add_argument("--only-model", type=str, default=None, help="Filtro parcial sobre model exacto (ej. qsvc_pauli_xyz_r1)")
    parser.add_argument("--only-family", type=str, default=None, help="Filtro parcial sobre model_family (ej. classical, quantum)")
    parser.add_argument("--only-protocol", type=str, default=None, help="Filtro exacto sobre protocol (id/ood)")
    parser.add_argument("--only-dataset-tag", type=str, default=None, help="Filtro parcial sobre dataset_tag")
    parser.add_argument("--skip-summary-csv", action="store_true", help="No exportar CSVs de resumen")
    parser.add_argument("--skip-family-heatmap", action="store_true", help="Omitir heatmap secundario classical vs quantum")
    parser.add_argument("--skip-top-stealth-bar", action="store_true", help="Omitir barras top-stealth por modelo")
    parser.add_argument("--skip-id-vs-ood", action="store_true", help="Omitir comparativas directas ID vs OOD")
    parser.add_argument("--skip-id-vs-ood-family", action="store_true", help="Omitir comparativas ID vs OOD separadas por attack_family")
    parser.add_argument("--top-n-heatmap-attacks", type=int, default=18, help="Número máximo de filas attack|severity en heatmaps por modelo")
    parser.add_argument("--top-n-strength-attacks-per-family", type=int, default=6, help="Número máximo de ataques por familia en curvas de severidad")
    parser.add_argument("--top-n-stealth-bar", type=int, default=12, help="Número máximo de ataques en barplot top-stealth")
    parser.add_argument("--top-n-summary-stealth", type=int, default=50, help="Número máximo de filas en summary_top_stealth_overall.csv")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    outdir = Path(args.outdir)
    _ensure_dir(outdir)

    if not csv_path.exists():
        raise FileNotFoundError(f"No existe el CSV: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"[INFO] CSV cargado: {csv_path} | shape={df.shape}")

    cols = _infer_columns(df)
    df, cols = _prepare_df(df, cols)

    df = _filter_df(
        df=df,
        cols=cols,
        only_model=args.only_model,
        only_protocol=args.only_protocol,
        only_dataset_tag=args.only_dataset_tag,
        only_family=args.only_family,
    )
    print(f"[INFO] shape tras filtros: {df.shape}")

    if df.empty:
        print("[WARN] DataFrame vacío tras filtros. No hay plots que generar.")
        return

    if not args.skip_summary_csv:
        export_summary_tables(
            df,
            cols,
            outdir,
            top_n_summary_stealth=int(args.top_n_summary_stealth),
        )

    # Clean performance
    plot_clean_metric_by_svd(df, cols, outdir, "bal_acc_mean", "bal_acc_std", "clean_balacc_by_model_svd")
    plot_clean_metric_by_svd(df, cols, outdir, "roc_auc_mean", "roc_auc_std", "clean_rocauc_by_model_svd")
    plot_clean_metric_by_svd(df, cols, outdir, "f1_pos_mean", "f1_pos_std", "clean_f1_by_model_svd")

    # Severity-response curves aligned with paper narrative
    if cols.get("impact_bal_acc_mean") is not None:
        plot_attack_strength_vs_metric_by_family(
            df, cols, outdir,
            "impact_bal_acc_mean", "attack_strength_vs_impact_balacc_by_family",
            top_n_attacks_per_family=int(args.top_n_strength_attacks_per_family),
        )
    elif cols.get("bal_acc_drop_mean") is not None:
        plot_attack_strength_vs_metric_by_family(
            df, cols, outdir,
            "bal_acc_drop_mean", "attack_strength_vs_balacc_drop_by_family",
            top_n_attacks_per_family=int(args.top_n_strength_attacks_per_family),
        )

    if cols.get("detectability_score_mean") is not None:
        plot_attack_strength_vs_metric_by_family(
            df, cols, outdir,
            "detectability_score_mean", "attack_strength_vs_detectability_by_family",
            top_n_attacks_per_family=int(args.top_n_strength_attacks_per_family),
        )

    if cols.get("stealth_score_mean") is not None:
        plot_attack_strength_vs_metric_by_family(
            df, cols, outdir,
            "stealth_score_mean", "attack_strength_vs_stealth_by_family",
            top_n_attacks_per_family=int(args.top_n_strength_attacks_per_family),
        )

    # Core auditability plots
    plot_detectability_vs_impact_scatter(df, cols, outdir)
    plot_time_cost_by_model_dim_train_infer(df, cols, outdir)
    plot_time_cost_by_model_dim_audit(df, cols, outdir)
    plot_attack_family_boxplot(df, cols, outdir)

    # Heatmaps per exact model (main heatmaps no longer collapse severities)
    if cols.get("impact_bal_acc_mean") is not None:
        plot_metric_heatmap_by_model(
            df, cols, outdir,
            metric_key="impact_bal_acc_mean",
            outname_prefix="heatmap_impact_balacc_by_model",
            top_n_attacks=int(args.top_n_heatmap_attacks),
        )
    elif cols.get("bal_acc_drop_mean") is not None:
        plot_metric_heatmap_by_model(
            df, cols, outdir,
            metric_key="bal_acc_drop_mean",
            outname_prefix="heatmap_balacc_drop_by_model",
            top_n_attacks=int(args.top_n_heatmap_attacks),
        )

    if cols.get("detectability_score_mean") is not None:
        plot_metric_heatmap_by_model(
            df, cols, outdir,
            metric_key="detectability_score_mean",
            outname_prefix="heatmap_detectability_by_model",
            top_n_attacks=int(args.top_n_heatmap_attacks),
        )

    if cols.get("stealth_score_mean") is not None:
        plot_metric_heatmap_by_model(
            df, cols, outdir,
            metric_key="stealth_score_mean",
            outname_prefix="heatmap_stealth_by_model",
            top_n_attacks=int(args.top_n_heatmap_attacks),
        )

    if not args.skip_top_stealth_bar and cols.get("stealth_score_mean") is not None:
        plot_top_stealth_bar_by_model(
            df, cols, outdir,
            top_n=int(args.top_n_stealth_bar),
        )

    if not args.skip_family_heatmap:
        family_metric_key = "impact_bal_acc_mean" if cols.get("impact_bal_acc_mean") is not None else (
            "bal_acc_drop_mean" if cols.get("bal_acc_drop_mean") is not None else _preferred_impact_key(cols)
        )
        plot_family_delta_heatmap(df, cols, outdir, metric_key=family_metric_key)

    if not args.skip_id_vs_ood:
        if cols.get("impact_bal_acc_mean") is not None:
            plot_id_vs_ood_by_model(
                df, cols, outdir,
                metric_key="impact_bal_acc_mean",
                outname_prefix="id_vs_ood_by_model",
            )
        if cols.get("detectability_score_mean") is not None:
            plot_id_vs_ood_by_model(
                df, cols, outdir,
                metric_key="detectability_score_mean",
                outname_prefix="id_vs_ood_by_model",
            )
        if cols.get("stealth_score_mean") is not None:
            plot_id_vs_ood_by_model(
                df, cols, outdir,
                metric_key="stealth_score_mean",
                outname_prefix="id_vs_ood_by_model",
            )

    if not args.skip_id_vs_ood_family:
        if cols.get("impact_bal_acc_mean") is not None:
            plot_id_vs_ood_by_model_attack_family(
                df, cols, outdir,
                metric_key="impact_bal_acc_mean",
                outname_prefix="id_vs_ood_by_model_attack_family",
            )
        if cols.get("detectability_score_mean") is not None:
            plot_id_vs_ood_by_model_attack_family(
                df, cols, outdir,
                metric_key="detectability_score_mean",
                outname_prefix="id_vs_ood_by_model_attack_family",
            )
        if cols.get("stealth_score_mean") is not None:
            plot_id_vs_ood_by_model_attack_family(
                df, cols, outdir,
                metric_key="stealth_score_mean",
                outname_prefix="id_vs_ood_by_model_attack_family",
            )

    print("[DONE] Plots generados.")


if __name__ == "__main__":
    main()