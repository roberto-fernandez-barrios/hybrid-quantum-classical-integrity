"""Deterministic per-job replay for the preregistered v1.3.7 correction.

The runner reconstructs only frozen model configurations.  It emits corrected
sensor observations into an ignored raw-results directory; no historical
evidence file is read-write or overwritten.
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

from src.experiments.build_q1_reinforcement_evidence import CALIBRATED_SENSORS
from src.experiments.run_benchmark import (
    _apply_attack,
    _binary_jsd_from_labels,
    _build_attacks,
    _confusion_profile_shift,
    _get_scores,
    _safe_absdiff,
    _stable_attack_seed,
    sha256_file,
)
from src.experiments.run_v11_reinforcement_queue import (
    GATE_N_ENVIRONMENTS,
    Q_BACKEND,
    Q_MAX_ITER,
    Q_REPS,
)
from src.experiments.run_v135_geometry_sensitivity import (
    ALL_BATCH_SENSOR_COLUMNS,
    _batch_stats,
    _fresh_batch,
    _load_frozen_job_rows,
    _load_split,
    _scalar_attack_meta,
    _scaled_arrays,
    geometry_attack_specs,
)
from src.integrity.signals import MMDConfig
from src.integrity.signals import jsd_feature_shift, score_drift_jsd
from src.qml.classical import ClassicalCfg, train_classical_svc
from src.qml.quantum_qsvc import QuantumCfg, train_qsvc
from src.utils.seed import seed_everything


PREREGISTRATION = "manuscript/v137_jsd_label_geometry_prereg.md"
ANALYSIS = "paper15_v137_jsd_label_geometry_correction"
CORRECTED_JSD_SENSORS = (
    "integrity_jsd_vs_clean_eval",
    "integrity_score_jsd_vs_clean_eval",
)
NON_JSD_BATCH_SENSORS = tuple(
    sensor for sensor in ALL_BATCH_SENSOR_COLUMNS if sensor not in CORRECTED_JSD_SENSORS
)
TOL = 1e-9

GATE1_ENVIRONMENT: dict[str, object] = {
    "gate": "gate1_id_cicids",
    "protocol": "id",
    "data": "data/cicids_subset.csv",
    "maps": ["zz", "z", "pauli_xyz"],
    "n": 128,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pool(arrays: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    return {
        "X": arrays["X_pool"],
        "y": arrays["y_pool"],
        "calibration_idx": arrays["calibration_idx"],
        "evaluation_idx": arrays["evaluation_idx"],
    }


def _attack_kind(tag: str, scope: str) -> tuple[str, str]:
    if tag == "clean":
        return "clean", "clean"
    if tag.startswith(("clean_resample_calib", "clean_resample_calibration")):
        return "null_calibration", "clean_resample"
    if tag.startswith("clean_resample_eval"):
        return "null_evaluation", "clean_resample"
    if tag == "sham_identity":
        return "identity", "identity"
    if tag.startswith("sham_tiny_gaussian"):
        return "near_null", "tiny_gaussian"
    if tag.startswith("sham_tiny_scaling"):
        return "near_null", "tiny_scaling"
    if tag.startswith("label_flip_prior_preserving"):
        return "label", "label_flip_prior_preserving"
    if tag.startswith("label_flip"):
        return "label", "label_flip"
    if tag.startswith("feature_sign_flip"):
        return "control", "sign_flip"
    if tag.startswith("mean_shift_pf"):
        return "control", "mean_shift"
    if tag.startswith("scaling_drift"):
        return "control", "scaling_drift"
    if tag.startswith("feature_dropout"):
        return "control", "dropout"
    if tag.startswith("cluster_preserving_mean_shift"):
        return "adaptive", "mean_shift"
    if tag.startswith("cluster_preserving_scaling"):
        return "adaptive", "scaling_drift"
    raise ValueError(f"Unexpected attack tag in {scope}: {tag}")


def _evaluate(
    *,
    scope: str,
    gate: str,
    dim: int,
    split_seed: int,
    model_seed: int,
    model_label: str,
    model_family: str,
    model: Any,
    X_ref: np.ndarray,
    y_ref: np.ndarray,
    pred_ref: np.ndarray,
    scores_ref: np.ndarray,
    X_base: np.ndarray,
    y_base: np.ndarray,
    pred_base: np.ndarray,
    scores_base: np.ndarray,
    spec: Any,
    pool: dict[str, np.ndarray] | None,
    mmd_cfg: MMDConfig,
    clean_stats: dict[str, float],
) -> dict[str, Any]:
    attack_seed = _stable_attack_seed(model_seed, spec.tag)
    X_cur, y_cur, meta = _apply_attack(
        spec.attack_obj, X_base, y_base, seed=attack_seed, pool=pool
    )
    X_cur = np.asarray(X_cur)
    y_cur = np.asarray(y_cur).astype(int)
    same_features = np.array_equal(X_cur, X_base)
    pred_cur = pred_base if same_features else np.asarray(model.predict(X_cur)).astype(int)
    scores = scores_base if same_features else _get_scores(model, X_cur)
    if scores is None:
        raise RuntimeError(f"Continuous scores unavailable for {model_label}/{scope}/{spec.tag}")
    scores_cur = np.asarray(scores)
    stats: dict[str, float] = {
        "integrity_jsd_vs_clean_eval": float(
            jsd_feature_shift(X_ref, X_cur, bins=40, clip_q=(0.005, 0.995))
        ),
        "integrity_score_jsd_vs_clean_eval": float(
            score_drift_jsd(scores_ref, scores_cur, bins=40, clip_q=(0.005, 0.995))
        ),
    }
    if not np.isfinite([stats[s] for s in CORRECTED_JSD_SENSORS]).all():
        raise ValueError(f"Nonfinite corrected sensor in {gate}/{model_label}/{scope}/{spec.tag}")
    if scope == "label_aligned":
        conf_l1, conf_jsd = _confusion_profile_shift(
            y_ref, pred_ref, y_cur, pred_cur
        )
        stats.update(
            {
                "integrity_mmd_vs_clean_eval": clean_stats["integrity_mmd_vs_clean_eval"],
                "integrity_ks_reject05_vs_clean_eval": clean_stats["integrity_ks_reject05_vs_clean_eval"],
                "integrity_pred_pos_rate_shift": clean_stats["integrity_pred_pos_rate_shift"],
                "integrity_pred_jsd": clean_stats["integrity_pred_jsd"],
                "integrity_label_prior_shift": float(
                    _safe_absdiff(float(np.mean(y_cur)), float(np.mean(y_ref)))
                ),
                "integrity_label_jsd": float(_binary_jsd_from_labels(y_ref, y_cur)),
                "integrity_confusion_profile_l1": float(conf_l1),
                "integrity_confusion_profile_jsd": float(conf_jsd),
                "integrity_ks_mean_vs_clean_eval": clean_stats["integrity_ks_mean_vs_clean_eval"],
            }
        )
    attack_class, mechanism = _attack_kind(spec.tag, scope)
    strength = float(
        meta.get("strength_nominal", meta.get("strength", spec.strength_nominal_decl))
    )
    row: dict[str, Any] = {
        "scope": scope,
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
        "n_reference": int(len(X_ref)),
        "n_current": int(len(X_cur)),
        "clean_bal_acc": float(balanced_accuracy_score(y_base, pred_base)),
        "attack_bal_acc": float(balanced_accuracy_score(y_cur, pred_cur)),
        "delta_bal_acc": float(
            balanced_accuracy_score(y_base, pred_base)
            - balanced_accuracy_score(y_cur, pred_cur)
        ),
        "same_base_items": bool(scope not in {"null"} or not spec.tag.startswith("clean_resample")),
        **stats,
        **_scalar_attack_meta(meta),
    }
    if scope in {"feature_aligned", "label_aligned"}:
        paired_jsd = {
            "integrity_jsd_vs_clean_eval": float(
                jsd_feature_shift(X_base, X_cur, bins=40, clip_q=(0.005, 0.995))
            ),
            "integrity_score_jsd_vs_clean_eval": float(
                score_drift_jsd(scores_base, scores_cur, bins=40, clip_q=(0.005, 0.995))
            ),
        }
        for sensor in CORRECTED_JSD_SENSORS:
            row[f"clean__{sensor}"] = float(clean_stats[sensor])
            row[f"paired__{sensor}"] = float(paired_jsd[sensor])
            row[f"delta__{sensor}"] = float(stats[sensor] - clean_stats[sensor])
        if scope == "label_aligned":
            paired_conf_l1, paired_conf_jsd = _confusion_profile_shift(
                y_base, pred_base, y_cur, pred_cur
            )
            paired = {
                "integrity_jsd_vs_clean_eval": 0.0,
                "integrity_mmd_vs_clean_eval": 0.0,
                "integrity_ks_reject05_vs_clean_eval": 0.0,
                "integrity_score_jsd_vs_clean_eval": 0.0,
                "integrity_pred_pos_rate_shift": 0.0,
                "integrity_pred_jsd": 0.0,
                "integrity_label_prior_shift": float(
                    _safe_absdiff(float(np.mean(y_cur)), float(np.mean(y_base)))
                ),
                "integrity_label_jsd": float(_binary_jsd_from_labels(y_base, y_cur)),
                "integrity_confusion_profile_l1": float(paired_conf_l1),
                "integrity_confusion_profile_jsd": float(paired_conf_jsd),
                "integrity_ks_mean_vs_clean_eval": 0.0,
            }
            for sensor in ALL_BATCH_SENSOR_COLUMNS:
                row[f"clean__{sensor}"] = float(clean_stats[sensor])
                row[f"paired__{sensor}"] = float(paired[sensor])
                row[f"delta__{sensor}"] = float(stats[sensor] - clean_stats[sensor])
        row["paired_pred_disagreement"] = float(np.mean(pred_base != pred_cur))
        row["paired_label_flip_rate"] = float(np.mean(y_base != y_cur))
        if scope == "label_aligned":
            row["paired_confusion_profile_l1"] = float(paired["integrity_confusion_profile_l1"])
            row["paired_confusion_profile_jsd"] = float(paired["integrity_confusion_profile_jsd"])
    return row


def _run_model(
    *,
    repo: Path,
    gate: str,
    dim: int,
    split_seed: int,
    model_seed: int,
    model_label: str,
    model_family: str,
    arrays: dict[str, np.ndarray],
    train_fn: Callable[[np.ndarray, np.ndarray], Any],
    scopes: tuple[str, ...],
    frozen: pd.DataFrame | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    seed_everything(model_seed)
    model = train_fn(arrays["X_tr"], arrays["y_tr"])
    X_E, y_E = arrays["X_E"], arrays["y_E"]
    pred_E = np.asarray(model.predict(X_E)).astype(int)
    raw_scores_E = _get_scores(model, X_E)
    if raw_scores_E is None:
        raise RuntimeError(f"Continuous scores unavailable for {model_label}")
    scores_E = np.asarray(raw_scores_E)
    mmd_cfg = MMDConfig(max_samples=512, gamma="median", rng_seed=model_seed, max_pairs=4096)
    X_B, y_B = _fresh_batch(arrays, model_seed)
    pred_B = np.asarray(model.predict(X_B)).astype(int)
    raw_scores_B = _get_scores(model, X_B)
    if raw_scores_B is None:
        raise RuntimeError(f"Continuous scores unavailable for {model_label}/B")
    scores_B = np.asarray(raw_scores_B)

    clean_stats = _batch_stats(
        X_ref=X_E,
        y_ref=y_E,
        pred_ref=pred_E,
        scores_ref=scores_E,
        X_cur=X_B,
        y_cur=y_B,
        pred_cur=pred_B,
        scores_cur=scores_B,
        mmd_cfg=mmd_cfg,
    )
    replay_max = 0.0
    if frozen is not None:
        old_clean = frozen[(frozen["model"] == model_label) & (frozen["attack"] == "clean")]
        old_b = frozen[(frozen["model"] == model_label) & (frozen["attack"] == "clean_resample_eval_01")]
        if len(old_clean) != 1 or len(old_b) != 1:
            raise RuntimeError(f"Frozen clean rows missing for {gate}/{model_label}")
        checks = [
            abs(float(balanced_accuracy_score(y_E, pred_E)) - float(old_clean.iloc[0]["bal_acc_clean"])),
            abs(float(balanced_accuracy_score(y_B, pred_B)) - float(old_b.iloc[0]["bal_acc"])),
        ]
        checks.extend(
            abs(float(clean_stats[sensor]) - float(old_b.iloc[0][sensor]))
            for sensor in NON_JSD_BATCH_SENSORS
        )
        replay_max = max(checks)
        if replay_max > TOL:
            raise RuntimeError(
                f"Frozen non-JSD replay failed for {gate}/{model_label}: {replay_max:.3g}"
            )

    rows: list[dict[str, Any]] = []
    common = {
        "gate": gate,
        "dim": dim,
        "split_seed": split_seed,
        "model_seed": model_seed,
        "model_label": model_label,
        "model_family": model_family,
        "model": model,
        "X_ref": X_E,
        "y_ref": y_E,
        "pred_ref": pred_E,
        "scores_ref": scores_E,
        "mmd_cfg": mmd_cfg,
        "clean_stats": clean_stats,
    }
    if "null" in scopes:
        for spec in _build_attacks("paper_null"):
            rows.append(
                _evaluate(
                    scope="null_draw", X_base=X_E, y_base=y_E, pred_base=pred_E,
                    scores_base=scores_E, spec=spec, pool=_pool(arrays), **common
                )
            )
    if "core_original" in scopes:
        for spec in [s for s in _build_attacks("paper_core") if s.tag != "clean"]:
            rows.append(
                _evaluate(
                    scope="core_original", X_base=X_E, y_base=y_E, pred_base=pred_E,
                    scores_base=scores_E, spec=spec, pool=_pool(arrays), **common
                )
            )
    if "gateA_original" in scopes:
        for spec in [s for s in _build_attacks("paper_f5") if s.tag != "clean"]:
            rows.append(
                _evaluate(
                    scope="gateA_original", X_base=X_E, y_base=y_E, pred_base=pred_E,
                    scores_base=scores_E, spec=spec, pool=_pool(arrays), **common
                )
            )
    if "feature_aligned" in scopes:
        for spec in geometry_attack_specs():
            rows.append(
                _evaluate(
                    scope="feature_aligned", X_base=X_B, y_base=y_B, pred_base=pred_B,
                    scores_base=scores_B, spec=spec, pool=None, **common
                )
            )
    if "label_aligned" in scopes:
        label_specs = [s for s in _build_attacks("paper_core") if s.tag.startswith("label_flip")]
        for spec in label_specs:
            rows.append(
                _evaluate(
                    scope="label_aligned", X_base=X_B, y_base=y_B, pred_base=pred_B,
                    scores_base=scores_B, spec=spec, pool=None, **common
                )
            )
    return rows, {
        "model": model_label,
        "n_rows": len(rows),
        "replay_max_abs_non_jsd_difference": replay_max,
        "all_corrected_jsd_finite": bool(
            all(np.isfinite(row[sensor]) for row in rows for sensor in CORRECTED_JSD_SENSORS)
        ),
    }


def run_job(
    repo: Path,
    job_kind: str,
    gate: str,
    split_seed: int,
    model_seed: int,
    dim: int,
    out_dir: Path,
) -> tuple[Path, Path]:
    envs = {str(env["gate"]): env for env in GATE_N_ENVIRONMENTS}
    if job_kind == "gate1":
        env = GATE1_ENVIRONMENT
        if gate != "gate1_id_cicids" or model_seed not in (42, 43, 44, 45):
            raise ValueError("Gate1 job outside frozen grid")
        scopes = ("core_original",)
        frozen = None
    elif job_kind == "calibrated":
        if gate not in envs or model_seed not in (42, 43):
            raise ValueError("Calibrated job outside frozen grid")
        env = envs[gate]
        scopes = ("null", "core_original", "gateA_original", "feature_aligned", "label_aligned")
        frozen, _, _ = _load_frozen_job_rows(repo, gate, split_seed, model_seed, dim)
    else:
        raise ValueError(f"Unknown job kind {job_kind}")
    if split_seed not in (42, 43, 44, 45, 46) or dim not in (8, 10, 12):
        raise ValueError("Seed/dimension outside frozen grid")

    split = _load_split(repo, env, split_seed, model_seed, dim)
    rows: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    classical = _scaled_arrays(split, "standard")
    model_rows, model_check = _run_model(
        repo=repo, gate=gate, dim=dim, split_seed=split_seed, model_seed=model_seed,
        model_label="svc_rbf", model_family="classical", arrays=classical,
        train_fn=lambda X, y: train_classical_svc(X, y, ClassicalCfg()), scopes=scopes,
        frozen=frozen,
    )
    rows.extend(model_rows)
    checks.append(model_check)

    quantum = _scaled_arrays(split, "minmax2pi")
    for fmap in [str(value) for value in env["maps"]]:  # type: ignore[index]
        label = f"qsvc_{fmap}_r1"
        qcfg = QuantumCfg(
            feature_map=fmap,  # type: ignore[arg-type]
            reps=Q_REPS,
            backend_method=Q_BACKEND,  # type: ignore[arg-type]
            shots=1024,
            seed=model_seed,
            max_iter=Q_MAX_ITER,
        )
        model_rows, model_check = _run_model(
            repo=repo, gate=gate, dim=dim, split_seed=split_seed, model_seed=model_seed,
            model_label=label, model_family="quantum", arrays=quantum,
            train_fn=lambda X, y, qcfg=qcfg: train_qsvc(X, y, qcfg)[0], scopes=scopes,
            frozen=frozen,
        )
        rows.extend(model_rows)
        checks.append(model_check)

    frame = pd.DataFrame.from_records(rows).sort_values(["model", "scope", "attack"]).reset_index(drop=True)
    expected_per_model = 18 if job_kind == "gate1" else 106
    expected_models = 1 + len(env["maps"])  # type: ignore[arg-type]
    if len(frame) != expected_per_model * expected_models:
        raise RuntimeError(f"Expected {expected_per_model * expected_models} rows, got {len(frame)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"v137__{job_kind}__{gate}__split{split_seed}__model{model_seed}__d{dim}"
    csv_path = out_dir / f"{stem}.csv"
    json_path = out_dir / f"{stem}.json"
    frame.to_csv(csv_path, index=False, lineterminator="\n")
    metadata = {
        "schema_version": 2,
        "analysis": ANALYSIS,
        "preregistration": PREREGISTRATION,
        "job": {
            "kind": job_kind,
            "gate": gate,
            "split_seed": split_seed,
            "model_seed": model_seed,
            "svd_dim": dim,
        },
        "environment": env,
        "scopes": scopes,
        "models": checks,
        "n_rows": int(len(frame)),
        "n_models": expected_models,
        "expected_rows_per_model": expected_per_model,
        "backend": Q_BACKEND,
        "dataset_hashes": {
            key: sha256_file(repo / str(env[key]))
            for key in ("data", "data_train", "data_test")
            if env.get(key)
        },
        "csv_sha256": _sha256(csv_path),
    }
    json_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8", newline="\n")
    return csv_path, json_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--job-kind", choices=("calibrated", "gate1"), required=True)
    parser.add_argument("--gate", required=True)
    parser.add_argument("--split-seed", type=int, required=True)
    parser.add_argument("--model-seed", type=int, required=True)
    parser.add_argument("--svd-dim", type=int, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("results/raw/paper15_v137_correction"))
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    csv_path, json_path = run_job(
        repo, args.job_kind, args.gate, args.split_seed, args.model_seed,
        args.svd_dim, repo / args.out_dir,
    )
    print(json.dumps({"status": "complete", "csv": csv_path.as_posix(), "metadata": json_path.as_posix()}, indent=2))


if __name__ == "__main__":
    main()
