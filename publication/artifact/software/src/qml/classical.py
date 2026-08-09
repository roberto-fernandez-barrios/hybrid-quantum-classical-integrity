# src/models/qml/classical.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Literal, Tuple, Any

import numpy as np
from sklearn.svm import SVC

__all__ = [
    "ClassicalCfg",
    "train_classical_svc",
    "predict_classical_svc",
    "scores_classical_svc",
]


# ----------------------------
# Types
# ----------------------------
KernelName = Literal["rbf", "linear", "poly", "sigmoid"]


# ----------------------------
# Config
# ----------------------------
@dataclass(frozen=True)
class ClassicalCfg:
    """
    Classical SVC configuration.

    Designed to be symmetric in rigor with QuantumCfg:
      - Explicit hyperparameters
      - Deterministic label normalization
      - Optional probability support
      - Class imbalance support
    """

    # Core SVC
    kernel: KernelName = "rbf"
    C: float = 1.0
    gamma: str | float = "scale"

    # Kernel-specific
    degree: int = 3          # used if kernel="poly"
    coef0: float = 0.0       # used in poly/sigmoid

    # Optimization
    tol: float = 1e-3
    shrinking: bool = True
    cache_size: float = 200.0
    max_iter: int = -1

    # Imbalance
    class_weight: Optional[Dict[int, float]] = None

    # Probability mode (slower but enables predict_proba)
    probability: bool = False

    # Safety
    enforce_binary_labels: bool = True
    require_finite: bool = True


# ----------------------------
# Validation utilities
# ----------------------------
def _as_2d_float64(X: np.ndarray) -> np.ndarray:
    X2 = np.asarray(X, dtype=np.float64)
    if X2.ndim != 2:
        raise ValueError(f"X must be 2D array (n_samples, n_features), got shape={X2.shape}")
    if X2.shape[1] <= 0:
        raise ValueError("X must have at least 1 feature.")
    return X2


def _as_1d(y: np.ndarray) -> np.ndarray:
    y2 = np.asarray(y)
    if y2.ndim != 1:
        raise ValueError(f"y must be 1D array (n_samples,), got shape={y2.shape}")
    return y2


def _normalize_binary_labels(y: np.ndarray) -> np.ndarray:
    """
    Deterministically map binary labels to {0,1}.
    """
    y2 = _as_1d(y)
    uniq = np.unique(y2)
    if uniq.size != 2:
        raise ValueError(f"Expected binary labels, got {uniq.tolist()}")

    # Fast path numeric {0,1}
    if np.issubdtype(y2.dtype, np.number):
        try:
            u = set(np.asarray(uniq, dtype=int).tolist())
            if u == {0, 1}:
                return np.asarray(y2, dtype=int)
        except Exception:
            pass

    # Stable mapping via string repr
    uniq_sorted = sorted(uniq.tolist(), key=lambda v: str(v))
    mapper = {uniq_sorted[0]: 0, uniq_sorted[1]: 1}
    y_mapped = np.array([mapper[v] for v in y2.tolist()], dtype=int)

    if set(np.unique(y_mapped).tolist()) != {0, 1}:
        raise ValueError("Binary normalization failed.")

    return y_mapped


def _validate_xy(X: np.ndarray, y: np.ndarray, cfg: ClassicalCfg) -> Tuple[np.ndarray, np.ndarray]:
    X2 = _as_2d_float64(X)
    y2 = _as_1d(y)

    if X2.shape[0] != y2.shape[0]:
        raise ValueError("X and y must have same number of samples.")

    if cfg.require_finite:
        if not np.isfinite(X2).all():
            raise ValueError("X contains NaN/Inf.")
        if np.issubdtype(y2.dtype, np.number) and not np.isfinite(y2).all():
            raise ValueError("y contains NaN/Inf.")

    if cfg.enforce_binary_labels:
        y2 = _normalize_binary_labels(y2)
    else:
        y2 = np.asarray(y2, dtype=int)

    return X2, y2


# ----------------------------
# Public API
# ----------------------------
def train_classical_svc(
    X: np.ndarray,
    y: np.ndarray,
    cfg: ClassicalCfg,
) -> SVC:
    """
    Train a classical SVC baseline.

    Assumes scaling has already been applied externally (as in run_benchmark).
    """
    X2, y2 = _validate_xy(X, y, cfg)

    clf = SVC(
        kernel=cfg.kernel,
        C=float(cfg.C),
        gamma=cfg.gamma,
        degree=int(cfg.degree),
        coef0=float(cfg.coef0),
        tol=float(cfg.tol),
        shrinking=bool(cfg.shrinking),
        cache_size=float(cfg.cache_size),
        max_iter=int(cfg.max_iter),
        class_weight=cfg.class_weight,
        probability=bool(cfg.probability),
    )

    clf.fit(X2, y2)
    return clf


def predict_classical_svc(model: SVC, X: np.ndarray) -> np.ndarray:
    X2 = _as_2d_float64(X)
    return np.asarray(model.predict(X2)).reshape(-1)


def scores_classical_svc(model: SVC, X: np.ndarray) -> Optional[np.ndarray]:
    """
    Continuous scores for drift metrics.
      - prefer decision_function
      - else predict_proba[:,1]
    """
    X2 = _as_2d_float64(X)

    if hasattr(model, "decision_function"):
        try:
            s = model.decision_function(X2)
            return np.asarray(s).reshape(-1)
        except Exception:
            pass

    if hasattr(model, "predict_proba"):
        try:
            p = np.asarray(model.predict_proba(X2))
            if p.ndim == 2 and p.shape[1] >= 2:
                return np.asarray(p[:, 1]).reshape(-1)
        except Exception:
            pass

    return None
