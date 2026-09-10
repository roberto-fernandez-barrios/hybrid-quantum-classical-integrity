"""Fail-closed verifier for the v1.3.7 label-geometry sensitivity evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


SENSORS = (
    "integrity_jsd_vs_clean_eval",
    "integrity_mmd_vs_clean_eval",
    "integrity_ks_reject05_vs_clean_eval",
    "integrity_score_jsd_vs_clean_eval",
    "integrity_pred_pos_rate_shift",
    "integrity_pred_jsd",
    "integrity_label_prior_shift",
    "integrity_label_jsd",
    "integrity_confusion_profile_l1",
    "integrity_confusion_profile_jsd",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(evidence_dir: Path) -> dict[str, object]:
    manifest_path = evidence_dir / "label_geometry_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "complete":
        raise ValueError("label-geometry manifest is not complete")
    if manifest.get("geometry") != {
        "original": "s(E,T_y(E))",
        "aligned": "s(E,T_y(B)) with clean comparator s(E,B)",
    }:
        raise ValueError("label-geometry definition differs from the preregistration")
    for name, record in manifest["outputs"].items():
        path = evidence_dir / name
        if not path.is_file() or _sha256(path) != record["sha256"]:
            raise ValueError(f"label-geometry output hash mismatch: {path}")
        if path.suffix == ".csv" and len(pd.read_csv(path, low_memory=False)) != int(record["rows"]):
            raise ValueError(f"label-geometry row-count mismatch: {path}")

    observations = pd.read_csv(evidence_dir / "label_geometry_observations.csv", low_memory=False)
    if len(observations) != 3600:
        raise ValueError("label-geometry evidence must contain exactly 3,600 rows")
    aligned_columns = [f"aligned__{sensor}" for sensor in SENSORS]
    aligned_values = observations[aligned_columns].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    if not np.isfinite(aligned_values).all():
        raise ValueError("nonfinite aligned label sensor value")
    pvalue_columns = [c for c in observations if c.startswith("aligned__pvalue_family__")]
    pvalues = observations[pvalue_columns].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    if not np.isfinite(pvalues).all() or ((pvalues < 0.0) | (pvalues > 1.0)).any():
        raise ValueError("invalid aligned label family p-value")

    summary = pd.read_csv(evidence_dir / "label_geometry_summary.csv").set_index("question")
    if (int(summary.loc["Q1", "v136"]), int(summary.loc["Q1", "v136_denominator"])) != (11, 2617):
        raise ValueError("historical conformal endpoint does not reproduce 11/2617")
    if (int(summary.loc["Q2", "v136"]), int(summary.loc["Q2", "v136_denominator"])) != (43, 2617):
        raise ValueError("historical union endpoint does not reproduce 43/2617")
    if (
        int(summary.loc["Q1", "v137"]), int(summary.loc["Q1", "v137_denominator"]),
        int(summary.loc["Q2", "v137"]), int(summary.loc["Q2", "v137_denominator"]),
    ) != (343, 2700, 1183, 2700):
        raise ValueError("aligned endpoints do not reproduce 343/2700 and 1183/2700")

    blind = observations[observations["aggregate_blind"].astype(bool)]
    for sensor in SENSORS:
        attacked = pd.to_numeric(blind[f"aligned__{sensor}"], errors="coerce").to_numpy(float)
        paired_clean = pd.to_numeric(blind[f"aligned__clean__{sensor}"], errors="coerce").to_numpy(float)
        if not np.allclose(attacked, paired_clean, rtol=0.0, atol=1e-12):
            raise ValueError(f"aggregate-blind rows alter declared sensor {sensor}")
    attack_only = 0
    for rule in ("family", "union"):
        attacked = blind[f"aligned__fire_{rule}__I_XFY"].astype(bool).to_numpy()
        paired_clean = blind[f"aligned__clean_fire_{rule}__I_XFY"].astype(bool).to_numpy()
        attack_only += int((attacked & ~paired_clean).sum())
        if not np.array_equal(attacked, paired_clean):
            raise ValueError(f"aggregate-blind rows change {rule} response relative to paired clean")

    result = {
        "status": "PASS",
        "rows": len(observations),
        "material_original": int(observations["original_material"].astype(bool).sum()),
        "material_aligned": int(observations["aligned_material"].astype(bool).sum()),
        "aligned_family_material_fires": int(summary.loc["Q1", "v137"]),
        "aligned_union_material_fires": int(summary.loc["Q2", "v137"]),
        "aggregate_separable_rows": int(observations["aggregate_separable"].astype(bool).sum()),
        "aggregate_blind_rows": len(blind),
        "aggregate_blind_attack_only_fires": attack_only,
    }
    print(json.dumps(result, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=Path("publication/artifact/evidence/label_geometry_sensitivity"),
    )
    args = parser.parse_args()
    verify(args.evidence_dir.resolve())


if __name__ == "__main__":
    main()
