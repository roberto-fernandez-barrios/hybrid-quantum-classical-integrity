"""Fail-closed verification of the Paper 1.5 publication evidence.

The verifier checks the SHA-256/row contracts embedded in every evidence
manifest and independently recomputes the manuscript's central count claims.
It intentionally does not treat unavailable raw-source hashes as failures when
run against the compact publication artifact; those raw inputs are covered by
the builders' original manifests and can be replayed from the documented public
datasets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


TOL = 1e-12
EXPECTED_MANIFESTS = 5  # gate1, expansion, quantum_integrity, hsaas, reinforcement (1.1.0)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _csv_rows(path: Path) -> int:
    with path.open("rb") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def verify_embedded_manifests(root: Path) -> dict[str, int]:
    manifests = sorted(root.rglob("*_manifest.json"))
    if len(manifests) != EXPECTED_MANIFESTS:
        raise ValueError(
            f"expected {EXPECTED_MANIFESTS} evidence manifests under {root}, found {len(manifests)}"
        )

    checked_outputs = 0
    for manifest_path in manifests:
        payload: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
        if payload.get("status", "complete") != "complete":
            raise ValueError(f"incomplete evidence manifest: {manifest_path}")
        checks = payload.get("acceptance_checks", {})
        failed = [name for name, passed in checks.items() if passed is not True]
        if failed:
            raise ValueError(f"failed acceptance checks in {manifest_path}: {failed}")

        for name, expected in payload.get("outputs", {}).items():
            output_path = manifest_path.parent / name
            if not output_path.is_file():
                raise FileNotFoundError(f"manifested output missing: {output_path}")
            observed_hash = _sha256(output_path)
            if observed_hash != expected["sha256"]:
                raise ValueError(f"SHA-256 mismatch: {output_path}")
            if output_path.suffix.lower() == ".csv":
                observed_rows = _csv_rows(output_path)
                if observed_rows != int(expected["rows"]):
                    raise ValueError(
                        f"row-count mismatch: {output_path}: {observed_rows} != {expected['rows']}"
                    )
            checked_outputs += 1
    return {"manifests": len(manifests), "manifested_outputs": checked_outputs}


def _assert_zero(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    maximum = frame[columns].astype(float).abs().to_numpy().max(initial=0.0)
    if maximum > TOL:
        raise ValueError(f"{label} is not invariant; max absolute response={maximum}")


def _verify_label_claims(path: Path, expected_total: int, expected_positive: int) -> None:
    frame = pd.read_csv(path, low_memory=False)
    label_side = frame[frame["attack_family"] == "target_shift"].copy()
    if len(label_side) != expected_total:
        raise ValueError(f"{path.name}: expected {expected_total} label rows, found {len(label_side)}")

    feature_prediction = [
        "integrity_jsd_vs_clean_eval",
        "integrity_mmd_vs_clean_eval",
        "integrity_ks_reject05_vs_clean_eval",
        "integrity_score_jsd_vs_clean_eval",
        "integrity_pred_disagreement",
        "integrity_pred_jsd",
    ]
    _assert_zero(label_side, feature_prediction, f"{path.name} feature/prediction evidence")

    prior = label_side[label_side["attack"].str.contains("prior_preserving", regex=False)]
    if len(prior) != expected_total // 2:
        raise ValueError(f"{path.name}: unexpected prior-preserving count {len(prior)}")
    _assert_zero(
        prior,
        ["integrity_label_prior_shift", "integrity_label_jsd"],
        f"{path.name} label-marginal evidence",
    )

    impact = label_side["impact_bal_acc"].astype(float)
    if int((impact > TOL).sum()) != expected_positive:
        raise ValueError(f"{path.name}: positive-impact count changed")
    if bool((impact < -TOL).any()):
        raise ValueError(f"{path.name}: negative label-side impact observed")

    positive = label_side[impact > TOL]
    joint = positive[
        ["integrity_confusion_profile_l1_delta", "integrity_confusion_profile_jsd_delta"]
    ].astype(float).abs().max(axis=1)
    if bool((joint <= TOL).any()):
        raise ValueError(f"{path.name}: a positive-impact label cell lacks joint-outcome evidence")


def verify_claims(root: Path) -> dict[str, int]:
    gate1 = next(root.rglob("gate1_unique_observations.csv"), None)
    expansion = next(root.rglob("expansion_unique_observations.csv"), None)
    if gate1 is None or expansion is None:
        raise FileNotFoundError("unique-observation tables required for independent claim verification")
    _verify_label_claims(gate1, expected_total=1440, expected_positive=1276)
    _verify_label_claims(expansion, expected_total=3600, expected_positive=2184)
    return {
        "gate1_label_rows": 1440,
        "gate1_positive_impact": 1276,
        "expansion_label_rows": 3600,
        "expansion_positive_impact": 2184,
    }


def verify_reinforcement_claims(root: Path) -> dict[str, int]:
    """Recompute the calibrated label-path consistency claims of artifact 1.1.0.

    The null-calibrated feature and feature-plus-prediction regimes must never
    fire on an evaluation-label intervention (Propositions 1--2 survive
    calibration), and the label-marginal regime must never fire on a
    prior-preserving intervention. The false-alarm table must exist and report
    the prespecified nominal level.
    """
    summary_path = next(root.rglob("calibrated_label_path_summary.csv"), None)
    fpr_path = next(root.rglob("null_evaluation_false_alarm_overall.csv"), None)
    thresholds_path = next(root.rglob("null_calibration_thresholds.csv"), None)
    if summary_path is None or fpr_path is None or thresholds_path is None:
        raise FileNotFoundError("reinforcement evidence tables required for claim verification")

    summary = pd.read_csv(summary_path)
    label_all = summary[summary["subset"] == "all_label_interventions"].set_index("regime")
    prior = summary[summary["subset"] == "prior_preserving_label_interventions"].set_index("regime")
    for regime in ("I_X", "I_XF"):
        if int(label_all.loc[regime, "n_fire"]) != 0:
            raise ValueError(f"calibrated {regime} regime fired on an evaluation-label intervention")
    if int(prior.loc["I_Ym", "n_fire"]) != 0:
        raise ValueError("calibrated label-marginal regime fired on a prior-preserving intervention")

    thresholds = pd.read_csv(thresholds_path)
    calibrated = thresholds[thresholds["order_statistic_rank"] > 0]
    if not (calibrated["alpha"].astype(float) == 0.05).all():
        raise ValueError("null-calibration nominal level changed from 0.05")
    if not (calibrated["n_cal"].astype(int) == 200).all():
        raise ValueError("null-calibration draw count changed from 200 per cell")

    fpr = pd.read_csv(fpr_path)
    return {
        "reinforcement_label_rows": int(label_all.loc["I_XF", "n"]),
        "reinforcement_calibrated_cells": int(len(calibrated) // calibrated["sensor"].nunique()),
        "reinforcement_fpr_rows": int(len(fpr)),
    }


def verify_release_hashes(root: Path) -> int:
    manifest = root / "ARTIFACT_MANIFEST.sha256"
    if not manifest.exists():
        return 0
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = root / Path(relative)
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError(f"release-manifest mismatch: {relative}")
        checked += 1
    return checked


def verify(root: Path) -> dict[str, int]:
    root = root.resolve()
    result = verify_embedded_manifests(root)
    result.update(verify_claims(root))
    result.update(verify_reinforcement_claims(root))
    result["release_files"] = verify_release_hashes(root)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("results/paper_digest"),
        help="Evidence root or publication artifact root",
    )
    args = parser.parse_args()
    print(json.dumps(verify(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
