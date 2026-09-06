"""Render the quantum-specific integrity-contract figure from Gate D outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ATTACK_LABELS = {
    "clean": "Clean control",
    "benign_transpile_o1": "Benign transpilation",
    "common_unitary_x": "Common-unitary rewrite",
    "parameterized_rz_alpha_0.020": "Parameterized RZ (0.02)",
    "parameterized_rz_alpha_0.100": "Parameterized RZ (0.10)",
    "feature_map_reps_2": "Feature-map reps 1→2",
    "kernel_asymmetric_delta_0.020": "Asymmetric kernel edit",
    "kernel_diagonal_erosion_0.020": "Kernel diagonal erosion",
    "kernel_psd_preserving_mix_0.050": "PSD-preserving kernel mix",
    "shot_emulator_256": "Shot estimator (256)",
    "shot_emulator_1024": "Shot estimator (1024)",
}

SENSORS = {
    "Circuit\nprovenance": "circuit_provenance_detection_rate",
    "Kernel\nprovenance": "kernel_provenance_detection_rate",
    "Semantic\nkernel": "semantic_kernel_detection_rate",
    "Algebraic\nkernel": "algebraic_kernel_detection_rate",
    "Repeated\nestimation": "repeated_estimation_detection_rate",
    "Model\noutput": "output_change_rate",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(evidence_dir: Path, out_dir: Path) -> None:
    manifest_path = evidence_dir / "quantum_integrity_gate_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "complete" or not all(
        manifest.get("acceptance_checks", {}).values()
    ):
        raise RuntimeError("Quantum-integrity evidence is not a completed accepted gate")

    source_path = evidence_dir / "quantum_integrity_gate_sensor_coverage.csv"
    coverage = pd.read_csv(source_path).set_index("attack")
    order = list(ATTACK_LABELS)
    missing = [attack for attack in order if attack not in coverage.index]
    if missing:
        raise ValueError(f"Coverage table is missing attacks: {missing}")
    coverage = coverage.loc[order]
    matrix = coverage[list(SENSORS.values())].to_numpy(dtype=float)

    fig, axis = plt.subplots(figsize=(11.2, 6.9))
    image = axis.imshow(matrix, vmin=0.0, vmax=1.0, cmap="viridis", aspect="auto")
    axis.set_xticks(np.arange(len(SENSORS)))
    axis.set_xticklabels(list(SENSORS), fontsize=9)
    axis.set_yticks(np.arange(len(order)))
    axis.set_yticklabels([ATTACK_LABELS[attack] for attack in order], fontsize=9)
    axis.set_title("Quantum-workflow integrity coverage is sensor-conditional", fontsize=13)

    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            value = float(matrix[row, column])
            axis.text(
                column,
                row,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=8,
                color="white" if value < 0.55 else "black",
            )

    fig.subplots_adjust(left=0.24, right=0.91, bottom=0.22, top=0.90)
    colorbar = fig.colorbar(image, ax=axis, shrink=0.82)
    colorbar.set_label("Detection fraction across 5 splits × 3 dimensions")
    fig.text(
        0.5,
        0.035,
        "Provenance assumes a trusted reference; semantic and algebraic checks answer different questions. Shot rows are binomial emulation, not QPU runs.",
        ha="center",
        fontsize=9,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / "fig_q1_quantum_integrity_contract.png"
    pdf = out_dir / "fig_q1_quantum_integrity_contract.pdf"
    values = out_dir / "fig_q1_quantum_integrity_contract_values.csv"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    coverage.reset_index().to_csv(values, index=False)

    figure_manifest = {
        "analysis": "paper15_q1_quantum_integrity_figure",
        "source_manifest_sha256": _sha256(manifest_path),
        "source_coverage_sha256": _sha256(source_path),
        "scope": manifest.get("scope"),
        "outputs": {
            path.name: {"bytes": path.stat().st_size, "sha256": _sha256(path)}
            for path in [png, pdf, values]
        },
    }
    (out_dir / "quantum_integrity_figure_manifest.json").write_text(
        json.dumps(figure_manifest, indent=2), encoding="utf-8"
    )
    print(f"Wrote quantum-integrity figure, values, and manifest to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=Path("results/paper_digest/paper15_q1_quantum_integrity_gate"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/figures/paper15_q1_quantum_integrity_gate"),
    )
    args = parser.parse_args()
    build(args.evidence_dir, args.out_dir)


if __name__ == "__main__":
    main()
