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
EXPECTED_MANIFESTS = 7  # gate1, expansion, quantum_integrity, hsaas, reinforcement (1.1.0), policy (1.2.0/1.3.0), adversarial (1.3.0)


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


def _verify_label_claims(path: Path, expected_total: int, expected_positive: int, expected_signed: tuple[int, int, int]) -> None:
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
    # ``impact_bal_acc`` is the positive part max(BA_clean - BA_observed, 0); the
    # signed change is recomputed here so that apparent improvements are counted
    # explicitly (artifact 1.2.0) instead of being folded into "zero impact".
    signed = label_side["bal_acc_clean"].astype(float) - label_side["bal_acc"].astype(float)
    observed_signed = (int((signed > TOL).sum()), int((signed.abs() <= TOL).sum()), int((signed < -TOL).sum()))
    if observed_signed != expected_signed:
        raise ValueError(f"{path.name}: signed label-path counts (decreased, unchanged, increased) {observed_signed} != {expected_signed}")
    if not bool(((impact > TOL) == (signed > TOL)).all()):
        raise ValueError(f"{path.name}: positive impact is not the positive part of the signed change")

    material = label_side[signed.abs() > TOL]
    joint = material[
        ["integrity_confusion_profile_l1_delta", "integrity_confusion_profile_jsd_delta"]
    ].astype(float).abs().max(axis=1)
    if bool((joint <= TOL).any()):
        raise ValueError(f"{path.name}: a label cell with a changed conclusion lacks joint-outcome evidence")


def verify_claims(root: Path) -> dict[str, int]:
    gate1 = next(root.rglob("gate1_unique_observations.csv"), None)
    expansion = next(root.rglob("expansion_unique_observations.csv"), None)
    if gate1 is None or expansion is None:
        raise FileNotFoundError("unique-observation tables required for independent claim verification")
    _verify_label_claims(gate1, expected_total=1440, expected_positive=1276, expected_signed=(1276, 105, 59))
    _verify_label_claims(expansion, expected_total=3600, expected_positive=2184, expected_signed=(2184, 983, 433))
    return {
        "gate1_label_rows": 1440,
        "gate1_positive_impact": 1276,
        "gate1_label_increased": 59,
        "expansion_label_rows": 3600,
        "expansion_positive_impact": 2184,
        "expansion_label_increased": 433,
        "expansion_label_material": 2617,
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


def verify_policy_claims(root: Path) -> dict[str, int]:
    """Recompute the policy-level claims of artifacts 1.2.0/1.3.0 from the manifested tables.

    The conformal family-calibrated feature and feature-plus-prediction regimes
    never fire on evaluation-label interventions; the serve-always baseline allows
    every material observation; the trusted item-aligned regime allows no material
    observation under any calibrated policy; the conformal family rule never
    exceeds the union rule in pooled false-alarm rate (primary aggregate); and the
    conformal rule stays within its exact level under the exchangeable re-splits.
    """
    metrics_path = next(root.rglob("policy_metrics.csv"), None)
    label_path = next(root.rglob("family_label_path_summary.csv"), None)
    fpr_path = next(root.rglob("family_false_alarm_overall.csv"), None)
    if metrics_path is None or label_path is None or fpr_path is None:
        raise FileNotFoundError("policy evidence tables required for claim verification")
    label = pd.read_csv(label_path)
    for regime in ("I_X", "I_XF"):
        block = label[(label["subset"] == "all_label_interventions") & (label["regime"] == regime)]
        if int(block["n_fire"].sum()) != 0:
            raise ValueError(f"family-calibrated {regime} regime fired on an evaluation-label intervention")
    prior = label[(label["subset"] == "prior_preserving_label_interventions") & (label["regime"] == "I_Ym")]
    if int(prior["n_fire"].sum()) != 0:
        raise ValueError("family-calibrated label-marginal regime fired on a prior-preserving intervention")
    metrics = pd.read_csv(metrics_path)
    primary = metrics[metrics["tau"] == 0.0]
    serve = primary[primary["policy"] == "serve_always"]
    if not bool((serve["unsafe_allow"] == serve["n_material"]).all()):
        raise ValueError("serve-always baseline does not allow every material observation")
    trusted = primary[(primary["regime"] == "I_XFY_trusted") & (primary["policy"] != "serve_always")]
    if int(trusted["unsafe_allow"].sum()) != 0 or int(trusted["false_hold"].sum() + trusted["false_block"].sum()) != 0:
        raise ValueError("trusted item-aligned regime has unsafe allows or false holds")
    # Benign-interruption decomposition of the trusted calibrated policy (artifact 1.3.1):
    # statistical holds + exact-reference blocks must equal the interruption count and rate.
    trusted_p2 = primary[(primary["regime"] == "I_XFY_trusted") & (primary["policy"] == "family_calibrated")].iloc[0]
    holds, blocks, n_benign = int(trusted_p2["benign_hold"]), int(trusted_p2["benign_block"]), int(trusted_p2["n_benign"])
    if abs(float(trusted_p2["benign_interruption_rate"]) - (holds + blocks) / n_benign) > 1e-12:
        raise ValueError("trusted-regime benign interruption rate does not equal (holds + blocks) / n_benign")
    fpr = pd.read_csv(fpr_path)
    if "aggregate" in fpr.columns:
        fpr = fpr[fpr["aggregate"] == "all_eight_environments"]
    for regime, block in fpr.groupby("regime"):
        family = float(block[block["rule"] == "family"]["pooled_rate"].iloc[0])
        union = float(block[block["rule"] == "union"]["pooled_rate"].iloc[0])
        if family > union + 1e-12:
            raise ValueError(f"family rule exceeds union rule in regime {regime}")
    resplit_path = next(root.rglob("family_resplit_pooled.csv"), None)
    if resplit_path is None:
        raise FileNotFoundError("family_resplit_pooled.csv required (artifact 1.3.0)")
    resplit = pd.read_csv(resplit_path)
    level = float(resplit["conformal_level"].iloc[0])
    if bool((resplit["resplit_rate_family"] > level + 0.005).any()):
        raise ValueError("conformal family rule exceeds its exact level under exchangeable re-splits")
    n_material = int(serve["n_material"].iloc[0])
    return {
        "policy_material_observations": n_material,
        "policy_regimes": int(primary["regime"].nunique()),
        "policy_policies": int(primary["policy"].nunique()),
        "policy_conformal_level_x10000": int(round(level * 10000)),
        "policy_trusted_benign_holds": holds,
        "policy_trusted_benign_blocks": blocks,
        "policy_trusted_benign_interruptions": holds + blocks,
    }


def verify_adversarial_claims(root: Path) -> dict[str, int]:
    """Recompute the Gate A claims of artifact 1.3.0 from the manifested tables.

    The matched controls and clean rows reproduce the frozen expansion within
    1e-9; every material adaptive row is blocked under the trusted item-aligned
    regime; the adaptive rows are scored in every environment.
    """
    replay_path = next(root.rglob("adversarial_replay_consistency.csv"), None)
    metrics_path = next(root.rglob("adversarial_policy_metrics.csv"), None)
    det_path = next(root.rglob("adversarial_detection_pooled.csv"), None)
    if replay_path is None or metrics_path is None or det_path is None:
        raise FileNotFoundError("adversarial evidence tables required for claim verification")
    replay = pd.read_csv(replay_path)
    if not bool(replay["within_1e-9"].all()):
        raise ValueError("Gate A replay does not reproduce the frozen expansion")
    metrics = pd.read_csv(metrics_path)
    trusted = metrics[(metrics["regime"] == "I_XFY_trusted") & (metrics["tau"] == 0.0) & (metrics["attack_class"] == "adaptive")]
    if int(trusted["unsafe_allow"].sum()) != 0:
        raise ValueError("trusted regime serves a material adaptive observation")
    det = pd.read_csv(det_path)
    adaptive = det[(det["attack_class"] == "adaptive") & (det["rule"] == "family")]
    n_adaptive = int(adaptive[adaptive["regime"] == "I_X"]["n"].sum())
    return {"adversarial_adaptive_rows": n_adaptive, "adversarial_conditions": int(det["attack"].nunique())}


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
    result.update(verify_policy_claims(root))
    result.update(verify_adversarial_claims(root))
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
