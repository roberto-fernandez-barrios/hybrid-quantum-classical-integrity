"""Fail-closed verifier for the v1.3.5 geometry-aligned sensitivity evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

from src.experiments.build_v135_geometry_sensitivity import (
    OLD_EVIDENCE_FILES,
    OLD_EVIDENCE_TREE_SHA256,
    TEXT_SHA256_STRATEGY,
    canonical_lf_bytes,
    derive_outputs,
    old_evidence_tree,
)
from src.experiments.run_v135_geometry_sensitivity import (
    ALL_BATCH_SENSOR_COLUMNS,
    ATTACK_CURRENT_GEOMETRY,
    CALIBRATION_DRAW_TAG,
    CLEAN_CURRENT_GEOMETRY,
    GEOMETRY_ID,
    IDENTITY_TOL,
    PREREGISTRATION,
    REFERENCE_GEOMETRY,
    geometry_attack_specs,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


FROZEN_PREREGISTRATION_COMMIT = "62cec146689e3ff8cdb95027c7a9c7371ef767fd"


def _text_binding_matches(path: Path, expected_sha256: str, strategy: str | None = None) -> bool:
    """Match a text binding while treating only LF and CRLF as equivalent.

    Published v1.3.5 bindings predate the canonical strategy marker, so their
    raw digest is checked first and then both EOL representations are tried.
    No whitespace, character, numeric, BOM, or final-newline normalization is
    performed. Future manifests declare canonical-LF explicitly.
    """

    if not path.is_file() or not isinstance(expected_sha256, str):
        return False
    raw = path.read_bytes()
    raw_digest = hashlib.sha256(raw).hexdigest()
    if strategy is None and raw_digest == expected_sha256:
        return True
    try:
        canonical = canonical_lf_bytes(raw)
    except ValueError:
        return False
    if strategy == TEXT_SHA256_STRATEGY:
        return hashlib.sha256(canonical).hexdigest() == expected_sha256
    if strategy is not None:
        return False
    crlf = canonical.replace(b"\n", b"\r\n")
    return expected_sha256 in {
        hashlib.sha256(canonical).hexdigest(),
        hashlib.sha256(crlf).hexdigest(),
    }


def _preregistration_binding_checks(
    repo: Path,
    spec: dict[str, object],
    required_commit: str = FROZEN_PREREGISTRATION_COMMIT,
) -> dict[str, bool]:
    """Verify the manifest, path history, and frozen preregistration blob."""

    prereg = repo / PREREGISTRATION
    manifest_commit = str(spec.get("commit", ""))
    expected_sha256 = str(spec.get("sha256", ""))
    strategy = spec.get("sha256_strategy")
    strategy_value = str(strategy) if strategy is not None else None
    try:
        latest_commit = subprocess.check_output(
            ["git", "log", "-1", "--format=%H", "--", PREREGISTRATION],
            cwd=repo,
            text=True,
        ).strip()
        blob_id = subprocess.check_output(
            ["git", "rev-parse", f"{required_commit}:{PREREGISTRATION}"],
            cwd=repo,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        committed_blob = subprocess.check_output(
            ["git", "cat-file", "blob", blob_id], cwd=repo
        )
        current_canonical = canonical_lf_bytes(prereg.read_bytes())
        blob_canonical = canonical_lf_bytes(committed_blob)
    except (OSError, subprocess.CalledProcessError, ValueError):
        latest_commit = ""
        current_canonical = b""
        blob_canonical = b"not-available"

    return {
        "manifest_commit_exact": manifest_commit == required_commit,
        "latest_path_commit_exact": latest_commit == required_commit,
        "current_matches_frozen_blob_eol_only": current_canonical == blob_canonical,
        "manifest_text_hash_matches": _text_binding_matches(
            prereg, expected_sha256, strategy_value
        ),
    }


def verify(repo: Path, evidence_dir: Path) -> dict[str, bool]:
    root = repo / evidence_dir
    manifest_path = root / "geometry_sensitivity_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["manifest_status_complete"] = manifest.get("status") == "complete"
    checks["manifest_analysis_exact"] = manifest.get("analysis") == "paper15_v135_geometry_aligned_sensitivity"
    prereg_checks = _preregistration_binding_checks(repo, manifest["preregistration"])
    checks.update({f"preregistration_{name}": ok for name, ok in prereg_checks.items()})
    checks["preregistration_hash_and_commit"] = all(prereg_checks.values())
    count, tree_hash = old_evidence_tree(repo)
    checks["old_evidence_byte_identical"] = count == OLD_EVIDENCE_FILES and tree_hash == OLD_EVIDENCE_TREE_SHA256
    for name, spec in manifest.get("outputs", {}).items():
        path = root / name
        checks[f"output_{name}_present_hash_rows"] = (
            path.is_file()
            and _sha256(path) == spec["sha256"]
            and len(pd.read_csv(path, low_memory=False)) == int(spec["rows"])
        )
    presentation = repo / manifest["presentation_output"]["path"]
    checks["presentation_macro_hash"] = _text_binding_matches(
        presentation,
        manifest["presentation_output"]["sha256"],
        manifest["presentation_output"].get("sha256_strategy"),
    )
    presentation_table = repo / manifest["presentation_table"]["path"]
    checks["presentation_table_hash"] = _text_binding_matches(
        presentation_table,
        manifest["presentation_table"]["sha256"],
        manifest["presentation_table"].get("sha256_strategy"),
    )

    obs_path = root / "geometry_observations.csv"
    obs = pd.read_csv(obs_path, low_memory=False)
    attacks = [s.tag for s in geometry_attack_specs()]
    key = ["gate", "svd_dim", "split_seed", "model_seed", "model", "attack"]
    checks["observation_count_and_uniqueness"] = len(obs) == 600 * len(attacks) and not obs.duplicated(key).any()
    checks["attack_set_exact"] = set(obs["attack"]) == set(attacks)
    checks["geometry_declarations_exact"] = bool(
        (obs["geometry_id"] == GEOMETRY_ID).all()
        and (obs["reference_geometry"] == REFERENCE_GEOMETRY).all()
        and (obs["clean_current_geometry"] == CLEAN_CURRENT_GEOMETRY).all()
        and (obs["attack_current_geometry"] == ATTACK_CURRENT_GEOMETRY).all()
        and (obs["clean_draw_tag"] == CALIBRATION_DRAW_TAG).all()
        and (obs["n_reference"] == obs["n_current"]).all()
    )
    checks["no_missing_cells"] = bool(obs.groupby("attack").size().eq(600).all())
    adaptive = obs[obs["attack_class"] == "adaptive"]
    checks["adaptive_strength_grid_exact"] = set(adaptive["strength"].round(3)) == {0.02, 0.05, 0.10, 0.25, 0.50}
    identity = obs[obs["attack"] == "sham_identity"]
    identity_cols = [f"paired__{s}" for s in ALL_BATCH_SENSOR_COLUMNS] + [
        "paired_pred_disagreement",
        "paired_label_flip_rate",
        "paired_confusion_profile_l1",
        "paired_confusion_profile_jsd",
    ]
    checks["paired_identity_exact_zero"] = bool(
        identity[identity_cols].apply(pd.to_numeric, errors="coerce").abs().to_numpy().max() <= IDENTITY_TOL
    )
    checks["identity_copy_not_confused_with_clean_resample"] = bool(
        max(
            float((pd.to_numeric(identity[s]) - pd.to_numeric(identity[f"clean__{s}"])).abs().max())
            for s in ALL_BATCH_SENSOR_COLUMNS
        )
        <= IDENTITY_TOL
    )
    checks["matched_control_adaptive_pairs_complete"] = bool(
        (pd.read_csv(root / "geometry_gateA_summary.csv")["n_environment_split_cells"] == 40).all()
    )

    recomputed = derive_outputs(repo, obs)
    for name, expected in recomputed.items():
        actual = pd.read_csv(root / name, low_memory=False)
        try:
            pd.testing.assert_frame_equal(actual, expected, check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12)
            checks[f"derived_{name}_recomputed"] = True
        except AssertionError:
            checks[f"derived_{name}_recomputed"] = False
    checks["manifest_acceptance_checks_all_true"] = all(bool(v) for v in manifest.get("acceptance_checks", {}).values())
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError(f"Geometry sensitivity verification failed: {failed}")
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--evidence-dir", type=Path, default=Path("publication/artifact/evidence/geometry_sensitivity"))
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    checks = verify(repo, args.evidence_dir)
    print(json.dumps({"status": "verified", "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
