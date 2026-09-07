"""Figure for the Paper 1.5 policy gates (artifact 1.2.0).

Panel (a): decision-level false-alarm rate of the uncalibrated union rule and
of the family-calibrated rule per information regime, with the range of the
eight per-environment cluster means and the nominal level. Panel (b): the
unsafe-allow / false-hold trade-off of every policy and regime at the primary
materiality threshold, with the label-path share of the unsafe allows.

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
MUTED = "#898781"
HAIRLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
BLUE_DARK = "#184f95"
ORANGE = "#d9822b"
GREEN = "#3a8f5c"
GREY = "#9a9891"

REGIME_ORDER = ["I_X", "I_XF", "I_Ym", "I_XFY", "I_XFY_trusted"]
BATCH = ["I_X", "I_XF", "I_Ym", "I_XFY"]
REGIME_LABEL = {"I_X": "$\\mathcal{I}_X$", "I_XF": "$\\mathcal{I}_{XF}$", "I_Ym": "$\\mathcal{I}_{Y_m}$", "I_XFY": "$\\mathcal{I}_{XFY}$", "I_XFY_trusted": "$\\mathcal{I}_{XFY}^{\\star}$"}
POLICY_STYLE = {
    "serve_always": ("P0 serve-always", GREY, "s"),
    "union_uncalibrated": ("P1 union (1.1.0)", ORANGE, "^"),
    "family_calibrated": ("P2 family-calibrated", BLUE, "o"),
    "family_calibrated_strict": ("P3 strict fail-closed", GREEN, "D"),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _panel_a_frame(evidence: Path) -> pd.DataFrame:
    fpr = pd.read_csv(evidence / "family_false_alarm_overall.csv")
    fpr = fpr[fpr["regime"].isin(BATCH)].copy()
    fpr["order"] = fpr["regime"].map({r: i for i, r in enumerate(BATCH)})
    return fpr.sort_values(["order", "rule"])[["regime", "rule", "n_draws", "n_fire", "pooled_rate", "environment_cluster_mean_min", "environment_cluster_mean_max", "nominal_alpha"]]


def _panel_b_frame(evidence: Path) -> pd.DataFrame:
    m = pd.read_csv(evidence / "policy_metrics.csv")
    m = m[m["tau"] == 0.0].copy()
    fam = pd.read_csv(evidence / "policy_metrics_by_family.csv")
    fam = fam[(fam["tau"] == 0.0) & (fam["attack_family"] == "target_shift")][["regime", "policy", "unsafe_allow"]].rename(columns={"unsafe_allow": "unsafe_allow_label_path"})
    m = m.merge(fam, on=["regime", "policy"], how="left")
    m["order"] = m["regime"].map({r: i for i, r in enumerate(REGIME_ORDER)})
    return m.sort_values(["order", "policy"])[["regime", "policy", "n_clean", "decision_fpr", "n_material", "unsafe_allow", "unsafe_allow_rate", "unsafe_allow_label_path", "containment", "residual_blind_material"]]


def _draw(a: pd.DataFrame, b: pd.DataFrame, paths: list[Path]) -> None:
    fig = plt.figure(figsize=(7.16, 3.0))
    grid = fig.add_gridspec(1, 2, width_ratios=[0.9, 1.1], wspace=0.35)

    ax = fig.add_subplot(grid[0, 0])
    x = np.arange(len(BATCH))
    width = 0.36
    for k, (rule, color, label) in enumerate((("union", ORANGE, "Union of per-sensor rules (1.1.0)"), ("family", BLUE, "Family-calibrated (Gate F)"))):
        block = a[a["rule"] == rule].set_index("regime").reindex(BATCH)
        xs = x + (k - 0.5) * width
        ax.bar(xs, block["pooled_rate"], width=width, color=color, label=label, zorder=3)
        lo = block["pooled_rate"] - block["environment_cluster_mean_min"]
        hi = block["environment_cluster_mean_max"] - block["pooled_rate"]
        ax.errorbar(xs, block["pooled_rate"], yerr=np.vstack([lo.clip(lower=0), hi.clip(lower=0)]), fmt="none", ecolor=INK_SECONDARY, elinewidth=0.8, capsize=2, zorder=4)
        for xi, v in zip(xs, block["pooled_rate"]):
            ax.text(xi + (k - 0.5) * 0.06, v + 0.012, f"{v:.3f}", ha="right" if k == 0 else "left", va="bottom", fontsize=5.6, color=INK)
    ax.axhline(0.05, color=BASELINE, linewidth=1.0, linestyle="--", zorder=2)
    ax.text(len(BATCH) - 0.55, 0.053, "nominal 0.05", fontsize=6, color=INK_SECONDARY, ha="right", va="bottom")
    ax.set_xticks(x)
    ax.set_xticklabels([REGIME_LABEL[r] for r in BATCH], fontsize=7.5, color=INK)
    ax.set_ylim(0, max(0.42, float(a["environment_cluster_mean_max"].max()) * 1.15))
    ax.tick_params(axis="y", labelsize=6.5, colors=INK_SECONDARY, length=2)
    ax.tick_params(axis="x", length=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(BASELINE)
    ax.spines["bottom"].set_color(BASELINE)
    ax.grid(axis="y", color=HAIRLINE, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_ylabel("Decision false-alarm rate on clean draws", fontsize=6.8, color=INK_SECONDARY)
    ax.set_title("(a) Per-sensor $\\alpha=0.05$ does not calibrate the decision", fontsize=7.6, color=INK, loc="left")
    ax.legend(fontsize=6, frameon=False, loc="upper left")
    ax.text(0.0, -0.2, "Bars: pooled rate over 12,000 draws; whiskers: range of the eight\nper-environment cluster means (five split clusters each).", transform=ax.transAxes, fontsize=5.8, color=INK_SECONDARY, va="top")

    axb = fig.add_subplot(grid[0, 1])
    for policy, (label, color, marker) in POLICY_STYLE.items():
        block = b[b["policy"] == policy]
        axb.scatter(block["decision_fpr"], block["unsafe_allow_rate"], s=26, color=color, marker=marker, label=label, zorder=4, edgecolor="white", linewidth=0.6)
    for regime in REGIME_ORDER:
        block = b[(b["regime"] == regime) & (b["policy"].isin(["union_uncalibrated", "family_calibrated"]))].sort_values("decision_fpr")
        if len(block) == 2:
            axb.plot(block["decision_fpr"], block["unsafe_allow_rate"], color=HAIRLINE, linewidth=0.9, zorder=2)
    offsets = {"I_X": (-4, 7), "I_XF": (10, -13), "I_Ym": (6, 4), "I_XFY": None, "I_XFY_trusted": (8, 4)}
    labels = {"I_XF": REGIME_LABEL["I_XF"] + ", " + REGIME_LABEL["I_XFY"]}
    for regime in REGIME_ORDER:
        if offsets[regime] is None:
            continue
        row = b[(b["regime"] == regime) & (b["policy"] == "family_calibrated")].iloc[0]
        dx, dy = offsets[regime]
        axb.annotate(labels.get(regime, REGIME_LABEL[regime]), (row["decision_fpr"], row["unsafe_allow_rate"]), xytext=(dx, dy), textcoords="offset points", fontsize=6.6, color=INK, arrowprops=dict(arrowstyle="-", color=HAIRLINE, lw=0.7) if regime == "I_XF" else None)
    strict = b[(b["policy"] == "family_calibrated_strict") & (b["regime"] == "I_X")].iloc[0]
    axb.annotate("P3 in $\\mathcal{I}_X$, $\\mathcal{I}_{XF}$, $\\mathcal{I}_{Y_m}$:\nnothing served", (strict["decision_fpr"], strict["unsafe_allow_rate"]), xytext=(-70, 10), textcoords="offset points", fontsize=5.8, color=INK_SECONDARY, ha="left")
    axb.set_xlim(-0.03, 1.05)
    axb.set_ylim(-0.04, 1.06)
    axb.set_xlabel("Decision false-alarm rate (clean held or blocked)", fontsize=6.8, color=INK_SECONDARY)
    axb.set_ylabel("Unsafe-allow rate (material served)", fontsize=6.8, color=INK_SECONDARY)
    axb.tick_params(labelsize=6.5, colors=INK_SECONDARY, length=2)
    for spine in ("top", "right"):
        axb.spines[spine].set_visible(False)
    axb.spines["left"].set_color(BASELINE)
    axb.spines["bottom"].set_color(BASELINE)
    axb.grid(color=HAIRLINE, linewidth=0.8)
    axb.set_axisbelow(True)
    axb.set_title("(b) Unsafe allow versus false hold, $|\\Delta_R|>0$", fontsize=7.6, color=INK, loc="left")
    axb.legend(fontsize=5.8, frameon=False, loc="upper right")

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
