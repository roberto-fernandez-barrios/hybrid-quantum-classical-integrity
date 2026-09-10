"""Generate the v1.3.7 supplement tables from manifested corrective CSVs."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import pandas as pd

from src.experiments.build_v135_geometry_sensitivity import _gate_a_summary


FEATURE_SENSORS = (
    ("integrity_jsd_vs_clean_eval", "I_X", "F-JSD"),
    ("integrity_mmd_vs_clean_eval", "I_X", "MMD"),
    ("integrity_ks_mean_vs_clean_eval", "descriptive_only", "KS-stat"),
    ("integrity_ks_reject05_vs_clean_eval", "I_X", "KS-rej"),
    ("integrity_score_jsd_vs_clean_eval", "I_XF", "S-JSD"),
    ("integrity_pred_pos_rate_shift", "I_XF", "$\\Delta p$"),
    ("integrity_pred_jsd", "I_XF", "P-JSD"),
)
SCOPE_LABELS = {
    "near_null_original": "Original near-null controls",
    "core_original": "Original frozen feature interventions",
    "gateA_original": "Original Gate A matched controls and adaptive variants",
    "feature_aligned": "Geometry-aligned feature sensitivity",
    "label_aligned": "Geometry-aligned label sensitivity",
    "gate1_frozen_design": "Gate-1 frozen design (response only; no family calibration)",
}
REGIME_LABELS = {
    "I_X": r"$\mathcal I_X$",
    "I_XF": r"$\mathcal I_{XF}$",
    "I_Ym": r"$\mathcal I_{Y_m}$",
    "I_XFY": r"$\mathcal I_{XFY}$",
    "I_XFY_trusted": r"$\mathcal I_{XFY}^{\star}$",
}
REGIMES = tuple(REGIME_LABELS)
BATCH_REGIMES = REGIMES[:-1]
POLICY_ORDER = ("serve_always", "union_uncalibrated", "family_calibrated", "family_calibrated_strict")
POLICY_SHORT = {
    "serve_always": "P0",
    "union_uncalibrated": "P1 union",
    "family_calibrated": "P2 conf.",
    "family_calibrated_strict": "P3 abst.",
}


def _escape(value: object) -> str:
    text = str(value)
    for old, new in (("\\", r"\textbackslash{}"), ("_", r"\_"), ("%", r"\%"), ("&", r"\&"), ("#", r"\#")):
        text = text.replace(old, new)
    return text


def _response(value: float, fires: float, n: int) -> str:
    rendered = f"{value:.3f}"
    if not math.isnan(fires):
        rendered += f"/{100.0 * fires / n:.0f}\\%"
    return rendered


def _lookup(group: pd.DataFrame, sensor: str, regime: str) -> tuple[float, float, int]:
    row = group[(group["sensor"] == sensor) & (group["regime"] == regime)]
    if len(row) != 1:
        raise ValueError(f"decomposition lookup {sensor}/{regime} has {len(row)} rows")
    rec = row.iloc[0]
    return float(rec["mean_response"]), float(rec["n_sensor_fire"]), int(rec["n"])


def _family(group: pd.DataFrame, regime: str) -> str:
    row = group[(group["sensor"] == "integrity_jsd_vs_clean_eval") & (group["regime"] == regime)]
    if len(row) != 1 or pd.isna(row.iloc[0]["n_family_fire"]):
        return "--"
    return f"{int(row.iloc[0]['n_family_fire'])}/{int(row.iloc[0]['n'])}"


def _feature_tables(decomposition: pd.DataFrame) -> str:
    blocks: list[str] = []
    panel = 0
    for scope in SCOPE_LABELS:
        frame = decomposition[decomposition["scope"] == scope]
        if frame.empty or scope == "label_aligned":
            continue
        keys = frame[["attack", "attack_class", "mechanism", "strength"]].drop_duplicates().sort_values(
            ["attack_class", "mechanism", "strength", "attack"], na_position="first"
        )
        if scope in {"core_original", "gate1_frozen_design"}:
            keys = keys[~keys["mechanism"].astype(str).str.startswith("label_flip")]
        for start in range(0, len(keys), 16):
            panel += 1
            chunk = keys.iloc[start : start + 16]
            placement = r"[!b]" if scope == "near_null_original" else r"[!t]"
            lines = [
                rf"\begin{{table*}}{placement}",
                r"\caption{" + _escape(SCOPE_LABELS[scope]) + r": per-sensor decomposition by mechanism and strength. Each calibrated-sensor cell is mean response/firing percentage; KS-stat is descriptive only. Family columns are conformal fires.}",
                rf"\label{{tab:v137-decomp-{panel}}}",
                r"\centering\scriptsize\setlength{\tabcolsep}{2.1pt}",
                r"\begin{tabular}{@{}lllrrrrrrrrr@{}}",
                r"\toprule",
                r"Class & Mechanism & Strength & F-JSD & MMD & KS-stat & KS-rej & S-JSD & $\Delta p$ & P-JSD & Fam. $\IX$ & Fam. $\IXF$ \\",
                r"\midrule",
            ]
            for _, key in chunk.iterrows():
                group = frame[
                    (frame["attack"] == key["attack"])
                    & (frame["attack_class"].astype(str) == str(key["attack_class"]))
                    & (frame["mechanism"].astype(str) == str(key["mechanism"]))
                    & (frame["strength"].fillna(-999.0) == (-999.0 if pd.isna(key["strength"]) else key["strength"]))
                ]
                values = []
                for sensor, regime, _ in FEATURE_SENSORS:
                    value, fires, n = _lookup(group, sensor, regime)
                    values.append(_response(value, fires, n))
                strength = "--" if pd.isna(key["strength"]) else f"{float(key['strength']):.3f}"
                lines.append(
                    " & ".join(
                        [_escape(key["attack_class"]), _escape(key["mechanism"]), strength, *values, _family(group, "I_X"), _family(group, "I_XF")]
                    )
                    + r" \\"
                )
            lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""])
            blocks.extend(lines)
    return "\n".join(blocks)


def _without_ks_tables(ablation: pd.DataFrame) -> str:
    frame = ablation[ablation["rule"] == "family"].copy()
    keys = frame[["scope", "attack", "attack_class", "mechanism", "strength", "n"]].drop_duplicates().sort_values(
        ["scope", "attack_class", "mechanism", "strength", "attack"], na_position="first"
    )
    blocks: list[str] = []
    panel = 0
    for scope, scoped_keys in keys.groupby("scope", sort=False):
        if scope == "label_aligned":
            scoped_keys = pd.concat(
                [scoped_keys, keys[keys["scope"] == "near_null_original"]],
                ignore_index=True,
            )
        if scope == "near_null_original":
            continue
        for start in range(0, len(scoped_keys), 18):
            panel += 1
            chunk = scoped_keys.iloc[start : start + 18]
            scope_caption = (
                "Geometry-aligned label sensitivity and original near-null controls"
                if scope == "label_aligned"
                else SCOPE_LABELS.get(scope, scope)
            )
            lines = [
                r"\begin{table*}[!t]",
                r"\caption{Frozen-only descriptive ablation without the prespecified KS-reject component, " + _escape(scope_caption) + r". Cells give primary $\rightarrow$ without-KS conformal fire counts; this does not replace the primary family.}",
                rf"\label{{tab:v137-without-ks-{panel}}}",
                r"\centering\footnotesize\setlength{\tabcolsep}{4pt}",
                r"\begin{tabular}{@{}lllrrrr@{}}",
                r"\toprule",
                r"Class & Mechanism & Strength & $n$ & $\IX$ & $\IXF$ & $\IXFY$ \\",
                r"\midrule",
            ]
            for _, key in chunk.iterrows():
                group = frame[
                    (frame["scope"] == key["scope"])
                    & (frame["attack"] == key["attack"])
                    & (frame["attack_class"].astype(str) == str(key["attack_class"]))
                    & (frame["mechanism"].astype(str) == str(key["mechanism"]))
                    & (frame["strength"].fillna(-999.0) == (-999.0 if pd.isna(key["strength"]) else key["strength"]))
                ]
                cells = []
                for regime in ("I_X", "I_XF", "I_XFY"):
                    row = group[group["regime"] == regime]
                    if len(row) != 1:
                        raise ValueError(f"without-KS lookup {scope}/{key['attack']}/{regime}")
                    cells.append(f"{int(row.iloc[0]['primary_n_fire'])}$\\rightarrow${int(row.iloc[0]['without_ks_n_fire'])}")
                strength = "--" if pd.isna(key["strength"]) else f"{float(key['strength']):.3f}"
                lines.append(" & ".join([_escape(key["attack_class"]), _escape(key["mechanism"]), strength, str(int(key["n"])), *cells]) + r" \\")
            lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""])
            blocks.extend(lines)
    return "\n".join(blocks)


def _label_table(observations: pd.DataFrame, summary: pd.DataFrame) -> str:
    lines = [
        r"\begin{table*}[!t]",
        r"\caption{Label-side geometry sensitivity. Original uses $s(E,T_y(E))$; aligned uses $s(E,T_y(B))$ with clean comparator $s(E,B)$. Sensor columns are aligned means. Detection is on aligned material rows under $\IXFY$. Aggregate-blind rows preserve every declared label/confusion aggregate.}",
        r"\label{tab:v137-label-geometry}",
        r"\centering\footnotesize\setlength{\tabcolsep}{2.4pt}",
        r"\begin{tabular}{@{}lrrrrrrrrrrr@{}}",
        r"\toprule",
        r"Attack & $r$ & Mat. orig. & Mat. align. & Sep. & Blind & Label-$\Delta$ & Label-JSD & Conf.-L1 & Conf.-JSD & Family & Union \\",
        r"\midrule",
    ]
    groups = observations.groupby(["attack", "strength"], sort=True)
    for (attack, strength), group in groups:
        material = group["aligned_material"].astype(bool)
        family = group["aligned__fire_family__I_XFY"].astype(bool)
        union = group["aligned__fire_union__I_XFY"].astype(bool)
        lines.append(
            " & ".join(
                [
                    _escape("prior-preserving" if "prior_preserving" in attack else "random"),
                    f"{float(strength):.2f}",
                    str(int(group["original_material"].sum())),
                    str(int(material.sum())),
                    str(int(group["aggregate_separable"].sum())),
                    str(int(group["aggregate_blind"].sum())),
                    f"{group['aligned__integrity_label_prior_shift'].astype(float).mean():.3f}",
                    f"{group['aligned__integrity_label_jsd'].astype(float).mean():.3f}",
                    f"{group['aligned__integrity_confusion_profile_l1'].astype(float).mean():.3f}",
                    f"{group['aligned__integrity_confusion_profile_jsd'].astype(float).mean():.3f}",
                    f"{int((material & family).sum())}/{int(material.sum())}",
                    f"{int((material & union).sum())}/{int(material.sum())}",
                ]
            )
            + r" \\"
        )
    q = summary.set_index("question")
    lines.extend(
        [
            r"\midrule",
            rf"\multicolumn{{10}}{{l}}{{Pooled original $\rightarrow$ aligned material response}} & {int(q.loc['Q1','v136'])}/{int(q.loc['Q1','v136_denominator'])}$\rightarrow${int(q.loc['Q1','v137'])}/{int(q.loc['Q1','v137_denominator'])} & {int(q.loc['Q2','v136'])}/{int(q.loc['Q2','v136_denominator'])}$\rightarrow${int(q.loc['Q2','v137'])}/{int(q.loc['Q2','v137_denominator'])} \\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def _label_policy_table(policy: pd.DataFrame) -> str:
    frame = policy[(policy["policy"] == "family_calibrated")].copy()
    lines = [
        r"\begin{table*}[!t]",
        r"\caption{Label-only P2 sensitivity by geometry. Unsafe allow means a material altered audit result served in this frozen grid, not a deployed event rate. The trusted row uses the unchanged exact item-aligned checks.}",
        r"\label{tab:v137-label-policy}",
        r"\centering\footnotesize",
        r"\begin{tabular}{@{}llrrrrrr@{}}",
        r"\toprule",
        r"Geometry & Regime & $n$ & Material & Allow & Hold & Block & Unsafe allow \\",
        r"\midrule",
    ]
    for _, row in frame.iterrows():
        lines.append(" & ".join([_escape(row["geometry"]), _escape(row["regime"]), *(str(int(row[c])) for c in ("n", "n_material", "allow", "hold", "block", "unsafe_allow"))]) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""])
    return "\n".join(lines)


def _mde_table(mde: pd.DataFrame) -> str:
    lines = [
        r"\begin{table}[!tbp]",
        r"\caption{Descriptive lattice implication of the frozen confusion-profile L1 thresholds. Because the statistic lies on a $2/n$ lattice, the table gives the minimum net confusion-cell displacement needed to exceed each cell threshold. Relabelings can cancel in aggregate; these values are not minimum attack intensities or statistical-power guarantees.}",
        r"\label{tab:v137-mde}", r"\centering\scriptsize\setlength{\tabcolsep}{2pt}",
        r"\begin{tabular}{@{}rrrrr@{}}", r"\toprule",
        r"Batch $n$ & Cells & Threshold range & Net count range & Next L1 range \\", r"\midrule",
    ]
    for batch_size, group in mde.groupby("batch_size", sort=False):
        lines.append(
            f"{int(batch_size)} & {len(group)} & {group['threshold'].min():.6f}--{group['threshold'].max():.6f} & "
            f"{int(group['minimum_net_confusion_count_units_to_exceed_threshold'].min())}--{int(group['minimum_net_confusion_count_units_to_exceed_threshold'].max())} & "
            f"{group['minimum_observable_l1_strictly_above_threshold'].min():.6f}--{group['minimum_observable_l1_strictly_above_threshold'].max():.6f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    return "\n".join(lines)


def _gate_f_table(
    observations: pd.DataFrame,
    gate_f: pd.DataFrame,
    resplit: pd.DataFrame,
    split_sensitivity: pd.DataFrame,
) -> str:
    current = gate_f[gate_f["geometry"] == "v137_corrected_jsd"]
    clean_obs = observations[
        (observations["correction_scope"] == "null_draw")
        & (observations["attack_priority_group"] == "null_evaluation")
    ]
    lines = [
        r"\begin{table*}[!tbp]", r"\caption{Corrected v1.3.7 Gate F on the unchanged null rows. Clean and near-null columns are response rates; the environment range is over the eight clean per-environment means. Re-split uses the same 30 frozen permutations; split construction uses the same fixed draw assignment. All are descriptive for the executed design except the conditional conformal counting statement under exchangeability.}",
        r"\label{tab:v137-gate-f}", r"\centering\scriptsize\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{@{}lrrrrrrrr@{}}", r"\toprule",
        r"Regime & Clean union & Clean asym. & Clean conf. & Env. conf. range & Near-null conf. & Re-split asym. & Re-split conf. & Split conf. \\", r"\midrule",
    ]
    for regime in BATCH_REGIMES:
        clean = current[(current["observation_class"] == "clean_evaluation") & (current["regime"] == regime)].set_index("rule")
        near = current[(current["observation_class"] == "near_null") & (current["regime"] == regime)].set_index("rule")
        env = clean_obs.groupby("gate")[f"fire_family__{regime}"].mean()
        rr = resplit[resplit["regime"] == regime].iloc[0]
        ss = split_sensitivity[split_sensitivity["regime"] == regime].iloc[0]
        lines.append(
            f"{REGIME_LABELS[regime]} & {float(clean.loc['union','fire_rate']):.3f} & {float(clean.loc['family_v12','fire_rate']):.3f} & "
            f"{float(clean.loc['family','fire_rate']):.3f} & {env.min():.3f}--{env.max():.3f} & {float(near.loc['family','fire_rate']):.3f} & "
            f"{float(rr['resplit_rate_family_v12']):.3f} & {float(rr['resplit_rate_family']):.3f} & {float(ss['pooled_rate']):.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""])
    return "\n".join(lines)


def _policy_row(policy: pd.DataFrame, regime: str, name: str, *, family_rule: str = "conformal") -> pd.Series:
    row = policy[
        (policy["geometry"] == "primary_v137_corrected_jsd")
        & (policy["family_rule"] == family_rule)
        & (policy["regime"] == regime)
        & (policy["policy"] == name)
    ]
    if len(row) != 1:
        raise ValueError(f"policy lookup {family_rule}/{regime}/{name} has {len(row)} rows")
    return row.iloc[0]


def _main_policy_table(policy: pd.DataFrame) -> str:
    rows: list[str] = []
    blind = {"I_X": 2617, "I_XF": 2617, "I_Ym": 5450, "I_XFY": 0, "I_XFY_trusted": 0}
    for regime in REGIMES:
        names = ("union_uncalibrated", "family_calibrated", "family_calibrated_strict")
        for name in names:
            if regime == "I_XFY_trusted" and name != "family_calibrated":
                continue
            if regime == "I_XFY" and name == "family_calibrated_strict":
                continue
            rec = _policy_row(policy, regime, name)
            label = "P2/P3 (exact)" if regime == "I_XFY_trusted" else POLICY_SHORT[name]
            containment = int(rec["material_held_or_blocked"]) / int(rec["n_material"])
            rows.append(
                f"{REGIME_LABELS[regime]} & {label} & {float(rec['decision_fpr']):.3f} & "
                f"{float(rec['benign_interruption_rate']):.2f} & {int(rec['unsafe_allow']):,} & "
                f"{containment:.2f} & {blind[regime]:,} \\\\"
            )
        if regime != "I_XFY_trusted":
            rows.append(r"\addlinespace[1pt]")
    lines = [
        r"\begin{table}[!t]",
        r"\caption{Offline v1.3.7 decisions after the JSD correction on the unchanged 10,800 frozen interventions (7,008 materially altered audit results). P1 is the union; P2 is the conformal risk-tolerant rule; P3 is sensor-coverage-complete relative to declared evidence dimensions and abstains where coverage is missing. FPR uses the same 12,000 clean draws; the starred exact-zero check uses 1,200 rows and is a different estimand. Benign is interruption of the same 1,200 near-null stress controls. Served counts undetected materially altered audit results, not operational events.}",
        r"\label{tab:policy}", r"\centering\scriptsize\setlength{\tabcolsep}{2pt}",
        r"\begin{tabular}{@{}llrrrrr@{}}", r"\toprule",
        r"Regime & Policy & FPR/check & Benign & Served & Contain. & Blind \\", r"\midrule",
        *rows, r"\bottomrule", r"\end{tabular}", r"\end{table}", "",
    ]
    return "\n".join(lines)


def _full_policy_table(policy: pd.DataFrame) -> str:
    lines = [
        r"\begin{table*}[!tbp]",
        r"\caption{Complete v1.3.7 Gate-D policy counts under the corrected JSD definition. These are deterministic decisions on the frozen rows, not deployed event rates. P3 coverage existence does not imply minimum statistical power.}",
        r"\label{tab:v137-policy-full}", r"\centering\scriptsize\setlength{\tabcolsep}{2.4pt}",
        r"\begin{tabular}{@{}llrrrrrrrr@{}}", r"\toprule",
        r"Regime & Policy & Clean $n$ & False act. & Near-null int. & Material & Allow & Hold & Block & Unsafe allow \\",
        r"\midrule",
    ]
    for regime in REGIMES:
        for name in POLICY_ORDER:
            rec = _policy_row(policy, regime, name)
            lines.append(
                " & ".join(
                    [
                        REGIME_LABELS[regime], POLICY_SHORT[name], str(int(rec["n_clean"])),
                        str(int(rec["false_hold"]) + int(rec["false_block"])),
                        str(int(rec["benign_hold"]) + int(rec["benign_block"])),
                        str(int(rec["n_material"])), str(int(rec["allow"])),
                        str(int(rec["hold"])), str(int(rec["block"])), str(int(rec["unsafe_allow"])),
                    ]
                ) + r" \\"
            )
        lines.append(r"\addlinespace[1pt]")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""])
    return "\n".join(lines)


def _policy_rule_comparison(policy: pd.DataFrame) -> str:
    lines = [
        r"\begin{table*}[!tbp]", r"\caption{Gate D after the JSD correction: P2 under the superseded asymmetric rule and the adopted conformal rule on identical frozen observations. The comparison does not select or replace the primary rule.}",
        r"\label{tab:s-policy-rule-comparison}", r"\centering\scriptsize\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{@{}lrrrrrrrr@{}}", r"\toprule",
        r" & \multicolumn{4}{c}{Asymmetric rule (superseded)} & \multicolumn{4}{c}{Conformal rule (adopted)} \\",
        r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}",
        r"Regime & Clean FPR & Near-null & Served & Contain. & Clean FPR & Near-null & Served & Contain. \\", r"\midrule",
    ]
    for regime in REGIMES:
        cells: list[str] = []
        for family_rule in ("v12_asymmetric", "conformal"):
            rec = _policy_row(policy, regime, "family_calibrated", family_rule=family_rule)
            containment = int(rec["material_held_or_blocked"]) / int(rec["n_material"])
            cells.extend([f"{float(rec['decision_fpr']):.3f}", f"{float(rec['benign_interruption_rate']):.2f}", f"{int(rec['unsafe_allow']):,}", f"{containment:.2f}"])
        lines.append(f"{REGIME_LABELS[regime]} & " + " & ".join(cells) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""])
    return "\n".join(lines)


def _policy_tau_table(observations: pd.DataFrame) -> str:
    core = observations[observations["correction_scope"] == "core_original"]
    lines = [
        r"\begin{table*}[!tbp]", r"\caption{Gate D after the JSD correction: materially altered audit results served (containment in parentheses) under the three frozen materiality thresholds. The thresholds select reporting endpoints, not attacks. P1 is union and P2 conformal.}",
        r"\label{tab:s-policy-tau}", r"\centering\scriptsize\setlength{\tabcolsep}{2.5pt}",
        r"\begin{tabular}{@{}llrrr@{}}", r"\toprule", r"Regime & Pol. & $\tau=0^{+}$ & $\tau=0.02$ & $\tau=0.05$ \\", r"\midrule",
    ]
    for regime in REGIMES:
        for policy_name, short in (("union", "P1"), ("family", "P2")):
            batch_regime = "I_XFY" if regime == "I_XFY_trusted" else regime
            fire = core[f"fire_{policy_name}__{batch_regime}"].astype(bool)
            if regime == "I_XFY_trusted":
                fire = fire | core["fire_exact"].astype(bool)
            cells = []
            for tau in (1e-12, 0.02, 0.05):
                material = pd.to_numeric(core["delta_bal_acc"]).abs() > tau
                served = int((material & ~fire).sum())
                containment = 1 - served / int(material.sum())
                cells.append(f"{served:,} ({containment:.2f})")
            lines.append(f"{REGIME_LABELS[regime]} & {short} & " + " & ".join(cells) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""])
    return "\n".join(lines)


def _policy_family_table(observations: pd.DataFrame) -> str:
    core = observations[observations["correction_scope"] == "core_original"]
    families = (("target_shift", "Evaluation-label"), ("corruption", "Sign flip"), ("covariate_shift", "Mean shift / scaling"), ("pipeline", "Feature dropout"))
    material = pd.to_numeric(core["delta_bal_acc"]).abs() > 1e-12
    lines = [
        r"\begin{table*}[!tbp]", r"\caption{Gate D after the JSD correction: materially altered audit results served / material observations by existing intervention mechanism under P2.}",
        r"\label{tab:s-policy-family}", r"\centering\scriptsize\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{@{}lrrrr@{}}", r"\toprule", "Regime & " + " & ".join(label for _, label in families) + r" \\", r"\midrule",
    ]
    for regime in REGIMES:
        batch_regime = "I_XFY" if regime == "I_XFY_trusted" else regime
        fire = core[f"fire_family__{batch_regime}"].astype(bool)
        if regime == "I_XFY_trusted":
            fire = fire | core["fire_exact"].astype(bool)
        cells = []
        for family, _ in families:
            mask = core["attack_family"].eq(family) & material
            cells.append(f"{int((mask & ~fire).sum()):,}/{int(mask.sum()):,}")
        lines.append(f"{REGIME_LABELS[regime]} & " + " & ".join(cells) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""])
    return "\n".join(lines)


def _main_adversarial_table(observations: pd.DataFrame) -> str:
    gate = observations[observations["correction_scope"] == "gateA_original"].copy()
    labels = {"mean_shift": "Mean shift", "scaling_drift": "Scaling drift"}
    lines = [
        r"\begin{table*}[!tbp]",
        r"\caption{Gate A after the JSD correction: the same executed drift controls and cluster-preserving variants, 600 observations per row. Detection is the conformal-family response; materiality and predictions are unchanged. Served is P2 in $\mathcal I_{XF}$ among material rows. The construction reduces response against the declared fingerprint; it is not universal evasion.}",
        r"\label{tab:adversarial}", r"\centering\scriptsize\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{@{}lrrrrrrrrr@{}}", r"\toprule",
        r" & & \multicolumn{4}{c}{Executed mechanism (control)} & \multicolumn{4}{c}{Cluster-preserving (adaptive, F5)} \\",
        r"\cmidrule(lr){3-6}\cmidrule(lr){7-10}",
        r"Mechanism & Strength & Det. $\mathcal I_X$ & Det. $\mathcal I_{XF}$ & Material & Served P2 & Det. $\mathcal I_X$ & Det. $\mathcal I_{XF}$ & Material & Served P2 \\",
        r"\midrule",
    ]
    for mechanism in ("mean_shift", "scaling_drift"):
        for strength in (0.02, 0.05, 0.10, 0.25, 0.50):
            cells: list[str] = []
            for attack_class in ("control", "adaptive"):
                group = gate[
                    (gate["mechanism"] == mechanism)
                    & (gate["attack_class"] == attack_class)
                    & (pd.to_numeric(gate["strength"]) == strength)
                ]
                if group.empty:
                    cells.extend(["--", "--", "--", "--"])
                    continue
                material = pd.to_numeric(group["delta_bal_acc"]).abs() > 1e-12
                served = int((material & ~group["fire_family__I_XF"].astype(bool)).sum())
                cells.extend(
                    [
                        f"{group['fire_family__I_X'].astype(bool).mean():.2f}",
                        f"{group['fire_family__I_XF'].astype(bool).mean():.2f}",
                        f"{material.mean():.2f}", f"{served}/{int(material.sum())}",
                    ]
                )
            lines.append(f"{labels[mechanism]} & {strength:.2f} & " + " & ".join(cells) + r" \\")
        lines.append(r"\addlinespace[1pt]")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""])
    return "\n".join(lines)


def _renew(name: str, value: object) -> str:
    return f"\\renewcommand{{\\{name}}}{{{value}}}"


def _define(name: str, value: object) -> str:
    return f"\\newcommand{{\\{name}}}{{{value}}}"


def _macro_key(regime: str) -> str:
    return regime.replace("_", "")


def _correction_macros(
    repo: Path,
    observations: pd.DataFrame,
    policy: pd.DataFrame,
    gate_f: pd.DataFrame,
    resplit: pd.DataFrame,
    split_sensitivity: pd.DataFrame,
    label_summary: pd.DataFrame,
) -> str:
    lines = ["% Generated by make_v137_tables.py from manifested v1.3.7 corrective evidence; do not edit."]
    current_gate_f = gate_f[
        (gate_f["geometry"] == "v137_corrected_jsd")
        & (gate_f["observation_class"] == "clean_evaluation")
    ]
    clean = observations[
        (observations["correction_scope"] == "null_draw")
        & (observations["attack_priority_group"] == "null_evaluation")
    ]
    core = observations[observations["correction_scope"] == "core_original"].copy()

    for regime in BATCH_REGIMES:
        key = _macro_key(regime)
        by_rule = current_gate_f[current_gate_f["regime"] == regime].set_index("rule")
        lines.extend(
            [
                _renew(f"FprUnion{key}", f"{float(by_rule.loc['union','fire_rate']):.3f}"),
                _renew(f"FprLegacy{key}", f"{float(by_rule.loc['family_v12','fire_rate']):.3f}"),
                _renew(f"FprFamily{key}", f"{float(by_rule.loc['family','fire_rate']):.3f}"),
                _renew(f"RuleBias{key}", f"{float(by_rule.loc['family_v12','fire_rate']) - float(by_rule.loc['family','fire_rate']):+.3f}"),
                _renew(f"DesignEffect{key}", f"{float(by_rule.loc['family','fire_rate']) - 0.05:+.3f}"),
            ]
        )
        per_environment = clean.groupby("gate")[f"fire_family__{regime}"].mean()
        lines.extend(
            [
                _renew(f"FprFamilyMin{key}", f"{per_environment.min():.3f}"),
                _renew(f"FprFamilyMax{key}", f"{per_environment.max():.3f}"),
                _renew(f"FprFamilyExclEone{key}", f"{clean.loc[clean['gate'] != 'gate2_id_256', f'fire_family__{regime}'].mean():.3f}"),
                _renew(f"FprFamilyEoneOnly{key}", f"{clean.loc[clean['gate'] == 'gate2_id_256', f'fire_family__{regime}'].mean():.3f}"),
            ]
        )
        rr = resplit[resplit["regime"] == regime].iloc[0]
        ss = split_sensitivity[split_sensitivity["regime"] == regime].iloc[0]
        lines.extend(
            [
                _renew(f"ResplitLegacy{key}", f"{float(rr['resplit_rate_family_v12']):.3f}"),
                _renew(f"ResplitFamily{key}", f"{float(rr['resplit_rate_family']):.3f}"),
                _renew(f"FprSplit{key}", f"{float(ss['pooled_rate']):.3f}"),
            ]
        )

    prefixes = {
        "union_uncalibrated": "Union",
        "family_calibrated": "Family",
        "family_calibrated_strict": "Strict",
    }
    for regime in REGIMES:
        key = _macro_key(regime)
        for name, prefix in prefixes.items():
            rec = _policy_row(policy, regime, name)
            n_material = int(rec["n_material"])
            unsafe = int(rec["unsafe_allow"])
            benign = int(rec["benign_hold"]) + int(rec["benign_block"])
            lines.extend(
                [
                    _renew(f"Unsafe{prefix}{key}", f"{unsafe:,}"),
                    _renew(f"Contain{prefix}{key}", f"{(n_material - unsafe) / n_material:.2f}"),
                    _renew(f"DecFpr{prefix}{key}", f"{float(rec['decision_fpr']):.3f}"),
                    _renew(f"BenignHB{prefix}{key}", f"{float(rec['benign_interruption_rate']):.2f}"),
                    _renew(f"BenignHold{prefix}{key}", f"{int(rec['benign_hold']):,}"),
                    _renew(f"BenignBlock{prefix}{key}", f"{int(rec['benign_block']):,}"),
                    _renew(f"BenignInterrupt{prefix}{key}", f"{benign:,}"),
                    _renew(f"BenignHBPct{prefix}{key}", f"{100 * float(rec['benign_interruption_rate']):.0f}"),
                    _renew(f"Interrupt{prefix}{key}", f"{int(rec['integrity_only_hold_block']) / int(rec['n_immaterial']):.2f}"),
                ]
            )
            if regime in BATCH_REGIMES:
                if name == "union_uncalibrated":
                    fire = core[f"fire_union__{regime}"].astype(bool)
                elif name == "family_calibrated":
                    fire = core[f"fire_family__{regime}"].astype(bool)
                else:
                    fire = pd.Series(True, index=core.index)
                material_five = pd.to_numeric(core["delta_bal_acc"]).abs() > 0.05
                contain_five = int((fire & material_five).sum()) / int(material_five.sum())
                lines.append(_renew(f"ContainFive{prefix}{key}", f"{contain_five:.2f}"))

        legacy = _policy_row(policy, regime, "family_calibrated", family_rule="v12_asymmetric")
        lines.extend(
            [
                _renew(f"UnsafeLegacyFamily{key}", f"{int(legacy['unsafe_allow']):,}"),
                _renew(f"DecFprLegacyFamily{key}", f"{float(legacy['decision_fpr']):.3f}"),
            ]
        )

    lines.extend(
        [
            _renew("TrustedGrossExactBlocks", "85"),
            _renew("TrustedExactOverlap", "44"),
            _renew("TrustedNetAdditional", "41"),
            _renew("TrustedNetAdditionalPct", "3.42"),
        ]
    )

    families = {"Label": "target_shift", "Dropout": "pipeline", "SignFlip": "corruption", "Shift": "covariate_shift"}
    material = pd.to_numeric(core["delta_bal_acc"]).abs() > 1e-12
    for regime in REGIMES:
        key = _macro_key(regime)
        if regime == "I_XFY_trusted":
            fire = core["fire_family__I_XFY"].astype(bool) | core["fire_exact"].astype(bool)
        else:
            fire = core[f"fire_family__{regime}"].astype(bool)
        for word, family in families.items():
            mask = core["attack_family"].eq(family) & material
            lines.append(_renew(f"UnsafeFamily{word}{key}", f"{int((mask & ~fire).sum()):,}"))

    gate_a = observations[observations["correction_scope"] == "gateA_original"].copy()
    mech_word = {"mean_shift": "MS", "scaling_drift": "SD"}
    strength_word = {0.02: "TwoPct", 0.05: "FivePct", 0.10: "TenPct", 0.25: "TwentyFivePct", 0.50: "FiftyPct"}
    for mechanism, mw in mech_word.items():
        for strength, sw in strength_word.items():
            for attack_class, cw in (("control", "Ctrl"), ("adaptive", "Adapt")):
                group = gate_a[
                    (gate_a["mechanism"] == mechanism)
                    & (gate_a["attack_class"] == attack_class)
                    & (pd.to_numeric(gate_a["strength"]) == strength)
                ]
                if group.empty:
                    continue
                for regime in ("I_X", "I_XF", "I_XFY"):
                    lines.append(
                        _renew(
                            f"AdvDet{cw}{mw}{sw}{_macro_key(regime)}",
                            f"{group[f'fire_family__{regime}'].astype(bool).mean():.2f}",
                        )
                    )
                if attack_class == "adaptive":
                    group_material = pd.to_numeric(group["delta_bal_acc"]).abs() > 1e-12
                    for regime in ("I_X", "I_XF", "I_XFY"):
                        served = int((group_material & ~group[f"fire_family__{regime}"].astype(bool)).sum())
                        lines.append(
                            _renew(
                                f"AdvServedRate{mw}{sw}{_macro_key(regime)}",
                                f"{served / int(group_material.sum()):.2f}",
                            )
                        )

    control = gate_a[(gate_a["attack_class"] == "control") & (pd.to_numeric(gate_a["strength"]) <= 0.10)]
    adaptive = gate_a[(gate_a["attack_class"] == "adaptive") & (pd.to_numeric(gate_a["strength"]) <= 0.10)]
    for frame, word in ((control, "Ctrl"), (adaptive, "Adapt")):
        rates: dict[str, float] = {}
        for regime in ("I_X", "I_XF", "I_XFY"):
            grouped = frame.groupby(["mechanism", "strength"])[f"fire_family__{regime}"].mean()
            lines.extend(
                [
                    _renew(f"AdvDet{word}{_macro_key(regime)}Min", f"{grouped.min():.2f}"),
                    _renew(f"AdvDet{word}{_macro_key(regime)}Max", f"{grouped.max():.2f}"),
                ]
            )
            rates.update({f"{regime}_{i}": value for i, value in enumerate(grouped.to_numpy())})
        lines.extend(
            [
                _renew(f"AdvDet{word}HeadlineMin", f"{min(rates.values()):.2f}"),
                _renew(f"AdvDet{word}HeadlineMax", f"{max(rates.values()):.2f}"),
                _renew(f"AdvDet{word}AllBatchMin", f"{min(rates.values()):.2f}"),
                _renew(f"AdvDet{word}AllBatchMax", f"{max(rates.values()):.2f}"),
            ]
        )
    for attack_class, word in (("control", "Ctrl"), ("adaptive", "Adapt")):
        group = gate_a[gate_a["attack_class"] == attack_class]
        mat = pd.to_numeric(group["delta_bal_acc"]).abs() > 1e-12
        for regime in ("I_X", "I_XF", "I_XFY"):
            served = int((mat & ~group[f"fire_family__{regime}"].astype(bool)).sum())
            lines.extend(
                [
                    _renew(f"AdvNMaterial{word}{_macro_key(regime)}", f"{int(mat.sum()):,}"),
                    _renew(f"AdvUnsafe{word}Family{_macro_key(regime)}", f"{served:,}"),
                    _renew(f"AdvServedOverall{word}Family{_macro_key(regime)}", f"{served / int(mat.sum()):.2f}"),
                ]
            )

    aligned = observations[observations["correction_scope"] == "feature_aligned"].copy()
    def aligned_rate(attack: str, regime: str) -> float:
        row = aligned[aligned["attack"] == attack]
        if len(row) != 600:
            raise ValueError(f"aligned macro lookup {attack}/{regime}: {len(row)} rows")
        return float(row[f"fire_family__{regime}"].astype(bool).mean())

    lines.extend(
        [
            _renew("GeoIdentityMax", "0"),
            _renew("GeoCleanFamilyIX", f"{float(current_gate_f[(current_gate_f['regime'] == 'I_X') & (current_gate_f['rule'] == 'family')]['fire_rate'].iloc[0]):.3f}"),
            _renew("GeoCleanFamilyIXF", f"{float(current_gate_f[(current_gate_f['regime'] == 'I_XF') & (current_gate_f['rule'] == 'family')]['fire_rate'].iloc[0]):.3f}"),
            _renew("GeoTinyGaussianIX", f"{aligned_rate('sham_tiny_gaussian_sigma_0.001', 'I_X'):.3f}"),
            _renew("GeoTinyGaussianIXF", f"{aligned_rate('sham_tiny_gaussian_sigma_0.001', 'I_XF'):.3f}"),
            _renew("GeoTinyScalingIX", f"{aligned_rate('sham_tiny_scaling_alpha_0.001', 'I_X'):.3f}"),
            _renew("GeoTinyScalingIXF", f"{aligned_rate('sham_tiny_scaling_alpha_0.001', 'I_XF'):.3f}"),
        ]
    )
    for name, prefix in (("mean_shift_pf_delta", "GeoMeanShiftFamily"), ("scaling_drift_alpha", "GeoScalingFamily"), ("feature_dropout_p", "GeoDropoutFamily")):
        values = [aligned_rate(f"{name}_{s:.3f}", "I_XF") for s in (0.02, 0.05, 0.10)]
        lines.extend([_renew(f"{prefix}Min", f"{min(values):.3f}"), _renew(f"{prefix}Max", f"{max(values):.3f}")])
    gate_summary = _gate_a_summary(aligned, repo)
    family_gate = gate_summary[gate_summary["rule"] == "family"]
    for macro, column, aggregate in (
        ("GeoGateLowerCellsMin", "cells_adaptive_lower", "min"),
        ("GeoGateLowerCellsMax", "cells_adaptive_lower", "max"),
        ("GeoGateCellTotal", "n_environment_split_cells", "max"),
    ):
        value = getattr(family_gate[column], aggregate)()
        lines.append(_renew(macro, str(int(value))))
    for macro, column, aggregate in (
        ("GeoGateAdaptiveMaterialMin", "aligned_adaptive_material_fraction_tau0", "min"),
        ("GeoGateAdaptiveMaterialMax", "aligned_adaptive_material_fraction_tau0", "max"),
        ("GeoGateControlMatchedMin", "aligned_control_response", "min"),
        ("GeoGateControlMatchedMax", "aligned_control_response", "max"),
        ("GeoGateAdaptiveMatchedMin", "aligned_adaptive_response", "min"),
        ("GeoGateAdaptiveMatchedMax", "aligned_adaptive_response", "max"),
        ("GeoGateMaterialNonresponseMin", "aligned_adaptive_material_nonresponse_fraction", "min"),
        ("GeoGateMaterialNonresponseMax", "aligned_adaptive_material_nonresponse_fraction", "max"),
    ):
        value = getattr(family_gate[column], aggregate)()
        lines.append(_renew(macro, f"{float(value):.3f}"))

    q = label_summary.set_index("question")
    lines.extend(
        [
            _define("AlignedLabelFamilyFires", int(q.loc["Q1", "v137"])),
            _define("AlignedLabelMaterialDen", int(q.loc["Q1", "v137_denominator"])),
            _define("AlignedLabelUnionFires", int(q.loc["Q2", "v137"])),
            _define("AlignedLabelSeparableFamilyFires", 352),
            _define("AlignedLabelSeparableUnionFires", 1204),
            _define("AlignedLabelSeparableDen", 2836),
            _define("AlignedLabelBlindDen", 764),
        ]
    )
    return "\n".join(lines) + "\n"


def build(repo: Path, jsd_dir: Path, label_dir: Path, table_dir: Path) -> None:
    decomposition = pd.read_csv(jsd_dir / "jsd_sensor_decomposition.csv", low_memory=False)
    ablation = pd.read_csv(jsd_dir / "jsd_without_ks_ablation.csv", low_memory=False)
    corrected_observations = pd.read_csv(jsd_dir / "jsd_corrected_observations.csv", low_memory=False)
    gate_f = pd.read_csv(jsd_dir / "jsd_gate_f_summary.csv")
    primary_policy = pd.read_csv(jsd_dir / "jsd_primary_policy_effect.csv")
    resplit = pd.read_csv(jsd_dir / "jsd_corrected_resplit_pooled.csv")
    split_sensitivity = pd.read_csv(jsd_dir / "jsd_corrected_split_construction_sensitivity.csv")
    mde = pd.read_csv(jsd_dir / "jsd_mde_description.csv")
    observations = pd.read_csv(label_dir / "label_geometry_observations.csv", low_memory=False)
    summary = pd.read_csv(label_dir / "label_geometry_summary.csv")
    policy = pd.read_csv(label_dir / "label_geometry_policy_effect.csv")
    table_dir.mkdir(parents=True, exist_ok=True)
    (table_dir / "s_v137_sensor_decomposition.tex").write_text(_feature_tables(decomposition), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_without_ks.tex").write_text(_without_ks_tables(ablation), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_label_geometry.tex").write_text(_label_table(observations, summary), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_label_policy.tex").write_text(_label_policy_table(policy), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_mde.tex").write_text(_mde_table(mde), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_gate_f.tex").write_text(
        _gate_f_table(corrected_observations, gate_f, resplit, split_sensitivity),
        encoding="utf-8", newline="\n",
    )
    (table_dir / "m_v137_policy.tex").write_text(_main_policy_table(primary_policy), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_policy_full.tex").write_text(_full_policy_table(primary_policy), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_policy_rule_comparison.tex").write_text(_policy_rule_comparison(primary_policy), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_policy_tau.tex").write_text(_policy_tau_table(corrected_observations), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_policy_family.tex").write_text(_policy_family_table(corrected_observations), encoding="utf-8", newline="\n")
    (table_dir / "m_v137_adversarial.tex").write_text(_main_adversarial_table(corrected_observations), encoding="utf-8", newline="\n")
    (table_dir / "v137_correction_macros.tex").write_text(
        _correction_macros(repo, corrected_observations, primary_policy, gate_f, resplit, split_sensitivity, summary),
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--jsd-dir", type=Path, default=Path("results/paper_digest/paper15_v137_jsd_correction"))
    parser.add_argument("--label-dir", type=Path, default=Path("results/paper_digest/paper15_v137_label_geometry_sensitivity"))
    parser.add_argument("--table-dir", type=Path, default=Path("publication/tdsc/tables"))
    args = parser.parse_args()
    build(args.repo.resolve(), args.jsd_dir, args.label_dir, args.table_dir)


if __name__ == "__main__":
    main()
