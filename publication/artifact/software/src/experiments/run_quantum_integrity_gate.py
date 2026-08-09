"""Quantum-specific integrity gate for the Paper 1.5 Q1 expansion.

This experiment isolates integrity boundaries that the data-perturbation suite
cannot cover: parameterized-circuit mutation, semantics-preserving circuit
rewrites, transpilation differentials, kernel-matrix corruption, and a
finite-shot fidelity-estimation emulator.  It records provenance, semantic,
algebraic, repeated-estimation, and model-output evidence separately.

The experiment is simulator evidence.  The shot rows use binomial sampling from
the exact fidelity matrix; they are not executions on a sampler backend or QPU.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import platform
from typing import Any

import numpy as np
import pandas as pd
import qiskit
from qiskit import qasm3, transpile
from qiskit.circuit.library import RZGate
import qiskit_machine_learning
from scipy.stats import t as student_t
import sklearn
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.svm import SVC

from src.datasets.cicids_subset import CicidsConfig, load_cicids_subset
from src.experiments.run_benchmark import (
    _stratified_subsample,
    build_scaler,
    fit_transform_scaler,
)
from src.qml.quantum_qsvc import QuantumCfg, _make_feature_map
from src.qml.statevector_fidelity_kernel import ExactStatevectorFidelityKernel


@dataclass(frozen=True)
class GateConfig:
    data: Path = Path("data/cicids_subset.csv")
    out_dir: Path = Path("results/paper_digest/paper15_q1_quantum_integrity_gate")
    split_seeds: tuple[int, ...] = (42, 43, 44, 45, 46)
    dimensions: tuple[int, ...] = (4, 6, 8)
    max_train: int = 64
    max_test: int = 64
    model_seed: int = 42
    feature_map: str = "zz"
    reps: int = 1


ATTACK_NAMES = (
    "clean",
    "benign_transpile_o1",
    "common_unitary_x",
    "parameterized_rz_alpha_0.020",
    "parameterized_rz_alpha_0.100",
    "feature_map_reps_2",
    "kernel_asymmetric_delta_0.020",
    "kernel_diagonal_erosion_0.020",
    "kernel_psd_preserving_mix_0.050",
    "shot_emulator_256",
    "shot_emulator_1024",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _stable_seed(split_seed: int, dimension: int, attack: str) -> int:
    payload = f"{split_seed}|{dimension}|{attack}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:4], "big")


def _circuit_hash(circuit: Any) -> str:
    canonical_qasm = qasm3.dumps(circuit)
    return hashlib.sha256(canonical_qasm.encode("utf-8")).hexdigest()


def _array_hash(array: np.ndarray) -> str:
    value = np.ascontiguousarray(array, dtype=np.float64)
    digest = hashlib.sha256()
    digest.update(np.asarray(value.shape, dtype=np.int64).tobytes())
    digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _primitive_profile(circuit: Any) -> tuple[int, Counter[str]]:
    decomposed = circuit.decompose(reps=10)
    return int(decomposed.depth()), Counter({str(k): int(v) for k, v in decomposed.count_ops().items()})


def _op_count_l1(left: Counter[str], right: Counter[str]) -> int:
    return int(sum(abs(left[key] - right[key]) for key in set(left) | set(right)))


def _make_parameterized_rz(feature_map: Any, alpha: float) -> Any:
    attacked = feature_map.copy()
    parameters = tuple(attacked.parameters)
    if not parameters:
        raise ValueError("Feature map exposes no parameters")
    attacked.append(RZGate(float(alpha) * parameters[0]), [0])
    attacked.name = f"{feature_map.name}_rz_alpha_{alpha:.3f}"
    return attacked


def _make_common_unitary(feature_map: Any) -> Any:
    attacked = feature_map.copy()
    attacked.x(0)
    attacked.name = f"{feature_map.name}_common_x"
    return attacked


def _make_transpiled(feature_map: Any, seed: int) -> Any:
    return transpile(
        feature_map,
        basis_gates=["rz", "sx", "x", "cx"],
        optimization_level=1,
        seed_transpiler=int(seed),
    )


def _kernel_blocks(feature_map: Any, x_train: np.ndarray, x_test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    kernel = ExactStatevectorFidelityKernel(feature_map=feature_map, enforce_psd=True)
    return kernel.evaluate(x_train), kernel.evaluate(x_test, x_train)


def _sample_symmetric_fidelity(kernel: np.ndarray, shots: int, rng: np.random.Generator) -> np.ndarray:
    source = np.clip(np.asarray(kernel, dtype=float), 0.0, 1.0)
    n = source.shape[0]
    out = np.eye(n, dtype=float)
    upper_i, upper_j = np.triu_indices(n, k=1)
    probabilities = source[upper_i, upper_j]
    estimates = rng.binomial(int(shots), probabilities) / float(shots)
    out[upper_i, upper_j] = estimates
    out[upper_j, upper_i] = estimates
    return out


def _sample_cross_fidelity(kernel: np.ndarray, shots: int, rng: np.random.Generator) -> np.ndarray:
    source = np.clip(np.asarray(kernel, dtype=float), 0.0, 1.0)
    return rng.binomial(int(shots), source) / float(shots)


def _nearest_psd(kernel: np.ndarray) -> np.ndarray:
    symmetric = 0.5 * (np.asarray(kernel, dtype=float) + np.asarray(kernel, dtype=float).T)
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    return (eigenvectors @ np.diag(np.maximum(0.0, eigenvalues)) @ eigenvectors.T).real


def _algebraic_signals(kernel: np.ndarray) -> dict[str, float]:
    value = np.asarray(kernel, dtype=float)
    symmetric = 0.5 * (value + value.T)
    repaired = _nearest_psd(value)
    denominator = max(float(np.linalg.norm(value, ord="fro")), np.finfo(float).eps)
    return {
        "kernel_symmetry_residual": float(np.max(np.abs(value - value.T))),
        "kernel_diagonal_residual": float(np.max(np.abs(np.diag(value) - 1.0))),
        "kernel_min_eigenvalue": float(np.linalg.eigvalsh(symmetric).min()),
        "kernel_psd_repair_relative_fro": float(np.linalg.norm(repaired - value, ord="fro") / denominator),
    }


def _evaluate_model(
    train_kernel: np.ndarray,
    test_kernel: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> tuple[SVC, np.ndarray, np.ndarray, dict[str, float]]:
    model = SVC(kernel="precomputed", C=1.0, tol=1e-3, max_iter=1000)
    model.fit(np.asarray(train_kernel, dtype=float), y_train)
    predictions = np.asarray(model.predict(np.asarray(test_kernel, dtype=float)), dtype=int)
    scores = np.asarray(model.decision_function(np.asarray(test_kernel, dtype=float)), dtype=float)
    try:
        auc = float(roc_auc_score(y_test, scores))
    except ValueError:
        auc = math.nan
    metrics = {
        "bal_acc": float(balanced_accuracy_score(y_test, predictions)),
        "f1_pos": float(f1_score(y_test, predictions, pos_label=1, zero_division=0)),
        "roc_auc": auc,
    }
    return model, predictions, scores, metrics


def _load_cell(config: GateConfig, split_seed: int, dimension: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x_train, y_train, x_test, y_test = load_cicids_subset(
        CicidsConfig(path=config.data, svd_dim=int(dimension)),
        seed=int(split_seed),
    )
    packed = int(split_seed) * 1_000_000 + int(config.model_seed)
    x_train, y_train = _stratified_subsample(
        x_train, y_train, int(config.max_train), seed=packed
    )
    x_test, y_test = _stratified_subsample(
        x_test, y_test, int(config.max_test), seed=packed + 1
    )
    scaler = build_scaler("minmax2pi")
    x_train, x_test = fit_transform_scaler(scaler, x_train, x_test)
    return x_train, y_train.astype(int), x_test, y_test.astype(int)


def _attack_kernels(
    attack: str,
    base_feature_map: Any,
    base_train: np.ndarray,
    base_test: np.ndarray,
    x_train: np.ndarray,
    x_test: np.ndarray,
    rng: np.random.Generator,
    split_seed: int,
    dimension: int,
) -> tuple[np.ndarray, np.ndarray, Any, float, str, str, int | None]:
    """Return train/test kernels, circuit, repeat discrepancy, family, boundary, shots."""

    if attack == "clean":
        return base_train.copy(), base_test.copy(), base_feature_map, 0.0, "clean", "none", None

    if attack == "benign_transpile_o1":
        circuit = _make_transpiled(base_feature_map, seed=split_seed)
        train, test = _kernel_blocks(circuit, x_train, x_test)
        return train, test, circuit, 0.0, "semantic_control", "transpilation", None

    if attack == "common_unitary_x":
        circuit = _make_common_unitary(base_feature_map)
        train, test = _kernel_blocks(circuit, x_train, x_test)
        return train, test, circuit, 0.0, "semantic_control", "circuit", None

    if attack.startswith("parameterized_rz_alpha_"):
        alpha = float(attack.rsplit("_", 1)[-1])
        circuit = _make_parameterized_rz(base_feature_map, alpha)
        train, test = _kernel_blocks(circuit, x_train, x_test)
        return train, test, circuit, 0.0, "circuit_tamper", "circuit", None

    if attack == "feature_map_reps_2":
        circuit = _make_feature_map(
            int(dimension),
            QuantumCfg(feature_map="zz", reps=2, backend_method="exact_statevector"),
        )
        train, test = _kernel_blocks(circuit, x_train, x_test)
        return train, test, circuit, 0.0, "circuit_tamper", "circuit", None

    if attack == "kernel_asymmetric_delta_0.020":
        train = base_train.copy()
        n_changes = max(1, int(round(0.02 * train.shape[0] * (train.shape[0] - 1) / 2)))
        upper_i, upper_j = np.triu_indices(train.shape[0], k=1)
        chosen = rng.choice(len(upper_i), size=min(n_changes, len(upper_i)), replace=False)
        train[upper_i[chosen], upper_j[chosen]] = np.clip(
            train[upper_i[chosen], upper_j[chosen]] + 0.02, 0.0, 1.0
        )
        return train, base_test.copy(), base_feature_map, 0.0, "kernel_tamper", "kernel", None

    if attack == "kernel_diagonal_erosion_0.020":
        train = base_train.copy()
        np.fill_diagonal(train, np.clip(np.diag(train) - 0.02, 0.0, 1.0))
        return train, base_test.copy(), base_feature_map, 0.0, "kernel_tamper", "kernel", None

    if attack == "kernel_psd_preserving_mix_0.050":
        strength = 0.05
        train = (1.0 - strength) * base_train + strength * np.eye(base_train.shape[0])
        test = (1.0 - strength) * base_test
        return train, test, base_feature_map, 0.0, "kernel_tamper", "kernel", None

    if attack.startswith("shot_emulator_"):
        shots = int(attack.rsplit("_", 1)[-1])
        train = _sample_symmetric_fidelity(base_train, shots, rng)
        test = _sample_cross_fidelity(base_test, shots, rng)
        repeat_rng = np.random.default_rng(_stable_seed(split_seed + 10_000, dimension, attack))
        repeat_train = _sample_symmetric_fidelity(base_train, shots, repeat_rng)
        repeat_test = _sample_cross_fidelity(base_test, shots, repeat_rng)
        discrepancy = max(
            float(np.max(np.abs(train - repeat_train))),
            float(np.max(np.abs(test - repeat_test))),
        )
        return train, test, base_feature_map, discrepancy, "finite_shot_emulator", "kernel_estimation", shots

    raise ValueError(f"Unknown quantum-integrity attack: {attack}")


def _mean_ci(values: pd.Series) -> dict[str, float | int]:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    n = int(len(clean))
    mean = float(clean.mean()) if n else math.nan
    if n < 2:
        return {"mean": mean, "ci95_low": math.nan, "ci95_high": math.nan, "n": n}
    std = float(clean.std(ddof=1))
    half = float(student_t.ppf(0.975, df=n - 1) * std / math.sqrt(n))
    return {"mean": mean, "ci95_low": mean - half, "ci95_high": mean + half, "n": n}


def _summaries(rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    metrics = [
        "bal_acc_drop",
        "prediction_disagreement",
        "kernel_max_abs_delta",
        "kernel_psd_repair_relative_fro",
        "repeated_estimation_discrepancy",
    ]
    records: list[dict[str, object]] = []
    for (attack, family, boundary, dimension), group in rows.groupby(
        ["attack", "attack_family", "boundary", "svd_dim"], sort=True
    ):
        for metric in metrics:
            records.append(
                {
                    "attack": attack,
                    "attack_family": family,
                    "boundary": boundary,
                    "svd_dim": int(dimension),
                    "metric": metric,
                    **_mean_ci(group[metric]),
                }
            )
    summary = pd.DataFrame.from_records(records)

    coverage = (
        rows.groupby(["attack", "attack_family", "boundary"], sort=True)
        .agg(
            n_cells=("split_seed", "size"),
            circuit_provenance_detection_rate=("circuit_hash_changed", "mean"),
            kernel_provenance_detection_rate=("kernel_hash_changed", "mean"),
            semantic_kernel_detection_rate=("semantic_kernel_detected", "mean"),
            algebraic_kernel_detection_rate=("algebraic_kernel_detected", "mean"),
            repeated_estimation_detection_rate=("repeated_estimation_detected", "mean"),
            output_change_rate=("model_output_detected", "mean"),
            mean_bal_acc_drop=("bal_acc_drop", "mean"),
            max_bal_acc_drop=("bal_acc_drop", "max"),
        )
        .reset_index()
    )
    return summary, coverage


def _acceptance_checks(rows: pd.DataFrame) -> dict[str, bool]:
    by_attack = {name: rows[rows["attack"] == name] for name in ATTACK_NAMES}
    tolerance = 1e-10
    checks = {
        "complete_design": len(rows) == 5 * 3 * len(ATTACK_NAMES),
        "clean_contract": bool(
            (by_attack["clean"]["kernel_max_abs_delta"] <= tolerance).all()
            and (~by_attack["clean"]["circuit_hash_changed"]).all()
            and (by_attack["clean"]["prediction_disagreement"] == 0.0).all()
        ),
        "transpile_hash_changes_semantics_preserved": bool(
            by_attack["benign_transpile_o1"]["circuit_hash_changed"].all()
            and (by_attack["benign_transpile_o1"]["kernel_max_abs_delta"] <= tolerance).all()
        ),
        "common_unitary_hash_changes_kernel_preserved": bool(
            by_attack["common_unitary_x"]["circuit_hash_changed"].all()
            and (by_attack["common_unitary_x"]["kernel_max_abs_delta"] <= tolerance).all()
        ),
        "parameterized_mutations_change_kernel": bool(
            (by_attack["parameterized_rz_alpha_0.020"]["kernel_max_abs_delta"] > tolerance).all()
            and (by_attack["parameterized_rz_alpha_0.100"]["kernel_max_abs_delta"] > tolerance).all()
            and (by_attack["feature_map_reps_2"]["kernel_max_abs_delta"] > tolerance).all()
        ),
        "asymmetry_sensor_detects": bool(
            by_attack["kernel_asymmetric_delta_0.020"]["algebraic_kernel_detected"].all()
        ),
        "diagonal_sensor_detects": bool(
            by_attack["kernel_diagonal_erosion_0.020"]["algebraic_kernel_detected"].all()
        ),
        "psd_preserving_attack_is_algebraically_blind": bool(
            (~by_attack["kernel_psd_preserving_mix_0.050"]["algebraic_kernel_detected"]).all()
            and by_attack["kernel_psd_preserving_mix_0.050"]["kernel_hash_changed"].all()
        ),
        "shot_repeats_disagree": bool(
            by_attack["shot_emulator_256"]["repeated_estimation_detected"].all()
            and by_attack["shot_emulator_1024"]["repeated_estimation_detected"].all()
        ),
    }
    return checks


def build(config: GateConfig) -> None:
    rows: list[dict[str, object]] = []
    for split_seed in config.split_seeds:
        for dimension in config.dimensions:
            x_train, y_train, x_test, y_test = _load_cell(config, split_seed, dimension)
            base_feature_map = _make_feature_map(
                int(dimension),
                QuantumCfg(
                    feature_map=config.feature_map,
                    reps=int(config.reps),
                    backend_method="exact_statevector",
                    seed=int(config.model_seed),
                ),
            )
            base_train, base_test = _kernel_blocks(base_feature_map, x_train, x_test)
            _, base_predictions, _, base_metrics = _evaluate_model(
                base_train, base_test, y_train, y_test
            )
            base_circuit_hash = _circuit_hash(base_feature_map)
            base_kernel_hash = _array_hash(base_train) + ":" + _array_hash(base_test)
            base_depth, base_ops = _primitive_profile(base_feature_map)

            for attack in ATTACK_NAMES:
                rng = np.random.default_rng(_stable_seed(split_seed, dimension, attack))
                (
                    train_kernel,
                    test_kernel,
                    attacked_circuit,
                    repeat_discrepancy,
                    family,
                    boundary,
                    shots,
                ) = _attack_kernels(
                    attack,
                    base_feature_map,
                    base_train,
                    base_test,
                    x_train,
                    x_test,
                    rng,
                    split_seed,
                    dimension,
                )

                _, predictions, _, metrics = _evaluate_model(
                    train_kernel, test_kernel, y_train, y_test
                )
                repaired_train = _nearest_psd(train_kernel)
                _, repaired_predictions, _, repaired_metrics = _evaluate_model(
                    repaired_train, test_kernel, y_train, y_test
                )

                attacked_hash = _circuit_hash(attacked_circuit)
                attacked_kernel_hash = _array_hash(train_kernel) + ":" + _array_hash(test_kernel)
                attacked_depth, attacked_ops = _primitive_profile(attacked_circuit)
                signals = _algebraic_signals(train_kernel)
                train_delta = float(np.max(np.abs(train_kernel - base_train)))
                test_delta = float(np.max(np.abs(test_kernel - base_test)))
                max_delta = max(train_delta, test_delta)
                pred_disagreement = float(np.mean(predictions != base_predictions))
                repaired_disagreement = float(np.mean(repaired_predictions != base_predictions))
                algebraic_detected = bool(
                    signals["kernel_symmetry_residual"] > 1e-8
                    or signals["kernel_diagonal_residual"] > 1e-8
                    or signals["kernel_min_eigenvalue"] < -1e-8
                )

                rows.append(
                    {
                        "split_seed": int(split_seed),
                        "model_seed": int(config.model_seed),
                        "svd_dim": int(dimension),
                        "n_train": int(len(y_train)),
                        "n_test": int(len(y_test)),
                        "attack": attack,
                        "attack_family": family,
                        "boundary": boundary,
                        "shots": shots,
                        "circuit_hash_changed": bool(attacked_hash != base_circuit_hash),
                        "circuit_depth_delta": int(attacked_depth - base_depth),
                        "circuit_op_count_l1": _op_count_l1(base_ops, attacked_ops),
                        "kernel_hash_changed": bool(attacked_kernel_hash != base_kernel_hash),
                        "kernel_max_abs_delta_train": train_delta,
                        "kernel_max_abs_delta_test": test_delta,
                        "kernel_max_abs_delta": max_delta,
                        **signals,
                        "repeated_estimation_discrepancy": float(repeat_discrepancy),
                        "prediction_disagreement": pred_disagreement,
                        "bal_acc": metrics["bal_acc"],
                        "bal_acc_clean": base_metrics["bal_acc"],
                        "bal_acc_drop": float(base_metrics["bal_acc"] - metrics["bal_acc"]),
                        "f1_pos": metrics["f1_pos"],
                        "roc_auc": metrics["roc_auc"],
                        "repair_bal_acc": repaired_metrics["bal_acc"],
                        "repair_bal_acc_drop": float(
                            base_metrics["bal_acc"] - repaired_metrics["bal_acc"]
                        ),
                        "repair_prediction_disagreement": repaired_disagreement,
                        "semantic_kernel_detected": bool(max_delta > 1e-8),
                        "algebraic_kernel_detected": algebraic_detected,
                        "repeated_estimation_detected": bool(repeat_discrepancy > 1e-8),
                        "model_output_detected": bool(pred_disagreement > 0.0),
                    }
                )

    frame = pd.DataFrame.from_records(rows).sort_values(
        ["svd_dim", "split_seed", "attack"]
    )
    checks = _acceptance_checks(frame)
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"Quantum-integrity gate failed acceptance checks: {failed}")

    summary, coverage = _summaries(frame)
    config.out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "quantum_integrity_gate_observations.csv": frame,
        "quantum_integrity_gate_clustered_summary.csv": summary,
        "quantum_integrity_gate_sensor_coverage.csv": coverage,
    }
    for name, table in outputs.items():
        table.to_csv(config.out_dir / name, index=False)

    manifest = {
        "analysis": "paper15_q1_quantum_integrity_gate",
        "status": "complete",
        "scope": "ideal-statevector circuits plus binomial finite-shot estimator emulator; no QPU",
        "config": {**asdict(config), "data": config.data.as_posix(), "out_dir": config.out_dir.as_posix()},
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "qiskit": qiskit.__version__,
            "qiskit_machine_learning": qiskit_machine_learning.__version__,
        },
        "input": {
            "path": config.data.as_posix(),
            "bytes": config.data.stat().st_size,
            "sha256": _sha256(config.data),
        },
        "acceptance_checks": checks,
        "outputs": {
            name: {"rows": int(len(table)), "sha256": _sha256(config.out_dir / name)}
            for name, table in outputs.items()
        },
    }
    manifest_path = config.out_dir / "quantum_integrity_gate_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"rows": len(frame), "acceptance_checks": checks}, indent=2))
    print(f"Wrote {len(outputs)} tables and manifest to {config.out_dir}")


def _parse_ints(value: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in value.split(",") if item.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/cicids_subset.csv"))
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/paper_digest/paper15_q1_quantum_integrity_gate"),
    )
    parser.add_argument("--split-seeds", type=str, default="42,43,44,45,46")
    parser.add_argument("--dimensions", type=str, default="4,6,8")
    parser.add_argument("--max-train", type=int, default=64)
    parser.add_argument("--max-test", type=int, default=64)
    args = parser.parse_args()
    build(
        GateConfig(
            data=args.data,
            out_dir=args.out_dir,
            split_seeds=_parse_ints(args.split_seeds),
            dimensions=_parse_ints(args.dimensions),
            max_train=int(args.max_train),
            max_test=int(args.max_test),
        )
    )


if __name__ == "__main__":
    main()
