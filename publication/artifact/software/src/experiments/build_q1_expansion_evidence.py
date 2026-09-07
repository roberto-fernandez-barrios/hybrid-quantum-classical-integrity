"""Build the cross-dataset and OOD evidence package for Paper 1.5.

Only explicitly tagged ``exact_statevector`` CSVs are admitted.  The builder
fails closed when a prespecified gate is incomplete, verifies matching JSON
metadata, removes repeated SVC rows only after numerical equality checks, and
uses split seeds as the primary uncertainty clusters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from src.experiments.build_q1_gate1_evidence import (
    FULL_SIGNAL_COLS,
    KEY_COLS,
    _deduplicate,
    _mean_ci,
    _per_seed_summary,
    _require_columns,
    _sensor_regime_table,
    _sha256,
    _shared_minmax,
)


GATES = (
    {
        "gate": "gate2_id_256",
        "path": "results/raw/paper15_q1_gate2a_id_size256_zz_svc",
        "expected_files": 30,
        "expected_models": {"svc_rbf", "qsvc_zz_r1"},
    },
    {
        "gate": "gate3a_ood_tue_wed",
        "path": "results/raw/paper15_q1_gate3a_ood_tue_wed_zz_svc",
        "expected_files": 30,
        "expected_models": {"svc_rbf", "qsvc_zz_r1"},
    },
    {
        "gate": "gate3b_ood_tue_fri_portscan",
        "path": "results/raw/paper15_q1_gate3b_ood_tue_fri_portscan_zz_svc",
        "expected_files": 30,
        "expected_models": {"svc_rbf", "qsvc_zz_r1"},
    },
    {
        "gate": "gate3c_ood_wed_thu_webattacks",
        "path": "results/raw/paper15_q1_gate3c_ood_wed_thu_webattacks_zz_svc",
        "expected_files": 30,
        "expected_models": {"svc_rbf", "qsvc_zz_r1"},
    },
    {
        "gate": "gate3d_ood_wed_fri_morning",
        "path": "results/raw/paper15_q1_gate3d_ood_wed_fri_morning_zz_svc",
        "expected_files": 30,
        "expected_models": {"svc_rbf", "qsvc_zz_r1"},
    },
    {
        "gate": "gate5a_id_unsw",
        "path": "results/raw/paper15_q1_gate5a_id_unsw_fmaps",
        "expected_files": 90,
        "expected_models": {
            "svc_rbf",
            "qsvc_zz_r1",
            "qsvc_z_r1",
            "qsvc_pauli_xyz_r1",
        },
    },
    {
        "gate": "gate5b_id_ton_iot",
        "path": "results/raw/paper15_q1_gate5b_id_ton_iot_fmaps",
        "expected_files": 90,
        "expected_models": {
            "svc_rbf",
            "qsvc_zz_r1",
            "qsvc_z_r1",
            "qsvc_pauli_xyz_r1",
        },
    },
    {
        "gate": "gate6_ood_unsw",
        "path": "results/raw/paper15_q1_gate6_ood_unsw_zz_svc",
        "expected_files": 30,
        "expected_models": {"svc_rbf", "qsvc_zz_r1"},
    },
)


def _json_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _relative_to_repo(path: Path, repo_root: Path) -> str:
    """Repository-relative POSIX path (artifact 1.2.0: no machine-specific paths in evidence)."""

    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _load_expansion(
    repo_root: Path,
    *,
    allow_partial: bool,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, object]]]:
    frames: list[pd.DataFrame] = []
    completeness: list[dict[str, object]] = []
    inputs: list[dict[str, object]] = []

    for spec in GATES:
        gate = str(spec["gate"])
        raw_dir = repo_root / str(spec["path"])
        paths = sorted(raw_dir.glob("*qbexact_statevector*.csv"))
        expected = int(spec["expected_files"])
        complete = len(paths) == expected
        completeness.append(
            {
                "gate": gate,
                "raw_directory": _relative_to_repo(raw_dir, repo_root),
                "observed_files": len(paths),
                "expected_files": expected,
                "complete": complete,
            }
        )
        if not allow_partial and not complete:
            raise RuntimeError(
                f"Gate {gate} is incomplete: observed {len(paths)} of {expected} CSVs"
            )

        for path in paths:
            json_path = path.with_suffix(".json")
            if not json_path.is_file():
                raise FileNotFoundError(f"Missing metadata for {path}: {json_path}")
            frame = pd.read_csv(path)
            frame["gate"] = gate
            frame["_source_file"] = path.name
            frames.append(frame)
            inputs.append(
                {
                    "gate": gate,
                    "csv": _relative_to_repo(path, repo_root),
                    "csv_sha256": _sha256(path),
                    "json": _relative_to_repo(json_path, repo_root),
                    "json_sha256": _json_sha256(json_path),
                }
            )

    if not frames:
        raise FileNotFoundError("No exact-statevector expansion CSVs were found")

    raw = pd.concat(frames, ignore_index=True, sort=False)
    _require_columns(
        raw,
        KEY_COLS
        + ["gate", "max_train", "max_test", "impact_bal_acc"]
        + FULL_SIGNAL_COLS,
    )
    return raw, pd.DataFrame.from_records(completeness), inputs


def _validate_gate_design(dedup: pd.DataFrame, completeness: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for spec in GATES:
        gate = str(spec["gate"])
        frame = dedup[dedup["gate"] == gate]
        if frame.empty:
            records.append({"gate": gate, "design_valid": False, "reason": "no rows"})
            continue

        models = set(frame["model"].dropna().astype(str))
        expected_models = set(spec["expected_models"])
        attacks_per_cell = frame[frame["attack"] != "clean"].groupby(
            ["model", "svd_dim", "split_seed", "model_seed"], dropna=False
        )["attack"].nunique()
        valid = (
            models == expected_models
            and set(frame["svd_dim"].astype(int)) == {8, 10, 12}
            and set(frame["split_seed"].astype(int)) == {42, 43, 44, 45, 46}
            and set(frame["model_seed"].astype(int)) == {42, 43}
            and attacks_per_cell.nunique() == 1
            and (attacks_per_cell.empty or int(attacks_per_cell.iloc[0]) == 18)
        )
        records.append(
            {
                "gate": gate,
                "design_valid": bool(valid),
                "models": ",".join(sorted(models)),
                "dimensions": ",".join(map(str, sorted(set(frame["svd_dim"].astype(int))))),
                "n_split_seeds": int(frame["split_seed"].nunique()),
                "n_model_seeds": int(frame["model_seed"].nunique()),
                "attacks_per_cell": (
                    int(attacks_per_cell.iloc[0]) if not attacks_per_cell.empty else 0
                ),
            }
        )

    design = completeness.merge(pd.DataFrame.from_records(records), on="gate", how="left")
    if bool(design["complete"].all()) and not bool(design["design_valid"].all()):
        invalid = design.loc[~design["design_valid"], "gate"].tolist()
        raise ValueError(f"Completed gates fail design validation: {invalid}")
    return design


def _environment_map(frame: pd.DataFrame) -> pd.DataFrame:
    columns = ["protocol", "dataset_tag", "gate", "max_train", "max_test"]
    mapping = frame[columns].drop_duplicates()
    duplicates = mapping.duplicated(["protocol", "dataset_tag"], keep=False)
    if duplicates.any():
        conflict = mapping.loc[duplicates].to_dict(orient="records")
        raise ValueError(f"Environment identifier is not unique: {conflict[:4]}")
    return mapping


def _paired_clustered(per_seed: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    metrics = ["impact_mean", "stealth_full_sharednorm_mean"]
    cluster = (
        per_seed.groupby(
            ["protocol", "dataset_tag", "model", "svd_dim", "split_seed"],
            dropna=False,
        )[metrics]
        .mean()
        .reset_index()
    )

    records: list[dict[str, object]] = []
    group_cols = ["protocol", "dataset_tag", "svd_dim"]
    for key, group in cluster.groupby(group_cols, dropna=False, sort=True):
        wide = group.pivot(index="split_seed", columns="model", values=metrics)
        for metric in metrics:
            required = [(metric, "qsvc_zz_r1"), (metric, "svc_rbf")]
            if not all(column in wide.columns for column in required):
                continue
            difference = wide[required[0]] - wide[required[1]]
            records.append(
                {
                    **dict(zip(group_cols, key, strict=True)),
                    "metric": metric,
                    "analysis_unit": "split_seed_cluster_primary",
                    **_mean_ci(difference),
                    "positive_split_clusters": int((difference > 0).sum()),
                    "all_positive": bool((difference > 0).all()),
                }
            )
    return cluster, pd.DataFrame.from_records(records)


def _external_consistency(paired: pd.DataFrame) -> pd.DataFrame:
    impact = paired[paired["metric"] == "impact_mean"].copy()
    return (
        impact.groupby("svd_dim", dropna=False)
        .agg(
            n_environments=("dataset_tag", "nunique"),
            mean_of_environment_differences=("mean", "mean"),
            min_environment_difference=("mean", "min"),
            max_environment_difference=("mean", "max"),
            environments_positive_mean=("mean", lambda x: int((x > 0).sum())),
            environments_ci_excludes_zero=("ci95_low", lambda x: int((x > 0).sum())),
        )
        .reset_index()
    )


def build(repo_root: Path, out_dir: Path, *, allow_partial: bool = False) -> None:
    raw, completeness, inputs = _load_expansion(repo_root, allow_partial=allow_partial)
    dedup, duplicate_audit = _deduplicate(raw)
    design = _validate_gate_design(dedup, completeness)
    environments = _environment_map(dedup)

    normalized = _shared_minmax(dedup)
    attacked = normalized[normalized["attack"] != "clean"].copy()
    per_seed = _per_seed_summary(attacked).merge(
        environments, on=["protocol", "dataset_tag"], how="left", validate="many_to_one"
    )
    cluster, paired = _paired_clustered(per_seed)
    cluster = cluster.merge(
        environments, on=["protocol", "dataset_tag"], how="left", validate="many_to_one"
    )
    paired = paired.merge(
        environments, on=["protocol", "dataset_tag"], how="left", validate="many_to_one"
    )
    consistency = _external_consistency(paired)
    sensor_regimes = _sensor_regime_table(attacked).merge(
        environments, on=["protocol", "dataset_tag"], how="left", validate="many_to_one"
    )
    blind_cases = sensor_regimes[
        sensor_regimes["feature_prediction_structurally_blind"]
        & (sensor_regimes["impact_mean"] > 0)
    ].copy()

    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "expansion_gate_completeness.csv": design,
        "expansion_unique_observations.csv": dedup.drop(columns=["_source_file"]),
        "expansion_per_seed_unit_summary.csv": per_seed,
        "expansion_per_split_cluster_summary.csv": cluster,
        "expansion_paired_zz_minus_svc_clustered.csv": paired,
        "expansion_external_consistency.csv": consistency,
        "expansion_sensor_regime_table.csv": sensor_regimes,
        "expansion_structurally_blind_positive_impact_cases.csv": blind_cases,
    }
    for name, frame in outputs.items():
        frame.to_csv(out_dir / name, index=False)

    manifest = {
        "analysis": "paper15_q1_expansion",
        "status": "partial" if allow_partial and not bool(design["complete"].all()) else "complete",
        "backend_filter": "qbexact_statevector",
        "primary_inference_unit": "split_seed after averaging nested model seeds",
        "cross_environment_summary": "descriptive fixed-environment consistency; not a random-effects population claim",
        "duplicate_audit": duplicate_audit,
        "gates": design.to_dict(orient="records"),
        "input_files": inputs,
        "outputs": {
            name: {"rows": int(len(frame)), "sha256": _sha256(out_dir / name)}
            for name, frame in outputs.items()
        },
    }
    manifest_path = out_dir / "expansion_evidence_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "duplicate_audit": duplicate_audit}, indent=2))
    print(f"Wrote {len(outputs)} tables and manifest to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/paper_digest/paper15_q1_expansion"),
    )
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Write a progress snapshot instead of failing on incomplete gates.",
    )
    args = parser.parse_args()
    build(args.repo_root.resolve(), args.out_dir, allow_partial=bool(args.allow_partial))


if __name__ == "__main__":
    main()
