"""Fail-closed verifier for the v1.3.7 corrective evidence package."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd


V136_TAG = "paper15-q1-v1.3.6"
HISTORICAL_ROOT = "publication/artifact/evidence"
NEW_DIRS = {
    "publication/artifact/evidence/jsd_correction",
    "publication/artifact/evidence/label_geometry_sensitivity",
}
CORRECTED = (
    "integrity_jsd_vs_clean_eval",
    "integrity_score_jsd_vs_clean_eval",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    return subprocess.check_output(["git", *args], cwd=repo, text=not binary)


def _verify_outputs(repo: Path, manifest: dict[str, object]) -> None:
    manifest_dir = (
        repo / "publication/artifact/evidence/jsd_correction"
        if manifest.get("corrected_sensors")
        else repo / "publication/artifact/evidence/label_geometry_sensitivity"
    )
    for name, item in manifest["outputs"].items():  # type: ignore[union-attr]
        record = dict(item)
        path = manifest_dir / str(name)
        if not path.is_file():
            raise FileNotFoundError(path)
        if _sha256(path) != record["sha256"]:
            raise ValueError(f"manifest hash mismatch: {path}")
        if path.suffix == ".csv" and len(pd.read_csv(path, low_memory=False)) != int(record["rows"]):
            raise ValueError(f"manifest row count mismatch: {path}")


def _verify_immutability(repo: Path) -> tuple[int, int]:
    listing = str(_git(repo, "ls-tree", "-r", "--name-only", V136_TAG, "--", HISTORICAL_ROOT))
    paths = [line for line in listing.splitlines() if line]
    changed: list[str] = []
    geometry_changed: list[str] = []
    for rel in paths:
        # New v1.3.7 directories do not exist in the tag and therefore never occur here.
        disk = repo / rel
        if not disk.is_file():
            changed.append(rel)
            continue
        tagged = _git(repo, "show", f"{V136_TAG}:{rel}", binary=True)
        if disk.read_bytes() != tagged:
            changed.append(rel)
            if rel.startswith(f"{HISTORICAL_ROOT}/geometry_sensitivity/"):
                geometry_changed.append(rel)
    if changed:
        raise ValueError(f"immutable v1.3.6 evidence changed: {changed[:10]}")
    return len(changed), len(geometry_changed)


def verify(repo: Path) -> dict[str, object]:
    jsd_dir = repo / "publication/artifact/evidence/jsd_correction"
    label_dir = repo / "publication/artifact/evidence/label_geometry_sensitivity"
    jsd_manifest = json.loads((jsd_dir / "jsd_correction_manifest.json").read_text(encoding="utf-8"))
    label_manifest = json.loads((label_dir / "label_geometry_manifest.json").read_text(encoding="utf-8"))
    _verify_outputs(repo, jsd_manifest)
    _verify_outputs(repo, label_manifest)
    historical_changed, geometry_changed = _verify_immutability(repo)

    observations = pd.read_csv(jsd_dir / "jsd_corrected_observations.csv", low_memory=False)
    current = observations[list(CORRECTED)].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    if len(observations) != 64560 or not np.isfinite(current).all():
        raise ValueError("corrected observation cardinality/finiteness failure")
    deltas = pd.read_csv(jsd_dir / "jsd_correction_deltas.csv", low_memory=False)
    required_delta = {
        "affected_row_identifier", "sensor", "previous_value", "corrected_value",
        "previous_sensor_fire", "corrected_sensor_fire", "reason",
    }
    if not required_delta.issubset(deltas.columns) or deltas.empty:
        raise ValueError("correction delta ledger is incomplete")

    label = pd.read_csv(label_dir / "label_geometry_observations.csv", low_memory=False)
    if len(label) != 3600:
        raise ValueError("aligned label row count is not 3,600")
    summary = pd.read_csv(label_dir / "label_geometry_summary.csv")
    q1 = summary.set_index("question").loc["Q1"]
    q2 = summary.set_index("question").loc["Q2"]
    if int(q1["v136"]) != 11 or int(q1["v136_denominator"]) != 2617:
        raise ValueError("historical conformal label endpoint is not 11/2617")
    if int(q2["v136"]) != 43 or int(q2["v136_denominator"]) != 2617:
        raise ValueError("historical union label endpoint is not 43/2617")
    blind = label[label["aggregate_blind"].astype(bool)]
    blind_fires = int(
        blind[["aligned__fire_family__I_XFY", "aligned__fire_union__I_XFY"]]
        .astype(bool)
        .to_numpy()
        .sum()
    )
    if blind_fires:
        raise ValueError(f"aggregate-blind label rows produced {blind_fires} statistical fires")

    ablation = pd.read_csv(jsd_dir / "jsd_without_ks_ablation.csv", low_memory=False)
    if ablation.empty or set(ablation["rule"]) != {"union", "family"}:
        raise ValueError("without-KS descriptive ablation is incomplete")
    decomposition = pd.read_csv(jsd_dir / "jsd_sensor_decomposition.csv", low_memory=False)
    expected_sensors = {
        "integrity_jsd_vs_clean_eval", "integrity_mmd_vs_clean_eval",
        "integrity_ks_reject05_vs_clean_eval", "integrity_ks_mean_vs_clean_eval",
        "integrity_score_jsd_vs_clean_eval", "integrity_pred_pos_rate_shift",
        "integrity_pred_jsd", "integrity_label_prior_shift", "integrity_label_jsd",
        "integrity_confusion_profile_l1", "integrity_confusion_profile_jsd",
    }
    if set(decomposition["sensor"]) != expected_sensors:
        raise ValueError("sensor decomposition does not cover the declared sensor set")

    result = {
        "status": "PASS",
        "v136_evidence_files_modified": historical_changed,
        "v135_geometry_evidence_files_modified": geometry_changed,
        "v137_evidence_files": len(jsd_manifest["outputs"]) + len(label_manifest["outputs"]) + 2,
        "corrected_observation_rows": len(observations),
        "delta_records": len(deltas),
        "aligned_label_rows": len(label),
        "aggregate_blind_rows": len(blind),
        "aggregate_blind_fires": blind_fires,
    }
    print(json.dumps(result, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    verify(args.repo_root.resolve())


if __name__ == "__main__":
    main()
