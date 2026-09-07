"""Render the LaTeX tables and number macros of the 1.2.0 policy gates from the CSVs.

Every number printed in the manuscript about Gates F and D (family-wise
calibration, end-to-end decisions, counterexample witnesses, inference units)
comes from the manifested tables under
``results/paper_digest/paper15_v12_policy``. This script writes
``publication/tdsc/tables/*.tex`` and a macro file
``publication/tdsc/tables/policy_macros.tex`` whose ``\\newcommand`` values are
used in the prose, so that the LaTeX source never contains hand-copied values.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


REGIME_LABEL = {
    "I_X": "$\\mathcal I_X$",
    "I_XF": "$\\mathcal I_{XF}$",
    "I_Ym": "$\\mathcal I_{Y_m}$",
    "I_XFY": "$\\mathcal I_{XFY}$",
    "I_XFY_trusted": "$\\mathcal I_{XFY}^{\\star}$",
}
REGIME_ORDER = ["I_X", "I_XF", "I_Ym", "I_XFY", "I_XFY_trusted"]
BATCH_REGIMES = ["I_X", "I_XF", "I_Ym", "I_XFY"]
POLICY_LABEL = {
    "serve_always": "P0 serve-always",
    "union_uncalibrated": "P1 union (1.1.0)",
    "family_calibrated": "P2 family-calibrated",
    "family_calibrated_strict": "P3 strict fail-closed",
}
POLICY_ORDER = ["serve_always", "union_uncalibrated", "family_calibrated", "family_calibrated_strict"]
ENV_LABEL = {
    "gate2_id_256": "E1 CICIDS ID 256",
    "gate5a_id_unsw": "E2 UNSW-NB15 ID",
    "gate5b_id_ton_iot": "E3 ToN-IoT ID",
    "gate3a_ood_tue_wed": "E4 Tue$\\to$Wed",
    "gate3b_ood_tue_fri_portscan": "E5 Tue$\\to$Fri-PortScan",
    "gate3c_ood_wed_thu_webattacks": "E6 Wed$\\to$Thu-Web",
    "gate3d_ood_wed_fri_morning": "E7 Wed$\\to$Fri-AM",
    "gate6_ood_unsw": "E8 UNSW temporal OOD",
}
ENV_ORDER = list(ENV_LABEL)
MECHANISM = [
    ("feature_sign_flip", "Feature sign flip"),
    ("mean_shift", "Mean shift"),
    ("scaling_drift", "Scaling drift"),
    ("feature_dropout", "Feature dropout"),
    ("label_flip_prior_preserving", "Prior-preserving label flip"),
    ("label_flip_r", "Random label flip"),
]
FAMILY_LABEL = {"target_shift": "Evaluation-label", "corruption": "Sign flip", "covariate_shift": "Mean shift / scaling", "pipeline": "Feature dropout"}


def _f(x: float, nd: int = 3) -> str:
    return f"{float(x):.{nd}f}"


def _n(x: int) -> str:
    return f"{int(x):,}"


def _mech(attack: str) -> tuple[int, str, float]:
    for i, (prefix, label) in enumerate(MECHANISM):
        if attack.startswith(prefix):
            return i, label, float(attack.rsplit("_", 1)[-1])
    raise ValueError(attack)


def _macro(name: str, value: str) -> str:
    return f"\\newcommand{{\\{name}}}{{{value}}}"


# ---------------------------------------------------------------------------
# Main-text tables
# ---------------------------------------------------------------------------


def table_main_policy(ev: Path) -> str:
    m = pd.read_csv(ev / "policy_metrics.csv")
    m = m[m["tau"] == 0.0]
    rows = []
    for regime in REGIME_ORDER:
        for policy in ("union_uncalibrated", "family_calibrated", "family_calibrated_strict"):
            r = m[(m["regime"] == regime) & (m["policy"] == policy)].iloc[0]
            if regime == "I_XFY_trusted" and policy != "family_calibrated":
                continue
            if regime == "I_XFY" and policy == "family_calibrated_strict":
                continue
            short = {"union_uncalibrated": "P1 union", "family_calibrated": "P2 family", "family_calibrated_strict": "P3 strict"}
            label = "P2/P3 (exact block)" if regime == "I_XFY_trusted" else short[policy]
            rows.append(
                f"{REGIME_LABEL[regime]} & {label} & {_f(r['decision_fpr'])} & {_n(r['unsafe_allow'])} & {_f(r['containment'], 2)} & {_n(r['residual_blind_material'])} \\\\"
            )
        if regime != "I_XFY_trusted":
            rows.append("\\addlinespace[1pt]")
    n_clean = int(m["n_clean"].max())
    n_mat = int(m["n_material"].iloc[0])
    return "\n".join([
        "\\begin{table}[!t]",
        "\\caption{End-to-end decisions on the frozen observations (primary materiality $|\\Delta_R|>0$; " + _n(n_mat) + " material of 10,800 intervened observations; decision false-alarm rate on " + _n(n_clean) + " clean draws, or on the 1,200 exact-zero rows for $\\mathcal I_{XFY}^{\\star}$). P0 serve-always allows all " + _n(n_mat) + " material observations in every regime. Residual blind: material observations structurally indistinguishable from the reference under the regime.}",
        "\\label{tab:policy}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{@{}llrrrr@{}}", "\\toprule",
        "Regime & Policy & Dec.\\ FPR & Unsafe allow & Contain. & Res.\\ blind \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table}", ""])


# ---------------------------------------------------------------------------
# Supplement tables
# ---------------------------------------------------------------------------


def table_family_fpr(ev: Path) -> str:
    fpr = pd.read_csv(ev / "family_false_alarm_overall.csv")
    rows = []
    for regime in BATCH_REGIMES:
        for rule in ("union", "family"):
            r = fpr[(fpr["regime"] == regime) & (fpr["rule"] == rule)].iloc[0]
            rows.append(f"{REGIME_LABEL[regime]} & {'union' if rule == 'union' else 'family'} & {_n(r['n_fire'])} & {_f(r['pooled_rate'])} & {_f(r['environment_cluster_mean_min'])}--{_f(r['environment_cluster_mean_max'])} \\\\")
    n = int(fpr["n_draws"].iloc[0])
    return "\n".join([
        "\\begin{table}[!t]",
        "\\caption{Gate F: decision-level false-alarm rate on the " + _n(n) + " disjoint clean evaluation draws (nominal $\\alpha=0.05$ per decision) of the union of per-sensor rules (1.1.0) and of the family-calibrated rule. Pooled rates are descriptive because draws within a cell overlap; the last column is the range of the eight per-environment cluster means (five split clusters each).}",
        "\\label{tab:s-family-fpr}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{@{}llrrl@{}}", "\\toprule",
        "Regime & Rule & Fires & Pooled & Env.\\ cluster means \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table}", ""])


def table_family_fpr_env(ev: Path) -> str:
    e = pd.read_csv(ev / "family_false_alarm_by_environment.csv")
    rows = []
    for gate in ENV_ORDER:
        cells = []
        for regime in BATCH_REGIMES:
            ru = e[(e["gate"] == gate) & (e["regime"] == regime) & (e["rule"] == "union")].iloc[0]
            rf = e[(e["gate"] == gate) & (e["regime"] == regime) & (e["rule"] == "family")].iloc[0]
            cells.append(f"{_f(ru['cluster_mean'], 3)} & {_f(rf['cluster_mean'], 3)} [{_f(rf['cluster_ci95_low'], 2)}, {_f(rf['cluster_ci95_high'], 2)}]")
        r0 = e[(e["gate"] == gate)].iloc[0]
        rows.append(f"{ENV_LABEL[gate]} & {int(r0['n_test'])} & {int(r0['max_disjoint_draws_per_half'])} & " + " & ".join(cells) + " \\\\")
    head = " & ".join(f"\\multicolumn{{2}}{{c}}{{{REGIME_LABEL[r]}: union, family [95\\% CI]}}" for r in BATCH_REGIMES)
    return "\n".join([
        "\\begin{table*}[!t]",
        "\\caption{Gate F: per-environment false-alarm rate of the union rule (cluster mean) and of the family-calibrated rule (cluster mean with two-sided 95\\% $t$ interval over the five split clusters, four degrees of freedom). $n$ is the batch size; ``disjoint'' is the number of mutually disjoint batches that one pool half can supply, an upper bound on the effective number of independent draws among the 20 per run (E1: one).}",
        "\\label{tab:s-family-fpr-env}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{1.8pt}",
        "\\begin{tabular}{@{}lrr" + "rl" * 4 + "@{}}", "\\toprule",
        "Environment & $n$ & disj. & " + head + " \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table*}", ""])


def table_family_detection(ev: Path) -> str:
    d = pd.read_csv(ev / "family_detection_pooled.csv")
    piv = d.pivot_table(index="attack", columns=["regime", "rule"], values="detection_rate")
    ben = pd.read_csv(ev / "family_benign_control_response.csv")
    bpiv = ben.pivot_table(index="attack", columns=["regime", "rule"], values="fire_rate")
    order = sorted(piv.index, key=lambda a: (_mech(a)[0], _mech(a)[2]))
    rows = []
    for attack in order:
        _, label, strength = _mech(attack)
        rows.append(f"{label} {strength:.2f} & " + " & ".join(f"{_f(piv.loc[attack, (r, 'union')], 2)} / {_f(piv.loc[attack, (r, 'family')], 2)}" for r in BATCH_REGIMES) + " \\\\")
    rows.append("\\midrule")
    for attack, label in (("sham_tiny_gaussian_sigma_0.001", "Near-null Gaussian $\\sigma=0.001$"), ("sham_tiny_scaling_alpha_0.001", "Near-null scaling $\\alpha=0.001$")):
        rows.append(f"{label} & " + " & ".join(f"{_f(bpiv.loc[attack, (r, 'union')], 2)} / {_f(bpiv.loc[attack, (r, 'family')], 2)}" for r in BATCH_REGIMES) + " \\\\")
    return "\n".join([
        "\\begin{table*}[!t]",
        "\\caption{Gate F: detection rate on the frozen \\texttt{paper\\_core} observations (600 per intervention row, eight environments pooled) and firing rate on the near-null in-place controls, as union rule / family-calibrated rule. The family rule trades a small loss of detection for the decision-level false-alarm budget of Table~\\ref{tab:s-family-fpr}.}",
        "\\label{tab:s-family-detection}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{4pt}",
        "\\begin{tabular}{@{}lllll@{}}", "\\toprule",
        "Intervention & " + " & ".join(REGIME_LABEL[r] for r in BATCH_REGIMES) + " \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table*}", ""])


def table_policy_full(ev: Path) -> str:
    m = pd.read_csv(ev / "policy_metrics.csv")
    m = m[m["tau"] == 0.0]
    rows = []
    for regime in REGIME_ORDER:
        for policy in POLICY_ORDER:
            r = m[(m["regime"] == regime) & (m["policy"] == policy)].iloc[0]
            short = {"serve_always": "P0", "union_uncalibrated": "P1", "family_calibrated": "P2", "family_calibrated_strict": "P3"}
            rows.append(f"{REGIME_LABEL[regime]} & {short[policy]} & {_n(r['n_clean'])} & {_n(r['false_hold'])} & {_n(r['false_block'])} & {_f(r['benign_hold_block_rate'], 2)} & {_n(r['unsafe_allow'])} & {_n(r['true_hold'])} & {_n(r['true_block'])} & {_n(r['integrity_only_hold_block'])} & {_n(r['immaterial_allow'])} & {_n(r['safe_allow'])} \\\\")
        rows.append("\\addlinespace[1pt]")
    n_mat = int(m["n_material"].iloc[0])
    n_imm = int(m["n_immaterial"].iloc[0])
    return "\n".join([
        "\\begin{table*}[!t]",
        "\\caption{Gate D: complete decision counts at the primary materiality threshold ($|\\Delta_R|>0$; " + _n(n_mat) + " material and " + _n(n_imm) + " non-material intervened observations; 1,200 near-null benign shams). P0 serve-always, P1 union, P2 family-calibrated, P3 strict. Clean draws: 12,000 for batch-level regimes; the 1,200 exact-zero rows for $\\mathcal I_{XFY}^{\\star}$. Ben.\\ h/b: fraction of benign shams held or blocked. Integ.: non-material intervened observations held or blocked. Safe allow: clean, benign and non-material observations allowed.}",
        "\\label{tab:s-policy-full}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{2.2pt}",
        "\\begin{tabular}{@{}llrrrrrrrrrr@{}}", "\\toprule",
        "Regime & Pol. & Clean & F.\\ hold & F.\\ block & Ben.\\ h/b & Unsafe & T.\\ hold & T.\\ block & Integ. & Imm.\\ allow & Safe allow \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table*}", ""])


def table_policy_tau(ev: Path) -> str:
    m = pd.read_csv(ev / "policy_metrics.csv")
    rows = []
    for regime in REGIME_ORDER:
        for policy in ("union_uncalibrated", "family_calibrated"):
            cells = []
            for tau in (0.0, 0.02, 0.05):
                r = m[(m["regime"] == regime) & (m["policy"] == policy) & (m["tau"] == tau)].iloc[0]
                cells.append(f"{_n(r['unsafe_allow'])} ({_f(r['containment'], 2)})")
            rows.append(f"{REGIME_LABEL[regime]} & {'P1' if policy == 'union_uncalibrated' else 'P2'} & " + " & ".join(cells) + " \\\\")
    n_tau = {tau: int(m[m["tau"] == tau]["n_material"].iloc[0]) for tau in (0.0, 0.02, 0.05)}
    return "\n".join([
        "\\begin{table}[!t]",
        "\\caption{Gate D: unsafe allows (containment in parentheses) under three materiality thresholds on $|\\Delta_R|$; material observations " + _n(n_tau[0.0]) + ", " + _n(n_tau[0.02]) + " and " + _n(n_tau[0.05]) + ". P1 union, P2 family-calibrated.}",
        "\\label{tab:s-policy-tau}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{2.5pt}",
        "\\begin{tabular}{@{}llrrr@{}}", "\\toprule",
        "Regime & Pol. & $\\tau=0^{+}$ & $\\tau=0.02$ & $\\tau=0.05$ \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table}", ""])


def table_policy_family(ev: Path) -> str:
    f = pd.read_csv(ev / "policy_metrics_by_family.csv")
    f = f[(f["tau"] == 0.0) & (f["policy"] == "family_calibrated")]
    fams = ["target_shift", "corruption", "covariate_shift", "pipeline"]
    rows = []
    for regime in REGIME_ORDER:
        cells = []
        for fam in fams:
            r = f[(f["regime"] == regime) & (f["attack_family"] == fam)].iloc[0]
            cells.append(f"{_n(r['unsafe_allow'])}/{_n(r['n_material'])}")
        rows.append(f"{REGIME_LABEL[regime]} & " + " & ".join(cells) + " \\\\")
    return "\n".join([
        "\\begin{table}[!t]",
        "\\caption{Gate D: unsafe allows / material observations by intervention mechanism under the family-calibrated policy P2 ($|\\Delta_R|>0$).}",
        "\\label{tab:s-policy-family}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{@{}lrrrr@{}}", "\\toprule",
        "Regime & " + " & ".join(FAMILY_LABEL[x] for x in fams) + " \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table}", ""])


def table_witnesses(ev: Path) -> str:
    w = pd.read_csv(ev / "counterexample_witnesses.csv")
    rows = [f"{r['witness']} & {r['property']} & {_n(r['count'])} / {_n(r['denominator'])} \\\\" for _, r in w.iterrows()]
    return "\n".join([
        "\\begin{table}[!t]",
        "\\caption{Counterexample witnesses realised in the frozen expansion (count / denominator). W1--W4 are evaluation-label rows, W5--W6 feature-side rows, W7 all intervened rows, W8 material label rows.}",
        "\\label{tab:s-witnesses}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabularx}{\\columnwidth}{@{}l>{\\raggedright\\arraybackslash}Xr@{}}", "\\toprule",
        "ID & Property & Count \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabularx}", "\\end{table}", ""])


def table_composition(ev: Path) -> str:
    c = pd.read_csv(ev / "policy_contract_composition.csv")
    names = {"clean": "Clean", "approved_transpilation": "Approved transpilation", "circuit_parameter_mutation": "Parameterized circuit mutation", "kernel_psd_preserving_substitution": "PSD-preserving kernel substitution", "label_prior_preserving_corruption": "Prior-preserving label corruption", "approved_shot_emulator_256": "Approved 256-shot emulator"}
    rows = [f"{names[r['scenario']]} & \\texttt{{{r['contract_action']}}} & {'yes' if r['exact_invariant_violated'] else 'no'} & \\texttt{{{r['policy_action']}}} & \\texttt{{{r['composed_action']}}} \\\\" for _, r in c.iterrows()]
    return "\n".join([
        "\\begin{table}[!t]",
        "\\caption{Composition of the frozen four-contract envelopes with the policy layer under $\\mathcal I_{XFY}^{\\star}$ (lattice maximum). Approved rewrites and approved stochastic estimation are not exact violations; the contract's own \\texttt{hold} for the approved emulator is preserved.}",
        "\\label{tab:s-composition}", "\\centering", "\\scriptsize", "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{@{}lllll@{}}", "\\toprule",
        "Scenario & Contract & Exact viol. & Policy & Composed \\\\", "\\midrule",
        *rows, "\\bottomrule", "\\end{tabular}", "\\end{table}", ""])


# ---------------------------------------------------------------------------
# Macros used in the prose
# ---------------------------------------------------------------------------


def macros(ev: Path, expansion_dir: Path, gate1_dir: Path) -> str:
    fpr = pd.read_csv(ev / "family_false_alarm_overall.csv").set_index(["regime", "rule"])
    m = pd.read_csv(ev / "policy_metrics.csv")
    m0 = m[m["tau"] == 0.0].set_index(["regime", "policy"])
    m5 = m[m["tau"] == 0.05].set_index(["regime", "policy"])
    lab = pd.read_csv(ev / "family_label_path_summary.csv").set_index(["subset", "regime", "rule"])
    w = pd.read_csv(ev / "counterexample_witnesses.csv").set_index("witness")
    fam = pd.read_csv(ev / "policy_metrics_by_family.csv")
    fam = fam[(fam["tau"] == 0.0) & (fam["policy"] == "family_calibrated")].set_index(["regime", "attack_family"])
    units = pd.read_csv(ev / "inference_units.csv").iloc[0]
    env = pd.read_csv(ev / "family_false_alarm_by_environment.csv")
    lines = ["% Generated by make_q1_policy_tables.py from the manifested 1.2.0 tables; do not edit."]
    for regime in BATCH_REGIMES:
        key = regime.replace("_", "")
        lines.append(_macro(f"FprUnion{key}", _f(fpr.loc[(regime, "union"), "pooled_rate"])))
        lines.append(_macro(f"FprFamily{key}", _f(fpr.loc[(regime, "family"), "pooled_rate"])))
        lines.append(_macro(f"FprFamilyMin{key}", _f(fpr.loc[(regime, "family"), "environment_cluster_mean_min"])))
        lines.append(_macro(f"FprFamilyMax{key}", _f(fpr.loc[(regime, "family"), "environment_cluster_mean_max"])))
    for regime in REGIME_ORDER:
        key = regime.replace("_", "")
        for policy, pk in (("union_uncalibrated", "Union"), ("family_calibrated", "Family"), ("family_calibrated_strict", "Strict")):
            r = m0.loc[(regime, policy)]
            lines.append(_macro(f"Unsafe{pk}{key}", _n(r["unsafe_allow"])))
            lines.append(_macro(f"Contain{pk}{key}", _f(r["containment"], 2)))
            lines.append(_macro(f"DecFpr{pk}{key}", _f(r["decision_fpr"])))
            lines.append(_macro(f"ContainFive{pk}{key}", _f(m5.loc[(regime, policy), "containment"], 2)))
            lines.append(_macro(f"BenignHB{pk}{key}", _f(r["benign_hold_block_rate"], 2)))
    lines.append(_macro("NMaterial", _n(m0.iloc[0]["n_material"])))
    lines.append(_macro("NMaterialFive", _n(m5.iloc[0]["n_material"])))
    lines.append(_macro("NImmaterial", _n(m0.iloc[0]["n_immaterial"])))
    lines.append(_macro("NMaterialLabel", _n(lab.loc[("material_label_interventions", "I_XFY", "union"), "n"])))
    lines.append(_macro("BatchUnionLabelFires", _n(lab.loc[("material_label_interventions", "I_XFY", "union"), "n_fire"])))
    lines.append(_macro("BatchFamilyLabelFires", _n(lab.loc[("material_label_interventions", "I_XFY", "family"), "n_fire"])))
    lines.append(_macro("BatchUnionLabelRate", _f(lab.loc[("material_label_interventions", "I_XFY", "union"), "detection_rate"], 3)))
    lines.append(_macro("BatchFamilyLabelRate", _f(lab.loc[("material_label_interventions", "I_XFY", "family"), "detection_rate"], 3)))
    words = {"1": "One", "2": "Two", "3": "Three", "4": "Four", "5": "Five", "6": "Six", "7": "Seven", "8": "Eight"}
    for wid in w.index:
        name = "Witness" + "".join(words.get(ch, ch) for ch in str(wid))  # LaTeX macro names cannot contain digits
        lines.append(_macro(name, _n(w.loc[wid, "count"])))
        lines.append(_macro(name + "Den", _n(w.loc[wid, "denominator"])))
    for regime in REGIME_ORDER:
        key = regime.replace("_", "")
        for family_name, fk in (("target_shift", "Label"), ("pipeline", "Dropout"), ("corruption", "SignFlip"), ("covariate_shift", "Shift")):
            r = fam.loc[(regime, family_name)]
            lines.append(_macro(f"UnsafeFamily{fk}{key}", _n(r["unsafe_allow"])))
            if regime == REGIME_ORDER[0]:
                lines.append(_macro(f"NMaterialFam{fk}", _n(r["n_material"])))
    lines.append(_macro("NRuns", _n(units["n_runs"])))
    lines.append(_macro("NClusters", _n(units["n_env_split_clusters"])))
    lines.append(_macro("NEvalDraws", _n(units["n_evaluation_draws"])))
    e1 = env[(env["gate"] == "gate2_id_256") & (env["regime"] == "I_XFY") & (env["rule"] == "family")].iloc[0]
    lines.append(_macro("FprFamilyIXFYEone", _f(e1["cluster_mean"])))
    # Signed label-path counts recomputed from the frozen unique-observation tables.
    for tag, path in (("Exp", expansion_dir / "expansion_unique_observations.csv"), ("Gone", gate1_dir / "gate1_unique_observations.csv")):
        frame = pd.read_csv(path, low_memory=False)
        rows = frame[(frame["attack"] != "clean") & (frame["attack_family"] == "target_shift")]
        signed = rows["bal_acc_clean"].astype(float) - rows["bal_acc"].astype(float)
        lines.append(_macro(f"LabelDecreased{tag}", _n((signed > 1e-12).sum())))
        lines.append(_macro(f"LabelUnchanged{tag}", _n((signed.abs() <= 1e-12).sum())))
        lines.append(_macro(f"LabelIncreased{tag}", _n((signed < -1e-12).sum())))
        lines.append(_macro(f"LabelMaterial{tag}", _n((signed.abs() > 1e-12).sum())))
        lines.append(_macro(f"LabelRows{tag}", _n(len(rows))))
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=Path("results/paper_digest/paper15_v12_policy"))
    parser.add_argument("--expansion", type=Path, default=Path("results/paper_digest/paper15_q1_expansion"))
    parser.add_argument("--gate1", type=Path, default=Path("results/paper_digest/paper15_q1_gate1_id_seeds_20_q1"))
    parser.add_argument("--out-dir", type=Path, default=Path("publication/tdsc/tables"))
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        "m_policy.tex": table_main_policy(args.evidence),
        "s_family_fpr.tex": table_family_fpr(args.evidence),
        "s_family_fpr_env.tex": table_family_fpr_env(args.evidence),
        "s_family_detection.tex": table_family_detection(args.evidence),
        "s_policy_full.tex": table_policy_full(args.evidence),
        "s_policy_tau.tex": table_policy_tau(args.evidence),
        "s_policy_family.tex": table_policy_family(args.evidence),
        "s_witnesses.tex": table_witnesses(args.evidence),
        "s_composition.tex": table_composition(args.evidence),
        "policy_macros.tex": macros(args.evidence, args.expansion, args.gate1),
    }
    for name, text in tables.items():
        (args.out_dir / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", args.out_dir / name)
    manifest = {name: {"bytes": len(text.encode("utf-8"))} for name, text in tables.items()}
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
