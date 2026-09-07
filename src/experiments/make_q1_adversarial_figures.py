"""Figure for the Paper 1.5 adversarial gate (artifact 1.3.0, Gate A).

Panel (a): detection rate of the executed drift mechanisms (matched controls)
and of their adaptive cluster-preserving variants under the conformal family
rule in the feature and feature-plus-prediction regimes, as a function of the
strength. Panel (b): material fraction (changed balanced accuracy) of the same
rows, showing that the attacker keeps most of the materiality while evading
the batch-level fingerprint. Every plotted value is written to a CSV next to
the figure and hashed in a figure manifest.
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
import pandas as pd


INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
HAIRLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
BLUE_DARK = "#184f95"
ORANGE = "#d9822b"
ORANGE_DARK = "#9a5410"

STYLE = {
    ("mean_shift", "control", "I_X"): (BLUE, "-", "o", "Mean shift, executed, $\\mathcal{I}_X$"),
    ("mean_shift", "control", "I_XF"): (BLUE_DARK, "-", "s", "Mean shift, executed, $\\mathcal{I}_{XF}$"),
    ("mean_shift", "adaptive", "I_X"): (BLUE, "--", "o", "Mean shift, cluster-preserving, $\\mathcal{I}_X$"),
    ("mean_shift", "adaptive", "I_XF"): (BLUE_DARK, "--", "s", "Mean shift, cluster-preserving, $\\mathcal{I}_{XF}$"),
    ("scaling_drift", "control", "I_X"): (ORANGE, "-", "o", "Scaling, executed, $\\mathcal{I}_X$"),
    ("scaling_drift", "control", "I_XF"): (ORANGE_DARK, "-", "s", "Scaling, executed, $\\mathcal{I}_{XF}$"),
    ("scaling_drift", "adaptive", "I_X"): (ORANGE, "--", "o", "Scaling, cluster-preserving, $\\mathcal{I}_X$"),
    ("scaling_drift", "adaptive", "I_XF"): (ORANGE_DARK, "--", "s", "Scaling, cluster-preserving, $\\mathcal{I}_{XF}$"),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _frames(adv: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    det = pd.read_csv(adv / "adversarial_detection_pooled.csv")
    det = det[(det["rule"] == "family") & (det["regime"].isin(["I_X", "I_XF"]))][["mechanism", "attack_class", "strength", "regime", "n", "n_fire", "detection_rate"]].sort_values(["mechanism", "attack_class", "regime", "strength"])
    mat = pd.read_csv(adv / "adversarial_materiality.csv")[["mechanism", "attack_class", "strength", "n", "material_fraction_tau0", "material_fraction_tau002", "material_fraction_tau005", "prediction_change_rate", "mean_perturbed_entry_fraction"]].sort_values(["mechanism", "attack_class", "strength"])
    return det, mat


def _draw(det: pd.DataFrame, mat: pd.DataFrame, paths: list[Path]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.55), gridspec_kw={"wspace": 0.32})
    ax = axes[0]
    for (mech, cls, regime), (color, ls, marker, label) in STYLE.items():
        block = det[(det["mechanism"] == mech) & (det["attack_class"] == cls) & (det["regime"] == regime)]
        ax.plot(block["strength"], block["detection_rate"], color=color, linestyle=ls, marker=marker, markersize=3.6, linewidth=1.2, label=label, zorder=3)
    ax.set_xscale("log")
    ax.set_xticks([0.02, 0.05, 0.10, 0.25, 0.50])
    ax.set_xticklabels(["0.02", "0.05", "0.10", "0.25", "0.50"], fontsize=6.5, color=INK_SECONDARY)
    ax.set_ylim(-0.03, 1.05)
    ax.set_xlabel("Strength ($\\delta$ or $\\alpha$, standard deviations of the scaled feature)", fontsize=6.6, color=INK_SECONDARY)
    ax.set_ylabel("Detection rate, conformal family rule", fontsize=6.8, color=INK_SECONDARY)
    ax.set_title("(a) Executed drift (solid) versus cluster-preserving attacker (dashed)", fontsize=7.4, color=INK, loc="left")
    ax.tick_params(axis="y", labelsize=6.5, colors=INK_SECONDARY, length=2)
    ax.tick_params(axis="x", length=2)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(BASELINE)
    ax.spines["bottom"].set_color(BASELINE)
    ax.grid(color=HAIRLINE, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(fontsize=5.2, frameon=False, loc="lower right", ncol=1)

    axb = axes[1]
    for mech, color in (("mean_shift", BLUE_DARK), ("scaling_drift", ORANGE_DARK)):
        for cls, ls in (("control", "-"), ("adaptive", "--")):
            block = mat[(mat["mechanism"] == mech) & (mat["attack_class"] == cls)]
            label = f"{'Mean shift' if mech == 'mean_shift' else 'Scaling'}, {'executed' if cls == 'control' else 'cluster-preserving'}"
            axb.plot(block["strength"], block["material_fraction_tau0"], color=color, linestyle=ls, marker="o", markersize=3.6, linewidth=1.2, label=label, zorder=3)
    axb.set_xscale("log")
    axb.set_xticks([0.02, 0.05, 0.10, 0.25, 0.50])
    axb.set_xticklabels(["0.02", "0.05", "0.10", "0.25", "0.50"], fontsize=6.5, color=INK_SECONDARY)
    axb.set_ylim(-0.03, 1.05)
    axb.set_xlabel("Strength", fontsize=6.6, color=INK_SECONDARY)
    axb.set_ylabel("Material fraction ($|\\Delta_R|>0$)", fontsize=6.8, color=INK_SECONDARY)
    axb.set_title("(b) Conclusion change kept by the attacker", fontsize=7.4, color=INK, loc="left")
    axb.tick_params(axis="y", labelsize=6.5, colors=INK_SECONDARY, length=2)
    axb.tick_params(axis="x", length=2)
    for spine in ("top", "right"):
        axb.spines[spine].set_visible(False)
    axb.spines["left"].set_color(BASELINE)
    axb.spines["bottom"].set_color(BASELINE)
    axb.grid(color=HAIRLINE, linewidth=0.8)
    axb.set_axisbelow(True)
    axb.legend(fontsize=5.4, frameon=False, loc="lower right")
    for path in paths:
        if path.suffix.lower() == ".png":
            fig.savefig(path, dpi=300, bbox_inches="tight")
        else:
            fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adversarial", type=Path, default=Path("results/paper_digest/paper15_v13_adversarial"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/figures/paper15_v13_adversarial"))
    parser.add_argument("--manuscript-figures", type=Path, default=Path("manuscript/figures"))
    parser.add_argument("--manuscript-tables", type=Path, default=Path("manuscript/tables"))
    parser.add_argument("--tdsc-figures", type=Path, default=Path("publication/tdsc/figures"))
    args = parser.parse_args()
    det, mat = _frames(args.adversarial)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = "fig_q1_adversarial_cluster_preserving"
    pdf = args.out_dir / f"{stem}.pdf"
    png = args.out_dir / f"{stem}.png"
    _draw(det, mat, [pdf, png])
    values_a = args.out_dir / f"{stem}_panel_a_values.csv"
    values_b = args.out_dir / f"{stem}_panel_b_values.csv"
    det.to_csv(values_a, index=False)
    mat.to_csv(values_b, index=False)
    manifest = {"figure": stem, "source_evidence": args.adversarial.as_posix(), "outputs": {p.name: {"sha256": _sha256(p)} for p in (pdf, png, values_a, values_b)}}
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
