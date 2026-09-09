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


def verify(repo: Path, evidence_dir: Path) -> dict[str, bool]:
    root = repo / evidence_dir
    manifest_path = root / "geometry_sensitivity_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["manifest_status_complete"] = manifest.get("status") == "complete"
    checks["manifest_analysis_exact"] = manifest.get("analysis") == "paper15_v135_geometry_aligned_sensitivity"
    prereg = repo / PREREGISTRATION
    prereg_commit = subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", PREREGISTRATION], cwd=repo, text=True
    ).strip()
    checks["preregistration_hash_and_commit"] = (
        manifest["preregistration"]["sha256"] == _sha256(prereg)
        and manifest["preregistration"]["commit"] == prereg_commit
    )
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
    checks["presentation_macro_hash"] = presentation.is_file() and _sha256(presentation) == manifest["presentation_output"]["sha256"]
    presentation_table = repo / manifest["presentation_table"]["path"]
    checks["presentation_table_hash"] = presentation_table.is_file() and _sha256(presentation_table) == manifest["presentation_table"]["sha256"]

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
