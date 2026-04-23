# src/utils/seed.py
from __future__ import annotations

import os
import random
from typing import Optional, Dict, Any

import numpy as np


_THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",  # macOS Accelerate
    "BLIS_NUM_THREADS",
)


def _set_thread_caps(
    threads: int,
    *,
    respect_existing_env: bool = True,
    force_env: bool = False,
) -> None:
    """
    Best-effort thread caps for BLAS/OpenMP runtimes.

    Notes:
      - For full effect, set these before importing numpy / heavy libs,
        or enforce at process launch (recommended: set env in run_grid subprocess).
      - If respect_existing_env=True (default), do not overwrite variables already set.
      - If force_env=True, overwrite regardless (wins over respect_existing_env).
      - threads <= 0 => no-op.
    """
    if threads <= 0:
        return

    v = str(int(threads))
    for k in _THREAD_ENV_KEYS:
        if force_env:
            os.environ[k] = v
        else:
            if respect_existing_env and k in os.environ:
                continue
            os.environ[k] = v


def seed_everything(
    seed: int,
    deterministic: bool = True,
    *,
    set_hash_seed: bool = False,
    force_omp_threads: Optional[int] = None,
    respect_existing_env: bool = True,
    force_env: bool = False,
) -> np.random.Generator:
    """
    Seed major RNG sources for reproducibility.

    Seeded:
      - Python's random
      - NumPy legacy RNG (np.random.seed)
      - NumPy Generator API (returns seeded Generator)
      - Qiskit algorithm_globals (if available)

    Notes:
      - For full determinism of BLAS/OpenMP threads, set env vars at process launch.
      - PYTHONHASHSEED only fully applies if set before Python starts.
      - force_omp_threads:
          * None => if deterministic=True, defaults to 1
          * 0    => do not set thread caps (even if deterministic=True)
    """
    seed = int(seed)
    if seed < 0:
        raise ValueError(f"seed must be >= 0, got {seed}")

    # Traceability: may not retroactively affect hashing
    if set_hash_seed:
        os.environ["PYTHONHASHSEED"] = str(seed)

    # Best-effort deterministic thread caps
    if deterministic:
        threads = 1 if force_omp_threads is None else int(force_omp_threads)
        if threads < 0:
            raise ValueError(f"force_omp_threads must be >= 0 (or None), got {threads}")
        _set_thread_caps(threads, respect_existing_env=respect_existing_env, force_env=force_env)

    # Python RNG
    random.seed(seed)

    # NumPy RNG (legacy + Generator)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)

    # Optional: Qiskit RNG
    try:
        from qiskit.utils import algorithm_globals  # type: ignore

        algorithm_globals.random_seed = seed
    except Exception:
        pass

    return rng


def get_rng_state(rng: Optional[np.random.Generator] = None) -> Dict[str, Any]:
    """
    Capture RNG state for:
      - Python random
      - NumPy legacy RNG
      - optional NumPy Generator (bit_generator.state)

    Not JSON-serializable as-is; intended for in-memory save/restore.

    Includes some traceability env fields for reproducibility debugging.
    """
    state: Dict[str, Any] = {
        "python_random": random.getstate(),
        "numpy_legacy": np.random.get_state(),
        "env": {
            "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
            **{k: os.environ.get(k) for k in _THREAD_ENV_KEYS if k in os.environ},
        },
    }
    if rng is not None:
        state["numpy_generator"] = rng.bit_generator.state
    return state


def set_rng_state(state: Dict[str, Any], rng: Optional[np.random.Generator] = None) -> None:
    """
    Restore RNG state captured via get_rng_state().

    Note: we do not automatically restore env vars here (on purpose).
    If you want env restoration, do it explicitly at process launch.
    """
    if "python_random" in state:
        random.setstate(state["python_random"])
    if "numpy_legacy" in state:
        np.random.set_state(state["numpy_legacy"])
    if rng is not None and "numpy_generator" in state:
        rng.bit_generator.state = state["numpy_generator"]
