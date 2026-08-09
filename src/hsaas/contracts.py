"""Layered integrity contracts for a hybrid quantum-classical service.

The module is deliberately transport-agnostic: the same envelope can be
returned by a CLI, an HTTP endpoint, or a batch job.  It creates a tamper-
evident hash chain, not an authenticated digital signature.  Provider identity
and signatures belong to the operational ATHENA gate.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from typing import Any

import numpy as np
from sklearn.metrics import balanced_accuracy_score


CONTRACT_VERSION = "athena-aegis-contract/0.1"
ZERO_HASH = "0" * 64


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def array_bundle_sha256(values: Mapping[str, np.ndarray]) -> str:
    return canonical_sha256({name: array_sha256(value) for name, value in values.items()})


def kernel_algebraic_evidence(kernel: np.ndarray) -> dict[str, float]:
    value = np.asarray(kernel, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"Training kernel must be square, got {value.shape}")
    symmetric = 0.5 * (value + value.T)
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    repaired = (eigenvectors @ np.diag(np.maximum(eigenvalues, 0.0)) @ eigenvectors.T).real
    denominator = max(float(np.linalg.norm(value, ord="fro")), np.finfo(float).eps)
    return {
        "symmetry_residual": float(np.max(np.abs(value - value.T))),
        "diagonal_residual": float(np.max(np.abs(np.diag(value) - 1.0))),
        "minimum_eigenvalue": float(eigenvalues.min()),
        "psd_repair_relative_fro": float(np.linalg.norm(repaired - value, ord="fro") / denominator),
    }


def _kernel_delta(
    reference_train: np.ndarray,
    observed_train: np.ndarray,
    reference_test: np.ndarray,
    observed_test: np.ndarray,
) -> float:
    pairs = (
        (np.asarray(reference_train, dtype=float), np.asarray(observed_train, dtype=float)),
        (np.asarray(reference_test, dtype=float), np.asarray(observed_test, dtype=float)),
    )
    deltas: list[float] = []
    for reference, observed in pairs:
        if reference.shape != observed.shape:
            return math.inf
        deltas.append(float(np.max(np.abs(reference - observed))))
    return max(deltas)


def _contract_record(
    *,
    name: str,
    evidence: Mapping[str, Any],
    violations: list[str],
    reviews: list[str],
    previous_hash: str,
) -> dict[str, Any]:
    if violations:
        status = "fail"
    elif reviews:
        status = "review"
    else:
        status = "pass"
    record: dict[str, Any] = {
        "name": name,
        "status": status,
        "evidence": _jsonable(evidence),
        "violations": list(violations),
        "reviews": list(reviews),
        "previous_contract_sha256": previous_hash,
    }
    record["record_sha256"] = canonical_sha256(record)
    return record


def _reported_balanced_accuracy(
    reported_metrics: Mapping[str, Any],
    predictions: np.ndarray,
    labels: np.ndarray,
) -> tuple[float, float]:
    if "balanced_accuracy" not in reported_metrics:
        return math.nan, float(balanced_accuracy_score(labels, predictions))
    reported = float(reported_metrics["balanced_accuracy"])
    recomputed = float(balanced_accuracy_score(labels, predictions))
    return reported, recomputed


def audit_hybrid_run(
    *,
    scenario: str,
    reference_inputs: Mapping[str, np.ndarray],
    observed_inputs: Mapping[str, np.ndarray],
    reference_preprocessing: Mapping[str, Any],
    observed_preprocessing: Mapping[str, Any],
    reference_circuit_sha256: str,
    observed_circuit_sha256: str,
    reference_train_kernel: np.ndarray,
    observed_train_kernel: np.ndarray,
    reference_test_kernel: np.ndarray,
    observed_test_kernel: np.ndarray,
    expected_execution: Mapping[str, Any],
    observed_execution: Mapping[str, Any],
    repeated_estimation_discrepancy: float,
    reference_predictions: np.ndarray,
    observed_predictions: np.ndarray,
    reference_labels: np.ndarray,
    observed_labels: np.ndarray,
    reported_metrics: Mapping[str, Any],
    approved_circuit_rewrite: bool = False,
    approved_stochastic_estimation: bool = False,
    semantic_tolerance: float = 1e-10,
    algebraic_tolerance: float = 1e-10,
    repeated_estimation_limit: float = 0.20,
    report_tolerance: float = 1e-12,
) -> dict[str, Any]:
    """Evaluate four ordered contracts and return a hash-chained envelope.

    ``pass`` is the only serveable outcome. ``review`` maps to a fail-closed
    hold and ``fail`` maps to a block. Semantic-equivalence and stochastic
    estimation must be approved explicitly; neither is inferred from hashes.
    """

    if semantic_tolerance < 0 or algebraic_tolerance < 0:
        raise ValueError("Tolerances must be non-negative")
    if repeated_estimation_limit < 0 or report_tolerance < 0:
        raise ValueError("Tolerances must be non-negative")

    reference_predictions = np.asarray(reference_predictions, dtype=int).reshape(-1)
    observed_predictions = np.asarray(observed_predictions, dtype=int).reshape(-1)
    reference_labels = np.asarray(reference_labels, dtype=int).reshape(-1)
    observed_labels = np.asarray(observed_labels, dtype=int).reshape(-1)
    if observed_predictions.shape != observed_labels.shape:
        raise ValueError("Observed predictions and labels must have equal length")
    if reference_predictions.shape != reference_labels.shape:
        raise ValueError("Reference predictions and labels must have equal length")

    contracts: list[dict[str, Any]] = []
    previous_hash = ZERO_HASH

    reference_input_hash = array_bundle_sha256(reference_inputs)
    observed_input_hash = array_bundle_sha256(observed_inputs)
    reference_preprocessing_hash = canonical_sha256(reference_preprocessing)
    observed_preprocessing_hash = canonical_sha256(observed_preprocessing)
    input_violations: list[str] = []
    if reference_input_hash != observed_input_hash:
        input_violations.append("input_provenance_mismatch")
    if reference_preprocessing_hash != observed_preprocessing_hash:
        input_violations.append("preprocessing_contract_mismatch")
    record = _contract_record(
        name="input_preprocessing",
        evidence={
            "reference_input_sha256": reference_input_hash,
            "observed_input_sha256": observed_input_hash,
            "reference_preprocessing_sha256": reference_preprocessing_hash,
            "observed_preprocessing_sha256": observed_preprocessing_hash,
        },
        violations=input_violations,
        reviews=[],
        previous_hash=previous_hash,
    )
    contracts.append(record)
    previous_hash = record["record_sha256"]

    kernel_delta = _kernel_delta(
        reference_train_kernel,
        observed_train_kernel,
        reference_test_kernel,
        observed_test_kernel,
    )
    algebra = kernel_algebraic_evidence(observed_train_kernel)
    reference_kernel_hash = array_bundle_sha256(
        {"train": reference_train_kernel, "test": reference_test_kernel}
    )
    observed_kernel_hash = array_bundle_sha256(
        {"train": observed_train_kernel, "test": observed_test_kernel}
    )
    circuit_changed = reference_circuit_sha256 != observed_circuit_sha256
    circuit_violations: list[str] = []
    circuit_reviews: list[str] = []
    if circuit_changed and not approved_circuit_rewrite:
        circuit_violations.append("unapproved_circuit_provenance_change")
    if circuit_changed and approved_circuit_rewrite and kernel_delta > semantic_tolerance:
        circuit_violations.append("approved_rewrite_failed_semantic_equivalence")
    if kernel_delta > semantic_tolerance:
        if approved_stochastic_estimation:
            circuit_reviews.append("stochastic_kernel_differs_from_exact_reference")
        else:
            circuit_violations.append("semantic_kernel_mismatch")

    algebraic_faults = []
    if algebra["symmetry_residual"] > algebraic_tolerance:
        algebraic_faults.append("kernel_symmetry_violation")
    if algebra["diagonal_residual"] > algebraic_tolerance:
        algebraic_faults.append("kernel_diagonal_violation")
    if algebra["minimum_eigenvalue"] < -algebraic_tolerance:
        algebraic_faults.append("kernel_psd_violation")
    if algebraic_faults and approved_stochastic_estimation:
        circuit_reviews.extend(algebraic_faults)
    else:
        circuit_violations.extend(algebraic_faults)

    record = _contract_record(
        name="circuit_kernel",
        evidence={
            "reference_circuit_sha256": reference_circuit_sha256,
            "observed_circuit_sha256": observed_circuit_sha256,
            "circuit_changed": circuit_changed,
            "approved_circuit_rewrite": approved_circuit_rewrite,
            "reference_kernel_sha256": reference_kernel_hash,
            "observed_kernel_sha256": observed_kernel_hash,
            "semantic_kernel_max_abs_delta": kernel_delta,
            "semantic_tolerance": semantic_tolerance,
            "algebraic": algebra,
        },
        violations=list(dict.fromkeys(circuit_violations)),
        reviews=list(dict.fromkeys(circuit_reviews)),
        previous_hash=previous_hash,
    )
    contracts.append(record)
    previous_hash = record["record_sha256"]

    execution_violations: list[str] = []
    execution_reviews: list[str] = []
    if canonical_sha256(expected_execution) != canonical_sha256(observed_execution):
        execution_violations.append("execution_metadata_mismatch")
    discrepancy = float(repeated_estimation_discrepancy)
    if approved_stochastic_estimation:
        if discrepancy > repeated_estimation_limit:
            execution_violations.append("repeated_estimation_limit_exceeded")
        else:
            execution_reviews.append("approved_stochastic_execution_requires_adjudication")
    elif discrepancy > semantic_tolerance:
        execution_violations.append("unexpected_repeated_estimation_discrepancy")

    prediction_disagreement = (
        float(np.mean(reference_predictions != observed_predictions))
        if reference_predictions.shape == observed_predictions.shape
        else 1.0
    )
    if kernel_delta <= semantic_tolerance and prediction_disagreement > 0 and not approved_stochastic_estimation:
        execution_violations.append("deterministic_output_mismatch")
    record = _contract_record(
        name="execution_result",
        evidence={
            "expected_execution_sha256": canonical_sha256(expected_execution),
            "observed_execution_sha256": canonical_sha256(observed_execution),
            "observed_execution": observed_execution,
            "approved_stochastic_estimation": approved_stochastic_estimation,
            "repeated_estimation_discrepancy": discrepancy,
            "repeated_estimation_limit": repeated_estimation_limit,
            "reference_prediction_sha256": array_sha256(reference_predictions),
            "observed_prediction_sha256": array_sha256(observed_predictions),
            "prediction_disagreement": prediction_disagreement,
        },
        violations=list(dict.fromkeys(execution_violations)),
        reviews=list(dict.fromkeys(execution_reviews)),
        previous_hash=previous_hash,
    )
    contracts.append(record)
    previous_hash = record["record_sha256"]

    label_changed = array_sha256(reference_labels) != array_sha256(observed_labels)
    prior_reference = float(np.mean(reference_labels == 1)) if reference_labels.size else math.nan
    prior_observed = float(np.mean(observed_labels == 1)) if observed_labels.size else math.nan
    reported_bal_acc, recomputed_bal_acc = _reported_balanced_accuracy(
        reported_metrics,
        observed_predictions,
        observed_labels,
    )
    evaluation_violations: list[str] = []
    if label_changed:
        evaluation_violations.append("label_provenance_mismatch")
    if not math.isfinite(reported_bal_acc):
        evaluation_violations.append("balanced_accuracy_missing_or_nonfinite")
    elif abs(reported_bal_acc - recomputed_bal_acc) > report_tolerance:
        evaluation_violations.append("reported_metric_mismatch")
    record = _contract_record(
        name="evaluation_report",
        evidence={
            "reference_label_sha256": array_sha256(reference_labels),
            "observed_label_sha256": array_sha256(observed_labels),
            "label_changed": label_changed,
            "reference_positive_rate": prior_reference,
            "observed_positive_rate": prior_observed,
            "label_prior_abs_delta": abs(prior_observed - prior_reference),
            "joint_outcome_sha256": array_bundle_sha256(
                {"labels": observed_labels, "predictions": observed_predictions}
            ),
            "reported_balanced_accuracy": reported_bal_acc,
            "recomputed_balanced_accuracy": recomputed_bal_acc,
            "report_tolerance": report_tolerance,
        },
        violations=evaluation_violations,
        reviews=[],
        previous_hash=previous_hash,
    )
    contracts.append(record)
    previous_hash = record["record_sha256"]

    statuses = [item["status"] for item in contracts]
    if "fail" in statuses:
        overall_status, action = "fail", "block"
    elif "review" in statuses:
        overall_status, action = "review", "hold"
    else:
        overall_status, action = "pass", "allow"

    envelope: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "scenario": str(scenario),
        "overall_status": overall_status,
        "fail_closed_action": action,
        "contracts": contracts,
        "chain_head_sha256": previous_hash,
        "scope": "research prototype; hash chain is tamper-evident but not provider-authenticated",
    }
    envelope["envelope_sha256"] = canonical_sha256(envelope)
    return envelope


def verify_audit_envelope(envelope: Mapping[str, Any]) -> bool:
    """Verify the contract hash chain and top-level envelope digest."""

    contracts = list(envelope.get("contracts", []))
    previous_hash = ZERO_HASH
    for raw in contracts:
        record = dict(raw)
        declared = record.pop("record_sha256", None)
        if record.get("previous_contract_sha256") != previous_hash:
            return False
        calculated = canonical_sha256(record)
        if declared != calculated:
            return False
        previous_hash = calculated
    if envelope.get("chain_head_sha256") != previous_hash:
        return False
    unsigned = dict(envelope)
    declared_envelope = unsigned.pop("envelope_sha256", None)
    return declared_envelope == canonical_sha256(unsigned)
