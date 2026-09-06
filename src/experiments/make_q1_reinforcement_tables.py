"""Render the supplement tables of the reinforcement gates as LaTeX from the CSVs.

Every number printed in the supplement's reinforcement section comes from the
manifested tables under ``results/paper_digest/paper15_v11_reinforcement``;
this script writes ``publication/tdsc/tables/*.tex`` so that the LaTeX source
never contains hand-copied values.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


SENSOR_LABEL = {
    "integrity_jsd_vs_clean_eval": "Feature JSD",
    "integrity_mmd_vs_clean_eval": "Feature MMD",
    "integrity_ks_reject05_vs_clean_eval": "KS rejection rate",
    "integrity_score_jsd_vs_clean_eval": "Score JSD",
    "integrity_pred_pos_rate_shift": "Prediction-rate shift",
    "integrity_pred_jsd": "Prediction JSD",
    "integrity_label_prior_shift": "Label prior shift",
    "integrity_label_jsd": "Label JSD",
    "integrity_confusion_profile_l1": "Confusion profile $L_1$",
    "integrity_confusion_profile_jsd": "Confusion profile JSD",
}
REGIME_LABEL = {
    "I_X": "$\\mathcal I_X$",
    "I_XF": "$\\mathcal I_{XF}$",
    "I_Ym": "$\\mathcal I_{Y_m}$",
    "I_XFY": "$\\mathcal I_{XFY}$",
    "I_XF_item_aligned": "$\\mathcal I_{XF}$ item-aligned",
    "I_XFY_item_aligned": "$\\mathcal I_{XFY}$ item-aligned",
}
ENV_LABEL = {
    "gate2_id_256": "E1 CICIDS ID 256",
    "gate3a_ood_tue_wed": "E4 Tue$\\to$Wed",
    "gate3b_ood_tue_fri_portscan": "E5 Tue$\\to$Fri-PortScan",
    "gate3c_ood_wed_thu_webattacks": "E6 Wed$\\to$Thu-Web",
    "gate3d_ood_wed_fri_morning": "E7 Wed$\\to$Fri-AM",
    "gate5a_id_unsw": "E2 UNSW-NB15 ID",
    "gate5b_id_ton_iot": "E3 ToN-IoT ID",
    "gate6_ood_unsw": "E8 UNSW temporal OOD",
}
ENV_ORDER = ["gate2_id_256", "gate5a_id_unsw", "gate5b_id_ton_iot", "gate3a_ood_tue_wed", "gate3b_ood_tue_fri_portscan", "gate3c_ood_wed_thu_webattacks", "gate3d_ood_wed_fri_morning", "gate6_ood_unsw"]
MECHANISM = [
    ("feature_sign_flip", "Feature sign flip"),
    ("mean_shift", "Mean shift"),
    ("scaling_drift", "Scaling drift"),
    ("feature_dropout", "Feature dropout"),
    ("label_flip_prior_preserving", "Prior-preserving label flip"),
    ("label_flip_r", "Random label flip"),
]
CONDITION_LABEL = {
    "P0_reference": "P0 reference (standard / minmax2$\\pi$)",
    "PA_standard_standard": "PA standard / standard",
    "PB_minmax2pi_minmax2pi": "PB minmax2$\\pi$ / minmax2$\\pi$",
    "gate1_id_cicids__reference_untuned": "CICIDS ID, frozen defaults",
    "gate1_id_cicids__tuned_cv5": "CICIDS ID, both tuned (CV5)",
    "gate6_ood_unsw__reference_untuned": "UNSW OOD, frozen defaults",
    "gate6_ood_unsw__tuned_cv5": "UNSW OOD, both tuned (CV5)",
}


def _mech(attack: str) -> tuple[int, str, float]:
    for i, (prefix, label) in enumerate(MECHANISM):
        if attack.startswith(prefix):
            return i, label, float(attack.rsplit("_", 1)[-1])
    raise ValueError(attack)


def _f(x: float, nd: int = 3) -> str:
    return f"{x:.{nd}f}"


def table_false_alarm(ev: Path) -> str:
    fpr = pd.read_csv(ev / "null_evaluation_false_alarm_overall.csv")
    rows = []
    for _, r in fpr[fpr.target_kind == "sensor"].iterrows():
        rows.append(f"{SENSOR_LABEL[r.target]} & {int(r.n_fire)} & {_f(r.false_alarm_rate)} & [{_f(r.ci95_low)}, {_f(r.ci95_high)}] \\\\")
    rows.append("\\midrule")
    for _, r in fpr[fpr.target_kind == "regime"].iterrows():
        rows.append(f"{REGIME_LABEL[r.target]} (any sensor) & {int(r.n_fire)} & {_f(r.false_alarm_rate)} & [{_f(r.ci95_low)}, {_f(r.ci95_high)}] \\\\")
    n = int(fpr.n.iloc[0])
    return "\n".join([
        "\\begin{table}[!t]",
        "\\caption{Gate N: empirical false-alarm rate of the null-calibrated sensors and batch-level regimes on " + f"{n:,}" + " disjoint clean evaluation draws (all eight environments pooled; nominal $\\alpha=0.05$ per sensor). Intervals are descriptive Clopper--Pearson 95\\% intervals: draws within a cell share a pool half and are not independent. Regime rows are unions without correction.}",
        "\\label{tab:s-fpr}", "\\centering", "\\footnotesize", "\\setlength{\\tabcolsep}{4pt}",
        "\\begin{tabular}{@{}lrrl@{}}", "\\toprule",
        "Sensor / regime & Fires & Rate & 95\\% CI \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table}", ""])


def table_fpr_by_environment(ev: Path) -> str:
    fpr = pd.read_csv(ev / "null_evaluation_false_alarm_by_environment.csv")
    piv = fpr[fpr.target_kind == "regime"].pivot_table(index="gate", columns="target", values="false_alarm_rate").reindex(ENV_ORDER)
    sens = fpr[fpr.target_kind == "sensor"].groupby("gate")["false_alarm_rate"].agg(["min", "max"]).reindex(ENV_ORDER)
    pool = pd.read_csv(ev / "null_pool_design.csv").groupby("gate")[["n_calibration_half", "n_test"]].first().reindex(ENV_ORDER)
    rows = [f"{ENV_LABEL[g]} & {int(pool.loc[g, 'n_test'])} & {int(pool.loc[g, 'n_calibration_half'])} & {_f(sens.loc[g, 'min'])}--{_f(sens.loc[g, 'max'])} & {_f(piv.loc[g, 'I_X'])} & {_f(piv.loc[g, 'I_XF'])} & {_f(piv.loc[g, 'I_Ym'])} & {_f(piv.loc[g, 'I_XFY'])} \\\\" for g in ENV_ORDER]
    return "\n".join([
        "\\begin{table*}[!t]",
        "\\caption{Gate N: per-environment false-alarm rates on 1,200 evaluation draws (three dimensions, two or four models, 200 draws per cell). Sensor range is the minimum and maximum per-sensor rate in the environment; regime columns are batch-level unions. E1 draws 256 rows from 322-row pool halves and is indicative only.}",
        "\\label{tab:s-fpr-env}", "\\centering", "\\footnotesize", "\\setlength{\\tabcolsep}{5pt}",
        "\\begin{tabular}{@{}lrrlrrrr@{}}", "\\toprule",
        "Environment & $n$ & Pool half & Sensor range & $\\mathcal I_X$ & $\\mathcal I_{XF}$ & $\\mathcal I_{Y_m}$ & $\\mathcal I_{XFY}$ \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table*}", ""])


def table_detection(ev: Path) -> str:
    det = pd.read_csv(ev / "calibrated_detection_pooled.csv")
    det = det[det.target_kind.isin(["regime", "regime_exact"])]
    piv = det.pivot_table(index="attack", columns="target", values="detection_rate")
    ben = pd.read_csv(ev / "null_benign_control_response.csv")
    ben = ben[ben.target_kind.isin(["regime", "regime_exact"])].groupby(["attack", "target"])["fire_rate"].mean().unstack()
    order = sorted(piv.index, key=lambda a: _mech(a)[:1] + (_mech(a)[2],))
    cols = ["I_X", "I_XF", "I_Ym", "I_XFY", "I_XF_item_aligned", "I_XFY_item_aligned"]
    rows = []
    for attack in order:
        i, label, strength = _mech(attack)
        rows.append(f"{label} {strength:.2f} & " + " & ".join(_f(piv.loc[attack, c]) for c in cols) + " \\\\")
    rows.append("\\midrule")
    for attack, label in (("sham_tiny_gaussian_sigma_0.001", "Near-null Gaussian $\\sigma=0.001$"), ("sham_tiny_scaling_alpha_0.001", "Near-null scaling $\\alpha=0.001$")):
        rows.append(f"{label} & " + " & ".join(_f(ben.loc[attack, c]) for c in cols) + " \\\\")
    return "\n".join([
        "\\begin{table*}[!t]",
        "\\caption{Gate N: detection rate of each regime on the frozen \\texttt{paper\\_core} observations (all environments, dimensions and models pooled; 600 observations per intervention row) at the null-calibrated thresholds, and firing rate on the in-place near-null controls. Batch-level regimes use calibrated distributional sensors; item-aligned regimes use exact zero thresholds on item-wise deltas.}",
        "\\label{tab:s-detection}", "\\centering", "\\footnotesize", "\\setlength{\\tabcolsep}{5pt}",
        "\\begin{tabular}{@{}lrrrrrr@{}}", "\\toprule",
        "Intervention & $\\mathcal I_X$ & $\\mathcal I_{XF}$ & $\\mathcal I_{Y_m}$ & $\\mathcal I_{XFY}$ & $\\mathcal I_{XF}$ item & $\\mathcal I_{XFY}$ item \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table*}", ""])


def table_label_path(ev: Path) -> str:
    lab = pd.read_csv(ev / "calibrated_label_path_summary.csv")
    subsets = [("all_label_interventions", "All label interventions"), ("prior_preserving_label_interventions", "Prior-preserving"), ("positive_impact_label_interventions", "Positive conclusion impact")]
    regimes = ["I_X", "I_XF", "I_Ym", "I_XFY", "I_XFY_item_aligned"]
    rows = []
    for key, label in subsets:
        block = lab[lab.subset == key].set_index("regime")
        n = int(block.n.iloc[0])
        rows.append(f"{label} & {n:,} & " + " & ".join(f"{int(block.loc[r, 'n_fire']):,}" for r in regimes) + " \\\\")
    return "\n".join([
        "\\begin{table}[!t]",
        "\\caption{Gate N: label-path interventions in the frozen expansion; number of observations on which each regime fires after calibration (batch-level) or by exact item-aligned comparison.}",
        "\\label{tab:s-labelpath}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{2.5pt}",
        "\\begin{tabular}{@{}lrrrrrr@{}}", "\\toprule",
        "Subset & $n$ & $\\mathcal I_X$ & $\\mathcal I_{XF}$ & $\\mathcal I_{Y_m}$ & $\\mathcal I_{XFY}$ & item-aligned \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table}", ""])


def table_paired(ev: Path) -> str:
    prep = pd.read_csv(ev / "prep_ablation_paired_zz_minus_svc.csv")
    tuned = pd.read_csv(ev / "tuned_paired_zz_minus_svc.csv")
    frame = pd.concat([prep, tuned], ignore_index=True)
    order = ["P0_reference", "PA_standard_standard", "PB_minmax2pi_minmax2pi", "gate1_id_cicids__tuned_cv5", "gate6_ood_unsw__reference_untuned", "gate6_ood_unsw__tuned_cv5"]
    rows = []
    for cond in order:
        block = frame[frame.condition == cond].sort_values("svd_dim")
        cells = " & ".join(f"{r['mean']:.4f} [{r['ci95_low']:.4f}, {r['ci95_high']:.4f}] ({int(r['clusters_positive'])}/5)" for _, r in block.iterrows())
        rows.append(f"{CONDITION_LABEL[cond]} & {cells} \\\\")
    return "\n".join([
        "\\begin{table*}[!t]",
        "\\caption{Gates P and T: within-split ZZ-minus-SVC difference in suite-average balanced-accuracy conclusion impact, mean with 95\\% $t$ interval over five split clusters and number of positive clusters. CICIDS ID reference is the re-executed P0 configuration; UNSW OOD reference is the frozen 1.0.0 environment E8.}",
        "\\label{tab:s-paired}", "\\centering", "\\footnotesize", "\\setlength{\\tabcolsep}{4pt}",
        "\\begin{tabular}{@{}llll@{}}", "\\toprule",
        "Condition & $d=8$ & $d=10$ & $d=12$ \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table*}", ""])


def table_clean_and_hyper(ev: Path) -> str:
    pc = pd.concat([pd.read_csv(ev / "prep_ablation_clean_performance.csv"), pd.read_csv(ev / "tuned_clean_performance.csv")], ignore_index=True)
    order = ["P0_reference", "PA_standard_standard", "PB_minmax2pi_minmax2pi", "gate1_id_cicids__tuned_cv5", "gate6_ood_unsw__reference_untuned", "gate6_ood_unsw__tuned_cv5"]
    rows = []
    for cond in order:
        block = pc[pc.condition == cond]
        svc = block[block.model == "svc_rbf"].set_index("svd_dim")["mean"]
        zz = block[block.model == "qsvc_zz_r1"].set_index("svd_dim")["mean"]
        rows.append(f"{CONDITION_LABEL[cond]} & " + " & ".join(f"{svc[d]:.3f} / {zz[d]:.3f}" for d in (8, 10, 12)) + " \\\\")
    hyper = pd.read_csv(ev / "tuned_selected_hyperparameters_summary.csv")
    hrows = []
    for gate, label in (("gate1_id_cicids", "CICIDS ID"), ("gate6_ood_unsw", "UNSW OOD")):
        q = hyper[(hyper.gate == gate) & (hyper.model == "qsvc_zz_r1")].groupby("model_C")["n_cells"].sum()
        s = hyper[(hyper.gate == gate) & (hyper.model == "svc_rbf")].groupby("model_C")["n_cells"].sum()
        hrows.append(f"{label} & \\multicolumn{{2}}{{l}}{{" + ", ".join(f"$C={c:g}$: {int(n)}" for c, n in q.items()) + "} & " + ", ".join(f"$C={c:g}$: {int(n)}" for c, n in s.items()) + " \\\\")
    return "\n".join([
        "\\begin{table*}[!t]",
        "\\caption{Gates P and T: clean balanced accuracy (SVC / ZZ, mean over five split clusters) per configuration and dimension, and the distribution of cross-validated regularisation constants over the 30 cells of each tuned environment (SVC also selects $\\gamma$; see the artifact table).}",
        "\\label{tab:s-clean}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{@{}llll@{}}", "\\toprule",
        "Condition & $d=8$ & $d=10$ & $d=12$ \\\\", "\\midrule",
        *rows, "\\midrule",
        "Tuned environment & \\multicolumn{2}{l}{QSVC $C$ selections} & SVC $C$ selections \\\\", "\\midrule",
        *hrows, "\\bottomrule", "\\end{tabular}", "\\end{table*}", ""])


def table_mass(ev: Path) -> str:
    mass = pd.read_csv(ev / "null_mass_point_profile.csv").groupby("gate")[["near_duplicate_row_fraction_1e-6", "max_cluster_mass_width_0.01sd", "mean_cluster_mass_width_0.01sd", "max_cluster_mass_width_0.001sd"]].mean().reindex(ENV_ORDER)
    rows = [f"{ENV_LABEL[g]} & {_f(mass.loc[g, 'near_duplicate_row_fraction_1e-6'])} & {_f(mass.loc[g, 'max_cluster_mass_width_0.01sd'])} & {_f(mass.loc[g, 'mean_cluster_mass_width_0.01sd'])} & {_f(mass.loc[g, 'max_cluster_mass_width_0.001sd'])} \\\\" for g in ENV_ORDER]
    return "\n".join([
        "\\begin{table}[!t]",
        "\\caption{Cluster structure of the frozen evaluation batches (mean over the 30 cells of each environment, standardized projected features): fraction of near-duplicate rows, and the largest fraction of rows within a window of 0.01 or 0.001 standard deviations in any feature (max) or on average over features (mean).}",
        "\\label{tab:s-mass}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{@{}lrrrr@{}}", "\\toprule",
        "Environment & Dup.\\ rows & Max 0.01 & Mean 0.01 & Max 0.001 \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table}", ""])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=Path("results/paper_digest/paper15_v11_reinforcement"))
    parser.add_argument("--out-dir", type=Path, default=Path("publication/tdsc/tables"))
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        "s_fpr.tex": table_false_alarm(args.evidence),
        "s_fpr_env.tex": table_fpr_by_environment(args.evidence),
        "s_detection.tex": table_detection(args.evidence),
        "s_labelpath.tex": table_label_path(args.evidence),
        "s_paired.tex": table_paired(args.evidence),
        "s_clean.tex": table_clean_and_hyper(args.evidence),
        "s_mass.tex": table_mass(args.evidence),
    }
    for name, text in tables.items():
        (args.out_dir / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", args.out_dir / name)


if __name__ == "__main__":
    main()
