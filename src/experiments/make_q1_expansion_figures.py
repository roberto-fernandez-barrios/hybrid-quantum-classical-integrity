"""Generate reviewer-facing figures from the strict Q1 expansion package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

from src.experiments.build_q1_gate1_evidence import (
    FEATURE_SIGNAL_COLS,
    JOINT_OUTCOME_SIGNAL_COLS,
    LABEL_MARGINAL_SIGNAL_COLS,
    PREDICTION_SIGNAL_COLS,
)


GATE_LABELS = {
    "gate2_id_256": "CICIDS ID (256)",
    "gate5a_id_unsw": "UNSW-NB15 ID",
    "gate5b_id_ton_iot": "ToN-IoT ID",
    "gate3a_ood_tue_wed": "CICIDS Tue→Wed",
    "gate3b_ood_tue_fri_portscan": "CICIDS Tue→Fri-PortScan",
    "gate3c_ood_wed_thu_webattacks": "CICIDS Wed→Thu-Web",
    "gate3d_ood_wed_fri_morning": "CICIDS Wed→Fri-AM",
    "gate6_ood_unsw": "UNSW temporal OOD",
}

GATE_ORDER = list(GATE_LABELS)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_complete_package(evidence_dir: Path, allow_partial: bool) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    manifest_path = evidence_dir / "expansion_evidence_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "complete" and not allow_partial:
        raise RuntimeError(
            "Expansion evidence is not complete. Rebuild without --allow-partial "
            "after the queue finishes."
        )
    paired = pd.read_csv(evidence_dir / "expansion_paired_zz_minus_svc_clustered.csv")
    observations = pd.read_csv(
        evidence_dir / "expansion_unique_observations.csv", low_memory=False
    )
    return paired, observations, manifest


def _forest_plot(paired: pd.DataFrame, out_dir: Path) -> list[Path]:
    data = paired[paired["metric"] == "impact_mean"].copy()
    data["gate"] = pd.Categorical(data["gate"], categories=GATE_ORDER, ordered=True)
    data = data.sort_values(["gate", "svd_dim"])

    environments = [gate for gate in GATE_ORDER if gate in set(data["gate"].dropna().astype(str))]
    y_positions = np.arange(len(environments))
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 6.2), sharex=True, sharey=True)

    for axis, dimension in zip(axes, [8, 10, 12], strict=True):
        subset = data[data["svd_dim"] == dimension].set_index("gate")
        for y, gate in zip(y_positions, environments, strict=True):
            if gate not in subset.index:
                continue
            row = subset.loc[gate]
            color = "#1f77b4" if str(row["protocol"]) == "id" else "#d95f02"
            mean = float(row["mean"])
            low = float(row["ci95_low"])
            high = float(row["ci95_high"])
            axis.errorbar(
                mean,
                y,
                xerr=[[mean - low], [high - mean]],
                fmt="o",
                color=color,
                ecolor=color,
                capsize=3,
                markersize=5,
            )
        axis.axvline(0.0, color="black", linewidth=0.9, linestyle="--")
        axis.grid(axis="x", alpha=0.25)
        axis.set_title(f"Projected dimension {dimension}")
        axis.set_xlabel("QSVC-ZZ − SVC-RBF\n(mean conclusion-impact difference)")
        axis.set_yticks(y_positions)
        axis.set_yticklabels([GATE_LABELS[gate] for gate in environments])
        axis.invert_yaxis()

    legend = [
        Line2D([0], [0], marker="o", color="#1f77b4", linestyle="none", label="ID"),
        Line2D([0], [0], marker="o", color="#d95f02", linestyle="none", label="OOD"),
    ]
    fig.subplots_adjust(left=0.22, right=0.98, bottom=0.18, top=0.82, wspace=0.08)
    fig.suptitle(
        "Split-clustered model-profile differences across fixed environments",
        fontsize=13,
        y=0.97,
    )
    fig.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, 0.91), ncol=2, frameon=False)
    fig.text(
        0.5,
        0.035,
        "Points are environment-specific means; bars are 95% t intervals over five split clusters. No population pooling.",
        ha="center",
        fontsize=9,
    )

    paths = [out_dir / "fig_q1_external_forest.png", out_dir / "fig_q1_external_forest.pdf"]
    fig.savefig(paths[0], dpi=300, bbox_inches="tight")
    fig.savefig(paths[1], bbox_inches="tight")
    plt.close(fig)
    return paths


def _nonzero_fraction(group: pd.DataFrame, columns: list[str], tolerance: float = 1e-12) -> float:
    values = group[columns].apply(pd.to_numeric, errors="coerce").abs()
    return float((values.max(axis=1) > tolerance).mean())


def _coverage_plot(observations: pd.DataFrame, out_dir: Path) -> tuple[list[Path], pd.DataFrame]:
    attacked = observations[observations["attack"] != "clean"].copy()
    regimes = {
        "Features": FEATURE_SIGNAL_COLS,
        "Features + prediction": FEATURE_SIGNAL_COLS + PREDICTION_SIGNAL_COLS,
        "Label marginal": LABEL_MARGINAL_SIGNAL_COLS,
        "Joint outcome": JOINT_OUTCOME_SIGNAL_COLS,
    }
    records: list[dict[str, object]] = []
    for (family, attack), group in attacked.groupby(["attack_family", "attack"], sort=True):
        record: dict[str, object] = {"attack_family": family, "attack": attack}
        for label, columns in regimes.items():
            record[label] = _nonzero_fraction(group, columns)
        records.append(record)

    coverage = pd.DataFrame.from_records(records).sort_values(["attack_family", "attack"])
    values = coverage[list(regimes)].to_numpy(dtype=float)
    row_labels = [f"{family}: {attack}" for family, attack in coverage[["attack_family", "attack"]].itertuples(index=False, name=None)]

    fig_height = max(7.0, 0.42 * len(coverage))
    fig, axis = plt.subplots(figsize=(10.5, fig_height), constrained_layout=True)
    image = axis.imshow(values, vmin=0.0, vmax=1.0, cmap="viridis", aspect="auto")
    axis.set_xticks(np.arange(len(regimes)))
    axis.set_xticklabels(list(regimes), rotation=20, ha="right")
    axis.set_yticks(np.arange(len(coverage)))
    axis.set_yticklabels(row_labels, fontsize=8)
    axis.set_title("Empirical sensor response by information regime")
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            value = values[row, column]
            axis.text(
                column,
                row,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=7,
                color="white" if value < 0.55 else "black",
            )
    colorbar = fig.colorbar(image, ax=axis, shrink=0.82)
    colorbar.set_label("Fraction of model/environment/seed cells with non-zero raw response")
    fig.text(
        0.5,
        0.005,
        "A zero is a raw invariance result, not an estimated detector power; practical alarms require calibration.",
        ha="center",
        fontsize=9,
    )

    paths = [out_dir / "fig_q1_sensor_coverage.png", out_dir / "fig_q1_sensor_coverage.pdf"]
    fig.savefig(paths[0], dpi=300, bbox_inches="tight")
    fig.savefig(paths[1], bbox_inches="tight")
    plt.close(fig)
    return paths, coverage


def build(evidence_dir: Path, out_dir: Path, *, allow_partial: bool = False) -> None:
    paired, observations, source_manifest = _load_complete_package(evidence_dir, allow_partial)
    out_dir.mkdir(parents=True, exist_ok=True)

    forest_paths = _forest_plot(paired, out_dir)
    coverage_paths, coverage = _coverage_plot(observations, out_dir)
    coverage_csv = out_dir / "fig_q1_sensor_coverage_values.csv"
    coverage.to_csv(coverage_csv, index=False)

    paths = [*forest_paths, *coverage_paths, coverage_csv]
    manifest = {
        "analysis": "paper15_q1_expansion_figures",
        "source_evidence_status": source_manifest.get("status"),
        "partial_watermark_required": bool(source_manifest.get("status") != "complete"),
        "source_manifest_sha256": _sha256(evidence_dir / "expansion_evidence_manifest.json"),
        "outputs": {
            path.name: {"bytes": path.stat().st_size, "sha256": _sha256(path)}
            for path in paths
        },
    }
    manifest_path = out_dir / "figure_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {len(paths)} figure artifacts and manifest to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=Path("results/paper_digest/paper15_q1_expansion"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/figures/paper15_q1_expansion"),
    )
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    build(args.evidence_dir, args.out_dir, allow_partial=bool(args.allow_partial))


if __name__ == "__main__":
    main()
