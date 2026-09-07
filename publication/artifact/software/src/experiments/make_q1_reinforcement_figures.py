"""Figure for the Paper 1.5 reinforcement gates (artifact 1.1.0).

Panel (a): null-calibrated detection rate of each information regime on the
frozen ``paper_core`` interventions, with the empirical false-alarm rate of
clean evaluation draws in the first row. Panel (b): the secondary ZZ-minus-SVC
conclusion-impact difference under the three preprocessing configurations and
under cross-validated tuning, with split-cluster intervals.

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
from matplotlib.colors import LinearSegmentedColormap


INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"
HAIRLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
SEQUENTIAL_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

REGIME_ORDER = ["I_X", "I_XF", "I_Ym", "I_XFY", "I_XFY_item_aligned"]
REGIME_LABEL = {
    "I_X": "$\\mathcal{I}_X$",
    "I_XF": "$\\mathcal{I}_{XF}$",
    "I_Ym": "$\\mathcal{I}_{Y_m}$",
    "I_XFY": "$\\mathcal{I}_{XFY}$\nbatch",
    "I_XFY_item_aligned": "$\\mathcal{I}_{XFY}$\nitem",
}
MECHANISM_ORDER = [
    ("feature_sign_flip", "Feature sign flip"),
    ("mean_shift", "Feature-wise mean shift"),
    ("scaling_drift", "Scaling drift"),
    ("feature_dropout", "Feature dropout"),
    ("label_flip_prior_preserving", "Prior-preserving label flip"),
    ("label_flip_r", "Random label flip"),
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _mechanism(attack: str) -> tuple[int, str, float]:
    for order, (prefix, label) in enumerate(MECHANISM_ORDER):
        if attack.startswith(prefix):
            strength = float(attack.rsplit("_", 1)[-1])
            return order, label, strength
    raise ValueError(f"Unknown attack tag {attack}")


def _heatmap_frame(evidence: Path) -> pd.DataFrame:
    det = pd.read_csv(evidence / "calibrated_detection_pooled.csv")
    det = det[det["target_kind"].isin(["regime", "regime_exact"]) & det["target"].isin(REGIME_ORDER)].copy()
    det[["order", "mechanism", "strength"]] = det["attack"].apply(lambda a: pd.Series(_mechanism(a)))
    det["row_label"] = det.apply(lambda r: f"{r['mechanism']} {r['strength']:.2f}", axis=1)
    det = det.sort_values(["order", "strength"])
    fpr = pd.read_csv(evidence / "null_evaluation_false_alarm_overall.csv")
    fpr = fpr[fpr["target_kind"] == "regime"].copy()
    fpr["row_label"] = "Clean evaluation draws (false alarm)"
    fpr["order"] = -1
    fpr["strength"] = 0.0
    fpr = fpr.rename(columns={"false_alarm_rate": "detection_rate"})
    fpr["mechanism"] = "clean_null"
    fpr["attack"] = "clean_resample_eval"
    fpr["attack_family"] = "null_control"
    cols = ["row_label", "order", "strength", "mechanism", "attack", "attack_family", "target", "n", "n_fire", "detection_rate", "ci95_low", "ci95_high"]
    return pd.concat([fpr[cols], det[cols]], ignore_index=True)


def _forest_frame(evidence: Path) -> pd.DataFrame:
    prep = pd.read_csv(evidence / "prep_ablation_paired_zz_minus_svc.csv")
    tuned = pd.read_csv(evidence / "tuned_paired_zz_minus_svc.csv")
    labels = {
        "P0_reference": "CICIDS ID, reference scalers",
        "PA_standard_standard": "CICIDS ID, standard / standard",
        "PB_minmax2pi_minmax2pi": "CICIDS ID, minmax2π / minmax2π",
        "gate1_id_cicids__tuned_cv5": "CICIDS ID, both tuned (CV5)",
        "gate6_ood_unsw__reference_untuned": "UNSW OOD, frozen defaults",
        "gate6_ood_unsw__tuned_cv5": "UNSW OOD, both tuned (CV5)",
    }
    frame = pd.concat([prep, tuned], ignore_index=True)
    frame = frame[frame["condition"].isin(labels)].copy()
    frame["label"] = frame["condition"].map(labels)
    frame["order"] = frame["condition"].map({k: i for i, k in enumerate(labels)})
    return frame.sort_values(["svd_dim", "order"])


def _draw(heat: pd.DataFrame, forest: pd.DataFrame, paths: list[Path]) -> None:
    rows = list(dict.fromkeys(heat["row_label"]))
    matrix = heat.pivot_table(index="row_label", columns="target", values="detection_rate", aggfunc="first").reindex(index=rows, columns=REGIME_ORDER)
    values = matrix.to_numpy(dtype=float)

    fig = plt.figure(figsize=(7.16, 4.7))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.0, 0.95], wspace=1.05)
    ax = fig.add_subplot(grid[0, 0])
    cmap = LinearSegmentedColormap.from_list("paper15_blue", SEQUENTIAL_BLUE)
    ax.imshow(np.ma.masked_invalid(values), cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_xticks(range(len(REGIME_ORDER)))
    ax.set_xticklabels([REGIME_LABEL[r] for r in REGIME_ORDER], fontsize=6.5, color=INK)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=6.3, color=INK)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            v = values[i, j]
            if np.isnan(v):
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color="#f0efec", zorder=2))
                ax.text(j, i, "n/a", ha="center", va="center", fontsize=6.5, color=MUTED, zorder=3)
            else:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.0, color="white" if v >= 0.5 else INK)
    ax.axhline(0.5, color=HAIRLINE, linewidth=1.0)
    for k in (2.5, 5.5, 8.5, 11.5, 14.5):
        ax.axhline(k + 1, color="white", linewidth=1.2)
    ax.set_title("(a) Null-calibrated detection rate, $\\alpha=0.05$ per sensor", fontsize=8, color=INK, loc="left")
    ax.set_xlabel("Regime fires if any sensor fires. Columns 1-4: batch-level, null-calibrated;\ncolumn 5: exact item-aligned (n/a on clean draws)", fontsize=6.3, color=INK_SECONDARY)

    dims = sorted(forest["svd_dim"].unique())
    sub = grid[0, 1].subgridspec(len(dims), 1, hspace=0.35)
    ymax = float(np.nanmax(forest["ci95_high"])) * 1.1
    ymin = min(0.0, float(np.nanmin(forest["ci95_low"]))) * 1.1 - 0.002
    for k, dim in enumerate(dims):
        axf = fig.add_subplot(sub[k, 0])
        block = forest[forest["svd_dim"] == dim].sort_values("order", ascending=False)
        y = np.arange(len(block))
        axf.axvline(0.0, color=BASELINE, linewidth=1.0)
        axf.hlines(y, block["ci95_low"], block["ci95_high"], color=BLUE, linewidth=1.6)
        axf.scatter(block["mean"], y, s=22, color=BLUE, zorder=3, edgecolor="white", linewidth=1.0)
        axf.set_yticks(y)
        axf.set_yticklabels(block["label"], fontsize=6.2, color=INK)
        axf.set_xlim(ymin, ymax)
        axf.tick_params(axis="x", labelsize=6.5, colors=INK_SECONDARY, length=2)
        axf.tick_params(axis="y", length=0)
        for spine in ("top", "right", "left"):
            axf.spines[spine].set_visible(False)
        axf.spines["bottom"].set_color(BASELINE)
        axf.grid(axis="x", color=HAIRLINE, linewidth=0.8)
        axf.set_axisbelow(True)
        axf.text(0.985, 0.94, f"$d={dim}$", transform=axf.transAxes, ha="right", va="top", fontsize=7, color=INK_SECONDARY)
        if k == 0:
            axf.set_title("(b) ZZ $-$ SVC conclusion impact, 95% $t$ over 5 splits", fontsize=8, color=INK, loc="left", pad=8)
        if k == len(dims) - 1:
            axf.set_xlabel("Within-split difference in suite-average balanced-accuracy impact", fontsize=7, color=INK_SECONDARY)

    for path in paths:
        if path.suffix.lower() == ".png":
            fig.savefig(path, dpi=300, bbox_inches="tight")
        else:
            fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=Path("results/paper_digest/paper15_v11_reinforcement"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/figures/paper15_v11_reinforcement"))
    parser.add_argument("--manuscript-figures", type=Path, default=Path("manuscript/figures"))
    parser.add_argument("--manuscript-tables", type=Path, default=Path("manuscript/tables"))
    parser.add_argument("--tdsc-figures", type=Path, default=Path("publication/tdsc/figures"))
    args = parser.parse_args()

    heat = _heatmap_frame(args.evidence)
    forest = _forest_frame(args.evidence)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = "fig_q1_calibrated_coverage"
    pdf = args.out_dir / f"{stem}.pdf"
    png = args.out_dir / f"{stem}.png"
    _draw(heat, forest, [pdf, png])

    values_heat = args.out_dir / f"{stem}_panel_a_values.csv"
    values_forest = args.out_dir / f"{stem}_panel_b_values.csv"
    heat.to_csv(values_heat, index=False)
    forest.to_csv(values_forest, index=False)

    manifest = {
        "figure": stem,
        "source_evidence": args.evidence.as_posix(),
        "outputs": {p.name: {"sha256": _sha256(p)} for p in (pdf, png, main_pdf, main_png, values_heat, values_forest)},
    }
    (args.out_dir / "figure_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    for target in (args.manuscript_figures, args.tdsc_figures):
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, target / pdf.name)
        shutil.copy2(main_pdf, target / main_pdf.name)
        if target == args.manuscript_figures:
            shutil.copy2(png, target / png.name)
            shutil.copy2(main_png, target / main_png.name)
    args.manuscript_tables.mkdir(parents=True, exist_ok=True)
    shutil.copy2(values_heat, args.manuscript_tables / values_heat.name)
    shutil.copy2(values_forest, args.manuscript_tables / values_forest.name)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
