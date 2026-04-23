# src/experiments/make_plots.py
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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


def _safe_filename(s: str) -> str:
    s = str(s).strip()
    s = re.sub(r"\s+", "_", s)
    return re.sub(r"[^a-zA-Z0-9_\-\.]+", "_", s)


def _extract_severity_from_name(name: str) -> float:
    """
    Intenta extraer severidad de nombres de ataque (ej. suffix numérico):
      - mean_shift_0.05
      - feature_sign_flip_p_0.1
      - label_flip_r_0.1
      - quantization_step_0.05
      - clipping_1_99  (devolverá 99 -> no ideal, pero fallback)
    Si no puede, devuelve NaN.
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


def _to_numeric_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def _normalize_model_family_name(v: object) -> str:
    s = str(v).strip().lower()
    if any(k in s for k in ["qsvc", "quantum"]):
        return "quantum"
    if any(k in s for k in ["classical", "svc", "rbf", "linear", "svm"]):
        return "classical"
    return s or "unknown"


def _infer_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    cols: Dict[str, Optional[str]] = {}

    # identificación / agrupación
    cols["protocol"] = _pick_col(df, ["protocol"])
    cols["dataset_tag"] = _pick_col(df, ["dataset_tag", "dataset", "dataset_id_tag"])
    cols["svd_dim"] = _pick_col(df, ["svd_dim", "dim", "d"])
    cols["model_family"] = _pick_col(df, ["model_family", "model", "family"])
    cols["attack_name"] = _pick_col(df, ["attack_name", "attack", "attack_id"])
    cols["attack_family"] = _pick_col(df, ["attack_family", "attack_group", "family_attack"])
    cols["attack_is_clean"] = _pick_col(df, ["attack_is_clean", "is_clean", "clean"])
    cols["severity"] = _pick_col(df, ["attack_severity", "severity", "attack_strength", "strength"])

    # métricas agregadas (mean)
    cols["bal_acc_mean"] = _pick_col(df, ["bal_acc_mean", "balanced_accuracy_mean", "balacc_mean"])
    cols["roc_auc_mean"] = _pick_col(df, ["roc_auc_mean", "auc_mean"])
    cols["f1_pos_mean"] = _pick_col(df, ["f1_pos_mean", "f1_mean"])

    # métricas agregadas (std) opcionales
    cols["bal_acc_std"] = _pick_col(df, ["bal_acc_std", "balanced_accuracy_std", "balacc_std"])
    cols["roc_auc_std"] = _pick_col(df, ["roc_auc_std", "auc_std"])
    cols["f1_pos_std"] = _pick_col(df, ["f1_pos_std", "f1_std"])

    # drops agregados
    cols["bal_acc_drop_mean"] = _pick_col(df, ["bal_acc_drop_mean", "balanced_accuracy_drop_mean", "balacc_drop_mean"])
    cols["roc_auc_drop_mean"] = _pick_col(df, ["roc_auc_drop_mean", "auc_drop_mean"])
    cols["f1_pos_drop_mean"] = _pick_col(df, ["f1_pos_drop_mean", "f1_drop_mean"])

    # señales
    cols["integrity_jsd_mean"] = _pick_col(df, ["integrity_jsd_mean", "jsd_mean"])
    cols["integrity_mmd_mean"] = _pick_col(df, ["integrity_mmd_mean", "mmd_mean"])
    cols["integrity_score_jsd_mean"] = _pick_col(df, ["integrity_score_jsd_mean", "score_jsd_mean"])
    cols["integrity_ks_reject05_mean"] = _pick_col(df, ["integrity_ks_reject05_mean", "ks_reject05_mean"])

    # tiempo
    cols["train_time_s_mean"] = _pick_col(df, ["train_time_s_mean", "fit_time_s_mean", "train_time_mean"])
    cols["predict_time_s_mean"] = _pick_col(df, ["predict_time_s_mean", "inference_time_s_mean", "pred_time_s_mean"])

    return cols


def _prepare_df(df: pd.DataFrame, cols: Dict[str, Optional[str]]) -> Tuple[pd.DataFrame, Dict[str, Optional[str]]]:
    out = df.copy()
    cols = dict(cols)  # copia para poder modificar sin efectos laterales

    # severity inferida si no viene
    if cols["severity"] is None:
        if cols["attack_name"] is not None:
            out["__severity_inferred"] = out[cols["attack_name"]].map(_extract_severity_from_name)
            cols["severity"] = "__severity_inferred"
        else:
            out["__severity_inferred"] = np.nan
            cols["severity"] = "__severity_inferred"

    # attack_is_clean normalizado
    if cols["attack_is_clean"] is not None:
        c = cols["attack_is_clean"]
        out["__is_clean_norm"] = out[c].astype(str).str.strip().str.lower().map({
            "1": True, "0": False,
            "true": True, "false": False,
            "clean": True, "attacked": False
        })
        mask_na = out["__is_clean_norm"].isna()
        if mask_na.any():
            try:
                out.loc[mask_na, "__is_clean_norm"] = _to_numeric_series(out.loc[mask_na, c]) == 1.0
            except Exception:
                pass
        cols["attack_is_clean"] = "__is_clean_norm"
    else:
        # inferir por attack_name == clean
        if cols["attack_name"] is not None:
            out["__is_clean_norm"] = out[cols["attack_name"]].astype(str).str.strip().str.lower().eq("clean")
            cols["attack_is_clean"] = "__is_clean_norm"

    # model family normalizado
    if cols["model_family"] is not None:
        out["__model_family_norm"] = out[cols["model_family"]].map(_normalize_model_family_name)
        cols["model_family"] = "__model_family_norm"

    # attack family fallback
    if cols["attack_family"] is None and cols["attack_name"] is not None:
        out["__attack_family_fallback"] = out[cols["attack_name"]].astype(str).str.replace(
            r"_[0-9]+(?:\.[0-9]+)?$", "", regex=True
        )
        cols["attack_family"] = "__attack_family_fallback"

    # Coerciones numéricas de columnas relevantes (si existen)
    for k in [
        "svd_dim", "severity",
        "bal_acc_mean", "roc_auc_mean", "f1_pos_mean",
        "bal_acc_std", "roc_auc_std", "f1_pos_std",
        "bal_acc_drop_mean", "roc_auc_drop_mean", "f1_pos_drop_mean",
        "integrity_jsd_mean", "integrity_mmd_mean", "integrity_score_jsd_mean", "integrity_ks_reject05_mean",
        "train_time_s_mean", "predict_time_s_mean"
    ]:
        c = cols.get(k)
        if c is not None and c in out.columns:
            out[c] = _to_numeric_series(out[c])

    return out, cols


def _filter_df(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
    only_model: Optional[str] = None,
    only_protocol: Optional[str] = None,
    only_dataset_tag: Optional[str] = None,
) -> pd.DataFrame:
    d = df.copy()

    if only_model and cols["model_family"] is not None:
        d = d[d[cols["model_family"]].astype(str).str.contains(only_model, case=False, na=False)]

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
# Summary exports (muy útil para análisis)
# ============================================================

def export_summary_tables(df: pd.DataFrame, cols: Dict[str, Optional[str]], outdir: Path) -> None:
    rows = []

    # resumen global por modelo / svd
    keys = []
    if cols["model_family"] is not None:
        keys.append(cols["model_family"])
    if cols["svd_dim"] is not None:
        keys.append(cols["svd_dim"])

    if not keys:
        print("[WARN] No se puede exportar summary tables (faltan model_family/svd_dim).")
        return

    metric_keys = [
        "bal_acc_mean", "roc_auc_mean", "f1_pos_mean",
        "bal_acc_drop_mean", "roc_auc_drop_mean", "f1_pos_drop_mean",
        "integrity_jsd_mean", "integrity_mmd_mean", "integrity_score_jsd_mean",
        "train_time_s_mean", "predict_time_s_mean"
    ]
    metric_cols = [cols[k] for k in metric_keys if cols.get(k) is not None]

    d_clean = _clean_rows_only(df, cols)
    if not d_clean.empty and metric_cols:
        g = d_clean.groupby(keys, dropna=False)[metric_cols].mean(numeric_only=True).reset_index()
        g.to_csv(outdir / "summary_clean_by_model_dim.csv", index=False)
        print(f"[OK] {outdir / 'summary_clean_by_model_dim.csv'}")

    d_att = _attacked_rows_only(df, cols)
    if not d_att.empty and metric_cols:
        keys_att = keys.copy()
        if cols["attack_family"] is not None:
            keys_att.append(cols["attack_family"])
        if cols["severity"] is not None:
            keys_att.append(cols["severity"])

        g2 = d_att.groupby(keys_att, dropna=False)[metric_cols].mean(numeric_only=True).reset_index()
        g2.to_csv(outdir / "summary_attacked_by_model_dim_family_severity.csv", index=False)
        print(f"[OK] {outdir / 'summary_attacked_by_model_dim_family_severity.csv'}")


# ============================================================
# Plotters
# ============================================================

def plot_clean_performance_by_svd(df: pd.DataFrame, cols: Dict[str, Optional[str]], outdir: Path) -> None:
    if cols["svd_dim"] is None or cols["model_family"] is None:
        print("[WARN] No se puede hacer clean_performance_by_svd (faltan svd_dim/model_family).")
        return

    metric_bal = cols["bal_acc_mean"]
    metric_auc = cols["roc_auc_mean"]
    metric_f1 = cols["f1_pos_mean"]

    if metric_bal is None and metric_auc is None and metric_f1 is None:
        print("[WARN] No se puede hacer clean_performance_by_svd (faltan métricas *_mean).")
        return

    d = _clean_rows_only(df, cols)
    if d.empty:
        print("[WARN] No hay filas clean para clean_performance_by_svd.")
        return

    d = d.dropna(subset=[cols["svd_dim"]]).copy()
    if d.empty:
        print("[WARN] No hay svd_dim válidos en clean_performance_by_svd.")
        return

    d = d.sort_values(by=[cols["model_family"], cols["svd_dim"]])

    plt.figure(figsize=(10, 6))
    for model, g in d.groupby(cols["model_family"]):
        x = _to_numeric_series(g[cols["svd_dim"]]).values
        if metric_bal is not None:
            y = _to_numeric_series(g[metric_bal]).values
            plt.plot(x, y, marker="o", label=f"{model} | bal_acc")
        if metric_auc is not None:
            y = _to_numeric_series(g[metric_auc]).values
            plt.plot(x, y, marker="s", linestyle="--", label=f"{model} | roc_auc")
        if metric_f1 is not None:
            y = _to_numeric_series(g[metric_f1]).values
            plt.plot(x, y, marker="^", linestyle=":", label=f"{model} | f1_pos")

    plt.xlabel("SVD dim")
    plt.ylabel("Score")
    plt.title("Clean performance by SVD dimension")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "clean_performance_by_svd.png", dpi=180)
    plt.close()
    print(f"[OK] {outdir / 'clean_performance_by_svd.png'}")


def plot_attack_severity_vs_drop(
    df: pd.DataFrame,
    cols: Dict[str, Optional[str]],
    outdir: Path,
    drop_col_key: str,
    outname_prefix: str
) -> None:
    if cols["severity"] is None or cols["model_family"] is None:
        print(f"[WARN] No se puede hacer {outname_prefix} (faltan severity/model_family).")
        return

    drop_col = cols.get(drop_col_key)
    if drop_col is None:
        print(f"[WARN] No se puede hacer {outname_prefix} (falta {drop_col_key}).")
        return

    d = _attacked_rows_only(df, cols)
    if d.empty:
        print(f"[WARN] No hay filas attacked para {outname_prefix}.")
        return

    d = d.copy()
    d["__sev"] = _to_numeric_series(d[cols["severity"]])
    d["__drop"] = _to_numeric_series(d[drop_col])

    fam_col = cols["attack_family"]
    if fam_col is None:
        d["__attack_family_fallback"] = "all_attacks"
        fam_col = "__attack_family_fallback"

    for model, gm in d.groupby(cols["model_family"]):
        gm = gm.dropna(subset=["__drop"]).copy()
        if gm.empty:
            continue

        plt.figure(figsize=(11, 6))

        grp = (
            gm.groupby([fam_col, "__sev"], dropna=False)["__drop"]
            .mean()
            .reset_index()
            .sort_values([fam_col, "__sev"])
        )

        valid_sev = grp["__sev"].notna().sum()
        if valid_sev < 3:
            # fallback a ranking por ataque
            if cols["attack_name"] is None:
                print(f"[WARN] {outname_prefix}: no hay severidad ni attack_name para {model}.")
                plt.close()
                continue

            g2 = (
                gm.groupby(cols["attack_name"], dropna=False)["__drop"]
                .mean()
                .reset_index()
                .sort_values("__drop", ascending=False)
            )
            x = np.arange(len(g2))
            plt.scatter(x, g2["__drop"].values)
            plt.xticks(
                x,
                g2[cols["attack_name"]].astype(str).values,
                rotation=75,
                ha="right",
                fontsize=8
            )
            plt.ylabel(drop_col)
            plt.title(f"{model} | {outname_prefix} (fallback by attack)")
            plt.grid(True, alpha=0.25)
            plt.tight_layout()
            fname = f"{outname_prefix}__{_safe_filename(model)}.png"
            plt.savefig(outdir / fname, dpi=180)
            plt.close()
            print(f"[OK] {outdir / fname}")
            continue

        for fam, gf in grp.groupby(fam_col):
            gf = gf.dropna(subset=["__sev", "__drop"])
            if gf.empty:
                continue
            x = gf["__sev"].astype(float).values
            y = gf["__drop"].astype(float).values
            order = np.argsort(x)
            plt.plot(x[order], y[order], marker="o", label=str(fam))

        plt.xlabel("Attack severity")
        plt.ylabel(drop_col)
        plt.title(f"{model} | {outname_prefix}")
        plt.grid(True, alpha=0.25)
        plt.legend(fontsize=8, ncol=2)
        plt.tight_layout()
        fname = f"{outname_prefix}__{_safe_filename(model)}.png"
        plt.savefig(outdir / fname, dpi=180)
        plt.close()
        print(f"[OK] {outdir / fname}")


def plot_signals_vs_drop_scatter(df: pd.DataFrame, cols: Dict[str, Optional[str]], outdir: Path) -> None:
    if cols["model_family"] is None:
        print("[WARN] No se puede hacer signals_vs_drop_scatter (falta model_family).")
        return

    drop_col = cols["bal_acc_drop_mean"] or cols["roc_auc_drop_mean"] or cols["f1_pos_drop_mean"]
    signal_col = cols["integrity_score_jsd_mean"] or cols["integrity_jsd_mean"] or cols["integrity_mmd_mean"]

    if drop_col is None or signal_col is None:
        print("[WARN] No se puede hacer signals_vs_drop_scatter (faltan columnas de drop/signal).")
        return

    d = _attacked_rows_only(df, cols)
    if d.empty:
        print("[WARN] No hay filas attacked para signals_vs_drop_scatter.")
        return

    d = d.copy()
    d["__drop"] = _to_numeric_series(d[drop_col])
    d["__sig"] = _to_numeric_series(d[signal_col])

    fam_col = cols["attack_family"]
    if fam_col is None:
        d["__fam"] = "all"
        fam_col = "__fam"

    corr_rows = []

    for model, gm in d.groupby(cols["model_family"]):
        plt.figure(figsize=(8.5, 6))
        for fam, gf in gm.groupby(fam_col):
            gf = gf.dropna(subset=["__sig", "__drop"])
            if gf.empty:
                continue
            plt.scatter(gf["__sig"].values, gf["__drop"].values, label=str(fam), alpha=0.8)

            corr_f = np.nan
            if len(gf) >= 2:
                try:
                    corr_f = gf[["__sig", "__drop"]].corr().iloc[0, 1]
                except Exception:
                    pass
            corr_rows.append({
                "model_family": model,
                "attack_family": fam,
                "n_points": int(len(gf)),
                "signal_col": signal_col,
                "drop_col": drop_col,
                "corr_pearson": corr_f,
            })

        corr = np.nan
        gm2 = gm[["__sig", "__drop"]].dropna()
        if len(gm2) >= 2:
            try:
                corr = gm2.corr().iloc[0, 1]
            except Exception:
                pass

        title = f"{model} | signal vs drop"
        if not np.isnan(corr):
            title += f" (corr={corr:.3f})"

        plt.xlabel(signal_col)
        plt.ylabel(drop_col)
        plt.title(title)
        plt.grid(True, alpha=0.25)
        plt.legend(fontsize=8, ncol=2)
        plt.tight_layout()
        fname = f"signals_vs_drop_scatter__{_safe_filename(model)}.png"
        plt.savefig(outdir / fname, dpi=180)
        plt.close()
        print(f"[OK] {outdir / fname}")

    if corr_rows:
        corr_df = pd.DataFrame(corr_rows)
        corr_df.to_csv(outdir / "signals_vs_drop_correlations.csv", index=False)
        print(f"[OK] {outdir / 'signals_vs_drop_correlations.csv'}")


def plot_time_cost_by_model_dim(df: pd.DataFrame, cols: Dict[str, Optional[str]], outdir: Path) -> None:
    if cols["svd_dim"] is None or cols["model_family"] is None:
        print("[WARN] No se puede hacer time_cost_by_model_dim (faltan svd_dim/model_family).")
        return

    train_col = cols["train_time_s_mean"]
    pred_col = cols["predict_time_s_mean"]
    if train_col is None and pred_col is None:
        print("[WARN] No se puede hacer time_cost_by_model_dim (faltan tiempos).")
        return

    d = df.copy()
    dc = _clean_rows_only(d, cols)
    if not dc.empty:
        d = dc

    if d.empty:
        print("[WARN] No hay filas para time_cost_by_model_dim.")
        return

    d = d.dropna(subset=[cols["svd_dim"]]).copy()

    plt.figure(figsize=(10, 6))
    for model, gm in d.groupby(cols["model_family"]):
        gm = gm.sort_values(cols["svd_dim"])
        x = _to_numeric_series(gm[cols["svd_dim"]]).values

        if train_col is not None:
            y = _to_numeric_series(gm[train_col]).values
            plt.plot(x, y, marker="o", label=f"{model} | train")

        if pred_col is not None:
            y = _to_numeric_series(gm[pred_col]).values
            plt.plot(x, y, marker="s", linestyle="--", label=f"{model} | predict")

    plt.xlabel("SVD dim")
    plt.ylabel("Time (s)")
    plt.title("Time cost by model and SVD dimension")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "time_cost_by_model_dim.png", dpi=180)
    plt.close()
    print(f"[OK] {outdir / 'time_cost_by_model_dim.png'}")


def plot_classical_vs_quantum_heatmap(df: pd.DataFrame, cols: Dict[str, Optional[str]], outdir: Path) -> None:
    """
    Heatmap comparando bal_acc_drop_mean por (attack_name, svd_dim):
      delta = quantum - classical
    """
    if cols["model_family"] is None or cols["attack_name"] is None or cols["svd_dim"] is None:
        print("[WARN] No se puede hacer heatmap clásico-vs-cuántico (faltan columnas base).")
        return

    drop_col = cols["bal_acc_drop_mean"] or cols["roc_auc_drop_mean"]
    if drop_col is None:
        print("[WARN] No se puede hacer heatmap clásico-vs-cuántico (falta drop mean).")
        return

    d = _attacked_rows_only(df, cols)
    if d.empty:
        print("[WARN] No hay filas attacked para heatmap comparativo.")
        return

    d = d.copy()
    d["__model_norm"] = d[cols["model_family"]].map(_normalize_model_family_name)
    d["__drop"] = _to_numeric_series(d[drop_col])
    d["__svd_dim_num"] = _to_numeric_series(d[cols["svd_dim"]])

    d = d.dropna(subset=["__drop", "__svd_dim_num"])
    if d.empty:
        print("[WARN] Heatmap comparativo sin datos válidos.")
        return

    models_present = set(d["__model_norm"].astype(str).unique().tolist())
    if not {"classical", "quantum"}.issubset(models_present):
        print("[INFO] No hay ambos modelos (classical + quantum). Se omite heatmap comparativo.")
        return

    grp = (
        d.groupby(["__model_norm", cols["attack_name"], "__svd_dim_num"], dropna=False)["__drop"]
        .mean()
        .reset_index()
    )

    piv = grp.pivot_table(
        index=[cols["attack_name"], "__svd_dim_num"],
        columns="__model_norm",
        values="__drop",
        aggfunc="mean",
    )

    if "classical" not in piv.columns or "quantum" not in piv.columns:
        print("[INFO] No hay suficientes filas para heatmap comparativo.")
        return

    piv["delta_q_minus_c"] = piv["quantum"] - piv["classical"]

    mat = piv["delta_q_minus_c"].unstack("__svd_dim_num")
    if mat.empty:
        print("[INFO] Heatmap vacío.")
        return

    # ordenar columnas svd
    mat = mat.reindex(sorted(mat.columns), axis=1)

    # ordenar ataques por magnitud media absoluta
    mat = mat.reindex(mat.abs().mean(axis=1).sort_values(ascending=False).index)

    plt.figure(figsize=(12, max(6, 0.35 * len(mat))))
    im = plt.imshow(mat.values, aspect="auto")
    plt.colorbar(im, label=f"{drop_col} delta (quantum - classical)")
    plt.xticks(np.arange(mat.shape[1]), [str(int(c)) if float(c).is_integer() else str(c) for c in mat.columns])
    plt.yticks(np.arange(mat.shape[0]), [str(i) for i in mat.index], fontsize=8)
    plt.xlabel("SVD dim")
    plt.ylabel("Attack")
    plt.title("Classical vs Quantum robustness delta")
    plt.tight_layout()
    plt.savefig(outdir / "classical_vs_quantum_drop_heatmap.png", dpi=180)
    plt.close()
    print(f"[OK] {outdir / 'classical_vs_quantum_drop_heatmap.png'}")


def plot_attack_family_boxplot(df: pd.DataFrame, cols: Dict[str, Optional[str]], outdir: Path) -> None:
    """
    Boxplot de bal_acc_drop_mean por familia de ataque, separado por modelo.
    Muy útil para ver robustez global por tipo de perturbación.
    """
    if cols["model_family"] is None or cols["attack_family"] is None:
        print("[WARN] No se puede hacer attack_family_boxplot (faltan model_family/attack_family).")
        return

    drop_col = cols["bal_acc_drop_mean"] or cols["roc_auc_drop_mean"] or cols["f1_pos_drop_mean"]
    if drop_col is None:
        print("[WARN] No se puede hacer attack_family_boxplot (falta drop mean).")
        return

    d = _attacked_rows_only(df, cols)
    d = d.copy()
    d["__drop"] = _to_numeric_series(d[drop_col])
    d = d.dropna(subset=["__drop"])
    if d.empty:
        print("[WARN] No hay filas attacked válidas para attack_family_boxplot.")
        return

    for model, gm in d.groupby(cols["model_family"]):
        # ordenar familias por mediana de drop (de mayor a menor)
        fam_order = (
            gm.groupby(cols["attack_family"])["__drop"]
            .median()
            .sort_values(ascending=False)
            .index.tolist()
        )
        if not fam_order:
            continue

        data = [gm.loc[gm[cols["attack_family"]] == fam, "__drop"].values for fam in fam_order]

        plt.figure(figsize=(11, 6))
        plt.boxplot(data, tick_labels=[str(f) for f in fam_order], showfliers=False)
        plt.xticks(rotation=45, ha="right")
        plt.ylabel(drop_col)
        plt.title(f"{model} | Drop distribution by attack family")
        plt.grid(True, alpha=0.25, axis="y")
        plt.tight_layout()
        fname = f"attack_family_boxplot__{_safe_filename(model)}.png"
        plt.savefig(outdir / fname, dpi=180)
        plt.close()
        print(f"[OK] {outdir / fname}")


# ============================================================
# Main
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Make paper-friendly plots from aggregate_results CSV")
    parser.add_argument(
        "--csv",
        type=str,
        required=True,
        help="Ruta al CSV agregado (ej. results/agg/AGG_*.csv)",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default="results/plots",
        help="Directorio de salida para plots",
    )
    parser.add_argument(
        "--only-model",
        type=str,
        default=None,
        help="Filtro sobre model_family (ej. classical, quantum, qsvc, svc)",
    )
    parser.add_argument(
        "--only-protocol",
        type=str,
        default=None,
        help="Filtro exacto sobre protocol (ej. id / ood)",
    )
    parser.add_argument(
        "--only-dataset-tag",
        type=str,
        default=None,
        help="Filtro parcial sobre dataset_tag",
    )
    parser.add_argument(
        "--skip-heatmap",
        action="store_true",
        help="Omitir heatmap comparativo classical vs quantum",
    )
    parser.add_argument(
        "--skip-summary-csv",
        action="store_true",
        help="No exportar CSVs de resumen",
    )
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

    # filtros
    df = _filter_df(
        df=df,
        cols=cols,
        only_model=args.only_model,
        only_protocol=args.only_protocol,
        only_dataset_tag=args.only_dataset_tag,
    )
    print(f"[INFO] shape tras filtros: {df.shape}")

    if df.empty:
        print("[WARN] DataFrame vacío tras filtros. No hay plots que generar.")
        return

    # Export resumen tabular
    if not args.skip_summary_csv:
        export_summary_tables(df, cols, outdir)

    # Plots principales
    plot_clean_performance_by_svd(df, cols, outdir)

    plot_attack_severity_vs_drop(
        df, cols, outdir,
        drop_col_key="bal_acc_drop_mean",
        outname_prefix="attack_severity_vs_balacc_drop"
    )
    plot_attack_severity_vs_drop(
        df, cols, outdir,
        drop_col_key="roc_auc_drop_mean",
        outname_prefix="attack_severity_vs_rocauc_drop"
    )
    plot_attack_severity_vs_drop(
        df, cols, outdir,
        drop_col_key="f1_pos_drop_mean",
        outname_prefix="attack_severity_vs_f1_drop"
    )

    plot_signals_vs_drop_scatter(df, cols, outdir)
    plot_time_cost_by_model_dim(df, cols, outdir)
    plot_attack_family_boxplot(df, cols, outdir)

    if not args.skip_heatmap:
        plot_classical_vs_quantum_heatmap(df, cols, outdir)

    print("[DONE] Plots generados.")


if __name__ == "__main__":
    main()