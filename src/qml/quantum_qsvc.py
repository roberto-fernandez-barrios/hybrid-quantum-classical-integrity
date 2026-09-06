# src/qml/quantum_qsvc.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple
import time

import numpy as np

__all__ = [
    "QISKIT_OK",
    "QuantumCfg",
    "train_qsvc",
    "predict_qsvc",
    "scores_qsvc",
]

# ----------------------------
# Optional Qiskit imports (robust)
# ----------------------------
QISKIT_OK = False
_QISKIT_ERR: Optional[Exception] = None
_HAS_ZFEATUREMAP = False

try:
    # Aer (simulator backend)
    from qiskit_aer import AerSimulator

    # Feature maps (availability depends on qiskit version)
    from qiskit.circuit.library import ZZFeatureMap, PauliFeatureMap
    try:
        from qiskit.circuit.library import ZFeatureMap  # type: ignore
        _HAS_ZFEATUREMAP = True
    except Exception:
        _HAS_ZFEATUREMAP = False

    # Kernel + QSVC (qiskit-machine-learning)
    from qiskit_machine_learning.kernels import FidelityQuantumKernel
    from qiskit_machine_learning.algorithms import QSVC
    from src.qml.statevector_fidelity_kernel import ExactStatevectorFidelityKernel

    QISKIT_OK = True

except Exception as e:
    _QISKIT_ERR = e
    QISKIT_OK = False


# ----------------------------
# Types
# ----------------------------
FeatureMapName = Literal["zz", "z", "pauli_xz", "pauli_xyz"]
BackendMethod = Literal["statevector", "exact_statevector", "qasm"]


# ----------------------------
# Config
# ----------------------------
@dataclass(frozen=True)
class QuantumCfg:
    """
    Configuration for QSVC + FidelityQuantumKernel.

    Notes (paper/reproducibility):
      - `seed` sets qiskit's algorithm_globals.random_seed.
      - `statevector` uses Qiskit Machine Learning's reference fidelity kernel.
      - `exact_statevector` prepares each ideal state once and evaluates the same
        fidelity matrix by linear algebra; it is not a shot-based or hardware run.
      - `qasm` remains a traceability-only legacy option because primitive wiring varies
        across qiskit/qiskit-ml versions; do not interpret it as shot-noise evidence.
    """

    # Feature map
    feature_map: FeatureMapName = "zz"
    reps: int = 1

    # Backend execution (traceability for runs)
    backend_method: BackendMethod = "statevector"
    shots: int = 1024

    # Reproducibility
    seed: int = 42

    # QSVC hyperparams (paper knobs)
    C: float = 1.0
    tol: float = 1e-3
    max_iter: int = -1  # -1 => no limit (sklearn-style)
    cache_size: float = 200.0  # MB
    class_weight: Optional[Dict[int, float]] = None
    probability: bool = False  # if you need predict_proba (slower)

    # Sanity / safety
    enforce_binary_labels: bool = True
    require_finite: bool = True


# ----------------------------
# Validation / normalization
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

    - If already numeric {0,1}, keep.
    - Else create a stable mapping based on string representation of unique labels.
      This avoids brittle `int(label)` conversions (e.g., 'BENIGN'/'ATTACK').
    """
    y2 = _as_1d(y)
    uniq = np.unique(y2)
    if uniq.size != 2:
        raise ValueError(f"Expected binary labels, got {uniq.tolist()}")

    # Fast path: numeric {0,1}
    if np.issubdtype(y2.dtype, np.number):
        try:
            u = set(np.asarray(uniq, dtype=int).tolist())
            if u == {0, 1}:
                return np.asarray(y2, dtype=int)
        except Exception:
            pass

    # Stable mapping via string repr (deterministic across runs)
    uniq_sorted = sorted(uniq.tolist(), key=lambda v: str(v))
    mapper = {uniq_sorted[0]: 0, uniq_sorted[1]: 1}

    # list() to avoid numpy scalar hash weirdness in dict keys
    y_mapped = np.array([mapper[v] for v in y2.tolist()], dtype=int)

    if set(np.unique(y_mapped).tolist()) != {0, 1}:
        raise ValueError("Binary normalization failed.")
    return y_mapped


def _validate_xy(X: np.ndarray, y: np.ndarray, cfg: QuantumCfg) -> Tuple[np.ndarray, np.ndarray]:
    X2 = _as_2d_float64(X)
    y2 = _as_1d(y)

    if X2.shape[0] != y2.shape[0]:
        raise ValueError(f"X and y must have same n_samples, got {X2.shape[0]} != {y2.shape[0]}")

    if cfg.require_finite:
        if not np.isfinite(X2).all():
            raise ValueError("X contains NaN/Inf. Impute/clean before calling train_qsvc().")
        if np.issubdtype(y2.dtype, np.number) and not np.isfinite(y2).all():
            raise ValueError("y contains NaN/Inf. Clean labels before calling train_qsvc().")

    if cfg.enforce_binary_labels:
        y2 = _normalize_binary_labels(y2)
    else:
        # keep behavior aligned with runner expectations
        try:
            y2 = np.asarray(y2, dtype=int)
        except Exception as e:
            raise ValueError(f"y labels could not be converted to int: {e}")

    # Final safety: ensure {0,1} if enforced
    if cfg.enforce_binary_labels:
        uniq_final = np.unique(y2)
        if not (uniq_final.size == 2 and set(uniq_final.tolist()) == {0, 1}):
            raise ValueError(f"After normalization expected labels {{0,1}}, got {uniq_final.tolist()}")

    return X2, y2


# ----------------------------
# Utilities
# ----------------------------
def _require_qiskit() -> None:
    if not QISKIT_OK:
        msg = "Qiskit ML not available. Install 'qiskit-machine-learning' + 'qiskit-aer'."
        if _QISKIT_ERR is not None:
            msg += f" (import error: {_QISKIT_ERR})"
        raise RuntimeError(msg)


def _make_feature_map(dim: int, cfg: QuantumCfg):
    if cfg.reps <= 0:
        raise ValueError(f"reps must be >= 1, got reps={cfg.reps}")
    if dim <= 0:
        raise ValueError(f"dim must be >= 1, got dim={dim}")

    if cfg.feature_map == "zz":
        return ZZFeatureMap(feature_dimension=dim, reps=cfg.reps)

    if cfg.feature_map == "z":
        if not _HAS_ZFEATUREMAP:
            raise RuntimeError("ZFeatureMap not available in your qiskit version. Use 'zz' or 'pauli_*'.")
        return ZFeatureMap(feature_dimension=dim, reps=cfg.reps)  # type: ignore

    if cfg.feature_map == "pauli_xz":
        return PauliFeatureMap(feature_dimension=dim, reps=cfg.reps, paulis=["X", "Z"])

    if cfg.feature_map == "pauli_xyz":
        return PauliFeatureMap(feature_dimension=dim, reps=cfg.reps, paulis=["X", "Y", "Z"])

    raise ValueError(f"Unknown feature_map={cfg.feature_map}")


def _make_backend(cfg: QuantumCfg) -> Any:
    """
    Best-effort backend factory (currently traceability / future-proof).

    NOTE:
      - FidelityQuantumKernel's primitive wiring differs across qiskit/qiskit-ml versions.
      - We create the backend to validate config and keep it explicit, but we don't force-wire it
        into the kernel here (to avoid breaking your pipeline across environments).
    """
    if cfg.backend_method in {"statevector", "exact_statevector"}:
        return AerSimulator(method="statevector")

    if cfg.backend_method == "qasm":
        if cfg.shots <= 0:
            raise ValueError(f"shots must be > 0 for qasm mode, got shots={cfg.shots}")
        return AerSimulator(method="qasm")

    raise ValueError(f"Unknown backend_method={cfg.backend_method}")


def _make_kernel(feature_map: Any, cfg: QuantumCfg) -> Any:
    """
    Create the selected fidelity-kernel evaluator.

    ``exact_statevector`` is mathematically equivalent to the ideal reference
    kernel but avoids constructing one compute-uncompute circuit per pair.
    """
    if cfg.backend_method == "exact_statevector":
        return ExactStatevectorFidelityKernel(feature_map=feature_map)
    return FidelityQuantumKernel(feature_map=feature_map, fidelity=None)


def _seed_qiskit(seed: int) -> None:
    """
    Best-effort seeding across qiskit versions.
    Some stacks don't expose algorithm_globals anymore.
    """
    try:
        from qiskit.utils import algorithm_globals  # type: ignore
        algorithm_globals.random_seed = int(seed)
    except Exception:
        # If not available, ignore. Determinism is still mostly driven by numpy/sklearn and fixed circuits.
        pass


# ----------------------------
# Public API
# ----------------------------
def train_qsvc(
    X: np.ndarray,
    y: np.ndarray,
    cfg: QuantumCfg,
) -> Tuple[Any, Any, Any]:
    """
    Train a QSVC with a fidelity-based quantum kernel.

    Returns:
      model, feature_map, quantum_kernel
    """
    _require_qiskit()

    X2, y2 = _validate_xy(X, y, cfg)

    # Qiskit global seed for reproducibility
    _seed_qiskit(cfg.seed)

    dim = int(X2.shape[1])
    fmap = _make_feature_map(dim, cfg)

    # Validate backend config (and keep for future wiring)
    _ = _make_backend(cfg)

    qkernel = _make_kernel(fmap, cfg)

    model = QSVC(
        quantum_kernel=qkernel,
        C=float(cfg.C),
        tol=float(cfg.tol),
        max_iter=int(cfg.max_iter),
        cache_size=float(cfg.cache_size),
        class_weight=cfg.class_weight,
        probability=bool(cfg.probability),
    )

    print(
        f"[Q][FIT] start | X={X2.shape} y={y2.shape} "
        f"fmap={cfg.feature_map} reps={cfg.reps} "
        f"backend={cfg.backend_method} kernel={type(qkernel).__name__} shots={cfg.shots} "
        f"C={cfg.C} tol={cfg.tol} max_iter={cfg.max_iter}",
        flush=True,
    )
    t0 = time.time()
    model.fit(X2, y2)
    dt = time.time() - t0
    cache_info = qkernel.cache_info() if hasattr(qkernel, "cache_info") else None
    print(f"[Q][FIT] done  | {dt:.2f}s cache={cache_info}", flush=True)

    return model, fmap, qkernel


def predict_qsvc(model: Any, X: np.ndarray) -> np.ndarray:
    """
    Predict labels with a trained QSVC.
    """
    X2 = _as_2d_float64(X)
    print(f"[Q][PRED] start | X={X2.shape}", flush=True)
    t0 = time.time()
    yhat = np.asarray(model.predict(X2)).reshape(-1)
    dt = time.time() - t0
    print(f"[Q][PRED] done  | {dt:.2f}s", flush=True)
    return yhat


def scores_qsvc(model: Any, X: np.ndarray) -> Optional[np.ndarray]:
    """
    Best-effort continuous scores for drift metrics:
      - prefers decision_function
      - else predict_proba[:,1] if available
      - else None
    """
    X2 = _as_2d_float64(X)

    if hasattr(model, "decision_function"):
        try:
            print(f"[Q][SCORE] decision_function start | X={X2.shape}", flush=True)
            t0 = time.time()
            s = model.decision_function(X2)
            dt = time.time() - t0
            print(f"[Q][SCORE] decision_function done  | {dt:.2f}s", flush=True)
            return np.asarray(s).reshape(-1)
        except Exception as e:
            print(f"[Q][SCORE] decision_function failed | {type(e).__name__}: {e}", flush=True)

    if hasattr(model, "predict_proba"):
        try:
            print(f"[Q][SCORE] predict_proba start | X={X2.shape}", flush=True)
            t0 = time.time()
            p = np.asarray(model.predict_proba(X2))
            dt = time.time() - t0
            print(f"[Q][SCORE] predict_proba done  | {dt:.2f}s", flush=True)
            if p.ndim == 2 and p.shape[1] >= 2:
                return np.asarray(p[:, 1]).reshape(-1)
            print(f"[Q][SCORE] predict_proba shape unsupported | shape={p.shape}", flush=True)
        except Exception as e:
            print(f"[Q][SCORE] predict_proba failed | {type(e).__name__}: {e}", flush=True)

    print("[Q][SCORE] no continuous score available", flush=True)
    return None

# ----------------------------
# Prespecified cross-validated tuning (Paper 1.5 Gate T)
# ----------------------------

QSVC_TUNE_C_GRID: Tuple[float, ...] = (0.1, 1.0, 10.0, 100.0)


def select_qsvc_C_cv(
    X: np.ndarray,
    y: np.ndarray,
    cfg: QuantumCfg,
    *,
    seed: int,
    n_splits: int = 5,
    C_grid: Sequence[float] = QSVC_TUNE_C_GRID,
) -> Tuple[QuantumCfg, Dict[str, Any]]:
    """
    Select the QSVC regularisation constant C by stratified k-fold
    cross-validation on the precomputed training fidelity kernel, scoring
    balanced accuracy. Training rows only; evaluation rows are never seen.

    Tie rule (frozen in the preregistration): C ascending, strict improvement
    required, so ties resolve to the smallest C.
    """
    import dataclasses

    from sklearn.metrics import balanced_accuracy_score
    from sklearn.model_selection import StratifiedKFold
    from sklearn.svm import SVC

    _require_qiskit()
    X2, y2 = _validate_xy(X, y, cfg)
    _seed_qiskit(cfg.seed)

    dim = int(X2.shape[1])
    fmap = _make_feature_map(dim, cfg)
    qkernel = _make_kernel(fmap, cfg)
    K = np.asarray(qkernel.evaluate(X2), dtype=np.float64)
    if K.shape != (len(y2), len(y2)):
        raise RuntimeError(f"Unexpected training kernel shape {K.shape}")

    skf = StratifiedKFold(n_splits=int(n_splits), shuffle=True, random_state=int(seed))
    folds = list(skf.split(X2, y2))

    best: Optional[Tuple[float, float]] = None
    table: List[Dict[str, Any]] = []

    for C in C_grid:
        scores: List[float] = []
        for tr, va in folds:
            clf = SVC(
                kernel="precomputed",
                C=float(C),
                tol=float(cfg.tol),
                max_iter=int(cfg.max_iter),
                cache_size=float(cfg.cache_size),
                class_weight=cfg.class_weight,
                probability=False,
            )
            clf.fit(K[np.ix_(tr, tr)], y2[tr])
            pred = clf.predict(K[np.ix_(va, tr)])
            scores.append(float(balanced_accuracy_score(y2[va], pred)))
        mean_score = float(np.mean(scores))
        table.append({"C": float(C), "cv_bal_acc": mean_score})
        if best is None or mean_score > best[0] + 1e-12:
            best = (mean_score, float(C))

    assert best is not None
    tuned = dataclasses.replace(cfg, C=float(best[1]))
    info: Dict[str, Any] = {
        "mode": f"cv{int(n_splits)}",
        "selected_C": float(best[1]),
        "selected_gamma": "n/a",
        "cv_bal_acc": float(best[0]),
        "n_splits": int(n_splits),
        "cv_seed": int(seed),
        "scoring": "balanced_accuracy",
        "C_grid": [float(c) for c in C_grid],
        "kernel_source": "precomputed training fidelity kernel",
        "grid_table": table,
    }
    return tuned, info
