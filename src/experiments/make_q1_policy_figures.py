"""Figure for the Paper 1.5 policy gates (artifact 1.3.0).

Panel (a): decision-level false-alarm rate of the uncalibrated union rule, of
the superseded asymmetric 1.2.0 family rule and of the adopted conformal
family rule per information regime, with the range of the eight
per-environment cluster means, the nominal level and the exact level of the
conformal rule. Panel (b): the materially-altered-report-served /
clean-false-action trade-off of the batch policies only; the trusted
exact-zero invariant check is stated separately because it is a different
estimand and denominator. Panel (c): the
interruption response on the prespecified near-null in-place controls (the
same 1,200 rows for every regime) of every policy and regime, so that the
trusted regime's zero unsafe allows are shown together with the additional
interruption within that stress-control grid.

Every plotted value is written to a CSV next to the figure and hashed in a
figure manifest, so the figure can be regenerated and audited from tables.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["font.family"] = "sans-serif"

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
HAIRLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
BLUE_LIGHT = "#9ec5f4"
ORANGE = "#d9822b"
GREEN = "#3a8f5c"
GREY = "#9a9891"

REGIME_ORDER = ["I_X", "I_XF", "I_Ym", "I_XFY", "I_XFY_trusted"]
BATCH = ["I_X", "I_XF", "I_Ym", "I_XFY"]
REGIME_LABEL = {"I_X": "$\\mathcal{I}_X$", "I_XF": "$\\mathcal{I}_{XF}$", "I_Ym": "$\\mathcal{I}_{Y_m}$", "I_XFY": "$\\mathcal{I}_{XFY}$", "I_XFY_trusted": "$\\mathcal{I}_{XFY}^{\\star}$"}
POLICY_STYLE = {
    "serve_always": ("P0 serve-always", GREY, "s"),
    "union_uncalibrated": ("P1 union (uncalibrated)", ORANGE, "^"),
    "family_calibrated": ("P2 conformal-rule (risk-tolerant)", BLUE, "o"),
    "family_calibrated_strict": ("P3 coverage-complete abstaining", GREEN, "D"),
}
RULE_STYLE = (("union", ORANGE, "Union (1.1.0)"), ("family_v12", BLUE_LIGHT, "Family 1.2.0"), ("family", BLUE, "Conformal (adopted)"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _panel_a_frame(evidence: Path) -> pd.DataFrame:
    fpr = pd.read_csv(evidence / "family_false_alarm_overall.csv")
    fpr = fpr[(fpr["aggregate"] == "all_eight_environments") & fpr["regime"].isin(BATCH)].copy()
    fpr["order"] = fpr["regime"].map({r: i for i, r in enumerate(BATCH)})
    return fpr.sort_values(["order", "rule"])[["regime", "rule", "n_draws", "n_fire", "pooled_rate", "environment_cluster_mean_min", "environment_cluster_mean_max", "nominal_alpha", "conformal_exact_level"]]


def _panel_b_frame(evidence: Path) -> pd.DataFrame:
    m = pd.read_csv(evidence / "policy_metrics.csv")
    m = m[m["tau"] == 0.0].copy()
    fam = pd.read_csv(evidence / "policy_metrics_by_family.csv")
    fam = fam[(fam["tau"] == 0.0) & (fam["attack_family"] == "target_shift") & (fam["family_rule"] == "conformal")][["regime", "policy", "unsafe_allow"]].rename(columns={"unsafe_allow": "unsafe_allow_label_path"})
    m = m.merge(fam, on=["regime", "policy"], how="left")
    m["order"] = m["regime"].map({r: i for i, r in enumerate(REGIME_ORDER)})
    return m.sort_values(["order", "policy"])[["regime", "policy", "n_clean", "clean_denominator", "decision_fpr", "n_benign", "benign_hold", "benign_block", "benign_interruption_rate", "nonmaterial_interruption_rate", "n_material", "unsafe_allow", "unsafe_allow_rate", "unsafe_allow_label_path", "containment", "residual_blind_material"]]


def _style_axis(ax) -> None:
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(BASELINE)
    ax.spines["bottom"].set_color(BASELINE)
    ax.grid(axis="y", color=HAIRLINE, linewidth=0.8)
    ax.set_axisbelow(True)


def _draw(a: pd.DataFrame, b: pd.DataFrame, paths: list[Path]) -> None:
    # Layout (release 1.3.4): short panel titles that cannot collide, legends and
    # annotations placed in regions that carry no data, value labels lifted above the
    # whisker caps so that no glyph crosses a bar, an interval or another label, and
    # ticks large enough at 7.16 in print width.
    fig = plt.figure(figsize=(7.16, 2.7))
    grid = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.05, 1.0], wspace=0.46)

    ax = fig.add_subplot(grid[0, 0])
    x = np.arange(len(BATCH))
    width = 0.26
    for k, (rule, color, label) in enumerate(RULE_STYLE):
        block = a[a["rule"] == rule].set_index("regime").reindex(BATCH)
        xs = x + (k - 1) * width
        ax.bar(xs, block["pooled_rate"], width=width, color=color, label=label, zorder=3)
        lo = (block["pooled_rate"] - block["environment_cluster_mean_min"]).clip(lower=0)
        hi = (block["environment_cluster_mean_max"] - block["pooled_rate"]).clip(lower=0)
        ax.errorbar(xs, block["pooled_rate"], yerr=np.vstack([lo, hi]), fmt="none", ecolor=INK_SECONDARY, elinewidth=0.7, capsize=1.6, zorder=4)
        # The value label sits above the upper whisker cap, never inside the interval.
        for xi, v, cap in zip(xs, block["pooled_rate"], block["environment_cluster_mean_max"]):
            ax.text(xi, max(float(v), float(cap)) + 0.014, f"{v:.3f}", ha="center", va="bottom", fontsize=5.2, color=INK, rotation=90, zorder=5)
    ax.axhline(0.05, color=BASELINE, linewidth=1.0, linestyle="--", zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels([REGIME_LABEL[r] for r in BATCH], fontsize=7.4, color=INK)
    ax.set_xlim(-0.55, len(BATCH) - 0.45)
    ax.set_ylim(0, max(0.60, float(a["environment_cluster_mean_max"].max()) * 1.67))
    ax.tick_params(axis="y", labelsize=6.5, colors=INK_SECONDARY, length=2)
    ax.tick_params(axis="x", length=0)
    _style_axis(ax)
    ax.set_ylabel("Clean false-action rate (12,000 draws)", fontsize=6.6, color=INK_SECONDARY)
    ax.set_title("(a) Executed false actions", fontsize=7.6, color=INK, loc="left")
    # Short entries keep the legend inside the left half, clear of the tallest labels.
    ax.legend(fontsize=5.2, frameon=False, loc="upper left", handlelength=1.2, handletextpad=0.5, borderaxespad=0.3, labelspacing=0.35)
    ax.text(0.0, -0.20, "Bars: pooled rate; whiskers: range of the eight per-environment cluster\nmeans. Dashed: nominal 0.05; the 1.2.0 rule is superseded; conformal\nexact level 10/201 = 0.0498.", transform=ax.transAxes, fontsize=5.6, color=INK_SECONDARY, va="top")

    axb = fig.add_subplot(grid[0, 1])
    for policy, (label, color, marker) in POLICY_STYLE.items():
        block = b[(b["policy"] == policy) & b["regime"].isin(BATCH)]
        axb.scatter(block["decision_fpr"], block["unsafe_allow_rate"], s=26, color=color, marker=marker, label=label.split(" (")[0], zorder=4, edgecolor="white", linewidth=0.6)
    for regime in BATCH:
        block = b[(b["regime"] == regime) & (b["policy"].isin(["union_uncalibrated", "family_calibrated"]))].sort_values("decision_fpr")
        if len(block) == 2:
            axb.plot(block["decision_fpr"], block["unsafe_allow_rate"], color=HAIRLINE, linewidth=0.9, zorder=2)
    offsets = {"I_X": (-4, 7), "I_XF": (10, -13), "I_Ym": None, "I_XFY": None}
    labels = {"I_XF": REGIME_LABEL["I_XF"] + ", " + REGIME_LABEL["I_XFY"]}
    for regime in BATCH:
        if offsets[regime] is None:
            continue
        row = b[(b["regime"] == regime) & (b["policy"] == "family_calibrated")].iloc[0]
        dx, dy = offsets[regime]
        axb.annotate(labels.get(regime, REGIME_LABEL[regime]), (row["decision_fpr"], row["unsafe_allow_rate"]), xytext=(dx, dy), textcoords="offset points", fontsize=6.2, color=INK, arrowprops=dict(arrowstyle="-", color=HAIRLINE, lw=0.7) if regime == "I_XF" else None)
    # The saturated corner (0, 1) carries P0 for every regime and P1, P2 in the label
    # view; its label goes above the markers, in the headroom reserved for it.
    p0 = b[(b["policy"] == "serve_always") & (b["regime"] == "I_X")].iloc[0]
    axb.annotate("P0 (all regimes); P1, P2 in " + REGIME_LABEL["I_Ym"], (p0["decision_fpr"], p0["unsafe_allow_rate"]), xytext=(0, 5), textcoords="offset points", fontsize=5.8, color=INK, ha="left", va="bottom")
    strict = b[(b["policy"] == "family_calibrated_strict") & (b["regime"] == "I_X")].iloc[0]
    axb.annotate("P3 in $\\mathcal{I}_X$, $\\mathcal{I}_{XF}$, $\\mathcal{I}_{Y_m}$: nothing served", (strict["decision_fpr"], strict["unsafe_allow_rate"]), xytext=(-7, 5), textcoords="offset points", fontsize=5.6, color=INK_SECONDARY, ha="right", va="bottom")
    trusted = b[(b["regime"] == "I_XFY_trusted") & (b["policy"] == "family_calibrated")].iloc[0]
    # Upper right: free of data once the saturated corner is labelled above the markers.
    axb.text(0.995, 0.78,
             f"Trusted check (separate estimand):\n0/{int(trusted['n_clean']):,} exact-zero false actions;\n0/{int(trusted['n_material']):,} material reports served",
             transform=axb.transAxes, fontsize=5.2, color=INK_SECONDARY,
             ha="right", va="top", linespacing=1.35,
             bbox=dict(facecolor="white", edgecolor=HAIRLINE, boxstyle="round,pad=0.25"))
    axb.set_xlim(-0.03, 1.05)
    axb.set_ylim(-0.04, 1.20)
    axb.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    axb.set_xlabel("Clean false-action rate (12,000 batch draws)", fontsize=6.4, color=INK_SECONDARY)
    axb.set_ylabel("Materially altered audit result served", fontsize=6.6, color=INK_SECONDARY)
    axb.tick_params(labelsize=6.5, colors=INK_SECONDARY, length=2)
    _style_axis(axb)
    axb.grid(color=HAIRLINE, linewidth=0.8)
    axb.set_title("(b) Batch policy trade-off", fontsize=7.6, color=INK, loc="left")
    # The data occupy the left edge and the two corners; the lower centre-right is empty.
    axb.legend(fontsize=5.6, frameon=False, loc="center right", bbox_to_anchor=(1.02, 0.29), handletextpad=0.4)

    axc = fig.add_subplot(grid[0, 2])
    xr = np.arange(len(REGIME_ORDER))
    width = 0.26
    for k, policy in enumerate(("union_uncalibrated", "family_calibrated", "family_calibrated_strict")):
        label, color, _ = POLICY_STYLE[policy]
        short = label.split(" (")[0].replace("P3 coverage-complete abstaining", "P3 abstaining")
        block = b[b["policy"] == policy].set_index("regime").reindex(REGIME_ORDER)
        xs = xr + (k - 1) * width
        axc.bar(xs, block["benign_interruption_rate"], width=width, color=color, zorder=3, label=short)
        for xi, v in zip(xs, block["benign_interruption_rate"]):
            if v > 0:
                axc.text(xi, v + 0.014, f"{v:.2f}", ha="center", va="bottom", fontsize=5.2, color=INK, rotation=90, zorder=5)
    total = int(trusted["benign_hold"]) + int(trusted["benign_block"])
    batch_p2 = b[(b["regime"] == "I_XFY") & (b["policy"] == "family_calibrated")].iloc[0]
    batch_total = int(batch_p2["benign_hold"]) + int(batch_p2["benign_block"])
    net = total - batch_total
    # Headroom band above every value label; no leader line is needed, because the
    # trusted regime is named in the note and is the last group of the panel.
    axc.text(0.5, 0.985,
             f"{REGIME_LABEL['I_XFY_trusted']}: {int(trusted['benign_hold'])} statistical holds + {int(trusted['benign_block'])} gross\nexact blocks = {total}; net +{net} vs. batch P2",
             transform=axc.transAxes, fontsize=5.4, color=INK_SECONDARY, ha="center", va="top", linespacing=1.35)
    axc.set_xticks(xr)
    axc.set_xticklabels([REGIME_LABEL[r] for r in REGIME_ORDER], fontsize=7.2, color=INK)
    axc.set_ylim(0, 1.46)
    axc.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    axc.tick_params(axis="y", labelsize=6.5, colors=INK_SECONDARY, length=2)
    axc.tick_params(axis="x", length=0)
    _style_axis(axc)
    axc.set_ylabel("Interruption of 1,200 near-null controls", fontsize=6.6, color=INK_SECONDARY)
    axc.set_title("(c) Near-null control interruption", fontsize=7.6, color=INK, loc="left")
    axc.legend(fontsize=5.4, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, columnspacing=1.0, handlelength=1.2)
    axc.text(0.0, -0.26, "Same 1,200 rows for every regime; synthetic near-null variation,\nnot operational traffic.", transform=axc.transAxes, fontsize=5.6, color=INK_SECONDARY, va="top")

    for path in paths:
        if path.suffix.lower() == ".png":
            fig.savefig(path, dpi=300, bbox_inches="tight")
        else:
            fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=Path("results/paper_digest/paper15_v12_policy"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/figures/paper15_v12_policy"))
    parser.add_argument("--manuscript-figures", type=Path, default=Path("manuscript/figures"))
    parser.add_argument("--manuscript-tables", type=Path, default=Path("manuscript/tables"))
    parser.add_argument("--tdsc-figures", type=Path, default=Path("publication/tdsc/figures"))
    args = parser.parse_args()

    a = _panel_a_frame(args.evidence)
    b = _panel_b_frame(args.evidence)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = "fig_q1_policy_decisions"
    pdf = args.out_dir / f"{stem}.pdf"
    png = args.out_dir / f"{stem}.png"
    _draw(a, b, [pdf, png])
    values_a = args.out_dir / f"{stem}_panel_a_values.csv"
    values_b = args.out_dir / f"{stem}_panel_b_values.csv"
    a.to_csv(values_a, index=False)
    b.to_csv(values_b, index=False)
    manifest = {
        "figure": stem,
        "source_evidence": args.evidence.as_posix(),
        "outputs": {p.name: {"sha256": _sha256(p)} for p in (pdf, png, values_a, values_b)},
    }
    (args.out_dir / "figure_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for target in (args.manuscript_figures, args.tdsc_figures):
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, target / pdf.name)
        if target == args.manuscript_figures:
            shutil.copy2(png, target / png.name)
    args.manuscript_tables.mkdir(parents=True, exist_ok=True)
    shutil.copy2(values_a, args.manuscript_tables / values_a.name)
    shutil.copy2(values_b, args.manuscript_tables / values_b.name)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
