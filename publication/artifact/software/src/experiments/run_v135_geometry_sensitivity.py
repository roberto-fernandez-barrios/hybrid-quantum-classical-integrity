"""Deterministic replay runner for the preregistered v1.3.5 geometry sensitivity.

For each frozen model cell, reconstruct the original split/model, select
``clean_resample_eval_01`` as the fresh batch B, and score ``s(E, T(B))``
against the same fixed frozen evaluation reference E used by the clean null
``s(E, B)``.  The original ``s(E, T(E))`` evidence is never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

from src.attacks.sham import CleanResample, CleanResampleCfg
from src.datasets.cicids_subset import CicidsConfig, load_cicids_subset
from src.experiments.build_q1_reinforcement_evidence import CALIBRATED_SENSORS
from src.experiments.run_benchmark import (
    _apply_attack,
    _binary_jsd_from_labels,
    _build_attacks,
    _confusion_profile_shift,
    _get_scores,
    _packed_seed,
    _safe_absdiff,
    _stable_attack_seed,
    _stratified_subsample,
    _stratified_subsample_indices,
    build_scaler,
    fit_transform_scaler,
    sha256_file,
)
from src.experiments.run_v11_reinforcement_queue import (
    GATE_N_ENVIRONMENTS,
    Q_BACKEND,
    Q_MAX_ITER,
    Q_REPS,
)
from src.integrity.signals import (
    MMDConfig,
    jsd_feature_shift,
    ks_feature_shift,
    mmd_rbf,
    score_drift_jsd,
)
from src.qml.classical import ClassicalCfg, train_classical_svc
from src.qml.quantum_qsvc import QuantumCfg, train_qsvc
from src.utils.seed import seed_everything


PREREGISTRATION = "manuscript/v135_geometry_aligned_sensitivity_prereg.md"
GEOMETRY_ID = "fixed_frozen_E__fresh_eval_draw_01"
REFERENCE_GEOMETRY = "fixed_frozen_E"
CLEAN_CURRENT_GEOMETRY = "fresh_eval_draw_01"
ATTACK_CURRENT_GEOMETRY = "intervened_fresh_eval_draw_01"
CALIBRATION_DRAW_TAG = "clean_resample_eval_01"
REPLAY_TOL = 1e-9
IDENTITY_TOL = 1e-12

EXTRA_SENSOR_COLUMNS = ["integrity_ks_mean_vs_clean_eval"]
ALL_BATCH_SENSOR_COLUMNS = CALIBRATED_SENSORS + EXTRA_SENSOR_COLUMNS


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_attack_specs() -> list[Any]:
    """The exact existing feature-side interventions frozen by the preregistration."""

    identity_and_tiny = [s for s in _build_attacks("paper_sham") if s.tag != "clean"]
    feature_core = [
        s
        for s in _build_attacks("paper_core")
        if s.tag.startswith(("mean_shift_pf_", "scaling_drift_", "feature_dropout_"))
    ]
    adaptive = [s for s in _build_attacks("paper_f5") if s.tag.startswith("cluster_preserving_")]
    specs = identity_and_tiny + feature_core + adaptive
    tags = [s.tag for s in specs]
    if len(tags) != 22 or len(tags) != len(set(tags)):
        raise RuntimeError(f"Geometry suite must contain 22 unique existing interventions, got {tags}")
    return specs


def _attack_class_and_mechanism(tag: str) -> tuple[str, str]:
    if tag == "sham_identity":
        return "identity", "identity"
    if tag.startswith("sham_tiny_gaussian"):
        return "near_null", "tiny_gaussian"
    if tag.startswith("sham_tiny_scaling"):
        return "near_null", "tiny_scaling"
    if tag.startswith("cluster_preserving_mean_shift"):
        return "adaptive", "mean_shift"
    if tag.startswith("cluster_preserving_scaling"):
        return "adaptive", "scaling_drift"
    if tag.startswith("mean_shift_pf"):
        return "control", "mean_shift"
    if tag.startswith("scaling_drift"):
        return "control", "scaling_drift"
    if tag.startswith("feature_dropout"):
        return "control", "feature_dropout"
    raise ValueError(f"Unexpected geometry-sensitivity tag {tag}")


def validate_geometry_record(record: dict[str, Any]) -> None:
    """Fail closed if a row's declared geometry differs from the implementation contract."""

    expected = {
        "geometry_id": GEOMETRY_ID,
        "reference_geometry": REFERENCE_GEOMETRY,
        "clean_current_geometry": CLEAN_CURRENT_GEOMETRY,
        "attack_current_geometry": ATTACK_CURRENT_GEOMETRY,
        "clean_draw_tag": CALIBRATION_DRAW_TAG,
    }
    mismatched = {k: (record.get(k), v) for k, v in expected.items() if record.get(k) != v}
    if mismatched:
        raise ValueError(f"Declared/implemented geometry mismatch: {mismatched}")


def _batch_stats(
    *,
    X_ref: np.ndarray,
    y_ref: np.ndarray,
    pred_ref: np.ndarray,
    scores_ref: np.ndarray,
    X_cur: np.ndarray,
    y_cur: np.ndarray,
    pred_cur: np.ndarray,
    scores_cur: np.ndarray,
    mmd_cfg: MMDConfig,
) -> dict[str, float]:
    """Compute the frozen batch-level sensor vector for explicit reference/current arrays."""

    ks_mean, ks_reject, ks_n = ks_feature_shift(X_ref, X_cur)
    if ks_n <= 0 or not np.isfinite(ks_reject):
        raise ValueError("KS sensor is undefined for a geometry-sensitivity batch")
    conf_l1, conf_jsd = _confusion_profile_shift(y_ref, pred_ref, y_cur, pred_cur)
    return {
        "integrity_jsd_vs_clean_eval": float(jsd_feature_shift(X_ref, X_cur, bins=40, clip_q=(0.005, 0.995))),
        "integrity_mmd_vs_clean_eval": float(mmd_rbf(X_ref, X_cur, cfg=mmd_cfg)),
        "integrity_ks_reject05_vs_clean_eval": float(ks_reject),
        "integrity_score_jsd_vs_clean_eval": float(
            score_drift_jsd(scores_ref=scores_ref, scores_cur=scores_cur, bins=40, clip_q=(0.005, 0.995))
        ),
        "integrity_pred_pos_rate_shift": float(_safe_absdiff(float(np.mean(pred_cur)), float(np.mean(pred_ref)))),
        "integrity_pred_jsd": float(_binary_jsd_from_labels(pred_ref, pred_cur)),
        "integrity_label_prior_shift": float(_safe_absdiff(float(np.mean(y_cur)), float(np.mean(y_ref)))),
        "integrity_label_jsd": float(_binary_jsd_from_labels(y_ref, y_cur)),
        "integrity_confusion_profile_l1": float(conf_l1),
        "integrity_confusion_profile_jsd": float(conf_jsd),
        "integrity_ks_mean_vs_clean_eval": float(ks_mean),
    }


def _load_frozen_job_rows(repo: Path, gate: str, split_seed: int, model_seed: int, dim: int) -> tuple[pd.DataFrame, Path, Path]:
    raw_dir = repo / f"results/raw/paper15_v11_null_{gate}"
    pattern = f"*__split{split_seed}__model{model_seed}__d{dim}__*.csv"
    paths = sorted(raw_dir.glob(pattern))
    if len(paths) != 1:
        raise RuntimeError(f"Expected one frozen null CSV for {gate}/{split_seed}/{model_seed}/d{dim}, got {paths}")
    csv_path = paths[0]
    json_path = csv_path.with_suffix(".json")
    if not json_path.is_file():
        raise FileNotFoundError(json_path)
    return pd.read_csv(csv_path, low_memory=False), csv_path, json_path


def _load_split(repo: Path, env: dict[str, object], split_seed: int, model_seed: int, dim: int) -> dict[str, np.ndarray]:
    seed_everything(split_seed)
    if env["protocol"] == "ood":
        cfg = CicidsConfig(
            train_path=repo / str(env["data_train"]),
            test_path=repo / str(env["data_test"]),
            svd_dim=dim,
        )
    else:
        cfg = CicidsConfig(path=repo / str(env["data"]), svd_dim=dim)
    X_tr_all, y_tr_all, X_te_all, y_te_all = load_cicids_subset(cfg, seed=split_seed)
    n = int(env["n"])
    packed = _packed_seed(split_seed, model_seed)
    X_tr, y_tr = _stratified_subsample(X_tr_all, y_tr_all, n, seed=packed)
    te_idx = _stratified_subsample_indices(np.asarray(y_te_all), n, seed=packed + 1)
    pool_mask = np.ones(len(y_te_all), dtype=bool)
    pool_mask[te_idx] = False
    X_pool = np.asarray(X_te_all)[pool_mask]
    y_pool = np.asarray(y_te_all).astype(int)[pool_mask]
    X_E = np.asarray(X_te_all)[te_idx]
    y_E = np.asarray(y_te_all).astype(int)[te_idx]
    perm = np.random.default_rng(split_seed).permutation(len(y_pool))
    half = len(perm) // 2
    return {
        "X_tr": np.asarray(X_tr),
        "y_tr": np.asarray(y_tr).astype(int),
        "X_E": X_E,
        "y_E": y_E,
        "X_pool": X_pool,
        "y_pool": y_pool,
        "calibration_idx": np.sort(perm[:half]),
        "evaluation_idx": np.sort(perm[half:]),
    }


def _scaled_arrays(split: dict[str, np.ndarray], scale: str) -> dict[str, np.ndarray]:
    scaler = build_scaler(scale)
    X_tr, X_E = fit_transform_scaler(scaler, split["X_tr"], split["X_E"])
    X_pool = np.asarray(scaler.transform(split["X_pool"])) if scaler is not None else np.asarray(split["X_pool"])
    return {**split, "X_tr": X_tr, "X_E": X_E, "X_pool": X_pool}


def _fresh_batch(arrays: dict[str, np.ndarray], model_seed: int) -> tuple[np.ndarray, np.ndarray]:
    attack_seed = _stable_attack_seed(model_seed, CALIBRATION_DRAW_TAG)
    result = CleanResample(CleanResampleCfg(pool_half="evaluation", draw_index=1)).apply(
        arrays["X_E"],
        seed=attack_seed,
        y=arrays["y_E"],
        pool={
            "X": arrays["X_pool"],
            "y": arrays["y_pool"],
            "calibration_idx": arrays["calibration_idx"],
            "evaluation_idx": arrays["evaluation_idx"],
        },
    )
    return np.asarray(result.X_att), np.asarray(result.y_att).astype(int)


def _scalar_attack_meta(meta: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in meta.items():
        if isinstance(value, (str, bool, int, float, np.bool_, np.integer, np.floating)):
            out[f"atk_{key}"] = value.item() if isinstance(value, np.generic) else value
    return out


def _run_model(
    *,
    gate: str,
    dim: int,
    split_seed: int,
    model_seed: int,
    model_label: str,
    model_family: str,
    arrays: dict[str, np.ndarray],
    train_fn: Callable[[np.ndarray, np.ndarray], Any],
    frozen: pd.DataFrame,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    seed_everything(model_seed)
    model = train_fn(arrays["X_tr"], arrays["y_tr"])
    X_E, y_E = arrays["X_E"], arrays["y_E"]
    X_B, y_B = _fresh_batch(arrays, model_seed)
    pred_E = np.asarray(model.predict(X_E)).astype(int)
    scores_E = _get_scores(model, X_E)
    pred_B = np.asarray(model.predict(X_B)).astype(int)
    scores_B = _get_scores(model, X_B)
    if scores_E is None or scores_B is None:
        raise RuntimeError(f"Continuous scores unavailable for {model_label}")
    mmd_cfg = MMDConfig(max_samples=512, gamma="median", rng_seed=model_seed, max_pairs=4096)
    clean_stats = _batch_stats(
        X_ref=X_E,
        y_ref=y_E,
        pred_ref=pred_E,
        scores_ref=np.asarray(scores_E),
        X_cur=X_B,
        y_cur=y_B,
        pred_cur=pred_B,
        scores_cur=np.asarray(scores_B),
        mmd_cfg=mmd_cfg,
    )
    clean_bal_acc = float(balanced_accuracy_score(y_B, pred_B))
    frozen_row = frozen[(frozen["model"] == model_label) & (frozen["attack"] == CALIBRATION_DRAW_TAG)]
    frozen_clean = frozen[(frozen["model"] == model_label) & (frozen["attack"] == "clean")]
    if len(frozen_row) != 1 or len(frozen_clean) != 1:
        raise RuntimeError(f"Frozen replay rows missing for {gate}/{model_label}/{split_seed}/{model_seed}/d{dim}")
    comparisons: dict[str, float] = {
        "bal_acc": abs(clean_bal_acc - float(frozen_row.iloc[0]["bal_acc"])),
        "bal_acc_clean": abs(float(balanced_accuracy_score(y_E, pred_E)) - float(frozen_clean.iloc[0]["bal_acc_clean"])),
    }
    for sensor in ALL_BATCH_SENSOR_COLUMNS:
        comparisons[sensor] = abs(float(clean_stats[sensor]) - float(frozen_row.iloc[0][sensor]))
    replay_max = max(comparisons.values())
    if replay_max > REPLAY_TOL:
        raise RuntimeError(
            f"Deterministic replay failed for {gate}/{model_label}/{split_seed}/{model_seed}/d{dim}: "
            f"max difference {replay_max:.3g}, details={comparisons}"
        )

    base_geometry = {
        "geometry_id": GEOMETRY_ID,
        "reference_geometry": REFERENCE_GEOMETRY,
        "clean_current_geometry": CLEAN_CURRENT_GEOMETRY,
        "attack_current_geometry": ATTACK_CURRENT_GEOMETRY,
        "clean_draw_tag": CALIBRATION_DRAW_TAG,
    }
    validate_geometry_record(base_geometry)
    rows: list[dict[str, Any]] = []
    for spec in geometry_attack_specs():
        attack_seed = _stable_attack_seed(model_seed, spec.tag)
        X_att, y_att, meta = _apply_attack(spec.attack_obj, X_B, y_B, seed=attack_seed)
        pred_att = np.asarray(model.predict(X_att)).astype(int)
        scores_att = _get_scores(model, X_att)
        if scores_att is None:
            raise RuntimeError(f"Continuous scores unavailable for {model_label}/{spec.tag}")
        attack_stats = _batch_stats(
            X_ref=X_E,
            y_ref=y_E,
            pred_ref=pred_E,
            scores_ref=np.asarray(scores_E),
            X_cur=X_att,
            y_cur=y_att,
            pred_cur=pred_att,
            scores_cur=np.asarray(scores_att),
            mmd_cfg=mmd_cfg,
        )
        paired_stats = _batch_stats(
            X_ref=X_B,
            y_ref=y_B,
            pred_ref=pred_B,
            scores_ref=np.asarray(scores_B),
            X_cur=X_att,
            y_cur=y_att,
            pred_cur=pred_att,
            scores_cur=np.asarray(scores_att),
            mmd_cfg=mmd_cfg,
        )
        attack_class, mechanism = _attack_class_and_mechanism(spec.tag)
        strength = float(meta.get("strength_nominal", meta.get("strength", spec.strength_nominal_decl)))
        attack_bal_acc = float(balanced_accuracy_score(y_att, pred_att))
        row: dict[str, Any] = {
            "gate": gate,
            "svd_dim": dim,
            "split_seed": split_seed,
            "model_seed": model_seed,
            "model": model_label,
            "model_family": model_family,
            "branch": "classical" if model_family == "classical" else "quantum",
            "attack": spec.tag,
            "attack_class": attack_class,
            "mechanism": mechanism,
            "strength": strength,
            "attack_seed": attack_seed,
            "n_reference": int(len(X_E)),
            "n_current": int(len(X_B)),
            "labels_preserved": bool(np.array_equal(y_att, y_B)),
            "clean_bal_acc": clean_bal_acc,
            "attack_bal_acc": attack_bal_acc,
            "delta_bal_acc": clean_bal_acc - attack_bal_acc,
            "paired_pred_disagreement": float(np.mean(pred_B != pred_att)),
            "paired_label_flip_rate": float(np.mean(y_B != y_att)),
            "paired_confusion_profile_l1": float(paired_stats["integrity_confusion_profile_l1"]),
            "paired_confusion_profile_jsd": float(paired_stats["integrity_confusion_profile_jsd"]),
            "replay_max_abs_difference": replay_max,
            **base_geometry,
            **_scalar_attack_meta(meta),
        }
        for sensor in ALL_BATCH_SENSOR_COLUMNS:
            row[sensor] = float(attack_stats[sensor])
            row[f"clean__{sensor}"] = float(clean_stats[sensor])
            row[f"paired__{sensor}"] = float(paired_stats[sensor])
            row[f"delta__{sensor}"] = float(attack_stats[sensor] - clean_stats[sensor])
        validate_geometry_record(row)
        rows.append(row)
    identity = next(r for r in rows if r["attack"] == "sham_identity")
    identity_cols = [f"paired__{s}" for s in ALL_BATCH_SENSOR_COLUMNS] + [
        "paired_pred_disagreement",
        "paired_label_flip_rate",
        "paired_confusion_profile_l1",
        "paired_confusion_profile_jsd",
    ]
    identity_max = max(abs(float(identity[c])) for c in identity_cols)
    aligned_identity_diff = max(
        abs(float(identity[s]) - float(identity[f"clean__{s}"])) for s in ALL_BATCH_SENSOR_COLUMNS
    )
    if identity_max > IDENTITY_TOL or aligned_identity_diff > IDENTITY_TOL:
        raise RuntimeError(
            f"Identity separation failed for {gate}/{model_label}: exact={identity_max}, aligned={aligned_identity_diff}"
        )
    return rows, {
        "model": model_label,
        "replay_max_abs_difference": replay_max,
        "identity_exact_max_abs_response": identity_max,
        "identity_aligned_copy_max_abs_difference": aligned_identity_diff,
    }


def run_job(repo: Path, gate: str, split_seed: int, model_seed: int, dim: int, out_dir: Path) -> tuple[Path, Path]:
    envs = {str(e["gate"]): e for e in GATE_N_ENVIRONMENTS}
    if gate not in envs:
        raise ValueError(f"Unknown gate {gate}")
    if split_seed not in (42, 43, 44, 45, 46) or model_seed not in (42, 43) or dim not in (8, 10, 12):
        raise ValueError("Seed/dimension outside preregistered grid")
    env = envs[gate]
    split = _load_split(repo, env, split_seed, model_seed, dim)
    frozen, frozen_csv, frozen_json = _load_frozen_job_rows(repo, gate, split_seed, model_seed, dim)
    rows: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    classical = _scaled_arrays(split, "standard")
    r, c = _run_model(
        gate=gate,
        dim=dim,
        split_seed=split_seed,
        model_seed=model_seed,
        model_label="svc_rbf",
        model_family="classical",
        arrays=classical,
        train_fn=lambda X, y: train_classical_svc(X, y, ClassicalCfg()),
        frozen=frozen,
    )
    rows.extend(r)
    checks.append(c)

    quantum = _scaled_arrays(split, "minmax2pi")
    for fmap in [str(x) for x in env["maps"]]:  # type: ignore[index]
        label = f"qsvc_{fmap}_r1"
        qcfg = QuantumCfg(
            feature_map=fmap,  # type: ignore[arg-type]
            reps=Q_REPS,
            backend_method=Q_BACKEND,  # type: ignore[arg-type]
            shots=1024,
            seed=model_seed,
            max_iter=Q_MAX_ITER,
        )
        r, c = _run_model(
            gate=gate,
            dim=dim,
            split_seed=split_seed,
            model_seed=model_seed,
            model_label=label,
            model_family="quantum",
            arrays=quantum,
            train_fn=lambda X, y, qcfg=qcfg: train_qsvc(X, y, qcfg)[0],
            frozen=frozen,
        )
        rows.extend(r)
        checks.append(c)

    frame = pd.DataFrame.from_records(rows).sort_values(["model", "attack"]).reset_index(drop=True)
    expected_models = 1 + len(env["maps"])  # type: ignore[arg-type]
    if len(frame) != expected_models * 22:
        raise RuntimeError(f"Expected {expected_models * 22} rows, got {len(frame)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"geometry__{gate}__split{split_seed}__model{model_seed}__d{dim}"
    csv_path = out_dir / f"{stem}.csv"
    json_path = out_dir / f"{stem}.json"
    frame.to_csv(csv_path, index=False)
    metadata = {
        "analysis": "paper15_v135_geometry_aligned_sensitivity",
        "geometry_id": GEOMETRY_ID,
        "preregistration": PREREGISTRATION,
        "job": {"gate": gate, "split_seed": split_seed, "model_seed": model_seed, "svd_dim": dim},
        "environment": env,
        "models": checks,
        "n_rows": int(len(frame)),
        "n_models": expected_models,
        "n_attacks": 22,
        "backend": Q_BACKEND,
        "q_reps": Q_REPS,
        "q_max_iter": Q_MAX_ITER,
        "frozen_inputs": {
            "null_csv": frozen_csv.relative_to(repo).as_posix(),
            "null_csv_sha256": _sha256(frozen_csv),
            "null_json": frozen_json.relative_to(repo).as_posix(),
            "null_json_sha256": _sha256(frozen_json),
        },
        "dataset_hashes": {
            key: sha256_file(repo / str(env[key]))
            for key in ("data", "data_train", "data_test")
            if env.get(key)
        },
        "csv_sha256": _sha256(csv_path),
    }
    json_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return csv_path, json_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--gate", required=True)
    parser.add_argument("--split-seed", type=int, required=True)
    parser.add_argument("--model-seed", type=int, required=True)
    parser.add_argument("--svd-dim", type=int, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("results/raw/paper15_v135_geometry"))
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    csv_path, json_path = run_job(
        repo,
        args.gate,
        args.split_seed,
        args.model_seed,
        args.svd_dim,
        repo / args.out_dir,
    )
    print(json.dumps({"status": "complete", "csv": csv_path.as_posix(), "metadata": json_path.as_posix()}, indent=2))


if __name__ == "__main__":
    main()
