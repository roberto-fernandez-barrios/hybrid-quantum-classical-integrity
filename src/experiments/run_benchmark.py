# src/experiments/run_benchmark.py
# MAX-LEVEL VERSION
#
# Main goals for the auditability-gap paper:
#   - compare by CONCRETE MODEL, not only by family
#   - support multiple quantum feature maps in one run
#   - add paper-focused attack suites:
#       * paper_core
#       * paper_support
#       * paper_sham
#       * paper_full
#   - add prior-preserving label flip attack
#   - add sham controls
#   - add label-aware + prediction-aware auditability signals
#   - add confusion-profile auditability signals
#   - export raw rows rich enough for aggregation without guesswork
#   - keep backward compatibility with current CLI as much as possible
#
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from src.config import PATHS
from src.datasets.cicids_subset import CicidsConfig, load_cicids_subset
from src.qml.classical import ClassicalCfg, train_classical_svc
from src.qml.quantum_qsvc import QISKIT_OK, QuantumCfg, predict_qsvc, scores_qsvc, train_qsvc
from src.utils.io import ensure_dir
from src.utils.seed import seed_everything

# Attacks
from src.attacks.clipping import Clipping, ClippingCfg
from src.attacks.feature_dropout import FeatureDropout, FeatureDropoutCfg
from src.attacks.feature_sign_flip import FeatureSignFlip, FeatureSignFlipCfg
from src.attacks.gaussian_noise import GaussianNoise, GaussianNoiseCfg
from src.attacks.label_flip import LabelFlip, LabelFlipCfg
from src.attacks.label_flip_prior_preserving import (
    LabelFlipPriorPreserving,
    LabelFlipPriorPreservingCfg,
)
from src.attacks.mean_shift import MeanShift, MeanShiftCfg
from src.attacks.cluster_preserving import ClusterPreservingCfg, ClusterPreservingPerturbation
from src.attacks.quantization import Quantization, QuantizationCfg
from src.attacks.scaling_drift import ScalingDrift, ScalingDriftCfg
from src.attacks.sham import (
    CleanResample,
    CleanResampleCfg,
    IdentityAttack,
    TinyGaussianNoise,
    TinyScalingDrift,
)
from src.qml.classical import select_svc_params_cv
from src.qml.quantum_qsvc import select_qsvc_C_cv

from src.integrity.signals import (
    MMDConfig,
    jsd_feature_shift,
    ks_feature_shift,
    mmd_rbf,
    score_drift_jsd,
)

ALLOWED_Q_FEATURE_MAPS: Tuple[str, ...] = ("zz", "z", "pauli_xz", "pauli_xyz")
ALLOWED_CLASSICAL_MODELS: Tuple[str, ...] = ("svc_rbf",)
_PACK_MULT = 1_000_000


# ============================================================
# Small utilities
# ============================================================

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def _as_float_or_nan(x: Any) -> float:
    try:
        v = float(x)
        return float(v) if np.isfinite(v) else float("nan")
    except Exception:
        return float("nan")


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


def _metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    scores: Optional[np.ndarray],
) -> Dict[str, float]:
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)

    return {
        "bal_acc": float(balanced_accuracy_score(y_true, y_pred)),
        "f1_pos": float(f1_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "pos_rate_eval": float(np.mean(y_true)),
        "roc_auc": _safe_roc_auc(y_true, scores),
    }


def _get_scores(model: Any, X: np.ndarray) -> Optional[np.ndarray]:
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


def _binary_pmf_from_labels(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y).astype(int).reshape(-1)

    if y.size == 0:
        return np.array([0.5, 0.5], dtype=float)

    p1 = float(np.mean(y == 1))
    p0 = 1.0 - p1
    pmf = np.array([p0, p1], dtype=float)
    pmf = np.clip(pmf, 1e-12, 1.0)
    return pmf / float(pmf.sum())


def _binary_jsd_from_labels(y_ref: np.ndarray, y_cur: np.ndarray) -> float:
    p = _binary_pmf_from_labels(y_ref)
    q = _binary_pmf_from_labels(y_cur)
    m = 0.5 * (p + q)

    def _kl(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.sum(a * np.log(a / b)))

    return float(0.5 * _kl(p, m) + 0.5 * _kl(q, m))


def _safe_absdiff(a: float, b: float) -> float:
    if np.isfinite(a) and np.isfinite(b):
        return float(abs(a - b))
    return float("nan")


def _prediction_disagreement_rate(y_pred_ref: np.ndarray, y_pred_cur: np.ndarray) -> float:
    a = np.asarray(y_pred_ref).astype(int).reshape(-1)
    b = np.asarray(y_pred_cur).astype(int).reshape(-1)

    if a.shape != b.shape or a.size == 0:
        return float("nan")

    return float(np.mean(a != b))


def _safe_signed_drop(cur: float, ref: float) -> float:
    """
    Convention:
      drop = current - clean

    Negative value => performance decreased.
    Positive value => performance improved.
    """
    if np.isfinite(cur) and np.isfinite(ref):
        return float(cur - ref)
    return float("nan")


def _safe_positive_impact(ref: float, cur: float) -> float:
    """
    For metrics where higher is better.
    """
    if np.isfinite(ref) and np.isfinite(cur):
        return float(max(0.0, ref - cur))
    return float("nan")


def _safe_positive_impact_error(cur: float, ref: float) -> float:
    """
    For error metrics where higher is worse.
    """
    if np.isfinite(cur) and np.isfinite(ref):
        return float(max(0.0, cur - ref))
    return float("nan")


def _parse_choice_list(raw: str, allowed: Sequence[str], *, name: str) -> Tuple[str, ...]:
    s = (raw or "").strip()
    if not s:
        return tuple()

    parts: List[str] = []
    for chunk in s.replace(";", ",").split(","):
        chunk = chunk.strip()
        if chunk:
            parts.append(chunk)

    seen = set()
    out: List[str] = []

    for p in parts:
        if p not in allowed:
            raise ValueError(f"Invalid {name} '{p}'. Allowed: {list(allowed)}")

        if p not in seen:
            out.append(p)
            seen.add(p)

    return tuple(out)


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


def _parse_quantile_pair(lo: float, hi: float) -> Tuple[float, float]:
    lo = float(lo)
    hi = float(hi)

    if not (0.0 <= lo < hi <= 1.0):
        raise ValueError("Quantiles must satisfy 0 <= lo < hi <= 1")

    return lo, hi


def _packed_seed(split_seed: int, model_seed: int) -> int:
    ss = int(split_seed)
    ms = int(model_seed)

    if ss < 0:
        raise ValueError(f"split_seed={ss} must be >= 0 for packing.")

    if ms < 0 or ms >= _PACK_MULT:
        raise ValueError(
            f"model_seed={ms} out of range for packing "
            f"(need 0 <= model_seed < {_PACK_MULT})."
        )

    return ss * _PACK_MULT + ms


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
            raise SystemExit(
                "If you pass --split-seed you must also pass --model-seed "
                "(and vice versa)."
            )
        return int(seed), int(seed), int(seed), "legacy"

    if has_split and has_model:
        packed = _packed_seed(int(split_seed), int(model_seed))
        return int(packed), int(split_seed), int(model_seed), "packed"

    return int(seed), int(seed), int(seed), "legacy"


def _stable_attack_seed(model_seed: int, attack_tag: str) -> int:
    h = hashlib.sha1(attack_tag.encode("utf-8")).digest()
    tag_u32 = int.from_bytes(h[:4], byteorder="little", signed=False)
    return int((int(model_seed) ^ tag_u32) & 0xFFFFFFFF)


def _protocol_from_args(data: str, data_train: Optional[str], data_test: Optional[str]) -> str:
    has_tr = bool(data_train)
    has_te = bool(data_test)

    if has_tr or has_te:
        if not (has_tr and has_te):
            raise SystemExit("For OOD mode you must pass BOTH --data-train and --data-test.")
        return "ood"

    return "id"


def _require_dataset_files(
    protocol: str,
    data: str,
    data_train: Optional[str],
    data_test: Optional[str],
) -> None:
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


# ============================================================
# Confusion-profile signals
# ============================================================

def _pmf_jsd(p: np.ndarray, q: np.ndarray) -> float:
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)

    p = np.clip(p, 1e-12, None)
    q = np.clip(q, 1e-12, None)

    p = p / float(p.sum())
    q = q / float(q.sum())

    m = 0.5 * (p + q)

    def _kl(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.sum(a * np.log(a / b)))

    return float(0.5 * _kl(p, m) + 0.5 * _kl(q, m))


def _confusion_profile_pmf(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    y_true = np.asarray(y_true).astype(int).reshape(-1)
    y_pred = np.asarray(y_pred).astype(int).reshape(-1)

    if y_true.shape != y_pred.shape or y_true.size == 0:
        return np.array([0.25, 0.25, 0.25, 0.25], dtype=float)

    tn = float(np.sum((y_true == 0) & (y_pred == 0)))
    fp = float(np.sum((y_true == 0) & (y_pred == 1)))
    fn = float(np.sum((y_true == 1) & (y_pred == 0)))
    tp = float(np.sum((y_true == 1) & (y_pred == 1)))

    pmf = np.array([tn, fp, fn, tp], dtype=float)
    pmf = np.clip(pmf, 1e-12, None)

    return pmf / float(pmf.sum())


def _confusion_profile_shift(
    y_true_ref: np.ndarray,
    y_pred_ref: np.ndarray,
    y_true_cur: np.ndarray,
    y_pred_cur: np.ndarray,
) -> Tuple[float, float]:
    p = _confusion_profile_pmf(y_true_ref, y_pred_ref)
    q = _confusion_profile_pmf(y_true_cur, y_pred_cur)

    l1 = float(np.sum(np.abs(p - q)))
    jsd = float(_pmf_jsd(p, q))

    return l1, jsd


# ============================================================
# Attack compatibility / metadata
# ============================================================

def _apply_attack(
    atk: Any,
    X: np.ndarray,
    y: np.ndarray,
    seed: int,
    pool: Optional[Dict[str, Any]] = None,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Compatibility wrapper:
      - Pool-aware null controls: apply(X, seed=seed, y=y, pool=pool)
      - Preferred: apply(X, seed=seed, y=y)
      - Backward: apply(X, y=y, seed=seed) or apply(X, seed=seed)
    """
    if atk is None:
        return np.asarray(X), np.asarray(y), {}

    if bool(getattr(atk, "needs_pool", False)):
        out = atk.apply(X, seed=seed, y=y, pool=pool)
    else:
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


def _meta_family(meta: Dict[str, Any], fallback: str) -> str:
    fam = meta.get("family", None)
    return str(fallback) if fam is None else str(fam)


def _meta_priority_group(meta: Dict[str, Any], fallback: str) -> str:
    pg = meta.get("priority_group", None)
    return str(fallback) if pg is None else str(pg)


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


# ============================================================
# Subsampling
# ============================================================

def _stratified_subsample_indices(
    y: np.ndarray,
    n_max: int,
    *,
    seed: int,
) -> np.ndarray:
    """
    Indices of a stratified subsample of at most n_max rows.

    This is the exact random-number sequence used by the frozen 1.0.0 runs;
    it must not change, otherwise the frozen evaluation batches would differ.
    """
    y = np.asarray(y).astype(int)

    if n_max <= 0 or len(y) <= n_max:
        return np.arange(len(y))

    rng = np.random.default_rng(int(seed))
    idx_all = np.arange(len(y))

    classes, counts = np.unique(y, return_counts=True)
    frac = float(n_max) / float(len(y))

    chosen: List[np.ndarray] = []

    for c, cnt in zip(classes, counts):
        idx_c = idx_all[y == c]
        k = max(1, int(round(float(cnt) * frac)))
        k = min(k, len(idx_c))
        chosen.append(rng.choice(idx_c, size=k, replace=False))

    idx = np.concatenate(chosen) if chosen else rng.choice(idx_all, size=n_max, replace=False)

    if len(idx) > n_max:
        idx = rng.choice(idx, size=n_max, replace=False)

    return np.sort(idx)


def _stratified_subsample(
    X: np.ndarray,
    y: np.ndarray,
    n_max: int,
    *,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Stratified subsample to at most n_max rows.
    Deterministic via seed.
    """
    X = np.asarray(X)
    y = np.asarray(y).astype(int)

    if n_max <= 0 or len(y) <= n_max:
        return X, y

    idx = _stratified_subsample_indices(y, n_max, seed=seed)
    return X[idx], y[idx]


# ============================================================
# Scaling
# ============================================================

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


def fit_transform_scaler(
    scaler: Any,
    X_tr: np.ndarray,
    X_te: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    if scaler is None:
        return np.asarray(X_tr), np.asarray(X_te)

    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)

    return np.asarray(X_tr_s), np.asarray(X_te_s)


def scaler_info(scaler: Any) -> Dict[str, Any]:
    if scaler is None:
        return {"type": "none"}

    info: Dict[str, Any] = {"type": scaler.__class__.__name__}

    if isinstance(scaler, MinMaxScaler):
        info["feature_range"] = tuple(map(float, scaler.feature_range))

    if isinstance(scaler, StandardScaler):
        info["with_mean"] = bool(getattr(scaler, "with_mean", True))
        info["with_std"] = bool(getattr(scaler, "with_std", True))

    return info


# ============================================================
# Config dataclasses
# ============================================================

@dataclass(frozen=True)
class AttackSpec:
    tag: str
    family_decl: str
    strength_nominal_decl: float
    priority_group_decl: str
    attack_obj: Any


@dataclass(frozen=True)
class RunCfg:
    protocol: str
    data: str
    data_train: Optional[str]
    data_test: Optional[str]
    svd_dim: int

    seed: int
    split_seed: int
    model_seed: int

    outdir: str

    classical_models: Tuple[str, ...]
    run_quantum: bool
    q_feature_maps: Tuple[str, ...]
    q_reps: int
    q_shots: int
    q_backend_method: str
    q_max_iter: int

    scale_classical: str
    scale_quantum: str

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

    # Reinforcement gates (artifact 1.1.0). Defaults reproduce the frozen 1.0.0
    # behaviour exactly and are excluded from the fingerprint when at default,
    # so historical run identifiers and file names are unchanged.
    svc_tune: str = "none"
    qsvc_tune: str = "none"


_FINGERPRINT_DEFAULT_EXCLUDED: Dict[str, Any] = {"svc_tune": "none", "qsvc_tune": "none"}


def _cfg_fingerprint(cfg: RunCfg) -> str:
    payload_dict = asdict(cfg)
    for key, default in _FINGERPRINT_DEFAULT_EXCLUDED.items():
        if payload_dict.get(key) == default:
            payload_dict.pop(key, None)
    payload = json.dumps(payload_dict, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:10]


def _dataset_hashes_for_tag(cfg: RunCfg) -> Dict[str, str]:
    def _short(path_s: str) -> str:
        return sha256_file(Path(path_s))[:8]

    if cfg.protocol == "ood":
        assert cfg.data_train is not None and cfg.data_test is not None
        return {
            "train": _short(cfg.data_train),
            "test": _short(cfg.data_test),
            "id": "",
        }

    return {
        "train": "",
        "test": "",
        "id": _short(cfg.data),
    }


def _dataset_tag_from_hashes(protocol: str, hashes_short: Dict[str, str]) -> str:
    if protocol == "ood":
        return f"tr{hashes_short['train']}__te{hashes_short['test']}"
    return f"id{hashes_short['id']}"


# ============================================================
# Attack suite builder
# ============================================================

def _build_attacks(suite: str) -> List[AttackSpec]:
    suite = (suite or "v2").lower().strip()

    specs: List[AttackSpec] = [
        AttackSpec(
            tag="clean",
            family_decl="clean",
            strength_nominal_decl=0.0,
            priority_group_decl="clean",
            attack_obj=None,
        )
    ]

    def _add(tag: str, family: str, strength: float, priority: str, obj: Any) -> None:
        specs.append(
            AttackSpec(
                tag=tag,
                family_decl=family,
                strength_nominal_decl=float(strength),
                priority_group_decl=priority,
                attack_obj=obj,
            )
        )

    sev_core = [0.02, 0.05, 0.10]
    sev_support = [0.02, 0.05, 0.10]

    if suite in ("paper_sham", "sham"):
        _add(
            "sham_identity",
            "sham",
            0.0,
            "sham",
            IdentityAttack(),
        )
        _add(
            "sham_tiny_gaussian_sigma_0.001",
            "sham",
            0.001,
            "sham",
            TinyGaussianNoise(),
        )
        _add(
            "sham_tiny_scaling_alpha_0.001",
            "sham",
            0.001,
            "sham",
            TinyScalingDrift(),
        )
        return specs

    if suite in ("paper_null", "null"):
        # Null-calibration gate (artifact 1.1.0): 20 independent clean draws from
        # the calibration half of the held-out pool, 20 from the disjoint
        # evaluation half, plus the three benign specificity controls.
        for k in range(1, 21):
            _add(
                f"clean_resample_calib_{k:02d}",
                "null_control",
                0.0,
                "null_calibration",
                CleanResample(CleanResampleCfg(pool_half="calibration", draw_index=k)),
            )
        for k in range(1, 21):
            _add(
                f"clean_resample_eval_{k:02d}",
                "null_control",
                0.0,
                "null_evaluation",
                CleanResample(CleanResampleCfg(pool_half="evaluation", draw_index=k)),
            )
        specs.extend(_build_attacks("paper_sham")[1:])
        return specs

    if suite in ("paper_f5", "f5"):
        # Adversarial Gate A (artifact 1.3.0): the two executed feature-side drift
        # mechanisms at the frozen strengths as matched controls (identical tags
        # and therefore identical attack seeds to ``paper_core``), plus the
        # adaptive cluster-preserving variants of both mechanisms on the
        # prespecified strength grid (``manuscript/paper15_v13_prereg.md``).
        f5_strengths = [0.02, 0.05, 0.10, 0.25, 0.50]
        for a in sev_core:
            _add(
                f"scaling_drift_alpha_{a:.3f}",
                "covariate_shift",
                a,
                "core",
                ScalingDrift(ScalingDriftCfg(alpha=float(a))),
            )
        for d in sev_core:
            _add(
                f"mean_shift_pf_delta_{d:.3f}",
                "covariate_shift",
                d,
                "core",
                MeanShift(MeanShiftCfg(delta=float(d), per_feature=True)),
            )
        for d in f5_strengths:
            _add(
                f"cluster_preserving_mean_shift_delta_{d:.3f}",
                "adaptive_covariate_shift",
                d,
                "adaptive",
                ClusterPreservingPerturbation(ClusterPreservingCfg(mechanism="mean_shift", strength=float(d))),
            )
        for a in f5_strengths:
            _add(
                f"cluster_preserving_scaling_alpha_{a:.3f}",
                "adaptive_covariate_shift",
                a,
                "adaptive",
                ClusterPreservingPerturbation(ClusterPreservingCfg(mechanism="scaling_drift", strength=float(a))),
            )
        return specs

    if suite in ("paper_core", "core"):
        for r in sev_core:
            _add(
                f"label_flip_r_{r:.3f}",
                "target_shift",
                r,
                "core",
                LabelFlip(LabelFlipCfg(r=float(r))),
            )

        for r in sev_core:
            _add(
                f"label_flip_prior_preserving_r_{r:.3f}",
                "target_shift",
                r,
                "core",
                LabelFlipPriorPreserving(LabelFlipPriorPreservingCfg(r=float(r))),
            )

        for p in sev_core:
            _add(
                f"feature_sign_flip_p_{p:.3f}",
                "corruption",
                p,
                "core",
                FeatureSignFlip(FeatureSignFlipCfg(p=float(p))),
            )

        for a in sev_core:
            _add(
                f"scaling_drift_alpha_{a:.3f}",
                "covariate_shift",
                a,
                "core",
                ScalingDrift(ScalingDriftCfg(alpha=float(a))),
            )

        for d in sev_core:
            _add(
                f"mean_shift_pf_delta_{d:.3f}",
                "covariate_shift",
                d,
                "core",
                MeanShift(MeanShiftCfg(delta=float(d), per_feature=True)),
            )

        for p in sev_core:
            _add(
                f"feature_dropout_p_{p:.3f}",
                "pipeline",
                p,
                "core",
                FeatureDropout(FeatureDropoutCfg(p=float(p), strategy="median")),
            )

        return specs

    if suite in ("paper_support", "support"):
        for s in sev_support:
            _add(
                f"gaussian_noise_sigma_{s:.3f}",
                "noise",
                s,
                "support",
                GaussianNoise(GaussianNoiseCfg(sigma=float(s))),
            )

        for st in sev_support:
            _add(
                f"quantization_step_{st:.3f}",
                "distortion",
                st,
                "support",
                Quantization(QuantizationCfg(step=float(st))),
            )

        for lo, hi in [(1.0, 99.0), (2.5, 97.5), (5.0, 95.0)]:
            clip_tail = float(lo + (100.0 - hi))
            _add(
                f"clipping_q_{lo:.1f}_{hi:.1f}",
                "distortion",
                clip_tail,
                "support",
                Clipping(ClippingCfg(low_q=float(lo), high_q=float(hi))),
            )

        return specs

    if suite in ("paper_full", "paper_all"):
        return (
            _build_attacks("paper_core")
            + _build_attacks("paper_support")[1:]
            + _build_attacks("paper_sham")[1:]
        )

    if suite in ("v2", "all", "default"):
        for a in [0.02, 0.05, 0.10]:
            _add(
                f"scaling_drift_alpha_{a:.3f}",
                "covariate_shift",
                a,
                "core" if a in (0.05, 0.10) else "aux",
                ScalingDrift(ScalingDriftCfg(alpha=float(a))),
            )

        for p in [0.01, 0.05, 0.10]:
            _add(
                f"feature_sign_flip_p_{p:.3f}",
                "corruption",
                p,
                "core" if p in (0.05, 0.10) else "aux",
                FeatureSignFlip(FeatureSignFlipCfg(p=float(p))),
            )

        for s in [0.01, 0.05, 0.10]:
            _add(
                f"gaussian_noise_sigma_{s:.3f}",
                "noise",
                s,
                "support" if s in (0.05, 0.10) else "aux",
                GaussianNoise(GaussianNoiseCfg(sigma=float(s))),
            )

        for r in [0.01, 0.05, 0.10]:
            _add(
                f"label_flip_r_{r:.3f}",
                "target_shift",
                r,
                "core" if r in (0.05, 0.10) else "aux",
                LabelFlip(LabelFlipCfg(r=float(r))),
            )

        for r in [0.01, 0.05, 0.10]:
            _add(
                f"label_flip_prior_preserving_r_{r:.3f}",
                "target_shift",
                r,
                "core" if r in (0.05, 0.10) else "aux",
                LabelFlipPriorPreserving(LabelFlipPriorPreservingCfg(r=float(r))),
            )

        for d in [0.02, 0.05, 0.10]:
            _add(
                f"mean_shift_delta_{d:.3f}",
                "covariate_shift",
                d,
                "aux",
                MeanShift(MeanShiftCfg(delta=float(d), per_feature=False)),
            )

        for d in [0.02, 0.05, 0.10]:
            _add(
                f"mean_shift_pf_delta_{d:.3f}",
                "covariate_shift",
                d,
                "core" if d in (0.05, 0.10) else "aux",
                MeanShift(MeanShiftCfg(delta=float(d), per_feature=True)),
            )

        for p in [0.01, 0.05, 0.10]:
            _add(
                f"feature_dropout_p_{p:.3f}",
                "pipeline",
                p,
                "core" if p in (0.05, 0.10) else "aux",
                FeatureDropout(FeatureDropoutCfg(p=float(p), strategy="median")),
            )

        for lo, hi in [(1.0, 99.0), (2.5, 97.5), (5.0, 95.0)]:
            clip_tail = float(lo + (100.0 - hi))
            _add(
                f"clipping_q_{lo:.1f}_{hi:.1f}",
                "distortion",
                clip_tail,
                "support" if (lo, hi) in ((2.5, 97.5), (5.0, 95.0)) else "aux",
                Clipping(ClippingCfg(low_q=float(lo), high_q=float(hi))),
            )

        for st in [0.01, 0.05, 0.10]:
            _add(
                f"quantization_step_{st:.3f}",
                "distortion",
                st,
                "support" if st in (0.05, 0.10) else "aux",
                Quantization(QuantizationCfg(step=float(st))),
            )

        return specs

    if suite in ("tiny", "smoke"):
        _add(
            "scaling_drift_alpha_0.100",
            "covariate_shift",
            0.10,
            "core",
            ScalingDrift(ScalingDriftCfg(alpha=0.10)),
        )

        _add(
            "feature_sign_flip_p_0.050",
            "corruption",
            0.05,
            "core",
            FeatureSignFlip(FeatureSignFlipCfg(p=0.05)),
        )

        _add(
            "gaussian_noise_sigma_0.050",
            "noise",
            0.05,
            "support",
            GaussianNoise(GaussianNoiseCfg(sigma=0.05)),
        )

        _add(
            "label_flip_r_0.050",
            "target_shift",
            0.05,
            "core",
            LabelFlip(LabelFlipCfg(r=0.05)),
        )

        _add(
            "label_flip_prior_preserving_r_0.050",
            "target_shift",
            0.05,
            "core",
            LabelFlipPriorPreserving(LabelFlipPriorPreservingCfg(r=0.05)),
        )

        _add(
            "sham_identity",
            "sham",
            0.0,
            "sham",
            IdentityAttack(),
        )

        return specs

    raise ValueError(
        f"Unknown --attack-suite '{suite}'. "
        f"Use: paper_core|paper_support|paper_sham|paper_null|paper_f5|paper_full|v2|all|default|tiny|smoke"
    )


# ============================================================
# Main
# ============================================================

def main() -> None:
    ap = argparse.ArgumentParser()

    # Data
    ap.add_argument("--data", type=str, default=str(PATHS.data_dir / "cicids_subset.csv"))
    ap.add_argument("--data-train", type=str, default=None)
    ap.add_argument("--data-test", type=str, default=None)
    ap.add_argument("--svd-dim", type=int, default=8)

    # Seeds
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--split-seed", type=int, default=None)
    ap.add_argument("--model-seed", type=int, default=None)
    ap.add_argument("--non-strict-seeds", action="store_true")

    # Output
    ap.add_argument("--outdir", type=str, default=str(PATHS.raw_dir / "hais_cicids_runs"))

    # Classical
    ap.add_argument(
        "--classical-models",
        type=str,
        default="svc_rbf",
        help="Comma-separated classical models. Current project support: svc_rbf",
    )

    # Quantum
    ap.add_argument("--run-quantum", action="store_true")
    ap.add_argument(
        "--q-feature-map",
        type=str,
        default="zz",
        choices=list(ALLOWED_Q_FEATURE_MAPS),
        help="Legacy single quantum feature map.",
    )
    ap.add_argument(
        "--q-feature-maps",
        type=str,
        default="",
        help="Comma-separated quantum feature maps, e.g. zz,z,pauli_xz,pauli_xyz",
    )
    ap.add_argument("--q-reps", type=int, default=1)
    ap.add_argument("--q-shots", type=int, default=1024)
    ap.add_argument(
        "--q-backend-method",
        type=str,
        default="statevector",
        choices=["statevector", "exact_statevector", "qasm"],
        help="Quantum evaluator; exact_statevector is the cached ideal-statevector engine.",
    )
    ap.add_argument("--q-max-iter", type=int, default=2000)

    # Shared caps
    ap.add_argument("--max-train", type=int, default=512, help="Max train samples (0=all). Shared across models.")
    ap.add_argument("--max-test", type=int, default=512, help="Max test samples (0=all). Shared across models.")

    # Scaling
    ap.add_argument("--scale-classical", type=str, default="standard")
    ap.add_argument("--scale-quantum", type=str, default="minmax2pi")

    # Signals
    ap.add_argument("--sig-bins", type=int, default=40)
    ap.add_argument("--sig-clip-q-lo", type=float, default=0.005)
    ap.add_argument("--sig-clip-q-hi", type=float, default=0.995)

    ap.add_argument("--mmd-max-samples", type=int, default=512)
    ap.add_argument("--mmd-gamma", type=str, default="median")
    ap.add_argument("--mmd-max-pairs", type=int, default=4096)

    # Attacks
    ap.add_argument("--attack-suite", type=str, default="v2")
    ap.add_argument("--atk-meta-keys", type=str, default="")

    # Reinforcement gates (artifact 1.1.0). Defaults reproduce frozen behaviour.
    ap.add_argument(
        "--svc-tune",
        type=str,
        default="none",
        choices=["none", "cv5"],
        help="cv5 = prespecified 5-fold CV over C x gamma on training rows only (Gate T).",
    )
    ap.add_argument(
        "--qsvc-tune",
        type=str,
        default="none",
        choices=["none", "cv5"],
        help="cv5 = prespecified 5-fold CV over C on the precomputed training kernel (Gate T).",
    )

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

    classical_models = _parse_choice_list(
        args.classical_models,
        ALLOWED_CLASSICAL_MODELS,
        name="classical model",
    )
    if not classical_models:
        classical_models = ("svc_rbf",)

    q_feature_maps = _parse_choice_list(
        args.q_feature_maps,
        ALLOWED_Q_FEATURE_MAPS,
        name="quantum feature map",
    )
    if not q_feature_maps:
        q_feature_maps = (str(args.q_feature_map),)

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

        classical_models=tuple(classical_models),
        run_quantum=bool(args.run_quantum),
        q_feature_maps=tuple(q_feature_maps),
        q_reps=int(args.q_reps),
        q_shots=int(args.q_shots),
        q_backend_method=str(args.q_backend_method),
        q_max_iter=int(args.q_max_iter),

        scale_classical=str(args.scale_classical),
        scale_quantum=str(args.scale_quantum),

        sig_bins=int(args.sig_bins),
        sig_clip_q_lo=float(args.sig_clip_q_lo),
        sig_clip_q_hi=float(args.sig_clip_q_hi),

        mmd_max_samples=int(args.mmd_max_samples),
        mmd_gamma=str(args.mmd_gamma),
        mmd_max_pairs=int(args.mmd_max_pairs),

        attack_suite=str(args.attack_suite),
        atk_meta_whitelist=tuple(_parse_meta_keys(args.atk_meta_keys)),

        max_train=int(args.max_train),
        max_test=int(args.max_test),

        svc_tune=str(args.svc_tune),
        qsvc_tune=str(args.qsvc_tune),
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

    dataset_hashes_short = _dataset_hashes_for_tag(cfg)
    dataset_tag = _dataset_tag_from_hashes(cfg.protocol, dataset_hashes_short)

    print(
        f"[RUN] start | protocol={cfg.protocol} dataset_tag={dataset_tag} "
        f"split_seed={cfg.split_seed} model_seed={cfg.model_seed} "
        f"svd_dim={cfg.svd_dim} max_train={cfg.max_train} max_test={cfg.max_test} "
        f"classical_models={list(cfg.classical_models)} run_quantum={cfg.run_quantum} "
        f"q_maps={list(cfg.q_feature_maps)} attack_suite={cfg.attack_suite}",
        flush=True,
    )

    # --------------------------------------------------------
    # Load split
    # --------------------------------------------------------
    seed_everything(cfg.split_seed)

    print("[RUN] loading dataset...", flush=True)
    t_load0 = time.time()

    if cfg.protocol == "ood":
        assert cfg.data_train is not None and cfg.data_test is not None
        X_tr, y_tr, X_te, y_te = load_cicids_subset(
            CicidsConfig(
                train_path=Path(cfg.data_train),
                test_path=Path(cfg.data_test),
                svd_dim=cfg.svd_dim,
            ),
            seed=cfg.split_seed,
        )
    else:
        X_tr, y_tr, X_te, y_te = load_cicids_subset(
            CicidsConfig(
                path=Path(cfg.data),
                svd_dim=cfg.svd_dim,
            ),
            seed=cfg.split_seed,
        )

    print(f"[RUN] dataset loaded | {time.time() - t_load0:.2f}s", flush=True)

    n_train_raw = int(len(y_tr))
    n_test_raw = int(len(y_te))
    pos_rate_train_raw = float(np.mean(y_tr)) if n_train_raw > 0 else float("nan")
    pos_rate_test_raw = float(np.mean(y_te)) if n_test_raw > 0 else float("nan")

    print(
        f"[RUN] raw split | X_tr={X_tr.shape} X_te={X_te.shape} "
        f"pos_train={pos_rate_train_raw:.4f} pos_test={pos_rate_test_raw:.4f}",
        flush=True,
    )

    # Shared caps applied once for all models
    subsample_seed = int(_packed_seed(cfg.split_seed, cfg.model_seed))
    t_sub0 = time.time()

    X_tr, y_tr = _stratified_subsample(X_tr, y_tr, int(cfg.max_train), seed=subsample_seed)

    # Frozen evaluation batch plus the clean held-out pool: evaluation-side rows
    # that were not selected into the batch. The pool feeds the null-calibration
    # controls and is divided into disjoint calibration/evaluation halves by a
    # permutation seeded with the split seed. The frozen batch itself is
    # unchanged because the index selection uses the historical RNG sequence.
    te_idx = _stratified_subsample_indices(y_te, int(cfg.max_test), seed=subsample_seed + 1)
    pool_mask = np.ones(len(y_te), dtype=bool)
    pool_mask[te_idx] = False
    X_pool_raw = np.asarray(X_te)[pool_mask]
    y_pool_raw = np.asarray(y_te).astype(int)[pool_mask]
    X_te, y_te = np.asarray(X_te)[te_idx], np.asarray(y_te).astype(int)[te_idx]

    pool_perm = np.random.default_rng(int(cfg.split_seed)).permutation(len(y_pool_raw))
    pool_half_n = int(len(pool_perm) // 2)
    pool_calibration_idx = np.sort(pool_perm[:pool_half_n])
    pool_evaluation_idx = np.sort(pool_perm[pool_half_n:])

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
        "dataset_tag": str(dataset_tag),
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
        "clean_pool": {
            "source": "evaluation-side rows not selected into the frozen evaluation batch",
            "n_pool": int(len(y_pool_raw)),
            "n_calibration_half": int(len(pool_calibration_idx)),
            "n_evaluation_half": int(len(pool_evaluation_idx)),
            "partition_seed": int(cfg.split_seed),
            "pos_rate_pool": float(np.mean(y_pool_raw)) if len(y_pool_raw) else float("nan"),
            "null_draw_sampling": "simple random without replacement within one half",
        },
        "data_paths": {
            "id": str(cfg.data) if cfg.protocol == "id" else None,
            "train": str(cfg.data_train) if cfg.protocol == "ood" else None,
            "test": str(cfg.data_test) if cfg.protocol == "ood" else None,
        },
        "dataset_hashes_short": dataset_hashes_short,
    }

    attacks = _build_attacks(cfg.attack_suite)
    print(f"[RUN] attacks built | n_attacks={len(attacks)} suite={cfg.attack_suite}", flush=True)

    rows: List[Dict[str, Any]] = []
    model_summaries: Dict[str, Any] = {}

    def _export_atk_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export attack metadata safely.

        Numeric values remain numeric.
        Strings such as sham_type are preserved.
        Complex values are serialized as strings.
        """
        if not meta:
            return {}

        if cfg.atk_meta_whitelist:
            items = [(k, meta.get(k)) for k in cfg.atk_meta_whitelist if k in meta]
        else:
            items = list(meta.items())

        out: Dict[str, Any] = {}

        for k, v in items:
            col = f"atk_{k}"

            if v is None:
                out[col] = np.nan
            elif isinstance(v, (bool, np.bool_)):
                out[col] = int(v)
            elif isinstance(v, (int, np.integer)):
                out[col] = int(v)
            elif isinstance(v, (float, np.floating)):
                fv = float(v)
                out[col] = fv if np.isfinite(fv) else np.nan
            elif isinstance(v, str):
                out[col] = v
            else:
                try:
                    fv = float(v)
                    out[col] = fv if np.isfinite(fv) else np.nan
                except Exception:
                    out[col] = json.dumps(v, default=str)

        return out

    def _build_run_id(
        model_family: str,
        model_label: str,
        scale_label: str,
        attack_tag: str,
    ) -> str:
        return (
            f"proto{cfg.protocol}__dtag{dataset_tag}"
            f"__split{cfg.split_seed}__model{cfg.model_seed}__d{cfg.svd_dim}"
            f"__mt{cfg.max_train}__me{cfg.max_test}"
            f"__{model_family}__{model_label}__{scale_label}__{attack_tag}"
            f"__cfg{cfg_fp}"
        )

    def _run_model(
        *,
        model_family: str,
        model_label: str,
        scale_label: str,
        X_tr_f: np.ndarray,
        X_te_f: np.ndarray,
        y_tr_f: np.ndarray,
        y_te_f: np.ndarray,
        train_fn: Callable[[np.ndarray, np.ndarray], Any],
        predict_fn: Callable[[Any, np.ndarray], np.ndarray],
        get_scores_fn: Callable[[Any, np.ndarray], Optional[np.ndarray]],
        pool_f: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        X_ref = X_tr_f
        n_features = int(X_ref.shape[1])

        clean_ref_run_id = _build_run_id(model_family, model_label, scale_label, "clean")
        clean_ref_attack_seed = _stable_attack_seed(cfg.model_seed, "clean")

        print(
            f"[RUN][{model_label}] baseline signals start | "
            f"family={model_family} X_ref={X_ref.shape} X_te={X_te_f.shape} scale={scale_label}",
            flush=True,
        )

        t_base_sig0 = time.time()

        jsd_clean = float(jsd_feature_shift(X_ref, X_te_f, bins=cfg.sig_bins, clip_q=clip_q))
        mmd_clean = float(mmd_rbf(X_ref, X_te_f, cfg=mmd_cfg))
        ks_mean_clean, ks_rej_clean, ks_n_clean = ks_feature_shift(X_ref, X_te_f)

        print(f"[RUN][{model_label}] baseline signals done | {time.time() - t_base_sig0:.2f}s", flush=True)

        ks_rej_clean_f = (
            float(ks_rej_clean)
            if (int(ks_n_clean) > 0 and np.isfinite(ks_rej_clean))
            else float("nan")
        )

        print(
            f"[RUN][{model_label}] train start | "
            f"X_tr={X_tr_f.shape} X_te={X_te_f.shape} "
            f"y_tr={y_tr_f.shape} y_te={y_te_f.shape} "
            f"family={model_family} scale={scale_label}",
            flush=True,
        )

        t0 = time.time()
        model = train_fn(X_tr_f, y_tr_f)
        train_time_s = float(time.time() - t0)
        tuning_info: Dict[str, Any] = dict(getattr(model, "_paper15_tuning", None) or {})

        print(f"[RUN][{model_label}] train done | {train_time_s:.2f}s", flush=True)

        print(f"[RUN][{model_label}] ref scores start | X={X_te_f.shape}", flush=True)
        t_ref_scores0 = time.time()
        scores_ref = get_scores_fn(model, X_te_f)
        ref_scores_time_s = float(time.time() - t_ref_scores0)

        print(
            f"[RUN][{model_label}] ref scores done | {ref_scores_time_s:.2f}s "
            f"(available={scores_ref is not None})",
            flush=True,
        )

        score_jsd_clean = (
            float(score_drift_jsd(scores_ref=scores_ref, scores_cur=scores_ref, bins=cfg.sig_bins, clip_q=clip_q))
            if scores_ref is not None
            else float("nan")
        )

        print(f"[RUN][{model_label}] ref predict start | X={X_te_f.shape}", flush=True)
        t_ref_pred0 = time.time()
        y_pred_ref = predict_fn(model, X_te_f)
        ref_predict_time_s = float(time.time() - t_ref_pred0)

        print(f"[RUN][{model_label}] ref predict done | {ref_predict_time_s:.2f}s", flush=True)

        metrics_clean = _metrics(y_te_f, y_pred_ref, scores_ref)

        label_pos_rate_clean = float(np.mean(y_te_f)) if len(y_te_f) else float("nan")
        pred_pos_rate_clean = float(np.mean(y_pred_ref)) if len(y_pred_ref) else float("nan")
        pred_error_rate_clean = float(np.mean(y_pred_ref != y_te_f))

        conf_profile_l1_clean = 0.0
        conf_profile_jsd_clean = 0.0

        out_rows: List[Dict[str, Any]] = []

        for i, spec in enumerate(attacks, start=1):
            atk_seed = _stable_attack_seed(cfg.model_seed, spec.tag)

            print(
                f"[RUN][{model_label}] attack {i}/{len(attacks)} start | "
                f"tag={spec.tag} family_decl={spec.family_decl} seed={atk_seed}",
                flush=True,
            )

            t1 = time.time()
            X_eval, y_eval, atk_meta = _apply_attack(
                spec.attack_obj, X_te_f, y_te_f, seed=atk_seed, pool=pool_f
            )
            attack_prep_time_s = float(time.time() - t1)

            print(
                f"[RUN][{model_label}] attack {i}/{len(attacks)} prep done | "
                f"X_eval={X_eval.shape} y_eval={y_eval.shape} prep={attack_prep_time_s:.2f}s",
                flush=True,
            )

            if X_eval.ndim != 2:
                raise RuntimeError(f"Attack {spec.tag} produced X_eval with ndim={X_eval.ndim} (expected 2)")

            if int(X_eval.shape[1]) != int(X_te_f.shape[1]):
                raise RuntimeError(
                    f"Attack {spec.tag} changed n_features: "
                    f"{int(X_eval.shape[1])} vs {int(X_te_f.shape[1])}"
                )

            if int(len(y_eval)) != int(X_eval.shape[0]):
                raise RuntimeError(
                    f"Attack {spec.tag} produced y_eval length {int(len(y_eval))} "
                    f"but X_eval has {int(X_eval.shape[0])} rows"
                )

            attack_family = _meta_family(atk_meta, spec.family_decl)
            attack_priority_group = _meta_priority_group(atk_meta, spec.priority_group_decl)
            attack_strength_nominal = _meta_strength_nominal(atk_meta, spec.strength_nominal_decl)
            attack_strength_eff = _meta_strength_eff(atk_meta, spec.strength_nominal_decl)
            attack_strength = float(attack_strength_nominal)

            label_pos_rate_eval = float(np.mean(y_eval)) if len(y_eval) else float("nan")
            label_prior_shift = _safe_absdiff(label_pos_rate_eval, label_pos_rate_clean)
            label_jsd = float(_binary_jsd_from_labels(y_te_f, y_eval))
            label_flip_rate = (
                float("nan")
                if np.array_equal(y_eval, y_te_f)
                else float(np.mean(y_eval != y_te_f))
            )

            tp0 = time.time()
            y_pred = predict_fn(model, X_eval)
            predict_time_s = float(time.time() - tp0)

            print(
                f"[RUN][{model_label}] attack {i}/{len(attacks)} predict done | {predict_time_s:.2f}s",
                flush=True,
            )

            tg0 = time.time()
            scores = get_scores_fn(model, X_eval)
            scores_time_s = float(time.time() - tg0)

            print(
                f"[RUN][{model_label}] attack {i}/{len(attacks)} scores done | "
                f"{scores_time_s:.2f}s (available={scores is not None})",
                flush=True,
            )

            ts0 = time.time()

            sig_jsd = float(jsd_feature_shift(X_ref, X_eval, bins=cfg.sig_bins, clip_q=clip_q))
            sig_jsd_vs_clean_eval = float(jsd_feature_shift(X_te_f, X_eval, bins=cfg.sig_bins, clip_q=clip_q))

            sig_mmd = float(mmd_rbf(X_ref, X_eval, cfg=mmd_cfg))
            sig_mmd_vs_clean_eval = float(mmd_rbf(X_te_f, X_eval, cfg=mmd_cfg))

            ks_mean, ks_rej, ks_n = ks_feature_shift(X_ref, X_eval)
            ks_rej_f = float(ks_rej) if (int(ks_n) > 0 and np.isfinite(ks_rej)) else float("nan")

            ks_mean_vs_clean_eval, ks_rej_vs_clean_eval, ks_n_vs_clean_eval = ks_feature_shift(X_te_f, X_eval)
            ks_rej_vs_clean_eval_f = (
                float(ks_rej_vs_clean_eval)
                if (int(ks_n_vs_clean_eval) > 0 and np.isfinite(ks_rej_vs_clean_eval))
                else float("nan")
            )

            if scores_ref is not None and scores is not None:
                sig_score_jsd = float(
                    score_drift_jsd(
                        scores_ref=scores_ref,
                        scores_cur=scores,
                        bins=cfg.sig_bins,
                        clip_q=clip_q,
                    )
                )
                sig_score_jsd_delta = float(sig_score_jsd - score_jsd_clean)
                sig_score_jsd_vs_clean_eval = float(sig_score_jsd)
            else:
                sig_score_jsd = float("nan")
                sig_score_jsd_delta = float("nan")
                sig_score_jsd_vs_clean_eval = float("nan")

            signals_time_s = float(time.time() - ts0)

            print(
                f"[RUN][{model_label}] attack {i}/{len(attacks)} signals done | "
                f"{signals_time_s:.2f}s (tag={spec.tag})",
                flush=True,
            )

            sig_jsd_delta = float(sig_jsd - jsd_clean)
            sig_mmd_delta = float(sig_mmd - mmd_clean)
            ks_mean_delta = float(ks_mean - ks_mean_clean)

            ks_rej_delta = float("nan")
            if np.isfinite(ks_rej_f) and np.isfinite(ks_rej_clean_f):
                ks_rej_delta = float(ks_rej_f - ks_rej_clean_f)

            pred_error_rate = float(np.mean(y_pred != y_eval))
            pred_pos_rate_eval = float(np.mean(y_pred)) if len(y_pred) else float("nan")
            pred_pos_rate_shift = _safe_absdiff(pred_pos_rate_eval, pred_pos_rate_clean)
            pred_disagreement_rate = _prediction_disagreement_rate(y_pred_ref, y_pred)
            pred_jsd = float(_binary_jsd_from_labels(y_pred_ref, y_pred))

            conf_profile_l1, conf_profile_jsd = _confusion_profile_shift(
                y_true_ref=y_te_f,
                y_pred_ref=y_pred_ref,
                y_true_cur=y_eval,
                y_pred_cur=y_pred,
            )

            metrics_cur = _metrics(y_eval, y_pred, scores)
            is_clean = spec.attack_obj is None

            # Signed drops: current - clean
            bal_acc_drop = _safe_signed_drop(metrics_cur["bal_acc"], metrics_clean["bal_acc"])
            f1_pos_drop = _safe_signed_drop(metrics_cur["f1_pos"], metrics_clean["f1_pos"])
            roc_auc_drop = _safe_signed_drop(metrics_cur["roc_auc"], metrics_clean["roc_auc"])
            pred_error_rate_drop = _safe_signed_drop(pred_error_rate, pred_error_rate_clean)
            pos_rate_eval_drop = _safe_signed_drop(metrics_cur["pos_rate_eval"], metrics_clean["pos_rate_eval"])
            label_pos_rate_eval_drop = _safe_signed_drop(label_pos_rate_eval, label_pos_rate_clean)
            pred_pos_rate_eval_drop = _safe_signed_drop(pred_pos_rate_eval, pred_pos_rate_clean)

            # Positive impact: harm only
            impact_bal_acc = _safe_positive_impact(metrics_clean["bal_acc"], metrics_cur["bal_acc"])
            impact_f1 = _safe_positive_impact(metrics_clean["f1_pos"], metrics_cur["f1_pos"])
            impact_roc_auc = _safe_positive_impact(metrics_clean["roc_auc"], metrics_cur["roc_auc"])
            impact_pred_error = _safe_positive_impact_error(pred_error_rate, pred_error_rate_clean)

            row = {
                # Stable identifiers
                "run_id": _build_run_id(model_family, model_label, scale_label, spec.tag),
                "cfg_fingerprint": cfg_fp,
                "dataset_tag": str(dataset_tag),

                # Provenance
                "protocol": str(cfg.protocol),
                "seed": int(cfg.seed),
                "split_seed": int(cfg.split_seed),
                "model_seed": int(cfg.model_seed),
                "seed_semantics": seed_semantics,
                "svd_dim": int(cfg.svd_dim),
                "max_train": int(cfg.max_train),
                "max_test": int(cfg.max_test),
                "n_features": int(n_features),

                "data_hash_id_short": str(dataset_hashes_short["id"]),
                "data_hash_train_short": str(dataset_hashes_short["train"]),
                "data_hash_test_short": str(dataset_hashes_short["test"]),

                # Model
                "model_family": str(model_family),
                "model": str(model_label),
                "scale": str(scale_label),
                "model_tuning": str(tuning_info.get("mode", "none")),
                "model_C": float(_as_float_or_nan(tuning_info.get("selected_C", float("nan")))),
                "model_gamma": str(tuning_info.get("selected_gamma", "")),
                "model_cv_bal_acc": float(_as_float_or_nan(tuning_info.get("cv_bal_acc", float("nan")))),

                # Attack
                "attack_suite": str(cfg.attack_suite),
                "attack": str(spec.tag),
                "attack_is_clean": int(1 if is_clean else 0),
                "attack_family": str(attack_family),
                "attack_family_decl": str(spec.family_decl),
                "attack_priority_group": str(attack_priority_group),
                "attack_priority_group_decl": str(spec.priority_group_decl),
                "attack_strength": float(attack_strength),
                "attack_strength_nominal": float(attack_strength_nominal),
                "attack_strength_nominal_decl": float(spec.strength_nominal_decl),
                "attack_strength_eff": float(attack_strength_eff),
                "attack_seed": int(atk_seed),

                # Clean linkage
                "clean_ref_run_id": str(clean_ref_run_id),
                "clean_ref_attack_seed": int(clean_ref_attack_seed),

                # Clean references copied into every row
                "bal_acc_clean": float(metrics_clean["bal_acc"]),
                "f1_pos_clean": float(metrics_clean["f1_pos"]),
                "roc_auc_clean": float(metrics_clean["roc_auc"]),
                "pos_rate_eval_clean": float(metrics_clean["pos_rate_eval"]),
                "pred_error_rate_clean": float(pred_error_rate_clean),
                "label_pos_rate_clean": float(label_pos_rate_clean),
                "pred_pos_rate_clean": float(pred_pos_rate_clean),

                # Current performance
                "bal_acc": float(metrics_cur["bal_acc"]),
                "f1_pos": float(metrics_cur["f1_pos"]),
                "roc_auc": float(metrics_cur["roc_auc"]),
                "pos_rate_eval": float(metrics_cur["pos_rate_eval"]),
                "pred_error_rate": float(pred_error_rate),
                "label_pos_rate_eval": float(label_pos_rate_eval),
                "pred_pos_rate_eval": float(pred_pos_rate_eval),

                # Signed drops
                "bal_acc_drop": float(bal_acc_drop),
                "f1_pos_drop": float(f1_pos_drop),
                "roc_auc_drop": float(roc_auc_drop),
                "pred_error_rate_drop": float(pred_error_rate_drop),
                "pos_rate_eval_drop": float(pos_rate_eval_drop),
                "label_pos_rate_eval_drop": float(label_pos_rate_eval_drop),
                "pred_pos_rate_eval_drop": float(pred_pos_rate_eval_drop),

                # Positive impact
                "impact_bal_acc": float(impact_bal_acc),
                "impact_f1": float(impact_f1),
                "impact_roc_auc": float(impact_roc_auc),
                "impact_pred_error": float(impact_pred_error),

                # Feature-centric integrity
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

                # Eval-vs-clean-eval variants
                "integrity_jsd_vs_clean_eval": float(sig_jsd_vs_clean_eval),
                "integrity_mmd_vs_clean_eval": float(sig_mmd_vs_clean_eval),
                "integrity_ks_mean_vs_clean_eval": float(ks_mean_vs_clean_eval),
                "integrity_ks_reject05_vs_clean_eval": float(ks_rej_vs_clean_eval_f),
                "integrity_ks_n_vs_clean_eval": int(ks_n_vs_clean_eval),
                "integrity_score_jsd_vs_clean_eval": float(sig_score_jsd_vs_clean_eval),

                # Label-aware / prediction-aware integrity
                "label_flip_rate": float(label_flip_rate),
                "integrity_label_prior_shift": float(label_prior_shift),
                "integrity_label_jsd": float(label_jsd),
                "integrity_pred_pos_rate_shift": float(pred_pos_rate_shift),
                "integrity_pred_disagreement": float(pred_disagreement_rate),
                "integrity_pred_jsd": float(pred_jsd),

                # Confusion-profile integrity
                "integrity_confusion_profile_l1_clean": float(conf_profile_l1_clean),
                "integrity_confusion_profile_l1": float(conf_profile_l1),
                "integrity_confusion_profile_l1_delta": float(conf_profile_l1 - conf_profile_l1_clean),

                "integrity_confusion_profile_jsd_clean": float(conf_profile_jsd_clean),
                "integrity_confusion_profile_jsd": float(conf_profile_jsd),
                "integrity_confusion_profile_jsd_delta": float(conf_profile_jsd - conf_profile_jsd_clean),

                # Timings
                "train_time_s": float(train_time_s),
                "attack_prep_time_s": float(attack_prep_time_s),
                "predict_time_s": float(predict_time_s),
                "scores_time_s": float(scores_time_s),
                "signals_time_s": float(signals_time_s),
                "ref_scores_time_s": float(ref_scores_time_s),
                "ref_predict_time_s": float(ref_predict_time_s),

                # Optional attack metadata
                **_export_atk_meta(atk_meta or {}),
            }

            out_rows.append(row)

        summary = {
            "model_family": str(model_family),
            "model": str(model_label),
            "scale": str(scale_label),
            "n_features": int(n_features),
            "train_time_s": float(train_time_s),
            "ref_scores_time_s": float(ref_scores_time_s),
            "ref_predict_time_s": float(ref_predict_time_s),
            "clean_ref_run_id": str(clean_ref_run_id),
            "clean_ref_attack_seed": int(clean_ref_attack_seed),
            "tuning": {k: v for k, v in tuning_info.items() if k != "grid_table"},
            "tuning_grid_table": list(tuning_info.get("grid_table", [])),
            "clean_metrics": {
                "bal_acc": float(metrics_clean["bal_acc"]),
                "f1_pos": float(metrics_clean["f1_pos"]),
                "roc_auc": float(metrics_clean["roc_auc"]),
                "pos_rate_eval": float(metrics_clean["pos_rate_eval"]),
                "pred_error_rate": float(pred_error_rate_clean),
                "label_pos_rate_clean": float(label_pos_rate_clean),
                "pred_pos_rate_clean": float(pred_pos_rate_clean),
            },
            "clean_signals": {
                "integrity_jsd_clean": float(jsd_clean),
                "integrity_mmd_clean": float(mmd_clean),
                "integrity_ks_mean_clean": float(ks_mean_clean),
                "integrity_ks_reject05_clean": float(ks_rej_clean_f),
                "integrity_score_jsd_clean": float(score_jsd_clean),
                "integrity_confusion_profile_l1_clean": float(conf_profile_l1_clean),
                "integrity_confusion_profile_jsd_clean": float(conf_profile_jsd_clean),
            },
        }

        return out_rows, summary

    # --------------------------------------------------------
    # Shared scaled matrices
    # --------------------------------------------------------
    print("[RUN] classical scaling start", flush=True)
    scaler_c = build_scaler(cfg.scale_classical)
    t_sc0 = time.time()
    X_tr_c, X_te_c = fit_transform_scaler(scaler_c, X_tr, X_te)

    print(
        f"[RUN] classical scaling done | {time.time() - t_sc0:.2f}s | "
        f"X_tr={X_tr_c.shape} X_te={X_te_c.shape}",
        flush=True,
    )

    def _pool_dict(scaler: Any) -> Dict[str, Any]:
        if len(y_pool_raw) and scaler is not None:
            X_pool_scaled = np.asarray(scaler.transform(X_pool_raw))
        else:
            X_pool_scaled = np.asarray(X_pool_raw)
        return {
            "X": X_pool_scaled,
            "y": y_pool_raw,
            "calibration_idx": pool_calibration_idx,
            "evaluation_idx": pool_evaluation_idx,
        }

    pool_c = _pool_dict(scaler_c)

    scaler_q = None
    X_tr_q: Optional[np.ndarray] = None
    X_te_q: Optional[np.ndarray] = None
    pool_q: Optional[Dict[str, Any]] = None

    if cfg.run_quantum and QISKIT_OK:
        print("[RUN] quantum scaling start", flush=True)
        scaler_q = build_scaler(cfg.scale_quantum)
        t_sq0 = time.time()
        X_tr_q, X_te_q = fit_transform_scaler(scaler_q, X_tr, X_te)
        pool_q = _pool_dict(scaler_q)

        print(
            f"[RUN] quantum scaling done | {time.time() - t_sq0:.2f}s | "
            f"X_tr={X_tr_q.shape} X_te={X_te_q.shape}",
            flush=True,
        )

    # --------------------------------------------------------
    # Training policies (frozen defaults or prespecified CV tuning)
    # --------------------------------------------------------
    def _train_classical_with_policy(Xa: np.ndarray, ya: np.ndarray) -> Any:
        ccfg = ClassicalCfg()
        info: Dict[str, Any] = {
            "mode": "none",
            "selected_C": float(ccfg.C),
            "selected_gamma": str(ccfg.gamma),
        }
        if cfg.svc_tune == "cv5":
            ccfg, info = select_svc_params_cv(Xa, ya, ccfg, seed=int(cfg.model_seed), n_splits=5)
        elif cfg.svc_tune != "none":
            raise ValueError(f"Unknown --svc-tune '{cfg.svc_tune}' (use none|cv5)")
        model = train_classical_svc(Xa, ya, ccfg)
        try:
            model._paper15_tuning = info  # type: ignore[attr-defined]
        except Exception:
            pass
        return model

    def _train_quantum_with_policy(Xa: np.ndarray, ya: np.ndarray, qcfg0: QuantumCfg) -> Any:
        info: Dict[str, Any] = {
            "mode": "none",
            "selected_C": float(qcfg0.C),
            "selected_gamma": "n/a",
        }
        qcfg1 = qcfg0
        if cfg.qsvc_tune == "cv5":
            qcfg1, info = select_qsvc_C_cv(Xa, ya, qcfg0, seed=int(cfg.model_seed), n_splits=5)
        elif cfg.qsvc_tune != "none":
            raise ValueError(f"Unknown --qsvc-tune '{cfg.qsvc_tune}' (use none|cv5)")
        model = train_qsvc(Xa, ya, qcfg1)[0]
        try:
            model._paper15_tuning = info  # type: ignore[attr-defined]
        except Exception:
            pass
        return model

    # --------------------------------------------------------
    # Classical runs
    # --------------------------------------------------------
    for classical_model in cfg.classical_models:
        if classical_model != "svc_rbf":
            raise ValueError(
                f"Current runner only supports classical model '{ALLOWED_CLASSICAL_MODELS[0]}' "
                f"with the present project interfaces, but got '{classical_model}'."
            )

        rows_c, summary_c = _run_model(
            model_family="classical",
            model_label=classical_model,
            scale_label=cfg.scale_classical,
            X_tr_f=X_tr_c,
            X_te_f=X_te_c,
            y_tr_f=y_tr,
            y_te_f=y_te,
            train_fn=_train_classical_with_policy,
            predict_fn=lambda m, Xx: m.predict(Xx),
            get_scores_fn=lambda m, Xx: _get_scores(m, Xx),
            pool_f=pool_c,
        )

        rows.extend(rows_c)
        model_summaries[classical_model] = summary_c

        print(f"[RUN] classical model done | model={classical_model} rows={len(rows_c)}", flush=True)

    # --------------------------------------------------------
    # Quantum runs
    # --------------------------------------------------------
    if cfg.run_quantum:
        if not QISKIT_OK:
            print("[WARN] Qiskit ML not available. Skipping quantum.", flush=True)
        else:
            assert X_tr_q is not None and X_te_q is not None

            for qmap in cfg.q_feature_maps:
                qcfg = QuantumCfg(
                    feature_map=qmap,
                    reps=cfg.q_reps,
                    backend_method=cfg.q_backend_method,
                    shots=cfg.q_shots,
                    seed=cfg.model_seed,
                    max_iter=cfg.q_max_iter,
                )

                q_model_label = f"qsvc_{qcfg.feature_map}_r{qcfg.reps}"

                print(
                    f"[RUN] quantum model start | model={q_model_label} "
                    f"backend={qcfg.backend_method} shots={qcfg.shots} "
                    f"seed={qcfg.seed} max_iter={qcfg.max_iter}",
                    flush=True,
                )

                rows_q, summary_q = _run_model(
                    model_family="quantum",
                    model_label=q_model_label,
                    scale_label=cfg.scale_quantum,
                    X_tr_f=X_tr_q,
                    X_te_f=X_te_q,
                    y_tr_f=y_tr,
                    y_te_f=y_te,
                    train_fn=lambda Xa, ya, qcfg=qcfg: _train_quantum_with_policy(Xa, ya, qcfg),
                    predict_fn=lambda m, Xx: predict_qsvc(m, Xx),
                    get_scores_fn=lambda m, Xx: scores_qsvc(m, Xx),
                    pool_f=pool_q,
                )

                rows.extend(rows_q)
                model_summaries[q_model_label] = summary_q

                print(f"[RUN] quantum model done | model={q_model_label} rows={len(rows_q)}", flush=True)
    else:
        print("[RUN] quantum disabled", flush=True)

    # --------------------------------------------------------
    # Export dataframe
    # --------------------------------------------------------
    print("[RUN] building dataframe...", flush=True)

    df = (
        pd.DataFrame(rows)
        .sort_values(
            [
                "protocol",
                "dataset_tag",
                "model_family",
                "model",
                "attack_is_clean",
                "attack_priority_group",
                "attack_family",
                "attack_strength_nominal",
                "attack",
                "attack_strength_eff",
            ],
            ascending=[True, True, True, True, False, True, True, True, True, True],
        )
        .reset_index(drop=True)
    )

    print(f"[RUN] dataframe ready | shape={df.shape}", flush=True)

    qtag = (
        f"__qmaps{'-'.join(cfg.q_feature_maps)}__qr{cfg.q_reps}__qb{cfg.q_backend_method}"
        f"__qs{cfg.q_shots}__qmi{cfg.q_max_iter}"
        if cfg.run_quantum
        else "__qnone"
    )

    ctag = f"__cmodels{'-'.join(cfg.classical_models)}"

    run_tag = (
        f"proto{cfg.protocol}__{dataset_tag}"
        f"__seed{cfg.seed}__split{cfg.split_seed}__model{cfg.model_seed}__d{cfg.svd_dim}"
        f"__mt{cfg.max_train}__me{cfg.max_test}"
        f"{ctag}"
        f"__cscale{cfg.scale_classical}__qscale{cfg.scale_quantum}"
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
        "dataset_tag": dataset_tag,
        "dataset_hashes_short": dataset_hashes_short,
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
            "models": model_summaries,
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

    preview_cols = [
        "protocol",
        "dataset_tag",
        "model",
        "attack",
        "attack_family",
        "attack_priority_group",
        "attack_strength_nominal",
        "bal_acc",
        "bal_acc_clean",
        "bal_acc_drop",
        "impact_bal_acc",
        "integrity_jsd_vs_clean_eval",
        "integrity_score_jsd_vs_clean_eval",
        "integrity_label_prior_shift",
        "integrity_pred_disagreement",
        "integrity_confusion_profile_jsd",
        "atk_sham_type",
    ]
    preview_cols = [c for c in preview_cols if c in df.columns]

    if preview_cols:
        print(df[preview_cols])


if __name__ == "__main__":
    main()