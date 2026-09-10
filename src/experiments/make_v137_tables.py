"""Generate the v1.3.7 supplement tables from manifested corrective CSVs."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import pandas as pd


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
            lines = [
                r"\begin{table*}[!t]",
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
        for start in range(0, len(scoped_keys), 18):
            panel += 1
            chunk = scoped_keys.iloc[start : start + 18]
            lines = [
                r"\begin{table*}[!t]",
                r"\caption{Frozen-only descriptive ablation without the prespecified KS-reject component, " + _escape(SCOPE_LABELS.get(scope, scope)) + r". Cells give primary $\rightarrow$ without-KS conformal fire counts; this does not replace the primary family.}",
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


def build(jsd_dir: Path, label_dir: Path, table_dir: Path) -> None:
    decomposition = pd.read_csv(jsd_dir / "jsd_sensor_decomposition.csv", low_memory=False)
    ablation = pd.read_csv(jsd_dir / "jsd_without_ks_ablation.csv", low_memory=False)
    observations = pd.read_csv(label_dir / "label_geometry_observations.csv", low_memory=False)
    summary = pd.read_csv(label_dir / "label_geometry_summary.csv")
    policy = pd.read_csv(label_dir / "label_geometry_policy_effect.csv")
    table_dir.mkdir(parents=True, exist_ok=True)
    (table_dir / "s_v137_sensor_decomposition.tex").write_text(_feature_tables(decomposition), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_without_ks.tex").write_text(_without_ks_tables(ablation), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_label_geometry.tex").write_text(_label_table(observations, summary), encoding="utf-8", newline="\n")
    (table_dir / "s_v137_label_policy.tex").write_text(_label_policy_table(policy), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsd-dir", type=Path, default=Path("results/paper_digest/paper15_v137_jsd_correction"))
    parser.add_argument("--label-dir", type=Path, default=Path("results/paper_digest/paper15_v137_label_geometry_sensitivity"))
    parser.add_argument("--table-dir", type=Path, default=Path("publication/tdsc/tables"))
    args = parser.parse_args()
    build(args.jsd_dir, args.label_dir, args.table_dir)


if __name__ == "__main__":
    main()
