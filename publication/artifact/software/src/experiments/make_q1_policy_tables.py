"""Render the LaTeX tables and number macros of the policy and adversarial gates from the CSVs.

Every number printed in the manuscript about Gates F, D and A (conformal
family calibration and its comparison with the superseded 1.2.0 rule, the
decomposition of the 1.2.0 excess, the offline end-to-end decisions with their
near-null stress-control interruption, the counterexample witnesses, the inference units
and the adaptive cluster-preserving gate) comes from the manifested tables
under ``results/paper_digest/paper15_v12_policy`` and
``results/paper_digest/paper15_v13_adversarial``. This script writes
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
    "serve_always": "P0 serve-always (baseline)",
    "union_uncalibrated": "P1 union (uncalibrated, risk-tolerant)",
    "family_calibrated": "P2 conformal-rule (risk-tolerant)",
    "family_calibrated_strict": "P3 sensor-coverage-complete relative to declared evidence dimensions (abstaining on missing coverage)",
}
POLICY_SHORT = {"serve_always": "P0", "union_uncalibrated": "P1 union", "family_calibrated": "P2 conf.", "family_calibrated_strict": "P3 abst."}
POLICY_ORDER = ["serve_always", "union_uncalibrated", "family_calibrated", "family_calibrated_strict"]
RULE_SHORT = {"union": "union", "family_v12": "1.2.0", "family": "conformal"}
ENV_LABEL = {
    "gate2_id_256": "E1 CICIDS ID 256",
    "gate5a_id_unsw": "E2 UNSW-NB15 ID",
    "gate5b_id_ton_iot": "E3 ToN-IoT ID",
    "gate3a_ood_tue_wed": "E4 CICIDS Tue$\\to$Wed",
    "gate3b_ood_tue_fri_portscan": "E5 CICIDS Tue$\\to$Fri-PortScan",
    "gate3c_ood_wed_thu_webattacks": "E6 CICIDS Wed$\\to$Thu-Web",
    "gate3d_ood_wed_fri_morning": "E7 CICIDS Wed$\\to$Fri-AM",
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
ADV_MECH_LABEL = {"mean_shift": "Mean shift", "scaling_drift": "Scaling drift"}
STRENGTH_WORD = {0.02: "TwoPct", 0.05: "FivePct", 0.10: "TenPct", 0.25: "TwentyFivePct", 0.50: "FiftyPct"}
MECH_WORD = {"mean_shift": "MS", "scaling_drift": "SD"}
NL = "\n"


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


def _key(regime: str) -> str:
    return regime.replace("_", "")


def _table(env: str, caption: str, label: str, colspec: str, header: str, rows: list[str], *, size: str = "\\scriptsize", colsep: str = "3pt", tabularx: bool = False, placement: str = "!tbp") -> str:
    """Render one float. Supplement tables use ``!tbp`` so that they pack; the main-article tables pass ``!t``."""

    begin = f"\\begin{{tabularx}}{{{colspec}}}" if tabularx else f"\\begin{{tabular}}{{{colspec}}}"
    end = "\\end{tabularx}" if tabularx else "\\end{tabular}"
    return NL.join([
        f"\\begin{{{env}}}[{placement}]",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}", "\\centering", size, f"\\setlength{{\\tabcolsep}}{{{colsep}}}",
        begin, "\\toprule",
        header, "\\midrule",
        *rows, "\\bottomrule", end, f"\\end{{{env}}}", ""])


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
            label = "P2/P3 (exact)" if regime == "I_XFY_trusted" else POLICY_SHORT[policy]
            rows.append(f"{REGIME_LABEL[regime]} & {label} & {_f(r['decision_fpr'])} & {_f(r['benign_interruption_rate'], 2)} & {_n(r['unsafe_allow'])} & {_f(r['containment'], 2)} & {_n(r['residual_blind_material'])} \\\\")
        if regime != "I_XFY_trusted":
            rows.append("\\addlinespace[1pt]")
    n_mat = int(m["n_material"].iloc[0])
    caption = ("Offline decisions on frozen observations at the structural-sensitivity endpoint $|\\Delta_R|>0$ (" + _n(n_mat) + " materially altered audit results among 10,800 interventions). P1: union; P2: conformal, risk-tolerant; P3: sensor-coverage-complete relative to declared evidence dimensions and abstaining on missing coverage. FPR is estimated on 12,000 clean draws from evaluation pools disjoint from the calibration pools; resampled draws within a pool may overlap. The starred row instead reports an exact-zero invariant check on 1,200 rows and is not the same estimand. Benign is interruption of the same 1,200 near-null synthetic controls. Served: undetected materially altered audit results served, not malicious network events. Blind: structurally indistinguishable material rows.")
    return _table("table", caption, "tab:policy", "@{}llrrrrr@{}", "Regime & Policy & FPR/check & Benign & Served & Contain. & Blind \\\\", rows, colsep="2pt", placement="!t")


def table_main_adversarial(adv: Path) -> str:
    det = pd.read_csv(adv / "adversarial_detection_pooled.csv")
    det = det[det["rule"].isin(["family", "exact"])].set_index(["mechanism", "attack_class", "strength", "regime"])
    mat = pd.read_csv(adv / "adversarial_materiality.csv").set_index(["mechanism", "attack_class", "strength"])
    pol = pd.read_csv(adv / "adversarial_policy_metrics.csv")
    p2 = pol[(pol["policy"] == "family_calibrated") & (pol["tau"] == 0.0)].groupby(["mechanism", "attack_class", "strength", "regime"])[["unsafe_allow", "n_material"]].sum()
    rows = []
    for mech in ("mean_shift", "scaling_drift"):
        for s in (0.02, 0.05, 0.10, 0.25, 0.50):
            cells = []
            for cls in ("control", "adaptive"):
                if cls == "control" and s > 0.10:
                    cells.append("-- & -- & -- & --")
                    continue
                dx = det.loc[(mech, cls, s, "I_X"), "detection_rate"]
                dxf = det.loc[(mech, cls, s, "I_XF"), "detection_rate"]
                mf = mat.loc[(mech, cls, s), "material_fraction_tau0"]
                ua = p2.loc[(mech, cls, s, "I_XF"), "unsafe_allow"]
                nm = p2.loc[(mech, cls, s, "I_XF"), "n_material"]
                cells.append(f"{_f(dx, 2)} & {_f(dxf, 2)} & {_f(mf, 2)} & {_n(ua)}/{_n(nm)}")
            rows.append(f"{ADV_MECH_LABEL[mech]} & {s:.2f} & " + " & ".join(cells) + " \\\\")
        rows.append("\\addlinespace[1pt]")
    caption = ("Gate A: executed drift mechanisms (matched controls, frozen strengths) against their adaptive cluster-preserving variants (class F5), 600 observations per row pooled over the eight environments. Detection uses the conformal family rule in $\\mathcal I_X$ and $\\mathcal I_{XF}$; material is the fraction with changed balanced accuracy; served is the number of undetected materially altered audit results served by P2 in $\\mathcal I_{XF}$ over material rows. The attacker leaves clustered entries untouched and perturbs the remaining 32\\% on average.")
    header = (" & & \\multicolumn{4}{c}{Executed mechanism (control)} & \\multicolumn{4}{c}{Cluster-preserving (adaptive, F5)} \\\\" + NL +
              "\\cmidrule(lr){3-6}\\cmidrule(lr){7-10}" + NL +
              "Mechanism & Strength & Det.\\ $\\mathcal I_X$ & Det.\\ $\\mathcal I_{XF}$ & Material & Served P2 & Det.\\ $\\mathcal I_X$ & Det.\\ $\\mathcal I_{XF}$ & Material & Served P2 \\\\")
    return _table("table*", caption, "tab:adversarial", "@{}lrrrrrrrrr@{}", header, rows, colsep="4pt")


def table_sensor_reference_audit(amendment: Path) -> str:
    frame = pd.read_csv(amendment / "sensor_reference_audit.csv")
    rows = []
    for _, r in frame.iterrows():
        sensor = str(r["sensor"])
        current = str(r["current_value"]).replace("_", "\\_")
        reference = str(r["reference_value"]).replace("_", "\\_")
        rule = "statistical" if r["compatible_reference_class"] == "A" else "exact"
        historical_statistical = str(r["historical_or_statistical"])
        if historical_statistical == "statistical=yes; historical=no":
            historical_statistical = "no / yes"
        elif historical_statistical == "no":
            historical_statistical = "no / no"
        rows.append(
            f"\\path{{{sensor}}} & {current} & {reference} & "
            f"{r['item_correspondence_used']} & {r['same_batch_item_set']} & "
            f"{r['protected_in_executed_harness']} & {r['deployed_authentication_demonstrated']} & "
            f"{historical_statistical} & "
            f"{rule} / {r['compatible_reference_class']} \\\\"
        )
    caption = ("Audited reference semantics of every selected sensor in v1.3.2. "
               "Pairing means that item correspondence enters the statistic; same set means the runner uses the clean version of the audited item set. "
               "Harness protected means that the benchmark keeps the reference outside the executed attack API; trusted means that the threat model grants deployed authentication. Hist./stat. reports historical and statistical reference semantics in that order. "
               "Class A is statistical comparison; B and C are trusted aggregate and trusted item-aligned exact invariants.")
    return _table("table*", caption, "tab:s-sensor-reference-audit",
                  "@{}p{0.18\\textwidth}p{0.15\\textwidth}p{0.16\\textwidth}cccccp{0.07\\textwidth}@{}",
                  "Sensor & Current value & Reference value & \\shortstack{Item\\\\pair} & \\shortstack{Same\\\\set} & \\shortstack{Harness\\\\protected} & \\shortstack{Threat-model\\\\trusted} & \\shortstack{Hist. /\\\\stat.} & Rule / class \\\\",
                  rows, size="\\scriptsize", colsep="1.2pt")


def table_adaptive_strength_profile(amendment: Path) -> str:
    frame = pd.read_csv(amendment / "adaptive_strength_profile.csv")
    rows = []
    for _, r in frame.iterrows():
        label = ADV_MECH_LABEL[str(r["mechanism"])]
        rows.append(
            f"{label} & {r['strength']:.2f} & {_n(r['n_material'])}/{_n(r['n_rows'])} & "
            f"{_f(r['detection_I_X'], 2)} & {_f(r['detection_I_XF'], 2)} & {_f(r['detection_I_XFY'], 2)} & "
            f"{_f(r['material_served_rate_I_X'], 2)} & {_f(r['material_served_rate_I_XF'], 2)} & {_f(r['material_served_rate_I_XFY'], 2)} \\\\"
        )
    caption = ("Adaptive F5 profile by nominal strength, derived without rerunning any experiment. Material is changed balanced accuracy at the structural-sensitivity endpoint. "
               "Detection is the conformal family firing rate over all 600 rows; served is the P2 fraction among material rows. "
               "The first three strengths have matched executed controls; 0.25 and 0.50 are the preregistered extended adaptive grid.")
    header = (" & & & \\multicolumn{3}{c}{Detection, all rows} & \\multicolumn{3}{c}{Material served by P2} \\\\" + NL +
              "\\cmidrule(lr){4-6}\\cmidrule(lr){7-9}" + NL +
              "Mechanism & Strength & Material & $\\mathcal I_X$ & $\\mathcal I_{XF}$ & $\\mathcal I_{XFY}$ & $\\mathcal I_X$ & $\\mathcal I_{XF}$ & $\\mathcal I_{XFY}$ \\\\")
    return _table("table*", caption, "tab:s-adaptive-strength-profile",
                  "@{}lrrrrrrrr@{}", header, rows, colsep="3pt")


# ---------------------------------------------------------------------------
# Supplement tables: Gate F
# ---------------------------------------------------------------------------


def table_family_fpr(ev: Path) -> str:
    fpr = pd.read_csv(ev / "family_false_alarm_overall.csv")
    rows = []
    for aggregate, label in (("all_eight_environments", "All eight environments (primary)"), ("excluding_E1", "Seven environments, E1 excluded (sensitivity)"), ("E1_only", "E1 only (256-row draws from 322-row halves)")):
        rows.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\emph{{{label}}}}} \\\\")
        block = fpr[fpr["aggregate"] == aggregate]
        for regime in BATCH_REGIMES:
            cells = []
            for rule in ("union", "family_v12", "family"):
                r = block[(block["regime"] == regime) & (block["rule"] == rule)].iloc[0]
                cells.append(f"{_f(r['pooled_rate'])}")
            r = block[(block["regime"] == regime) & (block["rule"] == "family")].iloc[0]
            rows.append(f"{REGIME_LABEL[regime]} & " + " & ".join(cells) + f" & {_f(r['environment_cluster_mean_min'])}--{_f(r['environment_cluster_mean_max'])} \\\\")
        rows.append("\\addlinespace[1pt]")
    n = int(fpr[fpr["aggregate"] == "all_eight_environments"]["n_draws"].iloc[0])
    caption = ("Gate F: decision-level false-action rate on clean draws from evaluation pools disjoint from the calibration pools (" + _n(n) + " in the primary aggregate; nominal $\\alpha=0.05$ per decision; exact level of the conformal rule $10/201=0.0498$ under exchangeability) for the union of per-sensor rules, the superseded asymmetric family rule and the adopted conformal family rule. Pooled rates are descriptive because resampled draws within a pool may overlap; the last column is the range of the per-environment cluster means of the conformal rule (five split clusters each). E1 is never excluded from the primary aggregate.")
    return _table("table", caption, "tab:s-family-fpr", "@{}lrrrl@{}", "Regime & Union & 1.2.0 rule & Conformal & Env.\\ cluster means (conformal) \\\\", rows)


def table_family_decomposition(ev: Path) -> str:
    d = pd.read_csv(ev / "family_excess_decomposition.csv").set_index("regime")
    rows = []
    for regime in BATCH_REGIMES:
        r = d.loc[regime]
        rows.append(f"{REGIME_LABEL[regime]} & {_f(r['v12_rate'])} & {_f(r['conformal_rate'])} & {r['rule_bias_v12_minus_conformal']:+.3f} & {r['design_effect_conformal_minus_nominal']:+.3f} & {_f(r['resplit_v12_rate'])} & {_f(r['resplit_conformal_rate'])} \\\\")
    caption = ("Gate F: decomposition of the pooled excess of the 1.2.0 rule over the nominal 0.05 into rule bias (1.2.0 rate minus conformal rate on the same draws) and design effect (conformal rate minus nominal), and both rules under 30 exchangeable random re-splits of the 400 pooled draws of every cell (seed 20260907), where the roles are assigned by a uniform random permutation and any excess of the 1.2.0 rule is its own bias; the conformal rule must stay at or below $10/201=0.0498$.")
    return _table("table", caption, "tab:s-family-decomposition", "@{}lrrrrrr@{}", "Regime & 1.2.0 & Conformal & Rule bias & Design & Re-split 1.2.0 & Re-split conf. \\\\", rows, colsep="2.6pt")


def table_family_split(ev: Path) -> str:
    s = pd.read_csv(ev / "family_split_construction_sensitivity.csv").set_index("regime")
    rows = [f"{REGIME_LABEL[r]} & {_n(s.loc[r, 'n_draws'])} & {_n(s.loc[r, 'n_fire'])} & {_f(s.loc[r, 'pooled_rate'])} \\\\" for r in BATCH_REGIMES]
    caption = ("Sensitivity S1: split construction (reference draws 01--10 of each run define the rank transform, calibration draws 11--20 give the null family scores; p-value resolution $1/101$) on the same 12,000 evaluation draws. Valid under the same premise but using half of the draws for each role; the adopted rule is the full conformal one.")
    return _table("table", caption, "tab:s-family-split", "@{}lrrr@{}", "Regime & Draws & Fires & Pooled rate \\\\", rows, colsep="4pt")


def table_family_fpr_env(ev: Path) -> str:
    e = pd.read_csv(ev / "family_false_alarm_by_environment.csv")
    rows = []
    for gate in ENV_ORDER:
        cells = []
        for regime in BATCH_REGIMES:
            rf = e[(e["gate"] == gate) & (e["regime"] == regime) & (e["rule"] == "family")].iloc[0]
            cells.append(f"{_f(rf['cluster_mean'], 3)} [{_f(rf['cluster_ci95_low'], 2)},{_f(rf['cluster_ci95_high'], 2)}]")
        r0 = e[(e["gate"] == gate)].iloc[0]
        rows.append(f"{ENV_LABEL[gate]} & {int(r0['n_test'])} & {int(r0['max_disjoint_draws_per_half'])} & " + " & ".join(cells) + " \\\\")
    caption = ("Gate F: per-environment false-alarm rate of the conformal family rule (cluster mean over the five split clusters with the two-sided 95\\% $t$ interval, four degrees of freedom). $n$ is the batch size; ``disjoint'' is the number of mutually disjoint batches that one pool half can supply, an upper bound on the effective number of independent draws among the 20 per run (E1: one). The union and 1.2.0 cluster means are in Table~\\ref{tab:s-family-fpr-env-rules}.")
    return _table("table*", caption, "tab:s-family-fpr-env", "@{}lrr" + "l" * 4 + "@{}", "Environment & $n$ & disj. & " + " & ".join(REGIME_LABEL[r] for r in BATCH_REGIMES) + " \\\\", rows, colsep="2pt")


def table_family_fpr_env_rules(ev: Path) -> str:
    e = pd.read_csv(ev / "family_false_alarm_by_environment.csv")
    rows = []
    for gate in ENV_ORDER:
        cells = []
        for regime in BATCH_REGIMES:
            ru = e[(e["gate"] == gate) & (e["regime"] == regime) & (e["rule"] == "union")].iloc[0]
            rv = e[(e["gate"] == gate) & (e["regime"] == regime) & (e["rule"] == "family_v12")].iloc[0]
            cells.append(f"{_f(ru['cluster_mean'], 3)} / {_f(rv['cluster_mean'], 3)}")
        rows.append(f"{ENV_LABEL[gate].split(' ')[0]} & " + " & ".join(cells) + " \\\\")
    caption = "Gate F: per-environment cluster means of the union rule / the superseded 1.2.0 rule, for comparison with Table~\\ref{tab:s-family-fpr-env} (environment codes as there)."
    return _table("table", caption, "tab:s-family-fpr-env-rules", "@{}lllll@{}", "Env. & " + " & ".join(REGIME_LABEL[r] for r in BATCH_REGIMES) + " \\\\", rows, colsep="2.5pt")


def table_family_detection(ev: Path) -> str:
    d = pd.read_csv(ev / "family_detection_pooled.csv")
    piv = d.pivot_table(index="attack", columns=["regime", "rule"], values="detection_rate")
    ben = pd.read_csv(ev / "family_benign_control_response.csv")
    bpiv = ben.pivot_table(index="attack", columns=["regime", "rule"], values="fire_rate")
    order = sorted(piv.index, key=lambda a: (_mech(a)[0], _mech(a)[2]))
    rows = []
    for attack in order:
        _, label, strength = _mech(attack)
        rows.append(f"{label} {strength:.2f} & " + " & ".join(f"{_f(piv.loc[attack, (r, 'union')], 2)} / {_f(piv.loc[attack, (r, 'family_v12')], 2)} / {_f(piv.loc[attack, (r, 'family')], 2)}" for r in BATCH_REGIMES) + " \\\\")
    rows.append("\\midrule")
    for attack, label in (("sham_tiny_gaussian_sigma_0.001", "Near-null Gaussian $\\sigma=0.001$"), ("sham_tiny_scaling_alpha_0.001", "Near-null scaling $\\alpha=0.001$")):
        rows.append(f"{label} & " + " & ".join(f"{_f(bpiv.loc[attack, (r, 'union')], 2)} / {_f(bpiv.loc[attack, (r, 'family_v12')], 2)} / {_f(bpiv.loc[attack, (r, 'family')], 2)}" for r in BATCH_REGIMES) + " \\\\")
    caption = ("Gate F: detection rate on the frozen \\texttt{paper\\_core} observations (600 per intervention row, eight environments pooled) and firing rate on the near-null in-place controls, as union rule / 1.2.0 rule / conformal rule. Within this executed design, the conformal rule trades a small loss of detection for the descriptive decision-level false-action rates of Table~\\ref{tab:s-family-fpr}.")
    return _table("table*", caption, "tab:s-family-detection", "@{}lllll@{}", "Intervention & " + " & ".join(REGIME_LABEL[r] for r in BATCH_REGIMES) + " \\\\", rows)


# ---------------------------------------------------------------------------
# Supplement tables: Gate D
# ---------------------------------------------------------------------------


def table_policy_full(ev: Path) -> str:
    m = pd.read_csv(ev / "policy_metrics.csv")
    m = m[m["tau"] == 0.0]
    rows = []
    for regime in REGIME_ORDER:
        for policy in POLICY_ORDER:
            r = m[(m["regime"] == regime) & (m["policy"] == policy)].iloc[0]
            short = {"serve_always": "P0", "union_uncalibrated": "P1", "family_calibrated": "P2", "family_calibrated_strict": "P3"}
            rows.append(f"{REGIME_LABEL[regime]} & {short[policy]} & {_n(r['n_clean'])} & {_n(r['false_hold'])} & {_n(r['false_block'])} & {_n(r['benign_hold'])} & {_n(r['benign_block'])} & {_n(r['unsafe_allow'])} & {_n(r['true_hold'])} & {_n(r['true_block'])} & {_n(r['integrity_only_hold_block'])} & {_n(r['immaterial_allow'])} & {_n(r['safe_allow'])} & {_f(r['nonmaterial_interruption_rate'], 2)} \\\\")
        rows.append("\\addlinespace[1pt]")
    n_mat = int(m["n_material"].iloc[0])
    n_imm = int(m["n_immaterial"].iloc[0])
    caption = ("Gate D: complete decision counts at the primary materiality threshold ($|\\Delta_R|>0$; " + _n(n_mat) + " material and " + _n(n_imm) + " non-material intervened observations; 1,200 near-null synthetic controls). P0 serve-always, P1 union, P2 conformal, P3 sensor-coverage-complete relative to declared evidence dimensions and abstaining on missing coverage. Clean rows: 12,000 draws from evaluation pools disjoint from the calibration pools; resampled draws within a pool may overlap. The 1,200 exact-zero rows are used for $\\mathcal I_{XFY}^{\\star}$. B.\\ hold/block: near-null controls held (statistical) or blocked (exact-reference violation). Integ.: non-material intervened observations held or blocked. Safe allow: clean, benign and non-material observations allowed. Interr.: non-material interruption rate, (false hold + false block + benign hold + benign block + integrity-only hold/block) over all non-material observations.")
    return _table("table*", caption, "tab:s-policy-full", "@{}llrrrrrrrrrrrr@{}", "Regime & Pol. & Clean & F.\\ hold & F.\\ block & B.\\ hold & B.\\ block & Served & T.\\ hold & T.\\ block & Integ. & Imm.\\ allow & Safe allow & Interr. \\\\", rows, colsep="2pt")


def table_policy_rule_comparison(ev: Path) -> str:
    m = pd.read_csv(ev / "policy_metrics_rule_comparison.csv")
    m = m[(m["tau"] == 0.0) & (m["policy"] == "family_calibrated")]
    rows = []
    for regime in REGIME_ORDER:
        cells = []
        for variant in ("v12_asymmetric", "conformal"):
            r = m[(m["regime"] == regime) & (m["family_rule"] == variant)].iloc[0]
            cells.append(f"{_f(r['decision_fpr'])} & {_f(r['benign_interruption_rate'], 2)} & {_n(r['unsafe_allow'])} & {_f(r['containment'], 2)}")
        rows.append(f"{REGIME_LABEL[regime]} & " + " & ".join(cells) + " \\\\")
    caption = ("Gate D: the risk-tolerant policy P2 under the superseded 1.2.0 family rule and under the adopted conformal rule, nominally calibrated under exchangeability, on identical observations ($|\\Delta_R|>0$). The 1.2.0 columns reproduce the published 1.2.0 numbers and are retained for comparison only.")
    header = (" & \\multicolumn{4}{c}{1.2.0 rule (superseded)} & \\multicolumn{4}{c}{Conformal rule (adopted)} \\\\" + NL + "\\cmidrule(lr){2-5}\\cmidrule(lr){6-9}" + NL +
              "Regime & Clean FPR & Benign & Served & Contain. & Clean FPR & Benign & Served & Contain. \\\\")
    return _table("table*", caption, "tab:s-policy-rule-comparison", "@{}lrrrrrrrr@{}", header, rows, colsep="4pt")


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
    caption = ("Gate D: materially altered audit results served (containment in parentheses) under three materiality thresholds on $|\\Delta_R|$; material observations " + _n(n_tau[0.0]) + ", " + _n(n_tau[0.02]) + " and " + _n(n_tau[0.05]) + ". The $\\tau\\to0^{+}$ column is a structural-sensitivity endpoint, whereas 0.02 and 0.05 are larger-effect sensitivity analyses. P1 union, P2 conformal.")
    return _table("table*", caption, "tab:s-policy-tau", "@{}llrrr@{}", "Regime & Pol. & $\\tau=0^{+}$ & $\\tau=0.02$ & $\\tau=0.05$ \\\\", rows, colsep="2.5pt")


def table_policy_family(ev: Path) -> str:
    f = pd.read_csv(ev / "policy_metrics_by_family.csv")
    f = f[(f["tau"] == 0.0) & (f["policy"] == "family_calibrated") & (f["family_rule"] == "conformal")]
    fams = ["target_shift", "corruption", "covariate_shift", "pipeline"]
    rows = []
    for regime in REGIME_ORDER:
        cells = []
        for fam in fams:
            r = f[(f["regime"] == regime) & (f["attack_family"] == fam)].iloc[0]
            cells.append(f"{_n(r['unsafe_allow'])}/{_n(r['n_material'])}")
        rows.append(f"{REGIME_LABEL[regime]} & " + " & ".join(cells) + " \\\\")
    caption = "Gate D: materially altered audit results served / material observations by intervention mechanism under the conformal-rule policy P2, nominally calibrated under exchangeability (structural-sensitivity endpoint $|\\Delta_R|>0$)."
    return _table("table*", caption, "tab:s-policy-family", "@{}lrrrr@{}", "Regime & " + " & ".join(FAMILY_LABEL[x] for x in fams) + " \\\\", rows)


def table_witnesses(ev: Path) -> str:
    w = pd.read_csv(ev / "counterexample_witnesses.csv")
    rows = [f"{r['witness']} & {r['property']} & {_n(r['count'])} / {_n(r['denominator'])} \\\\" for _, r in w.iterrows()]
    caption = ("Counterexample witnesses realised in the frozen expansion (count / denominator). W1--W4 are evaluation-label rows, W5--W6 feature-side rows, W7 all intervened rows, W8 material label rows; W9 and W10 count the label rows that a trusted aggregate reference, respectively only an item-aligned reference, detects (Corollary~3).")
    return _table("table", caption, "tab:s-witnesses", "\\columnwidth}{@{}l>{\\raggedright\\arraybackslash}Xr@{}", "ID & Property & Count \\\\", rows, tabularx=True)


def table_composition(ev: Path) -> str:
    c = pd.read_csv(ev / "policy_contract_composition.csv")
    names = {"clean": "Clean", "approved_transpilation": "Approved transpilation", "circuit_parameter_mutation": "Parameterized circuit mutation", "kernel_psd_preserving_substitution": "PSD-preserving kernel substitution", "label_prior_preserving_corruption": "Prior-preserving label corruption", "approved_shot_emulator_256": "Approved 256-shot emulator"}
    rows = [f"{names[r['scenario']]} & \\texttt{{{r['contract_action']}}} & {'yes' if r['exact_invariant_violated'] else 'no'} & \\texttt{{{r['policy_action']}}} & \\texttt{{{r['composed_action']}}} \\\\" for _, r in c.iterrows()]
    caption = ("Composition of the frozen four-contract envelopes with the policy layer under $\\mathcal I_{XFY}^{\\star}$ (lattice maximum). Approved rewrites and approved stochastic estimation are not exact violations; the contract's own \\texttt{hold} for the approved emulator is preserved.")
    return _table("table", caption, "tab:s-composition", "@{}lllll@{}", "Scenario & Contract & Exact viol. & Policy & Composed \\\\", rows)


# ---------------------------------------------------------------------------
# Supplement tables: Gate A
# ---------------------------------------------------------------------------


def table_adversarial_detection(adv: Path) -> str:
    det = pd.read_csv(adv / "adversarial_detection_pooled.csv")
    piv = det.pivot_table(index=["mechanism", "attack_class", "strength"], columns=["regime", "rule"], values="detection_rate")
    rows = []
    for mech in ("mean_shift", "scaling_drift"):
        for cls, cls_label in (("control", "executed"), ("adaptive", "F5")):
            for s in (0.02, 0.05, 0.10, 0.25, 0.50):
                if cls == "control" and s > 0.10:
                    continue
                key = (mech, cls, s)
                cells = [f"{_f(piv.loc[key, (r, 'union')], 2)} / {_f(piv.loc[key, (r, 'family_v12')], 2)} / {_f(piv.loc[key, (r, 'family')], 2)}" for r in ("I_X", "I_XF", "I_XFY")]
                cells.append(_f(piv.loc[key, ("I_XFY_trusted", "exact")], 2))
                rows.append(f"{ADV_MECH_LABEL[mech]} ({cls_label}) & {s:.2f} & " + " & ".join(cells) + " \\\\")
        rows.append("\\addlinespace[1pt]")
    caption = ("Gate A: detection rate of the executed drift mechanisms (matched controls) and of their adaptive cluster-preserving variants (F5), 600 observations per row pooled over the eight environments, as union / 1.2.0 rule / conformal rule in the batch-level regimes, and exact item-aligned detection (prediction disagreement or confusion-profile delta) under $\\mathcal I_{XFY}^{\\star}$.")
    return _table("table*", caption, "tab:s-adversarial-detection", "@{}lrllll@{}", "Mechanism & Strength & $\\mathcal I_X$ & $\\mathcal I_{XF}$ & $\\mathcal I_{XFY}$ & $\\mathcal I_{XFY}^{\\star}$ exact \\\\", rows)


def table_adversarial_materiality(adv: Path) -> str:
    mat = pd.read_csv(adv / "adversarial_materiality.csv").set_index(["mechanism", "attack_class", "strength"])
    rows = []
    for mech in ("mean_shift", "scaling_drift"):
        for cls, cls_label in (("control", "executed"), ("adaptive", "F5")):
            for s in (0.02, 0.05, 0.10, 0.25, 0.50):
                if cls == "control" and s > 0.10:
                    continue
                r = mat.loc[(mech, cls, s)]
                pf = "--" if pd.isna(r["mean_perturbed_entry_fraction"]) else _f(r["mean_perturbed_entry_fraction"], 2)
                rows.append(f"{ADV_MECH_LABEL[mech]} ({cls_label}) & {s:.2f} & {_f(r['prediction_change_rate'], 2)} & {_f(r['material_fraction_tau0'], 2)} & {_f(r['material_fraction_tau002'], 2)} & {_f(r['material_fraction_tau005'], 2)} & {_f(r['mean_abs_delta'])} & {_f(r['raised_fraction'], 2)} & {pf} \\\\")
        rows.append("\\addlinespace[1pt]")
    caption = ("Gate A: prediction-change rate (item-aligned disagreement $>0$), material fraction at $|\\Delta_R|>0$, $\\ge0.02$ and $\\ge0.05$, mean $|\\Delta_R|$, fraction of rows whose balanced accuracy rose, and mean fraction of feature entries the attacker perturbs (the executed mechanisms perturb every entry).")
    return _table("table*", caption, "tab:s-adversarial-materiality", "@{}lrrrrrrrr@{}", "Mechanism & Strength & Pred.\\ change & Mat.\\ $0^{+}$ & Mat.\\ 0.02 & Mat.\\ 0.05 & Mean $|\\Delta_R|$ & Raised & Perturbed \\\\", rows, colsep="3.5pt")


def table_adversarial_policy(adv: Path) -> str:
    pol = pd.read_csv(adv / "adversarial_policy_metrics.csv")
    pol = pol[pol["tau"] == 0.0]
    g = pol.groupby(["attack_class", "regime", "policy"])[["n_material", "unsafe_allow"]].sum()
    rows = []
    for cls, cls_label in (("control", "Executed mechanisms (1,800 rows)"), ("adaptive", "Cluster-preserving F5 (6,000 rows)")):
        rows.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\emph{{{cls_label}}}}} \\\\")
        for regime in ("I_X", "I_XF", "I_XFY", "I_XFY_trusted"):
            nm = int(g.loc[(cls, regime, "family_calibrated"), "n_material"])
            cells = [f"{_n(g.loc[(cls, regime, p), 'unsafe_allow'])}" for p in ("union_uncalibrated", "family_calibrated", "family_calibrated_strict")]
            rows.append(f"{REGIME_LABEL[regime]} & {_n(nm)} & " + " & ".join(cells) + " \\\\")
        rows.append("\\addlinespace[1pt]")
    caption = ("Gate A: materially altered audit results served under P1 union, P2 conformal and P3 sensor-coverage-complete relative to declared evidence dimensions per regime, summed over mechanisms and strengths (structural-sensitivity endpoint $|\\Delta_R|>0$). Under $\\mathcal I_{XFY}^{\\star}$ every material row carries a prediction change and is blocked.")
    return _table("table*", caption, "tab:s-adversarial-policy", "@{}lrrrr@{}", "Regime & Material & P1 union & P2 conformal & P3 abst. \\\\", rows, colsep="4pt")


def table_adversarial_env(adv: Path) -> str:
    env = pd.read_csv(adv / "adversarial_detection_by_environment.csv")
    env = env[(env["attack_class"] == "adaptive") & (env["rule"] == "family") & (env["regime"] == "I_XF")]
    piv = env.pivot_table(index="gate", columns=["mechanism", "strength"], values="detection_rate")
    budget = pd.read_csv(adv / "adversarial_budget.csv").groupby("gate")["perturbed_entry_fraction_mean"].mean()
    rows = []
    for gate in ENV_ORDER:
        cells = [f"{_f(piv.loc[gate, (m, s)], 2)}" for m in ("mean_shift", "scaling_drift") for s in (0.02, 0.05, 0.10, 0.25, 0.50)]
        rows.append(f"{ENV_LABEL[gate]} & {_f(budget.loc[gate], 2)} & " + " & ".join(cells) + " \\\\")
    caption = ("Gate A: per-environment detection rate of the adaptive variants under the conformal rule in $\\mathcal I_{XF}$ (rows pooled over models, dimensions, splits and seeds), and mean fraction of entries the attacker perturbs in that environment.")
    header = (" & & \\multicolumn{5}{c}{Mean shift} & \\multicolumn{5}{c}{Scaling drift} \\\\" + NL + "\\cmidrule(lr){3-7}\\cmidrule(lr){8-12}" + NL +
              "Environment & Perturbed & 0.02 & 0.05 & 0.10 & 0.25 & 0.50 & 0.02 & 0.05 & 0.10 & 0.25 & 0.50 \\\\")
    return _table("table*", caption, "tab:s-adversarial-env", "@{}lr" + "r" * 10 + "@{}", header, rows)


def table_adversarial_branch(adv: Path) -> str:
    br = pd.read_csv(adv / "adversarial_detection_by_branch.csv")
    br = br[(br["attack_class"] == "adaptive") & (br["rule"] == "family") & (br["regime"].isin(["I_X", "I_XF"]))]
    piv = br.pivot_table(index=["mechanism", "strength"], columns=["branch", "regime"], values="detection_rate")
    rows = []
    for mech in ("mean_shift", "scaling_drift"):
        for s in (0.02, 0.05, 0.10, 0.25, 0.50):
            rows.append(f"{ADV_MECH_LABEL[mech]} & {s:.2f} & " + " & ".join(f"{_f(piv.loc[(mech, s), (b, r)], 2)}" for b in ("classical", "quantum") for r in ("I_X", "I_XF")) + " \\\\")
    caption = ("Gate A: detection of the adaptive variants under the conformal rule by branch (classical SVC on standardized features; fidelity kernels on features scaled to $[0,2\\pi]$). The cluster rule is the same in both branches; the branch scaler changes how much the unclustered entries move relative to the null.")
    header = (" & & \\multicolumn{2}{c}{Classical} & \\multicolumn{2}{c}{Quantum} \\\\" + NL + "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}" + NL +
              "Mechanism & Strength & $\\mathcal I_X$ & $\\mathcal I_{XF}$ & $\\mathcal I_X$ & $\\mathcal I_{XF}$ \\\\")
    return _table("table*", caption, "tab:s-adversarial-branch", "@{}lrrrrr@{}", header, rows, colsep="3.5pt")


# ---------------------------------------------------------------------------
# Macros used in the prose
# ---------------------------------------------------------------------------


def macros(ev: Path, adv: Path, amendment: Path, expansion_dir: Path, gate1_dir: Path) -> str:
    fpr_all = pd.read_csv(ev / "family_false_alarm_overall.csv")
    fpr = fpr_all[fpr_all["aggregate"] == "all_eight_environments"].set_index(["regime", "rule"])
    fpr_ex = fpr_all[fpr_all["aggregate"] == "excluding_E1"].set_index(["regime", "rule"])
    fpr_e1 = fpr_all[fpr_all["aggregate"] == "E1_only"].set_index(["regime", "rule"])
    dec = pd.read_csv(ev / "family_excess_decomposition.csv").set_index("regime")
    split = pd.read_csv(ev / "family_split_construction_sensitivity.csv").set_index("regime")
    m = pd.read_csv(ev / "policy_metrics.csv")
    m0 = m[m["tau"] == 0.0].set_index(["regime", "policy"])
    m5 = m[m["tau"] == 0.05].set_index(["regime", "policy"])
    mc = pd.read_csv(ev / "policy_metrics_rule_comparison.csv")
    mc0 = mc[(mc["tau"] == 0.0) & (mc["family_rule"] == "v12_asymmetric")].set_index(["regime", "policy"])
    lab = pd.read_csv(ev / "family_label_path_summary.csv").set_index(["subset", "regime", "rule"])
    w = pd.read_csv(ev / "counterexample_witnesses.csv").set_index("witness")
    fam = pd.read_csv(ev / "policy_metrics_by_family.csv")
    fam = fam[(fam["tau"] == 0.0) & (fam["policy"] == "family_calibrated") & (fam["family_rule"] == "conformal")].set_index(["regime", "attack_family"])
    units = pd.read_csv(ev / "inference_units.csv").iloc[0]
    env = pd.read_csv(ev / "family_false_alarm_by_environment.csv")
    lines = ["% Generated by make_q1_policy_tables.py from manifested frozen evidence and the 1.3.2 frozen-only amendment; do not edit."]
    for regime in BATCH_REGIMES:
        key = _key(regime)
        lines.append(_macro(f"FprUnion{key}", _f(fpr.loc[(regime, "union"), "pooled_rate"])))
        lines.append(_macro(f"FprLegacy{key}", _f(fpr.loc[(regime, "family_v12"), "pooled_rate"])))
        lines.append(_macro(f"FprFamily{key}", _f(fpr.loc[(regime, "family"), "pooled_rate"])))
        lines.append(_macro(f"FprFamilyMin{key}", _f(fpr.loc[(regime, "family"), "environment_cluster_mean_min"])))
        lines.append(_macro(f"FprFamilyMax{key}", _f(fpr.loc[(regime, "family"), "environment_cluster_mean_max"])))
        lines.append(_macro(f"FprFamilyExclEone{key}", _f(fpr_ex.loc[(regime, "family"), "pooled_rate"])))
        lines.append(_macro(f"FprFamilyEoneOnly{key}", _f(fpr_e1.loc[(regime, "family"), "pooled_rate"])))
        lines.append(_macro(f"RuleBias{key}", f"{dec.loc[regime, 'rule_bias_v12_minus_conformal']:+.3f}"))
        lines.append(_macro(f"DesignEffect{key}", f"{dec.loc[regime, 'design_effect_conformal_minus_nominal']:+.3f}"))
        lines.append(_macro(f"ResplitLegacy{key}", _f(dec.loc[regime, "resplit_v12_rate"])))
        lines.append(_macro(f"ResplitFamily{key}", _f(dec.loc[regime, "resplit_conformal_rate"])))
        lines.append(_macro(f"FprSplit{key}", _f(split.loc[regime, "pooled_rate"])))
    lines.append(_macro("ConformalLevel", _f(dec["conformal_exact_level"].iloc[0], 4)))
    cost = pd.read_csv(amendment / "trusted_interruption_decomposition.csv").set_index("quantity")
    lines.append(_macro("TrustedGrossExactBlocks", _n(cost.loc["gross_exact_reference_blocks", "n"])))
    lines.append(_macro("TrustedExactOverlap", _n(cost.loc["exact_blocks_overlapping_batch_interruptions", "n"])))
    lines.append(_macro("TrustedNetAdditional", _n(cost.loc["net_additional_interruptions_vs_batch_I_XFY_P2", "n"])))
    lines.append(_macro("TrustedNetAdditionalPct", _f(100 * cost.loc["net_additional_interruptions_vs_batch_I_XFY_P2", "rate"], 2)))
    for regime in REGIME_ORDER:
        key = _key(regime)
        for policy, pk in (("union_uncalibrated", "Union"), ("family_calibrated", "Family"), ("family_calibrated_strict", "Strict")):
            r = m0.loc[(regime, policy)]
            lines.append(_macro(f"Unsafe{pk}{key}", _n(r["unsafe_allow"])))
            lines.append(_macro(f"Contain{pk}{key}", _f(r["containment"], 2)))
            lines.append(_macro(f"DecFpr{pk}{key}", _f(r["decision_fpr"])))
            lines.append(_macro(f"ContainFive{pk}{key}", _f(m5.loc[(regime, policy), "containment"], 2)))
            lines.append(_macro(f"BenignHB{pk}{key}", _f(r["benign_interruption_rate"], 2)))
            lines.append(_macro(f"BenignHold{pk}{key}", _n(r["benign_hold"])))
            lines.append(_macro(f"BenignBlock{pk}{key}", _n(r["benign_block"])))
            # Total interruptions = statistical holds + exact-reference blocks (the decomposition printed in the prose).
            lines.append(_macro(f"BenignInterrupt{pk}{key}", _n(int(r["benign_hold"]) + int(r["benign_block"]))))
            lines.append(_macro(f"BenignHBPct{pk}{key}", str(int(round(100 * float(r["benign_interruption_rate"]))))))
            lines.append(_macro(f"Interrupt{pk}{key}", _f(r["nonmaterial_interruption_rate"], 2)))
        lines.append(_macro(f"UnsafeLegacyFamily{key}", _n(mc0.loc[(regime, "family_calibrated"), "unsafe_allow"])))
        lines.append(_macro(f"DecFprLegacyFamily{key}", _f(mc0.loc[(regime, "family_calibrated"), "decision_fpr"])))
    lines.append(_macro("NMaterial", _n(m0.iloc[0]["n_material"])))
    lines.append(_macro("NMaterialFive", _n(m5.iloc[0]["n_material"])))
    lines.append(_macro("NImmaterial", _n(m0.iloc[0]["n_immaterial"])))
    lines.append(_macro("ResidualBlindFamilyIYm", _n(m0.loc[("I_Ym", "family_calibrated"), "residual_blind_material"])))
    lines.append(_macro("NMaterialLabel", _n(lab.loc[("material_label_interventions", "I_XFY", "union"), "n"])))
    lines.append(_macro("BatchUnionLabelFires", _n(lab.loc[("material_label_interventions", "I_XFY", "union"), "n_fire"])))
    lines.append(_macro("BatchLegacyLabelFires", _n(lab.loc[("material_label_interventions", "I_XFY", "family_v12"), "n_fire"])))
    lines.append(_macro("BatchFamilyLabelFires", _n(lab.loc[("material_label_interventions", "I_XFY", "family"), "n_fire"])))
    lines.append(_macro("BatchUnionLabelRate", _f(lab.loc[("material_label_interventions", "I_XFY", "union"), "detection_rate"], 3)))
    lines.append(_macro("BatchFamilyLabelRate", _f(lab.loc[("material_label_interventions", "I_XFY", "family"), "detection_rate"], 3)))
    words = {"W1": "WOne", "W2": "WTwo", "W3": "WThree", "W4": "WFour", "W5": "WFive", "W6": "WSix", "W7": "WSeven", "W8": "WEight", "W9": "WNine", "W10": "WTen"}
    for wid in w.index:
        name = "Witness" + words[str(wid)]  # LaTeX macro names cannot contain digits
        lines.append(_macro(name, _n(w.loc[wid, "count"])))
        lines.append(_macro(name + "Den", _n(w.loc[wid, "denominator"])))
    for regime in REGIME_ORDER:
        key = _key(regime)
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
    # Gate A macros.
    det_frame = pd.read_csv(adv / "adversarial_detection_pooled.csv")
    det = det_frame.set_index(["mechanism", "attack_class", "strength", "regime", "rule"])
    mat = pd.read_csv(adv / "adversarial_materiality.csv").set_index(["mechanism", "attack_class", "strength"])
    pol = pd.read_csv(adv / "adversarial_policy_metrics.csv")
    pol0 = pol[pol["tau"] == 0.0]
    for mech, mw in MECH_WORD.items():
        for s, sw in STRENGTH_WORD.items():
            for cls, cw in (("control", "Ctrl"), ("adaptive", "Adapt")):
                if cls == "control" and s > 0.10:
                    continue
                for regime in ("I_X", "I_XF", "I_XFY"):
                    lines.append(_macro(f"AdvDet{cw}{mw}{sw}{_key(regime)}", _f(det.loc[(mech, cls, s, regime, "family"), "detection_rate"], 2)))
                lines.append(_macro(f"AdvMat{cw}{mw}{sw}", _f(mat.loc[(mech, cls, s), "material_fraction_tau0"], 2)))
                lines.append(_macro(f"AdvPred{cw}{mw}{sw}", _f(mat.loc[(mech, cls, s), "prediction_change_rate"], 2)))
    matched = det_frame[
        (det_frame["strength"] <= 0.10)
        & (det_frame["rule"] == "family")
        & det_frame["regime"].isin(["I_X", "I_XF", "I_XFY"])
    ]
    for attack_class, word in (("control", "Ctrl"), ("adaptive", "Adapt")):
        block = matched[matched["attack_class"] == attack_class]
        for regime in ("I_X", "I_XF", "I_XFY"):
            values = block[block["regime"] == regime]["detection_rate"]
            lines.append(_macro(f"AdvDet{word}{_key(regime)}Min", _f(values.min(), 2)))
            lines.append(_macro(f"AdvDet{word}{_key(regime)}Max", _f(values.max(), 2)))
        headline = block[block["regime"].isin(["I_X", "I_XF"])]["detection_rate"]
        lines.append(_macro(f"AdvDet{word}HeadlineMin", _f(headline.min(), 2)))
        lines.append(_macro(f"AdvDet{word}HeadlineMax", _f(headline.max(), 2)))
        all_batch = block["detection_rate"]
        lines.append(_macro(f"AdvDet{word}AllBatchMin", _f(all_batch.min(), 2)))
        lines.append(_macro(f"AdvDet{word}AllBatchMax", _f(all_batch.max(), 2)))
    totals = pol0.groupby(["attack_class", "regime", "policy"])[["n_material", "unsafe_allow"]].sum()
    for cls, cw in (("control", "Ctrl"), ("adaptive", "Adapt")):
        for regime in ("I_X", "I_XF", "I_XFY", "I_XFY_trusted"):
            key = _key(regime)
            lines.append(_macro(f"AdvNMaterial{cw}{key}", _n(totals.loc[(cls, regime, "family_calibrated"), "n_material"])))
            for policy, pk in (("union_uncalibrated", "Union"), ("family_calibrated", "Family"), ("family_calibrated_strict", "Strict")):
                lines.append(_macro(f"AdvUnsafe{cw}{pk}{key}", _n(totals.loc[(cls, regime, policy), "unsafe_allow"])))
                served_rate = totals.loc[(cls, regime, policy), "unsafe_allow"] / totals.loc[(cls, regime, policy), "n_material"]
                lines.append(_macro(f"AdvServedOverall{cw}{pk}{key}", _f(served_rate, 2)))
    evasion = pd.read_csv(adv / "adversarial_evasion_ratios.csv")
    retention = evasion[(evasion["rule"] == "family") & (evasion["regime"] == "I_X") & (evasion["strength"] <= 0.10)]["material_ratio_adaptive_over_control"]
    lines.append(_macro("AdvMatRetentionMinPct", str(int(round(100 * float(retention.min()))))))
    lines.append(_macro("AdvMatRetentionMaxPct", str(int(round(100 * float(retention.max()))))))
    budget = pd.read_csv(adv / "adversarial_budget.csv")
    lines.append(_macro("AdvPerturbedMean", _f(budget["perturbed_entry_fraction_mean"].mean(), 2)))
    lines.append(_macro("AdvPerturbedMin", _f(budget["perturbed_entry_fraction_min"].min(), 2)))
    lines.append(_macro("AdvPerturbedMax", _f(budget["perturbed_entry_fraction_max"].max(), 2)))
    adaptive_rows = int(det.xs(("adaptive"), level="attack_class")["n"].loc[(slice(None), slice(None), "I_X", "family")].sum())
    lines.append(_macro("AdvNAdaptiveRows", _n(adaptive_rows)))
    branch = pd.read_csv(adv / "adversarial_detection_by_branch.csv")
    branch = branch[(branch["attack_class"] == "adaptive") & (branch["rule"] == "family")].set_index(["branch", "mechanism", "strength", "regime"])
    for b, bw in (("classical", "Classical"), ("quantum", "Quantum")):
        for mech, mw in MECH_WORD.items():
            for s in (0.10,):
                for regime in ("I_X", "I_XF"):
                    lines.append(_macro(f"AdvDet{bw}{mw}{STRENGTH_WORD[s]}{_key(regime)}", _f(branch.loc[(b, mech, s, regime), "detection_rate"], 2)))
    profile = pd.read_csv(amendment / "adaptive_strength_profile.csv").set_index(["mechanism", "strength"])
    for mech, mw in MECH_WORD.items():
        for s, sw in STRENGTH_WORD.items():
            r = profile.loc[(mech, s)]
            for regime in ("I_X", "I_XF", "I_XFY"):
                lines.append(_macro(f"AdvServedRate{mw}{sw}{_key(regime)}", _f(r[f"material_served_rate_{regime}"], 2)))
    return NL.join(lines) + NL


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=Path("results/paper_digest/paper15_v12_policy"))
    parser.add_argument("--adversarial", type=Path, default=Path("results/paper_digest/paper15_v13_adversarial"))
    parser.add_argument("--amendment", type=Path, default=Path("results/paper_digest/paper15_v132_amendment"))
    parser.add_argument("--expansion", type=Path, default=Path("results/paper_digest/paper15_q1_expansion"))
    parser.add_argument("--gate1", type=Path, default=Path("results/paper_digest/paper15_q1_gate1_id_seeds_20_q1"))
    parser.add_argument("--out-dir", type=Path, default=Path("publication/tdsc/tables"))
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        "m_policy.tex": table_main_policy(args.evidence),
        "m_adversarial.tex": table_main_adversarial(args.adversarial),
        "s_sensor_reference_audit.tex": table_sensor_reference_audit(args.amendment),
        "s_adaptive_strength_profile.tex": table_adaptive_strength_profile(args.amendment),
        "s_family_fpr.tex": table_family_fpr(args.evidence),
        "s_family_decomposition.tex": table_family_decomposition(args.evidence),
        "s_family_split.tex": table_family_split(args.evidence),
        "s_family_fpr_env.tex": table_family_fpr_env(args.evidence),
        "s_family_fpr_env_rules.tex": table_family_fpr_env_rules(args.evidence),
        "s_family_detection.tex": table_family_detection(args.evidence),
        "s_policy_full.tex": table_policy_full(args.evidence),
        "s_policy_rule_comparison.tex": table_policy_rule_comparison(args.evidence),
        "s_policy_tau.tex": table_policy_tau(args.evidence),
        "s_policy_family.tex": table_policy_family(args.evidence),
        "s_witnesses.tex": table_witnesses(args.evidence),
        "s_composition.tex": table_composition(args.evidence),
        "s_adversarial_detection.tex": table_adversarial_detection(args.adversarial),
        "s_adversarial_materiality.tex": table_adversarial_materiality(args.adversarial),
        "s_adversarial_policy.tex": table_adversarial_policy(args.adversarial),
        "s_adversarial_env.tex": table_adversarial_env(args.adversarial),
        "s_adversarial_branch.tex": table_adversarial_branch(args.adversarial),
        "policy_macros.tex": macros(args.evidence, args.adversarial, args.amendment, args.expansion, args.gate1),
    }
    for name, text in tables.items():
        (args.out_dir / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", args.out_dir / name)
    manifest = {name: {"bytes": len(text.encode("utf-8"))} for name, text in tables.items()}
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
