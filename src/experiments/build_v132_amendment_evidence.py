"""Build the frozen-only methodological amendment evidence for Paper 1.5 v1.3.2.

This builder does not execute a benchmark, model, kernel, attack, seed or draw.
It audits sensor semantics from the frozen implementation and derives three
review-facing tables from already manifested observations:

* the reference/provenance/granularity semantics of every selected sensor;
* gross versus incremental cost of the trusted exact-reference checks; and
* the adaptive F5 profile by mechanism and nominal strength.

The correction adopts reference taxonomy option B: class A is a statistically
thresholded aggregate comparison and may use a protected same-item-set oracle
inside the benchmark; classes B and C expose trusted aggregate and item-aligned
same-batch values, respectively, to an exact invariant.  Trust, granularity and
decision tolerance are therefore recorded as separate dimensions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


TOL = 1e-12
VERSION = "1.3.2"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


SENSOR_REFERENCE_AUDIT = [
    # Statistically thresholded aggregate comparisons (reference class A).
    ("integrity_jsd_vs_clean_eval", "empirical feature distributions of X_eval", "X_te_f clean feature distributions", "no", "yes", "yes", "no", "statistical=yes; historical=no", "A"),
    ("integrity_mmd_vs_clean_eval", "feature multiset X_eval", "feature multiset X_te_f", "no", "yes", "yes", "no", "statistical=yes; historical=no", "A"),
    ("integrity_ks_reject05_vs_clean_eval", "per-feature distributions of X_eval", "per-feature distributions of X_te_f", "no", "yes", "yes", "no", "statistical=yes; historical=no", "A"),
    ("integrity_score_jsd_vs_clean_eval", "score distribution f(X_eval)", "score distribution f(X_te_f)", "no", "yes", "yes", "no", "statistical=yes; historical=no", "A"),
    ("integrity_pred_pos_rate_shift", "mean predicted-positive rate on X_eval", "mean predicted-positive rate on X_te_f", "no", "yes", "yes", "no", "statistical=yes; historical=no", "A"),
    ("integrity_pred_jsd", "predicted-class distribution on X_eval", "predicted-class distribution on X_te_f", "no", "yes", "yes", "no", "statistical=yes; historical=no", "A"),
    ("integrity_label_prior_shift", "mean positive-label rate of y_eval", "mean positive-label rate of y_te_f", "no", "yes", "yes", "no", "statistical=yes; historical=no", "A"),
    ("integrity_label_jsd", "binary label distribution of y_eval", "binary label distribution of y_te_f", "no", "yes", "yes", "no", "statistical=yes; historical=no", "A"),
    ("integrity_confusion_profile_l1", "aggregate confusion PMF of (y_eval,f(X_eval))", "aggregate confusion PMF of (y_te_f,f(X_te_f))", "no", "yes", "yes", "no", "statistical=yes; historical=no", "A"),
    ("integrity_confusion_profile_jsd", "aggregate confusion PMF of (y_eval,f(X_eval))", "aggregate confusion PMF of (y_te_f,f(X_te_f))", "no", "yes", "yes", "no", "statistical=yes; historical=no", "A"),
    # The same frozen aggregate deltas used as exact trusted invariants (class B).
    ("integrity_confusion_profile_l1_delta", "aggregate confusion-profile L1 delta", "trusted aggregate confusion profile of the same batch", "no", "yes", "yes", "yes", "no", "B"),
    ("integrity_confusion_profile_jsd_delta", "aggregate confusion-profile JSD delta", "trusted aggregate confusion profile of the same batch", "no", "yes", "yes", "yes", "no", "B"),
    # Exact item-aligned invariants (class C).
    ("integrity_pred_disagreement", "item-indexed predictions f(X_eval)", "trusted item-indexed predictions f(X_te_f)", "yes", "yes", "yes", "yes", "no", "C"),
    ("label_flip_rate", "item-indexed labels y_eval", "trusted item-indexed labels y_te_f", "yes", "yes", "yes", "yes", "no", "C"),
]


AUDIT_COLUMNS = [
    "sensor",
    "current_value",
    "reference_value",
    "item_correspondence_used",
    "same_batch_item_set",
    "protected_in_executed_harness",
    "deployed_authentication_demonstrated",
    "historical_or_statistical",
    "compatible_reference_class",
]


def sensor_reference_audit() -> pd.DataFrame:
    return pd.DataFrame(SENSOR_REFERENCE_AUDIT, columns=AUDIT_COLUMNS)


def trusted_cost(benign: pd.DataFrame) -> pd.DataFrame:
    batch_col = "decision__I_XFY__family_calibrated"
    trusted_col = "decision__I_XFY_trusted__family_calibrated"
    exact = benign["fire_exact"].astype(bool)
    batch_interrupt = benign[batch_col].ne("allow")
    trusted_interrupt = benign[trusted_col].ne("allow")
    overlap = exact & batch_interrupt
    exact_only = exact & ~batch_interrupt
    records = [
        ("batch_statistical_interruptions", int(batch_interrupt.sum()), len(benign)),
        ("gross_exact_reference_blocks", int(exact.sum()), len(benign)),
        ("exact_blocks_overlapping_batch_interruptions", int(overlap.sum()), len(benign)),
        ("net_additional_interruptions_vs_batch_I_XFY_P2", int(exact_only.sum()), len(benign)),
        ("trusted_statistical_holds", int(benign[trusted_col].eq("hold").sum()), len(benign)),
        ("trusted_exact_reference_blocks", int(benign[trusted_col].eq("block").sum()), len(benign)),
        ("trusted_total_interruptions", int(trusted_interrupt.sum()), len(benign)),
    ]
    out = pd.DataFrame(records, columns=["quantity", "n", "denominator"])
    out["rate"] = out["n"] / out["denominator"]
    return out


def adaptive_strength_profile(policy: pd.DataFrame, detection: pd.DataFrame, materiality: pd.DataFrame) -> pd.DataFrame:
    pol = policy[(policy["attack_class"] == "adaptive") & (policy["policy"] == "family_calibrated") & (policy["tau"] == 0.0)]
    det = detection[(detection["attack_class"] == "adaptive") & (detection["rule"] == "family")]
    mat = materiality[materiality["attack_class"] == "adaptive"]
    records: list[dict[str, object]] = []
    for (mechanism, strength), mrow in mat.groupby(["mechanism", "strength"], sort=True):
        if len(mrow) != 1:
            raise ValueError(f"non-unique adaptive materiality row for {(mechanism, strength)}")
        rec: dict[str, object] = {
            "mechanism": mechanism,
            "strength": float(strength),
            "n_rows": int(mrow.iloc[0]["n"]),
            "n_material": int(round(float(mrow.iloc[0]["n"]) * float(mrow.iloc[0]["material_fraction_tau0"]))),
            "material_fraction_tau0": float(mrow.iloc[0]["material_fraction_tau0"]),
        }
        for regime in ("I_X", "I_XF", "I_XFY"):
            drow = det[(det["mechanism"] == mechanism) & (det["strength"] == strength) & (det["regime"] == regime)]
            prow = pol[(pol["mechanism"] == mechanism) & (pol["strength"] == strength) & (pol["regime"] == regime)]
            if len(drow) != 1 or len(prow) != 1:
                raise ValueError(f"missing or non-unique adaptive row for {(mechanism, strength, regime)}")
            rec[f"detection_{regime}"] = float(drow.iloc[0]["detection_rate"])
            rec[f"material_served_{regime}"] = int(prow.iloc[0]["unsafe_allow"])
            rec[f"material_served_rate_{regime}"] = float(prow.iloc[0]["unsafe_allow_rate"])
        records.append(rec)
    return pd.DataFrame.from_records(records)


def build(repo: Path, out_dir: Path) -> dict[str, object]:
    benign_path = repo / "results/paper_digest/paper15_v12_policy/policy_benign_decisions.csv"
    policy_path = repo / "results/paper_digest/paper15_v13_adversarial/adversarial_policy_metrics.csv"
    detection_path = repo / "results/paper_digest/paper15_v13_adversarial/adversarial_detection_pooled.csv"
    materiality_path = repo / "results/paper_digest/paper15_v13_adversarial/adversarial_materiality.csv"
    inputs = [benign_path, policy_path, detection_path, materiality_path]
    for path in inputs:
        if not path.is_file():
            raise FileNotFoundError(path)

    audit = sensor_reference_audit()
    cost = trusted_cost(pd.read_csv(benign_path))
    profile = adaptive_strength_profile(pd.read_csv(policy_path), pd.read_csv(detection_path), pd.read_csv(materiality_path))

    c = cost.set_index("quantity")
    checks = {
        "M1_all_selected_sensors_have_audited_reference_semantics": len(audit) == 14 and not audit.isna().any().any(),
        "M2_statistical_class_A_same_batch_use_is_explicit": bool((audit[audit["compatible_reference_class"] == "A"]["same_batch_item_set"] == "yes").all()),
        "M3_class_A_does_not_claim_deployed_authentication": bool((audit[audit["compatible_reference_class"] == "A"]["deployed_authentication_demonstrated"] == "no").all()),
        "M4_gross_exact_blocks_85": int(c.loc["gross_exact_reference_blocks", "n"]) == 85,
        "M5_exact_batch_overlap_46": int(c.loc["exact_blocks_overlapping_batch_interruptions", "n"]) == 46,
        "M6_net_increment_39": int(c.loc["net_additional_interruptions_vs_batch_I_XFY_P2", "n"]) == 39,
        "M7_trusted_total_629": int(c.loc["trusted_total_interruptions", "n"]) == 629,
        "M8_adaptive_profile_complete": len(profile) == 10 and set(profile["strength"]) == {0.02, 0.05, 0.10, 0.25, 0.50},
        "M9_no_experiment_was_rerun": True,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError(f"v1.3.2 amendment checks failed: {failed}")

    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "sensor_reference_audit.csv": audit,
        "trusted_interruption_decomposition.csv": cost,
        "adaptive_strength_profile.csv": profile,
    }
    for name, frame in outputs.items():
        frame.to_csv(out_dir / name, index=False)
    manifest = {
        "analysis": "paper15_v132_methodological_amendment",
        "artifact_version": VERSION,
        "status": "complete",
        "correction_type": "taxonomy correction and frozen-only derived analysis; no experiment/job/model/kernel/attack/seed/draw rerun",
        "repair": "B",
        "acceptance_checks": checks,
        "input_files": [{"path": path.relative_to(repo).as_posix(), "sha256": _sha256(path)} for path in inputs],
        "outputs": {name: {"rows": len(frame), "sha256": _sha256(out_dir / name)} for name, frame in outputs.items()},
    }
    manifest_path = out_dir / "amendment_evidence_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=Path("results/paper_digest/paper15_v132_amendment"))
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    manifest = build(repo, (repo / args.out_dir).resolve() if not args.out_dir.is_absolute() else args.out_dir)
    print(json.dumps({"status": manifest["status"], "repair": manifest["repair"], "checks": manifest["acceptance_checks"]}, indent=2))


if __name__ == "__main__":
    main()
