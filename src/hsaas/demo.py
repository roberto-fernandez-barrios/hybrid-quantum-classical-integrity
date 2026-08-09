"""Executable ATHENA-AEGIS HSaaS integrity-contract demonstrator.

The CLI runs one compact CICIDS quantum-kernel case and emits six service-like
audit envelopes: clean, approved transpilation, circuit mutation, valid-looking
kernel substitution, prior-preserving label corruption, and approved stochastic
fidelity estimation.  It is a local research prototype, not a network service
or a QPU execution.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import platform
from typing import Any

import numpy as np
import pandas as pd
import qiskit
import qiskit_machine_learning
import sklearn

from src.attacks.label_flip_prior_preserving import (
    LabelFlipPriorPreserving,
    LabelFlipPriorPreservingCfg,
)
from src.experiments.run_quantum_integrity_gate import (
    GateConfig,
    _attack_kernels,
    _circuit_hash,
    _evaluate_model,
    _kernel_blocks,
    _load_cell,
)
from src.hsaas.contracts import audit_hybrid_run, verify_audit_envelope
from src.qml.quantum_qsvc import QuantumCfg, _make_feature_map


@dataclass(frozen=True)
class DemoConfig:
    data: Path = Path("data/cicids_subset.csv")
    out_dir: Path = Path("results/paper_digest/paper15_hsaas_demo")
    split_seed: int = 42
    dimension: int = 4
    max_train: int = 32
    max_test: int = 32
    model_seed: int = 42
    repeated_estimation_limit: float = 0.20


SCENARIOS = (
    "clean",
    "approved_transpilation",
    "circuit_parameter_mutation",
    "kernel_psd_preserving_substitution",
    "label_prior_preserving_corruption",
    "approved_shot_emulator_256",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _contract(envelope: dict[str, Any], name: str) -> dict[str, Any]:
    return next(item for item in envelope["contracts"] if item["name"] == name)


def _scenario_attack_name(scenario: str) -> str:
    mapping = {
        "clean": "clean",
        "approved_transpilation": "benign_transpile_o1",
        "circuit_parameter_mutation": "parameterized_rz_alpha_0.100",
        "kernel_psd_preserving_substitution": "kernel_psd_preserving_mix_0.050",
        "label_prior_preserving_corruption": "clean",
        "approved_shot_emulator_256": "shot_emulator_256",
    }
    return mapping[scenario]


def _execution_metadata(config: DemoConfig, scenario: str) -> dict[str, Any]:
    if scenario == "approved_shot_emulator_256":
        return {
            "executor": "local_binomial_fidelity_emulator",
            "backend_class": "emulator",
            "shots": 256,
            "split_seed": int(config.split_seed),
            "model_seed": int(config.model_seed),
            "qpu": False,
        }
    return {
        "executor": "local_exact_statevector",
        "backend_class": "ideal_simulator",
        "shots": None,
        "split_seed": int(config.split_seed),
        "model_seed": int(config.model_seed),
        "qpu": False,
    }


def _summary_row(envelope: dict[str, Any]) -> dict[str, Any]:
    circuit = _contract(envelope, "circuit_kernel")
    execution = _contract(envelope, "execution_result")
    evaluation = _contract(envelope, "evaluation_report")
    return {
        "scenario": envelope["scenario"],
        "overall_status": envelope["overall_status"],
        "fail_closed_action": envelope["fail_closed_action"],
        "input_preprocessing_status": _contract(envelope, "input_preprocessing")["status"],
        "circuit_kernel_status": circuit["status"],
        "execution_result_status": execution["status"],
        "evaluation_report_status": evaluation["status"],
        "circuit_changed": bool(circuit["evidence"]["circuit_changed"]),
        "semantic_kernel_max_abs_delta": float(
            circuit["evidence"]["semantic_kernel_max_abs_delta"]
        ),
        "kernel_symmetry_residual": float(circuit["evidence"]["algebraic"]["symmetry_residual"]),
        "kernel_diagonal_residual": float(circuit["evidence"]["algebraic"]["diagonal_residual"]),
        "kernel_minimum_eigenvalue": float(circuit["evidence"]["algebraic"]["minimum_eigenvalue"]),
        "prediction_disagreement": float(execution["evidence"]["prediction_disagreement"]),
        "repeated_estimation_discrepancy": float(
            execution["evidence"]["repeated_estimation_discrepancy"]
        ),
        "label_changed": bool(evaluation["evidence"]["label_changed"]),
        "label_prior_abs_delta": float(evaluation["evidence"]["label_prior_abs_delta"]),
        "balanced_accuracy": float(evaluation["evidence"]["recomputed_balanced_accuracy"]),
        "envelope_sha256": envelope["envelope_sha256"],
    }


def build(config: DemoConfig) -> dict[str, Any]:
    config.out_dir.mkdir(parents=True, exist_ok=True)
    gate_config = GateConfig(
        data=config.data,
        out_dir=config.out_dir,
        split_seeds=(int(config.split_seed),),
        dimensions=(int(config.dimension),),
        max_train=int(config.max_train),
        max_test=int(config.max_test),
        model_seed=int(config.model_seed),
    )
    x_train, y_train, x_test, y_test = _load_cell(
        gate_config,
        int(config.split_seed),
        int(config.dimension),
    )
    feature_map = _make_feature_map(
        int(config.dimension),
        QuantumCfg(
            feature_map="zz",
            reps=1,
            backend_method="exact_statevector",
            seed=int(config.model_seed),
        ),
    )
    base_train, base_test = _kernel_blocks(feature_map, x_train, x_test)
    _, reference_predictions, _, reference_metrics = _evaluate_model(
        base_train,
        base_test,
        y_train,
        y_test,
    )
    reference_circuit_hash = _circuit_hash(feature_map)
    input_bundle = {"train": x_train, "test": x_test}
    preprocessing = {
        "dataset": str(config.data.as_posix()),
        "split_seed": int(config.split_seed),
        "svd_dimension": int(config.dimension),
        "scaler": "minmax_0_2pi_fit_on_train",
        "train_shape": list(x_train.shape),
        "test_shape": list(x_test.shape),
    }

    envelopes: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        attack_name = _scenario_attack_name(scenario)
        rng_seed = int.from_bytes(
            hashlib.sha256(
                f"{config.split_seed}|{config.dimension}|{scenario}".encode("utf-8")
            ).digest()[:4],
            "big",
        )
        observed_train, observed_test, observed_circuit, discrepancy, _, _, _ = _attack_kernels(
            attack_name,
            feature_map,
            base_train,
            base_test,
            x_train,
            x_test,
            np.random.default_rng(rng_seed),
            int(config.split_seed),
            int(config.dimension),
        )
        _, observed_predictions, _, observed_metrics = _evaluate_model(
            observed_train,
            observed_test,
            y_train,
            y_test,
        )
        observed_labels = y_test.copy()
        if scenario == "label_prior_preserving_corruption":
            label_attack = LabelFlipPriorPreserving(
                LabelFlipPriorPreservingCfg(r=0.25, min_pairs=1)
            )
            observed_labels = label_attack.apply(
                x_test,
                seed=rng_seed,
                y=y_test,
            ).y_att
            observed_metrics["bal_acc"] = float(
                sklearn.metrics.balanced_accuracy_score(observed_labels, observed_predictions)
            )

        execution = _execution_metadata(config, scenario)
        envelope = audit_hybrid_run(
            scenario=scenario,
            reference_inputs=input_bundle,
            observed_inputs=input_bundle,
            reference_preprocessing=preprocessing,
            observed_preprocessing=preprocessing,
            reference_circuit_sha256=reference_circuit_hash,
            observed_circuit_sha256=_circuit_hash(observed_circuit),
            reference_train_kernel=base_train,
            observed_train_kernel=observed_train,
            reference_test_kernel=base_test,
            observed_test_kernel=observed_test,
            expected_execution=execution,
            observed_execution=execution,
            repeated_estimation_discrepancy=float(discrepancy),
            reference_predictions=reference_predictions,
            observed_predictions=observed_predictions,
            reference_labels=y_test,
            observed_labels=observed_labels,
            reported_metrics={"balanced_accuracy": float(observed_metrics["bal_acc"])},
            approved_circuit_rewrite=scenario == "approved_transpilation",
            approved_stochastic_estimation=scenario == "approved_shot_emulator_256",
            repeated_estimation_limit=float(config.repeated_estimation_limit),
        )
        envelopes.append(envelope)
        summaries.append(_summary_row(envelope))

    by_scenario = {item["scenario"]: item for item in envelopes}
    psd_contract = _contract(by_scenario["kernel_psd_preserving_substitution"], "circuit_kernel")
    label_contract = _contract(by_scenario["label_prior_preserving_corruption"], "evaluation_report")
    shot_contract = _contract(by_scenario["approved_shot_emulator_256"], "execution_result")
    acceptance_checks = {
        "complete_design": len(envelopes) == len(SCENARIOS),
        "all_hash_chains_verify": all(verify_audit_envelope(item) for item in envelopes),
        "clean_allows": by_scenario["clean"]["fail_closed_action"] == "allow",
        "approved_transpilation_allows": (
            by_scenario["approved_transpilation"]["fail_closed_action"] == "allow"
        ),
        "circuit_mutation_blocks": (
            by_scenario["circuit_parameter_mutation"]["fail_closed_action"] == "block"
        ),
        "psd_preserving_substitution_blocks_despite_valid_algebra": (
            by_scenario["kernel_psd_preserving_substitution"]["fail_closed_action"] == "block"
            and psd_contract["evidence"]["algebraic"]["symmetry_residual"] <= 1e-10
            and psd_contract["evidence"]["algebraic"]["diagonal_residual"] <= 1e-10
            and psd_contract["evidence"]["algebraic"]["minimum_eigenvalue"] >= -1e-10
        ),
        "prior_preserving_label_corruption_blocks": (
            by_scenario["label_prior_preserving_corruption"]["fail_closed_action"] == "block"
            and label_contract["evidence"]["label_prior_abs_delta"] == 0.0
        ),
        "approved_stochastic_execution_holds_for_review": (
            by_scenario["approved_shot_emulator_256"]["fail_closed_action"] == "hold"
            and shot_contract["evidence"]["repeated_estimation_discrepancy"] > 0.0
        ),
    }

    observation_path = config.out_dir / "hsaas_audit_envelopes.jsonl"
    observation_path.write_text(
        "\n".join(json.dumps(item, sort_keys=True, allow_nan=False) for item in envelopes) + "\n",
        encoding="utf-8",
    )
    summary = pd.DataFrame.from_records(summaries)
    summary_path = config.out_dir / "hsaas_contract_summary.csv"
    summary.to_csv(summary_path, index=False)

    complete = all(bool(value) for value in acceptance_checks.values())
    manifest = {
        "analysis": "paper15_hsaas_integrity_contract_demo",
        "status": "complete" if complete else "failed",
        "scope": (
            "local research prototype over ideal-statevector and binomial-shot emulation; "
            "not an HTTP deployment, authenticated provider ledger, or QPU run"
        ),
        "contract_version": envelopes[0]["contract_version"],
        "config": {**asdict(config), "data": str(config.data), "out_dir": str(config.out_dir)},
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "qiskit": qiskit.__version__,
            "qiskit_machine_learning": qiskit_machine_learning.__version__,
        },
        "input": {
            "path": str(config.data),
            "bytes": config.data.stat().st_size,
            "sha256": _sha256(config.data),
        },
        "reference_metrics": reference_metrics,
        "acceptance_checks": acceptance_checks,
        "outputs": {
            observation_path.name: {"rows": len(envelopes), "sha256": _sha256(observation_path)},
            summary_path.name: {"rows": len(summary), "sha256": _sha256(summary_path)},
        },
    }
    manifest_path = config.out_dir / "hsaas_audit_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    if not complete:
        failed = [name for name, value in acceptance_checks.items() if not value]
        raise RuntimeError(f"HSaaS acceptance checks failed: {failed}")
    print(f"Wrote {len(envelopes)} audit envelopes and manifest to {config.out_dir}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/cicids_subset.csv"))
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/paper_digest/paper15_hsaas_demo"),
    )
    parser.add_argument("--split-seed", type=int, default=42)
    parser.add_argument("--dimension", type=int, default=4)
    parser.add_argument("--max-train", type=int, default=32)
    parser.add_argument("--max-test", type=int, default=32)
    parser.add_argument("--model-seed", type=int, default=42)
    parser.add_argument("--repeated-estimation-limit", type=float, default=0.20)
    args = parser.parse_args()
    build(DemoConfig(**vars(args)))


if __name__ == "__main__":
    main()
