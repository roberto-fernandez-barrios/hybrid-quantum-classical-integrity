# src/experiments/run_benchmark.py
# DONE
#   --> Signals (JSD + MMD + score drift + KS) + paper hardening
#
# Updated (2026-02-19):
#   - Added stratified subsampling caps shared by classical+quantum:
#       * --max-train (default 512, 0=all)
#       * --max-test  (default 512, 0=all)
#   - Subsampling is applied ONCE after dataset load (post split / SVD) and BEFORE scaling/training,
#     so classical and quantum see the exact same samples.
#   - Logs split_info now includes raw vs used sizes.
#
# Updated (debug logs):
#   - Added detailed runtime logs for:
#       * model family train start/end
#       * reference score computation start/end
#       * per-attack prep/predict/scores/signals timing
#   - Added CSV timing columns:
#       * predict_time_s
#       * scores_time_s
#       * ref_scores_time_s
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List, Union, Callable

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from src.config import PATHS
from src.utils.seed import seed_everything
from src.utils.io import ensure_dir

from src.datasets.cicids_subset import CicidsConfig, load_cicids_subset
from src.qml.classical import ClassicalCfg, train_classical_svc
from src.qml.quantum_qsvc import QuantumCfg, train_qsvc, predict_qsvc, scores_qsvc, QISKIT_OK

# Attacks (v2)
from src.attacks.scaling_drift import ScalingDrift, ScalingDriftCfg
from src.attacks.feature_sign_flip import FeatureSignFlip, FeatureSignFlipCfg
from src.attacks.gaussian_noise import GaussianNoise, GaussianNoiseCfg
from src.attacks.label_flip import LabelFlip, LabelFlipCfg
from src.attacks.mean_shift import MeanShift, MeanShiftCfg
from src.attacks.feature_dropout import FeatureDropout, FeatureDropoutCfg
from src.attacks.clipping import Clipping, ClippingCfg
from src.attacks.quantization import Quantization, QuantizationCfg

from src.integrity.signals import (
    jsd_feature_shift,
    mmd_rbf,
    MMDConfig,
    score_drift_jsd,
    ks_feature_shift,
)

# ----------------------------
# Small utilities
# ----------------------------
def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def _safe_roc_auc(y_true: np.ndarray, scores: Optional[np.ndarray]) -> float:
    if scores is None:
        return float("nan")
    y_true = np.asarray(y_true).astype(int)
    if len(np.unique(y_true)) < 2:
        return float("nan")
    try:
        return float(roc_auc_score(y_true, scores))
    except Exception:
        return float("nan")


def _metrics(y_true: np.ndarray, y_pred: np.ndarray, scores: Optional[np.ndarray]) -> Dict[str, float]:
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    return {
        "bal_acc": float(balanced_accuracy_score(y_true, y_pred)),
        "f1_pos": float(f1_score(y_true, y_pred, pos_label=1)),
        "pos_rate_eval": float(np.mean(y_true)),
        "roc_auc": _safe_roc_auc(y_true, scores),
    }


def _get_scores(model, X: np.ndarray) -> Optional[np.ndarray]:
    if hasattr(model, "decision_function"):
        try:
            s = model.decision_function(X)
            return np.asarray(s).reshape(-1)
        except Exception:
            return None
    if hasattr(model, "predict_proba"):
        try:
            p = model.predict_proba(X)
            if p.ndim == 2 and p.shape[1] >= 2:
                return np.asarray(p[:, 1]).reshape(-1)
        except Exception:
            return None
    return None


def _apply_attack(atk: Any, X: np.ndarray, y: np.ndarray, seed: int) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Compatibility wrapper:
      - Preferred signature: apply(X, seed=seed, y=y)
      - Backward: apply(X, y=y, seed=seed) or apply(X, seed=seed)

    Returns:
      X_att, y_att, meta (dict)
    """
    if atk is None:
        return np.asarray(X), np.asarray(y), {}

    try:
        out = atk.apply(X, seed=seed, y=y)
    except TypeError:
        try:
            out = atk.apply(X, y=y, seed=seed)
        except TypeError:
            out = atk.apply(X, seed=seed)

    X_att = getattr(out, "X_att", None)
    y_att = getattr(out, "y_att", None)
    meta = getattr(out, "meta", {}) or {}

    if X_att is None:
        raise RuntimeError(f"Attack {atk.__class__.__name__}.apply did not return X_att")
    if y_att is None:
        y_att = y

    return np.asarray(X_att), np.asarray(y_att), dict(meta)


def _as_float_or_nan(x: Any) -> float:
    try:
        v = float(x)
        return float(v) if np.isfinite(v) else float("nan")
    except Exception:
        return float("nan")


def _meta_family(meta: Dict[str, Any], fallback: str) -> str:
    fam = meta.get("family", None)
    return str(fallback) if fam is None else str(fam)


def _meta_strength_nominal(meta: Dict[str, Any], fallback: float) -> float:
    if "strength_nominal" in meta:
        v = _as_float_or_nan(meta.get("strength_nominal"))
        return float(fallback) if not np.isfinite(v) else float(v)
    if "strength" in meta:
        v = _as_float_or_nan(meta.get("strength"))
        return float(fallback) if not np.isfinite(v) else float(v)
    return float(fallback)


def _meta_strength_eff(meta: Dict[str, Any], fallback: float) -> float:
    if "strength_eff" in meta:
        v = _as_float_or_nan(meta.get("strength_eff"))
        return float(fallback) if not np.isfinite(v) else float(v)
    if "strength" in meta:
        v = _as_float_or_nan(meta.get("strength"))
        return float(fallback) if not np.isfinite(v) else float(v)
    return float(fallback)


def _stable_attack_seed(model_seed: int, attack_tag: str) -> int:
    h = hashlib.sha1(attack_tag.encode("utf-8")).digest()
    tag_u32 = int.from_bytes(h[:4], byteorder="little", signed=False)
    return int((int(model_seed) ^ tag_u32) & 0xFFFFFFFF)


# ----------------------------
# Packed seed policy
# ----------------------------
_PACK_MULT = 1_000_000


def _packed_seed(split_seed: int, model_seed: int) -> int:
    ss = int(split_seed)
    ms = int(model_seed)
    if ss < 0:
        raise ValueError(f"split_seed={ss} must be >= 0 for packing.")
    if ms < 0 or ms >= _PACK_MULT:
        raise ValueError(
            f"model_seed={ms} out of range for packing (need 0 <= model_seed < {_PACK_MULT}). "
            f"Either reduce model_seed or increase _PACK_MULT."
        )
    return ss * _PACK_MULT + ms


# ----------------------------
# Subsampling (shared classical + quantum)
# ----------------------------
def _stratified_subsample(
    X: np.ndarray,
    y: np.ndarray,
    n_max: int,
    *,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Stratified subsample to at most n_max rows.
    Keeps class proportions roughly stable. Deterministic via seed.
    """
    X = np.asarray(X)
    y = np.asarray(y).astype(int)

    if n_max <= 0 or len(y) <= n_max:
        return X, y

    rng = np.random.default_rng(int(seed))
    idx_all = np.arange(len(y))

    classes, counts = np.unique(y, return_counts=True)
    frac = float(n_max) / float(len(y))

    chosen: List[np.ndarray] = []
    for c, cnt in zip(classes, counts):
        idx_c = idx_all[y == c]
        # proportional allocation, at least 1 per class if present
        k = max(1, int(round(float(cnt) * frac)))
        k = min(k, len(idx_c))
        chosen.append(rng.choice(idx_c, size=k, replace=False))

    idx = np.concatenate(chosen) if chosen else rng.choice(idx_all, size=n_max, replace=False)
    if len(idx) > n_max:
        idx = rng.choice(idx, size=n_max, replace=False)

    idx = np.sort(idx)
    return X[idx], y[idx]


# ----------------------------
# Scaling
# ----------------------------
def build_scaler(scale: str):
    scale = scale.lower().strip()
    if scale == "none":
        return None
    if scale == "standard":
        return StandardScaler()
    if scale == "minmax01":
        return MinMaxScaler(feature_range=(0.0, 1.0))
    if scale == "minmax2pi":
        return MinMaxScaler(feature_range=(0.0, 2.0 * np.pi))
    raise ValueError(f"Unknown scale '{scale}'. Use: none|standard|minmax01|minmax2pi")


def fit_transform_scaler(scaler, X_tr: np.ndarray, X_te: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    if scaler is None:
        return np.asarray(X_tr), np.asarray(X_te)
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)
    return np.asarray(X_tr_s), np.asarray(X_te_s)


def scaler_info(scaler) -> Dict[str, Any]:
    if scaler is None:
        return {"type": "none"}
    info = {"type": scaler.__class__.__name__}
    if isinstance(scaler, MinMaxScaler):
        info["feature_range"] = tuple(map(float, scaler.feature_range))
    if isinstance(scaler, StandardScaler):
        info["with_mean"] = bool(getattr(scaler, "with_mean", True))
        info["with_std"] = bool(getattr(scaler, "with_std", True))
    return info


# ----------------------------
# Config
# ----------------------------
@dataclass(frozen=True)
class RunCfg:
    protocol: str  # "id" | "ood"
    data: str
    data_train: Optional[str]
    data_test: Optional[str]
    svd_dim: int
    seed: int
    split_seed: int
    model_seed: int
    outdir: str
    run_quantum: bool
    scale_classical: str
    scale_quantum: str
    q_feature_map: str
    q_reps: int
    q_shots: int
    sig_bins: int
    sig_clip_q_lo: float
    sig_clip_q_hi: float
    mmd_max_samples: int
    mmd_gamma: str
    mmd_max_pairs: int
    attack_suite: str
    atk_meta_whitelist: Tuple[str, ...]
    max_train: int
    max_test: int


def _parse_quantile_pair(lo: float, hi: float) -> Tuple[float, float]:
    lo = float(lo)
    hi = float(hi)
    if not (0.0 <= lo < hi <= 1.0):
        raise ValueError("Quantiles must satisfy 0 <= lo < hi <= 1")
    return (lo, hi)


def _infer_split_model_seeds(
    seed: int,
    split_seed: Optional[int],
    model_seed: Optional[int],
    strict: bool,
) -> Tuple[int, int, int, str]:
    has_split = split_seed is not None
    has_model = model_seed is not None

    if has_split ^ has_model:
        if strict:
            raise SystemExit("If you pass --split-seed you must also pass --model-seed (and vice versa).")
        return int(seed), int(seed), int(seed), "legacy"

    if has_split and has_model:
        packed = _packed_seed(int(split_seed), int(model_seed))
        return int(packed), int(split_seed), int(model_seed), "packed"

    return int(seed), int(seed), int(seed), "legacy"


def _parse_meta_keys(raw: str) -> Tuple[str, ...]:
    s = (raw or "").strip()
    if not s:
        return tuple()
    s = s.replace(";", ",")
    parts: List[str] = []
    for chunk in s.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts.extend([p.strip() for p in chunk.split() if p.strip()])

    seen = set()
    out: List[str] = []
    for k in parts:
        if k not in seen:
            out.append(k)
            seen.add(k)
    return tuple(out)


def _cfg_fingerprint(cfg: RunCfg) -> str:
    payload = json.dumps(asdict(cfg), sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:10]


def _protocol_from_args(data: str, data_train: Optional[str], data_test: Optional[str]) -> str:
    has_tr = bool(data_train)
    has_te = bool(data_test)
    if has_tr or has_te:
        if not (has_tr and has_te):
            raise SystemExit("For OOD mode you must pass BOTH --data-train and --data-test.")
        return "ood"
    return "id"


def _require_dataset_files(protocol: str, data: str, data_train: Optional[str], data_test: Optional[str]) -> None:
    if protocol == "ood":
        if not data_train or not data_test:
            raise SystemExit("OOD mode requires --data-train and --data-test.")
        if not Path(data_train).exists():
            raise SystemExit(f"Missing OOD train dataset file: {data_train}")
        if not Path(data_test).exists():
            raise SystemExit(f"Missing OOD test dataset file: {data_test}")
    else:
        if not Path(data).exists():
            raise SystemExit(f"Missing ID dataset file: {data}")


def _dataset_hashes_for_tag(cfg: RunCfg) -> Dict[str, str]:
    def _short(path_s: str) -> str:
        return sha256_file(Path(path_s))[:8]

    if cfg.protocol == "ood":
        assert cfg.data_train is not None and cfg.data_test is not None
        return {"train": _short(cfg.data_train), "test": _short(cfg.data_test), "id": ""}
    return {"train": "", "test": "", "id": _short(cfg.data)}


# ----------------------------
# Attacks
# ----------------------------
@dataclass(frozen=True)
class AttackSpec:
    tag: str
    family_decl: str
    strength_nominal_decl: float
    attack_obj: Any  # None for clean


def _build_attacks(suite: str) -> List[AttackSpec]:
    suite = (suite or "v2").lower().strip()
    specs: List[AttackSpec] = [AttackSpec(tag="clean", family_decl="clean", strength_nominal_decl=0.0, attack_obj=None)]

    drift_alphas = [0.02, 0.05, 0.10]
    signflip_ps = [0.01, 0.05, 0.10]
    noise_sigmas = [0.01, 0.05, 0.10]
    labelflip_rs = [0.01, 0.05, 0.10]
    meanshift_deltas = [0.02, 0.05, 0.10]
    dropout_ps = [0.01, 0.05, 0.10]
    clip_windows = [(1.0, 99.0), (2.5, 97.5), (5.0, 95.0)]
    quant_steps = [0.01, 0.05, 0.10]

    if suite in ("v2", "all", "default"):
        for a in drift_alphas:
            specs.append(
                AttackSpec(
                    tag=f"scaling_drift_alpha_{a:.3f}",
                    family_decl="covariate_shift",
                    strength_nominal_decl=float(abs(a)),
                    attack_obj=ScalingDrift(ScalingDriftCfg(alpha=float(a))),
                )
            )
        for p in signflip_ps:
            specs.append(
                AttackSpec(
                    tag=f"feature_sign_flip_p_{p:.3f}",
                    family_decl="corruption",
                    strength_nominal_decl=float(p),
                    attack_obj=FeatureSignFlip(FeatureSignFlipCfg(p=float(p))),
                )
            )
        for s in noise_sigmas:
            specs.append(
                AttackSpec(
                    tag=f"gaussian_noise_sigma_{s:.3f}",
                    family_decl="noise",
                    strength_nominal_decl=float(s),
                    attack_obj=GaussianNoise(GaussianNoiseCfg(sigma=float(s))),
                )
            )
        for r in labelflip_rs:
            specs.append(
                AttackSpec(
                    tag=f"label_flip_r_{r:.3f}",
                    family_decl="target_shift",
                    strength_nominal_decl=float(r),
                    attack_obj=LabelFlip(LabelFlipCfg(r=float(r))),
                )
            )
        for d in meanshift_deltas:
            specs.append(
                AttackSpec(
                    tag=f"mean_shift_delta_{d:.3f}",
                    family_decl="covariate_shift",
                    strength_nominal_decl=float(abs(d)),
                    attack_obj=MeanShift(MeanShiftCfg(delta=float(d), per_feature=False)),
                )
            )
        for d in meanshift_deltas:
            specs.append(
                AttackSpec(
                    tag=f"mean_shift_pf_delta_{d:.3f}",
                    family_decl="covariate_shift",
                    strength_nominal_decl=float(abs(d)),
                    attack_obj=MeanShift(MeanShiftCfg(delta=float(d), per_feature=True)),
                )
            )
        for p in dropout_ps:
            specs.append(
                AttackSpec(
                    tag=f"feature_dropout_p_{p:.3f}",
                    family_decl="pipeline",
                    strength_nominal_decl=float(p),
                    attack_obj=FeatureDropout(FeatureDropoutCfg(p=float(p), strategy="median"))),
            )
        for lo, hi in clip_windows:
            clip_tail = float(lo + (100.0 - hi))
            specs.append(
                AttackSpec(
                    tag=f"clipping_q_{lo:.1f}_{hi:.1f}",
                    family_decl="distortion",
                    strength_nominal_decl=float(clip_tail),
                    attack_obj=Clipping(ClippingCfg(low_q=float(lo), high_q=float(hi))),
                )
            )
        for st in quant_steps:
            specs.append(
                AttackSpec(
                    tag=f"quantization_step_{st:.3f}",
                    family_decl="distortion",
                    strength_nominal_decl=float(st),
                    attack_obj=Quantization(QuantizationCfg(step=float(st))),
                )
            )
        return specs

    if suite in ("tiny", "smoke"):
        specs.extend(
            [
                AttackSpec("scaling_drift_alpha_0.100", "covariate_shift", 0.10, ScalingDrift(ScalingDriftCfg(alpha=0.10))),
                AttackSpec("feature_sign_flip_p_0.050", "corruption", 0.05, FeatureSignFlip(FeatureSignFlipCfg(p=0.05))),
                AttackSpec("gaussian_noise_sigma_0.050", "noise", 0.05, GaussianNoise(GaussianNoiseCfg(sigma=0.05))),
                AttackSpec("label_flip_r_0.050", "target_shift", 0.05, LabelFlip(LabelFlipCfg(r=0.05))),
            ]
        )
        return specs

    raise ValueError(f"Unknown --attack-suite '{suite}'. Use: v2|all|default|tiny|smoke")


# ----------------------------
# Main
# ----------------------------
def main():
    ap = argparse.ArgumentParser()

    ap.add_argument("--data", type=str, default=str(PATHS.data_dir / "cicids_subset.csv"))
    ap.add_argument("--data-train", type=str, default=None)
    ap.add_argument("--data-test", type=str, default=None)
    ap.add_argument("--svd-dim", type=int, default=8)

    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--split-seed", type=int, default=None)
    ap.add_argument("--model-seed", type=int, default=None)
    ap.add_argument("--non-strict-seeds", action="store_true")

    ap.add_argument("--outdir", type=str, default=str(PATHS.raw_dir / "hais_cicids_runs"))
    ap.add_argument("--run-quantum", action="store_true")

    ap.add_argument("--scale-classical", type=str, default="standard")
    ap.add_argument("--scale-quantum", type=str, default="minmax2pi")

    ap.add_argument("--q-feature-map", type=str, default="zz", choices=["zz", "z", "pauli_xz", "pauli_xyz"])
    ap.add_argument("--q-reps", type=int, default=1)
    ap.add_argument("--q-shots", type=int, default=1024)

    # Shared caps (same for classical + quantum)
    ap.add_argument("--max-train", type=int, default=512, help="Max train samples (0=all). Shared across models.")
    ap.add_argument("--max-test", type=int, default=219, help="Max test samples (0=all). Shared across models.")

    ap.add_argument("--sig-bins", type=int, default=40)
    ap.add_argument("--sig-clip-q-lo", type=float, default=0.005)
    ap.add_argument("--sig-clip-q-hi", type=float, default=0.995)

    ap.add_argument("--mmd-max-samples", type=int, default=512)
    ap.add_argument("--mmd-gamma", type=str, default="median")
    ap.add_argument("--mmd-max-pairs", type=int, default=4096)

    ap.add_argument("--attack-suite", type=str, default="v2")
    ap.add_argument("--atk-meta-keys", type=str, default="")

    args = ap.parse_args()

    strict = not bool(args.non_strict_seeds)
    packed_seed, split_seed, model_seed, seed_semantics = _infer_split_model_seeds(
        seed=int(args.seed),
        split_seed=args.split_seed,
        model_seed=args.model_seed,
        strict=strict,
    )

    protocol = _protocol_from_args(str(args.data), args.data_train, args.data_test)
    _require_dataset_files(protocol, str(args.data), args.data_train, args.data_test)

    atk_meta_whitelist = _parse_meta_keys(args.atk_meta_keys)

    cfg = RunCfg(
        protocol=str(protocol),
        data=str(args.data),
        data_train=str(args.data_train) if args.data_train else None,
        data_test=str(args.data_test) if args.data_test else None,
        svd_dim=int(args.svd_dim),
        seed=int(packed_seed),
        split_seed=int(split_seed),
        model_seed=int(model_seed),
        outdir=str(args.outdir),
        run_quantum=bool(args.run_quantum),
        scale_classical=str(args.scale_classical),
        scale_quantum=str(args.scale_quantum),
        q_feature_map=str(args.q_feature_map),
        q_reps=int(args.q_reps),
        q_shots=int(args.q_shots),
        sig_bins=int(args.sig_bins),
        sig_clip_q_lo=float(args.sig_clip_q_lo),
        sig_clip_q_hi=float(args.sig_clip_q_hi),
        mmd_max_samples=int(args.mmd_max_samples),
        mmd_gamma=str(args.mmd_gamma),
        mmd_max_pairs=int(args.mmd_max_pairs),
        attack_suite=str(args.attack_suite),
        atk_meta_whitelist=tuple(atk_meta_whitelist),
        max_train=int(args.max_train),
        max_test=int(args.max_test),
    )

    cfg_fp = _cfg_fingerprint(cfg)
    outdir = Path(cfg.outdir)
    ensure_dir(outdir)

    clip_q = _parse_quantile_pair(cfg.sig_clip_q_lo, cfg.sig_clip_q_hi)

    mmd_gamma: Union[str, float]
    if cfg.mmd_gamma.lower().strip() == "median":
        mmd_gamma = "median"
    else:
        mmd_gamma = float(cfg.mmd_gamma)

    mmd_cfg = MMDConfig(
        max_samples=int(cfg.mmd_max_samples),
        gamma=mmd_gamma,
        rng_seed=int(cfg.model_seed),
        max_pairs=int(cfg.mmd_max_pairs),
    )

    print(
        f"[RUN] start | protocol={cfg.protocol} split_seed={cfg.split_seed} model_seed={cfg.model_seed} "
        f"svd_dim={cfg.svd_dim} max_train={cfg.max_train} max_test={cfg.max_test} "
        f"run_quantum={cfg.run_quantum} attack_suite={cfg.attack_suite}",
        flush=True,
    )

    # ----------------------------
    # Split/model isolation
    # ----------------------------
    seed_everything(cfg.split_seed)

    print("[RUN] loading dataset...", flush=True)
    t_load0 = time.time()
    if cfg.protocol == "ood":
        assert cfg.data_train is not None and cfg.data_test is not None
        X_tr, y_tr, X_te, y_te = load_cicids_subset(
            CicidsConfig(train_path=Path(cfg.data_train), test_path=Path(cfg.data_test), svd_dim=cfg.svd_dim),
            seed=cfg.split_seed,
        )
    else:
        X_tr, y_tr, X_te, y_te = load_cicids_subset(
            CicidsConfig(path=Path(cfg.data), svd_dim=cfg.svd_dim),
            seed=cfg.split_seed,
        )
    print(f"[RUN] dataset loaded | {time.time() - t_load0:.2f}s", flush=True)

    # Raw sizes before caps
    n_train_raw = int(len(y_tr))
    n_test_raw = int(len(y_te))
    pos_rate_train_raw = float(np.mean(y_tr)) if n_train_raw > 0 else float("nan")
    pos_rate_test_raw = float(np.mean(y_te)) if n_test_raw > 0 else float("nan")

    print(
        f"[RUN] raw split | X_tr={X_tr.shape} X_te={X_te.shape} "
        f"pos_train={pos_rate_train_raw:.4f} pos_test={pos_rate_test_raw:.4f}",
        flush=True,
    )

    # Apply shared caps ONCE (same for classical + quantum)
    subsample_seed = int(_packed_seed(cfg.split_seed, cfg.model_seed))
    t_sub0 = time.time()
    X_tr, y_tr = _stratified_subsample(X_tr, y_tr, int(cfg.max_train), seed=subsample_seed)
    X_te, y_te = _stratified_subsample(X_te, y_te, int(cfg.max_test), seed=subsample_seed + 1)
    print(
        f"[RUN] subsample done | {time.time() - t_sub0:.2f}s | "
        f"X_tr={X_tr.shape} X_te={X_te.shape} "
        f"pos_train={float(np.mean(y_tr)) if len(y_tr) else float('nan'):.4f} "
        f"pos_test={float(np.mean(y_te)) if len(y_te) else float('nan'):.4f}",
        flush=True,
    )

    seed_everything(cfg.model_seed)

    split_info = {
        "protocol": str(cfg.protocol),
        "split_seed": int(cfg.split_seed),
        "model_seed": int(cfg.model_seed),
        "seed_semantics": seed_semantics,
        "packed_seed_if_any": int(cfg.seed) if seed_semantics == "packed" else None,
        "legacy_seed_if_any": int(cfg.seed) if seed_semantics == "legacy" else None,
        "n_train_raw": int(n_train_raw),
        "n_test_raw": int(n_test_raw),
        "pos_rate_train_raw": float(pos_rate_train_raw),
        "pos_rate_test_raw": float(pos_rate_test_raw),
        "n_train": int(len(y_tr)),
        "n_test": int(len(y_te)),
        "pos_rate_train": float(np.mean(y_tr)) if len(y_tr) else float("nan"),
        "pos_rate_test": float(np.mean(y_te)) if len(y_te) else float("nan"),
        "max_train": int(cfg.max_train),
        "max_test": int(cfg.max_test),
        "n_features_pre_scale": int(X_tr.shape[1]),
        "data_paths": {
            "id": str(cfg.data) if cfg.protocol == "id" else None,
            "train": str(cfg.data_train) if cfg.protocol == "ood" else None,
            "test": str(cfg.data_test) if cfg.protocol == "ood" else None,
        },
    }

    attacks = _build_attacks(cfg.attack_suite)
    print(f"[RUN] attacks built | n_attacks={len(attacks)} suite={cfg.attack_suite}", flush=True)

    rows: List[Dict[str, Any]] = []

    def _export_atk_meta(meta: Dict[str, Any]) -> Dict[str, float]:
        if not meta:
            return {}
        if cfg.atk_meta_whitelist:
            items = [(k, meta.get(k)) for k in cfg.atk_meta_whitelist if k in meta]
        else:
            items = list(meta.items())
        return {f"atk_{k}": _as_float_or_nan(v) for k, v in items}

    def _build_run_id(model_family: str, model_label: str, scale_label: str, attack_tag: str) -> str:
        return (
            f"proto{cfg.protocol}__split{cfg.split_seed}__model{cfg.model_seed}__d{cfg.svd_dim}"
            f"__mt{cfg.max_train}__me{cfg.max_test}"
            f"__{model_family}__{model_label}__{scale_label}__{attack_tag}"
            f"__cfg{cfg_fp}"
        )

    def _run_family(
        model_family: str,
        X_tr_f: np.ndarray,
        X_te_f: np.ndarray,
        y_tr_f: np.ndarray,
        y_te_f: np.ndarray,
        model_label: str,
        scale_label: str,
        train_fn: Callable[[np.ndarray, np.ndarray], Any],
        predict_fn: Callable[[Any, np.ndarray], np.ndarray],
        get_scores_fn: Callable[[Any, np.ndarray], Optional[np.ndarray]],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        X_ref = X_tr_f
        n_features = int(X_ref.shape[1])

        clean_ref_run_id = _build_run_id(model_family, model_label, scale_label, "clean")
        clean_ref_attack_seed = _stable_attack_seed(cfg.model_seed, "clean")

        print(
            f"[RUN][{model_family}] baseline signals start | "
            f"X_ref={X_ref.shape} X_te={X_te_f.shape} model={model_label} scale={scale_label}",
            flush=True,
        )
        t_base_sig0 = time.time()
        jsd_clean = float(jsd_feature_shift(X_ref, X_te_f, bins=cfg.sig_bins, clip_q=clip_q))
        mmd_clean = float(mmd_rbf(X_ref, X_te_f, cfg=mmd_cfg))
        ks_mean_clean, ks_rej_clean, ks_n_clean = ks_feature_shift(X_ref, X_te_f)
        print(f"[RUN][{model_family}] baseline signals done | {time.time() - t_base_sig0:.2f}s", flush=True)

        ks_rej_clean_f = float(ks_rej_clean) if (int(ks_n_clean) > 0 and np.isfinite(ks_rej_clean)) else float("nan")

        print(
            f"[RUN][{model_family}] train start | "
            f"X_tr={X_tr_f.shape} X_te={X_te_f.shape} y_tr={y_tr_f.shape} y_te={y_te_f.shape} "
            f"model={model_label} scale={scale_label}",
            flush=True,
        )
        t0 = time.time()
        model = train_fn(X_tr_f, y_tr_f)
        ttrain = float(time.time() - t0)
        print(f"[RUN][{model_family}] train done  | {ttrain:.2f}s", flush=True)

        print(f"[RUN][{model_family}] ref scores start | X={X_te_f.shape}", flush=True)
        t_ref_scores0 = time.time()
        scores_ref = get_scores_fn(model, X_te_f)
        ref_scores_time_s = float(time.time() - t_ref_scores0)
        print(
            f"[RUN][{model_family}] ref scores done  | {ref_scores_time_s:.2f}s "
            f"(available={scores_ref is not None})",
            flush=True,
        )

        score_jsd_clean = (
            float(score_drift_jsd(scores_ref=scores_ref, scores_cur=scores_ref, bins=cfg.sig_bins, clip_q=clip_q))
            if scores_ref is not None
            else float("nan")
        )

        out_rows: List[Dict[str, Any]] = []

        for i, spec in enumerate(attacks, start=1):
            atk_seed = _stable_attack_seed(cfg.model_seed, spec.tag)

            print(
                f"[RUN][{model_family}] attack {i}/{len(attacks)} start | "
                f"tag={spec.tag} family_decl={spec.family_decl} seed={atk_seed}",
                flush=True,
            )

            t1 = time.time()
            X_eval, y_eval, atk_meta = _apply_attack(spec.attack_obj, X_te_f, y_te_f, seed=atk_seed)
            teval_prep = float(time.time() - t1)
            print(
                f"[RUN][{model_family}] attack {i}/{len(attacks)} prep done | "
                f"X_eval={X_eval.shape} y_eval={y_eval.shape} prep={teval_prep:.2f}s",
                flush=True,
            )

            if X_eval.ndim != 2:
                raise RuntimeError(f"Attack {spec.tag} produced X_eval with ndim={X_eval.ndim} (expected 2)")
            if int(X_eval.shape[1]) != int(X_te_f.shape[1]):
                raise RuntimeError(
                    f"Attack {spec.tag} changed n_features: {int(X_eval.shape[1])} vs {int(X_te_f.shape[1])}"
                )
            if int(len(y_eval)) != int(X_eval.shape[0]):
                raise RuntimeError(
                    f"Attack {spec.tag} produced y_eval length {int(len(y_eval))} "
                    f"but X_eval has {int(X_eval.shape[0])} rows"
                )

            attack_family = _meta_family(atk_meta, spec.family_decl)
            attack_strength_nominal = _meta_strength_nominal(atk_meta, spec.strength_nominal_decl)
            attack_strength_eff = _meta_strength_eff(atk_meta, spec.strength_nominal_decl)
            attack_strength = float(attack_strength_nominal)

            tp0 = time.time()
            y_pred = predict_fn(model, X_eval)
            predict_time_s = float(time.time() - tp0)
            print(
                f"[RUN][{model_family}] attack {i}/{len(attacks)} predict done | "
                f"{predict_time_s:.2f}s",
                flush=True,
            )

            tg0 = time.time()
            scores = get_scores_fn(model, X_eval)
            scores_time_s = float(time.time() - tg0)
            print(
                f"[RUN][{model_family}] attack {i}/{len(attacks)} scores done  | "
                f"{scores_time_s:.2f}s (available={scores is not None})",
                flush=True,
            )

            ts0 = time.time()

            print(f"[RUN][{model_family}] attack {i}/{len(attacks)} jsd start", flush=True)
            sig_jsd = float(jsd_feature_shift(X_ref, X_eval, bins=cfg.sig_bins, clip_q=clip_q))

            print(f"[RUN][{model_family}] attack {i}/{len(attacks)} mmd start", flush=True)
            sig_mmd = float(mmd_rbf(X_ref, X_eval, cfg=mmd_cfg))

            print(f"[RUN][{model_family}] attack {i}/{len(attacks)} ks start", flush=True)
            ks_mean, ks_rej, ks_n = ks_feature_shift(X_ref, X_eval)
            ks_rej_f = float(ks_rej) if (int(ks_n) > 0 and np.isfinite(ks_rej)) else float("nan")

            if scores_ref is not None and scores is not None:
                sig_score_jsd = float(
                    score_drift_jsd(scores_ref=scores_ref, scores_cur=scores, bins=cfg.sig_bins, clip_q=clip_q)
                )
                sig_score_jsd_delta = float(sig_score_jsd - score_jsd_clean)
            else:
                sig_score_jsd = float("nan")
                sig_score_jsd_delta = float("nan")

            signals_time_s = float(time.time() - ts0)
            print(
                f"[RUN][{model_family}] attack {i}/{len(attacks)} signals done | "
                f"{signals_time_s:.2f}s (tag={spec.tag})",
                flush=True,
            )

            sig_jsd_delta = float(sig_jsd - jsd_clean)
            sig_mmd_delta = float(sig_mmd - mmd_clean)
            ks_mean_delta = float(ks_mean - ks_mean_clean)

            ks_rej_delta = float("nan")
            if np.isfinite(ks_rej_f) and np.isfinite(ks_rej_clean_f):
                ks_rej_delta = float(ks_rej_f - ks_rej_clean_f)

            label_flip_rate = float("nan") if np.array_equal(y_eval, y_te_f) else float(np.mean(y_eval != y_te_f))
            pred_error_rate = float(np.mean(y_pred != y_eval))

            is_clean = spec.attack_obj is None

            r = {
                "run_id": _build_run_id(model_family, model_label, scale_label, spec.tag),
                "cfg_fingerprint": cfg_fp,

                "clean_ref_run_id": clean_ref_run_id,
                "clean_ref_attack_seed": int(clean_ref_attack_seed),

                "protocol": str(cfg.protocol),
                "seed": int(cfg.seed),
                "split_seed": int(cfg.split_seed),
                "model_seed": int(cfg.model_seed),
                "seed_semantics": seed_semantics,
                "svd_dim": int(cfg.svd_dim),
                "max_train": int(cfg.max_train),
                "max_test": int(cfg.max_test),

                "model_family": model_family,
                "model": model_label,
                "scale": scale_label,
                "n_features": int(n_features),

                "attack": spec.tag,
                "attack_is_clean": int(1 if is_clean else 0),
                "attack_family": str(attack_family),
                "attack_strength": float(attack_strength),
                "attack_strength_nominal": float(attack_strength_nominal),
                "attack_strength_eff": float(attack_strength_eff),
                "attack_seed": int(atk_seed),

                "integrity_jsd_clean": float(jsd_clean),
                "integrity_jsd": float(sig_jsd),
                "integrity_jsd_delta": float(sig_jsd_delta),

                "integrity_mmd_clean": float(mmd_clean),
                "integrity_mmd": float(sig_mmd),
                "integrity_mmd_delta": float(sig_mmd_delta),

                "integrity_ks_mean_clean": float(ks_mean_clean),
                "integrity_ks_mean": float(ks_mean),
                "integrity_ks_mean_delta": float(ks_mean_delta),

                "integrity_ks_reject05_clean": float(ks_rej_clean_f),
                "integrity_ks_reject05": float(ks_rej_f),
                "integrity_ks_reject05_delta": float(ks_rej_delta),

                "integrity_ks_n_clean": int(ks_n_clean),
                "integrity_ks_n": int(ks_n),

                "integrity_score_jsd_clean": float(score_jsd_clean),
                "integrity_score_jsd": float(sig_score_jsd),
                "integrity_score_jsd_delta": float(sig_score_jsd_delta),

                "signals_time_s": float(signals_time_s),
                "train_time_s": float(ttrain),
                "attack_prep_time_s": float(teval_prep),
                "predict_time_s": float(predict_time_s),
                "scores_time_s": float(scores_time_s),
                "ref_scores_time_s": float(ref_scores_time_s),

                "label_flip_rate": float(label_flip_rate),
                "pred_error_rate": float(pred_error_rate),

                **_metrics(y_eval, y_pred, scores),
                **_export_atk_meta(atk_meta or {}),
            }
            out_rows.append(r)

        summary = {
            "jsd_clean": float(jsd_clean),
            "mmd_clean": float(mmd_clean),
            "ks_mean_clean": float(ks_mean_clean),
            "ks_reject05_clean": float(ks_rej_clean_f),
            "score_jsd_clean": float(score_jsd_clean),
            "n_features": int(n_features),
            "clean_ref_run_id": clean_ref_run_id,
            "clean_ref_attack_seed": int(clean_ref_attack_seed),
            "ref_scores_time_s": float(ref_scores_time_s),
            "train_time_s": float(ttrain),
        }
        return out_rows, summary

    # ----------------------------
    # Classical
    # ----------------------------
    print("[RUN] classical scaling start", flush=True)
    scaler_c = build_scaler(cfg.scale_classical)
    t_sc0 = time.time()
    X_tr_c, X_te_c = fit_transform_scaler(scaler_c, X_tr, X_te)
    print(f"[RUN] classical scaling done | {time.time() - t_sc0:.2f}s | X_tr={X_tr_c.shape} X_te={X_te_c.shape}", flush=True)

    def _train_classical(Xa, ya):
        return train_classical_svc(Xa, ya, ClassicalCfg())

    def _pred_classical(m, Xx):
        return m.predict(Xx)

    def _scores_classical(m, Xx):
        return _get_scores(m, Xx)

    rows_c, summary_c = _run_family(
        model_family="classical",
        X_tr_f=X_tr_c,
        X_te_f=X_te_c,
        y_tr_f=y_tr,
        y_te_f=y_te,
        model_label="svc_rbf",
        scale_label=cfg.scale_classical,
        train_fn=_train_classical,
        predict_fn=_pred_classical,
        get_scores_fn=_scores_classical,
    )
    rows.extend(rows_c)
    print(f"[RUN] classical done | rows={len(rows_c)}", flush=True)

    # ----------------------------
    # Quantum (optional)
    # ----------------------------
    scaler_q = None
    summary_q: Optional[Dict[str, Any]] = None

    if cfg.run_quantum:
        if not QISKIT_OK:
            print("[WARN] Qiskit ML not available. Skipping quantum.", flush=True)
        else:
            print("[RUN] quantum scaling start", flush=True)
            scaler_q = build_scaler(cfg.scale_quantum)
            t_sq0 = time.time()
            X_tr_q, X_te_q = fit_transform_scaler(scaler_q, X_tr, X_te)
            print(
                f"[RUN] quantum scaling done | {time.time() - t_sq0:.2f}s | "
                f"X_tr={X_tr_q.shape} X_te={X_te_q.shape}",
                flush=True,
            )

            qcfg = QuantumCfg(
                feature_map=cfg.q_feature_map,
                reps=cfg.q_reps,
                shots=cfg.q_shots,
                seed=cfg.model_seed,
                # útil para diagnóstico; quítalo o súbelo si ves convergencia corta
                max_iter=2000,
            )

            print(
                f"[RUN] quantum config | fmap={qcfg.feature_map} reps={qcfg.reps} "
                f"shots={qcfg.shots} seed={qcfg.seed} max_iter={qcfg.max_iter}",
                flush=True,
            )

            def _train_quantum(Xa, ya):
                # returns (model, fmap, qkernel)
                model, _fmap, _qkernel = train_qsvc(Xa, ya, qcfg)
                return model

            def _pred_quantum(m, Xx):
                return predict_qsvc(m, Xx)

            def _scores_quantum(m, Xx):
                return scores_qsvc(m, Xx)

            rows_q, summary_q = _run_family(
                model_family="quantum",
                X_tr_f=X_tr_q,
                X_te_f=X_te_q,
                y_tr_f=y_tr,
                y_te_f=y_te,
                model_label=f"qsvc_{qcfg.feature_map}_r{qcfg.reps}",
                scale_label=cfg.scale_quantum,
                train_fn=_train_quantum,
                predict_fn=_pred_quantum,
                get_scores_fn=_scores_quantum,
            )
            rows.extend(rows_q)
            print(f"[RUN] quantum done | rows={len(rows_q)}", flush=True)
    else:
        print("[RUN] quantum disabled", flush=True)

    print("[RUN] building dataframe...", flush=True)
    df = (
        pd.DataFrame(rows)
        .sort_values(
            ["protocol", "model_family", "attack_is_clean", "attack_family", "attack_strength_nominal", "attack", "attack_strength_eff"],
            ascending=[True, True, False, True, True, True, True],
        )
        .reset_index(drop=True)
    )
    print(f"[RUN] dataframe ready | shape={df.shape}", flush=True)

    qtag = f"__qfm{cfg.q_feature_map}__qr{cfg.q_reps}__qs{cfg.q_shots}" if cfg.run_quantum else "__qnone"
    dh = _dataset_hashes_for_tag(cfg)
    dtag = f"__id{dh['id']}" if cfg.protocol == "id" else f"__tr{dh['train']}__te{dh['test']}"

    run_tag = (
        f"proto{cfg.protocol}{dtag}"
        f"__seed{cfg.seed}__split{cfg.split_seed}__model{cfg.model_seed}__d{cfg.svd_dim}"
        f"__mt{cfg.max_train}__me{cfg.max_test}"
        f"__c{cfg.scale_classical}__q{cfg.scale_quantum}"
        f"__atk{cfg.attack_suite}{qtag}__cfg{cfg_fp}"
    )
    out_csv = outdir / f"run__{run_tag}.csv"

    print(f"[RUN] writing csv -> {out_csv}", flush=True)
    t_csv0 = time.time()
    df.to_csv(out_csv, index=False)
    print(f"[RUN] csv written | {time.time() - t_csv0:.2f}s", flush=True)

    meta = {
        "run_cfg": asdict(cfg),
        "cfg_fingerprint": cfg_fp,
        "seed_semantics": seed_semantics,
        "qiskit_ok": bool(QISKIT_OK),
        "paths": {
            "csv": str(out_csv),
            "data_id": str(cfg.data) if cfg.protocol == "id" else None,
            "data_train": str(cfg.data_train) if cfg.protocol == "ood" else None,
            "data_test": str(cfg.data_test) if cfg.protocol == "ood" else None,
        },
        "hashes": {
            "data_sha256": sha256_file(Path(cfg.data)) if cfg.protocol == "id" else None,
            "train_sha256": sha256_file(Path(cfg.data_train)) if (cfg.protocol == "ood" and cfg.data_train) else None,
            "test_sha256": sha256_file(Path(cfg.data_test)) if (cfg.protocol == "ood" and cfg.data_test) else None,
            "csv_sha256": sha256_file(out_csv),
        },
        "split": split_info,
        "scalers": {
            "classical": scaler_info(scaler_c),
            "quantum": scaler_info(scaler_q) if (cfg.run_quantum and QISKIT_OK) else {"type": "none"},
        },
        "summary": {
            "n_rows": int(df.shape[0]),
            "ran_quantum": bool(cfg.run_quantum and QISKIT_OK),
            "classical": summary_c,
            "quantum": summary_q,
        },
        "env": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }
    out_json = outdir / f"run__{run_tag}.json"

    print(f"[RUN] writing json -> {out_json}", flush=True)
    t_json0 = time.time()
    write_json(out_json, meta)
    print(f"[RUN] json written | {time.time() - t_json0:.2f}s", flush=True)

    print(f"[OK] Wrote {out_csv}")
    print(f"[OK] Wrote {out_json}")
    print(df)


if __name__ == "__main__":
    main()