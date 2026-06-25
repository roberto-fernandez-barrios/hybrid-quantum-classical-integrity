# src/experiments/run_grid.py
#
# Grid runner for src.experiments.run_benchmark
#
# Key features:
#   - Supports protocol="id" | "ood" | "all" (ALL = run every discovered ID + every discovered OOD pair).
#   - Supports multiple ID datasets (explicit --id-data and/or patterns via --id-glob).
#   - Supports multiple OOD pairs via --ood-train-glob/--ood-test-glob (auto-paired by filename key).
#   - Robust resume (prefix-based) + strict JSON validation (incl. dataset sha256) to avoid false skips.
#   - Dataset hashes computed per dataset (cached per path) instead of per job.
#   - Default python executable is sys.executable (more reliable with venv).
#   - Optional retries + max-fails (paper-friendly stability).
#   - Cleanup can remove partials by prefix (not only the one expected file).
#   - Optionally pass signal defaults explicitly to runner to avoid future drift.
#   - Parallel mode uses chunksize=1 for more responsive fail-fast/max-fails stopping.
#   - Windows-friendly multiprocessing (freeze_support).
#
# Hardening in this version:
#   - FIX classic-only resume: allow __q* globbing but DO NOT accept wrong runs by accidentally "matching" scale_quantum.
#     We validate with ignore_scale_quantum=True for classic-only candidates, AND always enforce rcfg.run_quantum.
#   - Safer default required CSV columns.
#   - Windows/mp friendliness: job tuples pass only JSON/pickle-friendly primitives (paths as str).
#   - Added --plan mode and optional --manifest-out to emit a reproducible job manifest without executing.
#   - Thread env caps aligned with seed.py (adds VECLIB_MAXIMUM_THREADS, BLIS_NUM_THREADS).
#   - Resume classic-only: prioritize candidates whose JSON says run_quantum=false (less scanning).
#   - OOD pairing strict mode is truly strict: key collisions in tests become an error.
#   - Tuple arity guard: assert job tuple length to avoid silent unpack drift.
#   - Path-key normalization for dedupe (Windows case-insensitive, resolves).
#   - max-train/max-test passed to runner and embedded in prefix to match run_benchmark filenames.
#   - q_backend_method/q_max_iter propagated end-to-end (cfg, cmd, resume, logs, manifest).
#
from __future__ import annotations

import argparse
import glob
import hashlib
import itertools
import json
import multiprocessing as mp
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from tqdm import tqdm

from src.config import PATHS

# ----------------------------
# Defaults (paper-style)
# ----------------------------
DEFAULT_SPLIT_SEEDS = [42, 123, 999, 7, 2024]
DEFAULT_MODEL_SEEDS = [42, 123, 999]
DEFAULT_DIMS = [4, 6, 8, 10, 12]
DEFAULT_Q_FEATURE_MAPS = ["zz", "z", "pauli_xz", "pauli_xyz"]

DEFAULT_CLASSICAL_SCALE = "standard"
DEFAULT_QUANTUM_SCALE = "minmax2pi"
DEFAULT_ATTACK_SUITE = "v2"
DEFAULT_Q_BACKEND_METHOD = "statevector"
DEFAULT_Q_MAX_ITER = 2000

# Shared sample caps (must match run_benchmark defaults if you rely on defaults)
DEFAULT_MAX_TRAIN = 512
DEFAULT_MAX_TEST = 512

# Must match run_benchmark.py packing policy
_PACK_MULT = 1_000_000

# Keep these aligned with run_benchmark defaults (optional flags we can pass explicitly)
DEFAULT_SIG_BINS = 40
DEFAULT_SIG_CLIP_Q_LO = 0.005
DEFAULT_SIG_CLIP_Q_HI = 0.995
DEFAULT_MMD_MAX_SAMPLES = 512
DEFAULT_MMD_GAMMA = "median"
DEFAULT_MMD_MAX_PAIRS = 4096

# Resume safety: require only minimal stable columns to treat as "complete"
DEFAULT_REQUIRED_CSV_COLS = [
    "protocol",
    "split_seed",
    "model_seed",
    "svd_dim",
]

# Job tuple arity guard
_JOB_TUPLE_LEN = 30


# ----------------------------
# Config
# ----------------------------
@dataclass(frozen=True)
class GridCfg:
    protocol: str  # "id" | "ood" | "all"

    id_datasets: List[Path]
    ood_pairs: List[Tuple[Path, Path]]  # (train, test)

    outdir: Path
    log_dir: Path

    attack_suite: str
    split_seeds: List[int]
    model_seeds: List[int]
    dims: List[int]
    q_feature_maps: List[str]

    classical_scale: str
    quantum_scale: str
    quantum_reps: int
    quantum_shots: int
    quantum_backend_method: str
    quantum_max_iter: int

    # shared caps passed to run_benchmark
    max_train: int
    max_test: int

    run_quantum: bool
    run_both: bool

    classic_qscale_mode: str  # "fixed" | "cli"

    n_jobs: int
    resume: bool
    dry_run: bool
    fail_fast: bool

    allow_parallel_quantum: bool
    python_exe: str

    keep_failed_partials: bool
    env_omp_threads: int

    retries: int
    max_fails: int

    pass_signal_defaults: bool
    strict_ood_pairing: bool

    required_csv_cols: List[str]
    fail_summary_n: int

    plan: bool
    manifest_out: Optional[Path]


# ----------------------------
# Helpers
# ----------------------------
def _is_windows() -> bool:
    return sys.platform.startswith("win")


def _norm_path_key(p: Path) -> str:
    """
    Stable path key for dedupe:
      - uses resolve() when possible
      - Windows: lowercased (case-insensitive FS)
    """
    try:
        s = str(p.resolve())
    except Exception:
        s = str(p.absolute())
    return s.lower() if _is_windows() else s


def _parse_int_list(s: str) -> List[int]:
    s = (s or "").strip()
    if not s:
        return []
    parts = [p.strip() for p in (s.split(",") if "," in s else s.split()) if p.strip()]
    return [int(p) for p in parts]


def _parse_str_list(s: str) -> List[str]:
    s = (s or "").strip()
    if not s:
        return []
    parts = [p.strip() for p in (s.split(",") if "," in s else s.split()) if p.strip()]
    return parts


def _set_runtime_env(base_env: dict, omp_threads: int) -> dict:
    """
    Force thread caps for BLAS/OpenMP to keep runs stable across machines.
    """
    env = dict(base_env)
    if omp_threads and int(omp_threads) > 0:
        v = str(int(omp_threads))
        env["OMP_NUM_THREADS"] = v
        env["MKL_NUM_THREADS"] = v
        env["OPENBLAS_NUM_THREADS"] = v
        env["NUMEXPR_NUM_THREADS"] = v
        env["VECLIB_MAXIMUM_THREADS"] = v  # macOS Accelerate
        env["BLIS_NUM_THREADS"] = v
    return env


# ----------------------------
# Hashing (cached)
# ----------------------------
_HASH_CACHE: Dict[str, str] = {}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_file_cached(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """
    Cached sha256 by normalized path key.
    """
    k = _norm_path_key(path)
    if k in _HASH_CACHE:
        return _HASH_CACHE[k]
    v = sha256_file(path, chunk_size=chunk_size)
    _HASH_CACHE[k] = v
    return v


def _job_log_path(
    log_dir: Path,
    protocol: str,
    dtag: str,
    split_seed: int,
    model_seed: int,
    svd_dim: int,
    attack_suite: str,
    scale_classical: str,
    scale_quantum: str,
    max_train: int,
    max_test: int,
    q_feature_map: str,
    q_reps: int,
    q_shots: int,
    q_backend_method: str,
    q_max_iter: int,
    run_quantum: bool,
    attempt: Optional[int] = None,
) -> Path:
    """
    Include the main run-shaping knobs to avoid log overwrites across different grids.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    if run_quantum:
        qtag = f"{q_feature_map}__qr{int(q_reps)}__qb{q_backend_method}__qs{int(q_shots)}__qmi{int(q_max_iter)}"
    else:
        qtag = "qnone"
    base = log_dir / (
        f"grid__{protocol}{dtag}__split{split_seed}__model{model_seed}__d{svd_dim}"
        f"__mt{int(max_train)}__me{int(max_test)}"
        f"__c{scale_classical}__q{scale_quantum}__atk{attack_suite}__{qtag}"
    )
    if attempt is None:
        return base.with_suffix(".log")
    return base.with_name(base.name + f"__attempt{attempt}.log")


def _looks_complete_csv(csv_path: Path, *, required_cols: Optional[List[str]] = None) -> bool:
    """
    Conservative "complete" check.
    """
    if not csv_path.exists() or csv_path.stat().st_size <= 0:
        return False
    try:
        with csv_path.open("r", encoding="utf-8", errors="ignore") as f:
            header = (f.readline() or "").strip()
            second = (f.readline() or "").strip()
            if not header or not second:
                return False

        if required_cols:
            cols = [c.strip() for c in header.split(",") if c.strip()]
            colset = set(cols)
            for c in required_cols:
                if c not in colset:
                    return False

        return True
    except Exception:
        return False


def _read_json_safely(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _looks_complete_json(json_path: Path) -> bool:
    """
    Stricter than "size>10":
      - must parse as JSON dict
      - must have at least run_cfg + hashes keys
    """
    if not json_path.exists() or json_path.stat().st_size <= 10:
        return False
    meta = _read_json_safely(json_path)
    if not isinstance(meta, dict):
        return False
    if not isinstance(meta.get("run_cfg", None), dict):
        return False
    if not isinstance(meta.get("hashes", None), dict):
        return False
    return True


def _cleanup_partials_by_prefix(outdir: Path, prefix: str) -> None:
    """
    Remove any partials matching run__{prefix}__cfg*.{csv,json} plus tolerant ".csv.json".
    """
    try:
        for p in outdir.glob(f"run__{prefix}__cfg*.csv"):
            try:
                p.unlink()
            except Exception:
                pass
        for p in outdir.glob(f"run__{prefix}__cfg*.json"):
            try:
                p.unlink()
            except Exception:
                pass
        for p in outdir.glob(f"run__{prefix}__cfg*.csv.json"):
            try:
                p.unlink()
            except Exception:
                pass
    except Exception:
        pass


def _packed_seed(split_seed: int, model_seed: int) -> int:
    ss = int(split_seed)
    ms = int(model_seed)
    if ss < 0:
        raise ValueError("split_seed must be >= 0")
    if ms < 0 or ms >= _PACK_MULT:
        raise ValueError(f"model_seed must be in [0, {_PACK_MULT})")
    return ss * _PACK_MULT + ms


def _dataset_dtag_id(data: Path) -> str:
    did = sha256_file_cached(data)[:8]
    return f"__id{did}"


def _dataset_dtag_ood(data_train: Path, data_test: Path) -> str:
    tr = sha256_file_cached(data_train)[:8]
    te = sha256_file_cached(data_test)[:8]
    return f"__tr{tr}__te{te}"


def _dataset_full_hashes_id(data: Path) -> Dict[str, Optional[str]]:
    return {"data_sha256": sha256_file_cached(data), "train_sha256": None, "test_sha256": None}


def _dataset_full_hashes_ood(data_train: Path, data_test: Path) -> Dict[str, Optional[str]]:
    return {
        "data_sha256": None,
        "train_sha256": sha256_file_cached(data_train),
        "test_sha256": sha256_file_cached(data_test),
    }


def _run_prefix(
    protocol: str,
    dtag: str,
    split_seed: int,
    model_seed: int,
    svd_dim: int,
    attack_suite: str,
    scale_classical: str,
    scale_quantum: str,
    max_train: int,
    max_test: int,
    q_feature_map: str,
    q_reps: int,
    q_shots: int,
    q_backend_method: str,
    q_max_iter: int,
    run_quantum: bool,
) -> str:
    """
    Prefix aligned with src.experiments.run_benchmark output filenames.

    Must match run_benchmark.run_tag, excluding the final __cfg<fingerprint>.
    Current run_benchmark tag shape:
      proto{id|ood}__<dataset_tag>__seed...__cmodelssvc_rbf__cscale...__qscale...__atk...__qmaps...__cfg...
    """
    seed_packed = _packed_seed(split_seed, model_seed)

    qtag = (
        f"__qmaps{q_feature_map}__qr{int(q_reps)}__qb{q_backend_method}__qs{int(q_shots)}__qmi{int(q_max_iter)}"
        if run_quantum
        else "__qnone"
    )

    return (
        f"proto{protocol}{dtag}"
        f"__seed{seed_packed}__split{split_seed}__model{model_seed}__d{svd_dim}"
        f"__mt{int(max_train)}__me{int(max_test)}"
        f"__cmodelssvc_rbf"
        f"__cscale{scale_classical}__qscale{scale_quantum}"
        f"__atk{attack_suite}{qtag}"
    )


def _json_matches_job(
    meta: Dict[str, Any],
    *,
    protocol: str,
    split_seed: int,
    model_seed: int,
    svd_dim: int,
    attack_suite: str,
    scale_classical: str,
    scale_quantum: str,
    max_train: int,
    max_test: int,
    q_feature_map: str,
    q_reps: int,
    q_shots: int,
    q_backend_method: str,
    q_max_iter: int,
    run_quantum: bool,
    expected_hashes: Dict[str, Optional[str]],
    ignore_scale_quantum: bool = False,
) -> bool:
    rcfg = (meta or {}).get("run_cfg", {}) or {}

    def _eq(a: Any, b: Any) -> bool:
        return str(a) == str(b)

    if not _eq(rcfg.get("protocol"), protocol):
        return False
    if int(rcfg.get("split_seed", -1)) != int(split_seed):
        return False
    if int(rcfg.get("model_seed", -1)) != int(model_seed):
        return False
    if int(rcfg.get("svd_dim", -1)) != int(svd_dim):
        return False
    if not _eq(rcfg.get("attack_suite"), attack_suite):
        return False
    if not _eq(rcfg.get("scale_classical"), scale_classical):
        return False

    if int(rcfg.get("max_train", -999999)) != int(max_train):
        return False
    if int(rcfg.get("max_test", -999999)) != int(max_test):
        return False

    if not ignore_scale_quantum:
        if not _eq(rcfg.get("scale_quantum"), scale_quantum):
            return False

    if bool(rcfg.get("run_quantum", False)) != bool(run_quantum):
        return False

    if run_quantum:
        raw_maps = rcfg.get("q_feature_maps", rcfg.get("q_feature_map", None))

        if isinstance(raw_maps, (list, tuple)):
            maps = [str(x) for x in raw_maps]
        elif raw_maps is None:
            maps = []
        else:
            maps = [
                p.strip()
                for p in str(raw_maps).replace(";", ",").split(",")
                if p.strip()
            ]

        if maps != [str(q_feature_map)]:
            return False

        if int(rcfg.get("q_reps", -1)) != int(q_reps):
            return False
        if int(rcfg.get("q_shots", -1)) != int(q_shots):
            return False
        if not _eq(rcfg.get("q_backend_method"), q_backend_method):
            return False
        if int(rcfg.get("q_max_iter", -1)) != int(q_max_iter):
            return False

    hashes = (meta or {}).get("hashes", {}) or {}
    for k, v in expected_hashes.items():
        if v is None:
            continue
        if not _eq(hashes.get(k), v):
            return False

    return True


def _candidate_sidecar_jsons_for_csv(csv_path: Path) -> List[Path]:
    """
    Tolerate runner naming variations.
    """
    candidates = [
        csv_path.with_name(csv_path.stem + ".json"),
        Path(str(csv_path) + ".json"),
        csv_path.with_suffix(".json"),
    ]

    uniq: List[Path] = []
    seen: Set[str] = set()
    for p in candidates:
        key = str(p.absolute())
        if key in seen:
            continue
        seen.add(key)
        if p.exists():
            uniq.append(p)
    return uniq


def _prefix_glob_pattern_for_resume(prefix: str, *, allow_q_wildcard: bool) -> str:
    """
    Resume pattern for CSV discovery.

    The current runner embeds both qscale and qtag explicitly. We keep exact prefix
    matching by default because strict JSON validation already handles correctness
    and exact matching avoids false skips across different quantum settings.

    `allow_q_wildcard` is kept for backward compatibility with older call sites,
    but intentionally does not widen the pattern for current filenames.
    """
    _ = allow_q_wildcard
    return f"run__{prefix}__cfg*.csv"


def _json_run_quantum_flag(json_path: Path) -> Optional[bool]:
    meta = _read_json_safely(json_path)
    if not isinstance(meta, dict):
        return None
    rcfg = meta.get("run_cfg", None)
    if not isinstance(rcfg, dict):
        return None
    if "run_quantum" not in rcfg:
        return None
    return bool(rcfg.get("run_quantum"))


def _find_completed_run_by_prefix(
    outdir: Path,
    prefix: str,
    *,
    job_params: Dict[str, Any],
    required_csv_cols: Optional[List[str]] = None,
) -> Optional[Tuple[Path, Path]]:
    """
    Robust resume.
    """
    run_quantum = bool(job_params.get("run_quantum", False))
    allow_q_wildcard = (not run_quantum)

    pattern = _prefix_glob_pattern_for_resume(prefix, allow_q_wildcard=allow_q_wildcard)
    csvs = sorted(outdir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not csvs:
        return None

    for csv_path in csvs:
        if not _looks_complete_csv(csv_path, required_cols=required_csv_cols):
            continue

        json_candidates = _candidate_sidecar_jsons_for_csv(csv_path)
        if not json_candidates:
            json_candidates = sorted(
                outdir.glob(f"{csv_path.stem}*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

        if not run_quantum and json_candidates:
            preferred: List[Path] = []
            other: List[Path] = []
            for jp in json_candidates:
                flag = _json_run_quantum_flag(jp)
                if flag is False:
                    preferred.append(jp)
                else:
                    other.append(jp)
            json_candidates = preferred + other

        for json_path in json_candidates:
            if not _looks_complete_json(json_path):
                continue
            meta = _read_json_safely(json_path)
            if meta is None:
                continue

            if run_quantum:
                if _json_matches_job(meta, **job_params, ignore_scale_quantum=False):
                    return csv_path, json_path
            else:
                if _json_matches_job(meta, **job_params, ignore_scale_quantum=True):
                    return csv_path, json_path

    return None


def _build_cmd(
    python_exe: str,
    protocol: str,
    data: Optional[Path],
    data_train: Optional[Path],
    data_test: Optional[Path],
    outdir: Path,
    split_seed: int,
    model_seed: int,
    svd_dim: int,
    attack_suite: str,
    scale_classical: str,
    scale_quantum: str,
    max_train: int,
    max_test: int,
    q_feature_map: str,
    q_reps: int,
    q_shots: int,
    q_backend_method: str,
    q_max_iter: int,
    run_quantum: bool,
    pass_signal_defaults: bool,
) -> List[str]:
    cmd = [
        python_exe,
        "-m",
        "src.experiments.run_benchmark",
        "--svd-dim",
        str(int(svd_dim)),
        "--outdir",
        str(outdir),
        "--scale-classical",
        str(scale_classical),
        "--scale-quantum",
        str(scale_quantum),
        "--attack-suite",
        str(attack_suite),
        "--split-seed",
        str(int(split_seed)),
        "--model-seed",
        str(int(model_seed)),
        "--max-train",
        str(int(max_train)),
        "--max-test",
        str(int(max_test)),
    ]

    if protocol == "ood":
        assert data_train is not None and data_test is not None
        cmd += ["--data-train", str(data_train), "--data-test", str(data_test)]
    else:
        assert data is not None
        cmd += ["--data", str(data)]

    if pass_signal_defaults:
        cmd += [
            "--sig-bins",
            str(int(DEFAULT_SIG_BINS)),
            "--sig-clip-q-lo",
            str(float(DEFAULT_SIG_CLIP_Q_LO)),
            "--sig-clip-q-hi",
            str(float(DEFAULT_SIG_CLIP_Q_HI)),
            "--mmd-max-samples",
            str(int(DEFAULT_MMD_MAX_SAMPLES)),
            "--mmd-gamma",
            str(DEFAULT_MMD_GAMMA),
            "--mmd-max-pairs",
            str(int(DEFAULT_MMD_MAX_PAIRS)),
        ]

    if run_quantum:
        cmd += [
            "--run-quantum",
            "--q-feature-maps",
            str(q_feature_map),
            "--q-reps",
            str(int(q_reps)),
            "--q-shots",
            str(int(q_shots)),
            "--q-backend-method",
            str(q_backend_method),
            "--q-max-iter",
            str(int(q_max_iter)),
        ]

    return cmd


# ----------------------------
# Worker (pickle-friendly args)
# ----------------------------
def _run_one(job: Tuple) -> Tuple[bool, str, Optional[str]]:
    """
    Returns:
      ok, message, fail_log_path (only for failures)
    """
    if len(job) != _JOB_TUPLE_LEN:
        return False, f"[FAIL] internal: bad job tuple len={len(job)} expected={_JOB_TUPLE_LEN}", None

    (
        python_exe,
        protocol,
        data_s,
        data_train_s,
        data_test_s,
        dtag,
        expected_hashes,
        outdir_s,
        log_dir_s,
        attack_suite,
        split_seed,
        model_seed,
        svd_dim,
        scale_classical,
        scale_quantum,
        max_train,
        max_test,
        q_feature_map,
        q_reps,
        q_shots,
        q_backend_method,
        q_max_iter,
        run_quantum,
        resume,
        dry_run,
        keep_failed_partials,
        env_omp_threads,
        retries,
        pass_signal_defaults,
        required_csv_cols,
    ) = job

    outdir = Path(outdir_s)
    log_dir = Path(log_dir_s)
    data = Path(data_s) if data_s else None
    data_train = Path(data_train_s) if data_train_s else None
    data_test = Path(data_test_s) if data_test_s else None

    prefix = _run_prefix(
        protocol=protocol,
        dtag=dtag,
        split_seed=split_seed,
        model_seed=model_seed,
        svd_dim=svd_dim,
        attack_suite=attack_suite,
        scale_classical=scale_classical,
        scale_quantum=scale_quantum,
        max_train=int(max_train),
        max_test=int(max_test),
        q_feature_map=q_feature_map,
        q_reps=q_reps,
        q_shots=q_shots,
        q_backend_method=q_backend_method,
        q_max_iter=q_max_iter,
        run_quantum=run_quantum,
    )

    tag = (
        f"proto={protocol}{dtag} split={split_seed} model={model_seed} dim={svd_dim} "
        f"mt={int(max_train)} me={int(max_test)} "
        f"q={'on' if run_quantum else 'off'} fmap={q_feature_map if run_quantum else 'qnone'} "
        f"backend={q_backend_method if run_quantum else 'none'} qmi={q_max_iter if run_quantum else 'na'}"
    )

    job_params = {
        "protocol": protocol,
        "split_seed": split_seed,
        "model_seed": model_seed,
        "svd_dim": svd_dim,
        "attack_suite": attack_suite,
        "scale_classical": scale_classical,
        "scale_quantum": scale_quantum,
        "max_train": int(max_train),
        "max_test": int(max_test),
        "q_feature_map": q_feature_map,
        "q_reps": q_reps,
        "q_shots": q_shots,
        "q_backend_method": q_backend_method,
        "q_max_iter": q_max_iter,
        "run_quantum": run_quantum,
        "expected_hashes": expected_hashes,
    }

    if resume:
        found = _find_completed_run_by_prefix(
            outdir,
            prefix,
            job_params=job_params,
            required_csv_cols=required_csv_cols,
        )
        if found is not None:
            csv_path, _json_path = found
            return True, f"[SKIP] {tag} (exists: {csv_path.name})", None

    cmd = _build_cmd(
        python_exe=python_exe,
        protocol=protocol,
        data=data,
        data_train=data_train,
        data_test=data_test,
        outdir=outdir,
        split_seed=split_seed,
        model_seed=model_seed,
        svd_dim=svd_dim,
        attack_suite=attack_suite,
        scale_classical=scale_classical,
        scale_quantum=scale_quantum,
        max_train=int(max_train),
        max_test=int(max_test),
        q_feature_map=q_feature_map,
        q_reps=q_reps,
        q_shots=q_shots,
        q_backend_method=q_backend_method,
        q_max_iter=q_max_iter,
        run_quantum=run_quantum,
        pass_signal_defaults=pass_signal_defaults,
    )

    if dry_run:
        return True, f"[DRY]  {tag} -> {' '.join(cmd)}", None

    env = _set_runtime_env(os.environ, env_omp_threads)

    try:
        py_dir = str(Path(python_exe).resolve().parent)
    except Exception:
        py_dir = str(Path(python_exe).parent)

    env["PATH"] = py_dir + os.pathsep + env.get("PATH", "")
    env["PYTHONUNBUFFERED"] = "1"
    env["QISKIT_NUM_PROCS"] = "1"
    env["QISKIT_PARALLEL"] = "FALSE"

    cmd_u = list(cmd)
    if len(cmd_u) >= 1 and cmd_u[0] == python_exe and "-u" not in cmd_u[1:3]:
        cmd_u.insert(1, "-u")

    attempts = max(1, int(retries) + 1)
    last_log_path: Optional[Path] = None

    for attempt in range(1, attempts + 1):
        log_path = _job_log_path(
            log_dir=log_dir,
            protocol=protocol,
            dtag=dtag,
            split_seed=split_seed,
            model_seed=model_seed,
            svd_dim=svd_dim,
            attack_suite=attack_suite,
            scale_classical=scale_classical,
            scale_quantum=scale_quantum,
            max_train=int(max_train),
            max_test=int(max_test),
            q_feature_map=q_feature_map,
            q_reps=q_reps,
            q_shots=q_shots,
            q_backend_method=q_backend_method,
            q_max_iter=q_max_iter,
            run_quantum=run_quantum,
            attempt=attempt if attempts > 1 else None,
        )
        last_log_path = log_path

        try:
            with log_path.open("w", encoding="utf-8") as f:
                f.write(f"# TAG: {tag}\n")
                f.write(f"# PREFIX: {prefix}\n")
                f.write(f"# CMD: {' '.join(cmd_u)}\n")
                f.write(f"# ATTEMPT: {attempt}/{attempts}\n")
                f.write(f"# PYTHON_EXE: {python_exe}\n")
                f.write(f"# PATH0: {env.get('PATH', '')[:240]}\n\n")
                f.flush()

                subprocess.run(cmd_u, check=True, stdout=f, stderr=f, text=True, env=env)

            found = _find_completed_run_by_prefix(
                outdir,
                prefix,
                job_params=job_params,
                required_csv_cols=required_csv_cols,
            )
            if found is None:
                if not keep_failed_partials:
                    _cleanup_partials_by_prefix(outdir, prefix)
                return (
                    False,
                    f"[FAIL] {tag} -> missing/partial outputs (see {log_path.name})",
                    str(log_path),
                )

            return True, f"[OK]   {tag}", None

        except subprocess.CalledProcessError as e:
            if not keep_failed_partials:
                _cleanup_partials_by_prefix(outdir, prefix)

            if attempt < attempts:
                time.sleep(2.0)
                continue
            return False, f"[FAIL] {tag} -> exit={e.returncode} (see {log_path.name})", str(log_path)

        except Exception as e:
            if not keep_failed_partials:
                _cleanup_partials_by_prefix(outdir, prefix)

            if attempt < attempts:
                time.sleep(2.0)
                continue
            return False, f"[FAIL] {tag} -> {type(e).__name__}: {e} (see {log_path.name})", str(log_path)

    if last_log_path is not None:
        return False, f"[FAIL] {tag} -> unknown failure (see {last_log_path.name})", str(last_log_path)
    return False, f"[FAIL] {tag} -> unknown failure", None


# ----------------------------
# Dataset discovery (ID + OOD)
# ----------------------------
def _expand_globs(patterns: List[str], *, only_csv: bool = True) -> List[Path]:
    """
    Expand glob patterns robustly.
    """
    out: List[Path] = []

    for pat in patterns or []:
        pat = (pat or "").strip()
        if not pat:
            continue
        subpats = [p.strip() for p in pat.split(",") if p.strip()]
        for sp in subpats:
            matches = glob.glob(sp, recursive=True)
            for m in matches:
                out.append(Path(m))

    resolved: List[Path] = []
    for p in out:
        try:
            rp = p.resolve()
        except Exception:
            rp = p.absolute()
        if rp.exists():
            if only_csv and rp.suffix.lower() != ".csv":
                continue
            resolved.append(rp)

    seen: Set[str] = set()
    uniq: List[Path] = []
    for p in resolved:
        k = _norm_path_key(p)
        if k in seen:
            continue
        seen.add(k)
        uniq.append(p)

    return uniq


def _ood_key_from_name(p: Path) -> str:
    s = p.stem.lower()
    s = re.sub(r"(?:^|[_\-.])(train|tr)(?:$|[_\-.])", "_", s)
    s = re.sub(r"(?:^|[_\-.])(test|te)(?:$|[_\-.])", "_", s)
    s = re.sub(r"^(train|test|tr|te)[_\-.]+", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _similarity(a: str, b: str) -> float:
    """
    Simple, dependency-free similarity in [0,1].
    """
    ta = [t for t in a.split("_") if t]
    tb = [t for t in b.split("_") if t]
    sa = set(ta)
    sb = set(tb)
    if sa and sb:
        inter = len(sa & sb)
        union = len(sa | sb)
        jac = inter / max(union, 1)
    else:
        jac = 0.0

    if jac >= 0.5:
        return jac

    ca = set(a)
    cb = set(b)
    inter2 = len(ca & cb)
    union2 = len(ca | cb)
    return 0.5 * jac + 0.5 * (inter2 / max(union2, 1))


def _pair_ood(
    trains: List[Path],
    tests: List[Path],
    *,
    strict: bool,
) -> Tuple[List[Tuple[Path, Path]], List[Path], List[Path]]:
    if not trains or not tests:
        return [], trains or [], tests or []

    test_map: Dict[str, List[Path]] = {}
    for te in tests:
        test_map.setdefault(_ood_key_from_name(te), []).append(te)

    collisions = [(k, v) for k, v in test_map.items() if len(v) > 1]
    if strict and collisions:
        lines = [f"Strict OOD pairing: {len(collisions)} test-key collision(s) detected."]
        for k, v in collisions[:10]:
            names = ", ".join(sorted([p.name for p in v])[:8])
            more = "" if len(v) <= 8 else f" ... (+{len(v) - 8} more)"
            lines.append(f"  - key='{k}': {names}{more}")
        if len(collisions) > 10:
            lines.append(f"  ... ({len(collisions) - 10} more collision keys)")
        lines.append(
            "Fix filenames/globs so each normalized key maps to exactly one test file, or disable --strict-ood-pairing."
        )
        raise SystemExit("\n".join(["[ERROR] " + lines[0]] + lines[1:]))

    pairs: List[Tuple[Path, Path]] = []
    used_tests: Set[str] = set()
    used_trains: Set[str] = set()

    for tr in sorted(trains, key=lambda x: x.name):
        k = _ood_key_from_name(tr)
        candidates = [p for p in test_map.get(k, []) if _norm_path_key(p) not in used_tests]

        if not candidates and strict:
            continue

        if not candidates and not strict:
            trk = _ood_key_from_name(tr)
            best: Optional[Path] = None
            best_score = 0.0
            for te in tests:
                if _norm_path_key(te) in used_tests:
                    continue
                tek = _ood_key_from_name(te)
                score = _similarity(trk, tek)
                if score > best_score:
                    best_score = score
                    best = te

            if best is None or best_score < 0.72:
                continue
            candidates = [best]

        te = sorted(candidates, key=lambda x: x.name)[0]
        used_tests.add(_norm_path_key(te))
        used_trains.add(_norm_path_key(tr))
        pairs.append((tr, te))

    seen = set()
    uniq_pairs: List[Tuple[Path, Path]] = []
    for tr, te in pairs:
        key = (_norm_path_key(tr), _norm_path_key(te))
        if key in seen:
            continue
        seen.add(key)
        uniq_pairs.append((tr, te))

    unused_trains = [p for p in trains if _norm_path_key(p) not in used_trains]
    unused_tests = [p for p in tests if _norm_path_key(p) not in used_tests]
    return uniq_pairs, unused_trains, unused_tests


# ----------------------------
# Execution helpers (single phase)
# ----------------------------
def _execute_jobs(
    *,
    jobs: List[Tuple],
    phase_name: str,
    n_jobs: int,
    fail_fast: bool,
    max_fails: int,
    fail_summary_n: int,
) -> Tuple[int, int, List[str]]:
    """
    Runs a list of jobs either sequentially or in parallel.
    Returns: (ok_count, fail_count, fail_logs)
    """
    if not jobs:
        print(f"[OK] Phase '{phase_name}': no jobs.")
        return 0, 0, []

    ok_count = 0
    fail_count = 0
    fail_logs: List[str] = []

    def _should_stop() -> bool:
        if fail_fast and fail_count > 0:
            return True
        if max_fails and fail_count >= max_fails:
            return True
        return False

    print("\n==============================")
    print(f"PHASE: {phase_name}")
    print(f"Jobs:  {len(jobs)}")
    print(f"Workers: {n_jobs}")
    print("==============================\n")

    if n_jobs <= 1:
        for job in tqdm(jobs, desc=f"{phase_name}", unit="run"):
            ok, msg, flog = _run_one(job)
            tqdm.write(msg)
            ok_count += int(ok)
            fail_count += int(not ok)
            if (not ok) and flog:
                fail_logs.append(flog)
            if _should_stop():
                break
        return ok_count, fail_count, fail_logs

    ctx = mp.get_context("spawn") if _is_windows() else mp.get_context()

    with ctx.Pool(processes=n_jobs) as pool:
        for ok, msg, flog in tqdm(
            pool.imap_unordered(_run_one, jobs, chunksize=1),
            total=len(jobs),
            desc=f"{phase_name}",
            unit="run",
        ):
            tqdm.write(msg)
            ok_count += int(ok)
            fail_count += int(not ok)
            if (not ok) and flog:
                fail_logs.append(flog)

            if _should_stop():
                pool.terminate()
                pool.join()
                break

    if fail_logs and int(fail_summary_n) > 0:
        n = min(int(fail_summary_n), len(fail_logs))
        print(f"\n[SUMMARY] Phase '{phase_name}' failures: {fail_count}. Last {n} log(s):")
        for p in fail_logs[-n:]:
            print(f"  - {p}")

    return ok_count, fail_count, fail_logs


# ----------------------------
# Plan / manifest
# ----------------------------
def _job_to_manifest_entry(job: Tuple) -> Dict[str, Any]:
    if len(job) != _JOB_TUPLE_LEN:
        return {"error": f"bad job tuple len={len(job)} expected={_JOB_TUPLE_LEN}"}

    (
        python_exe,
        protocol,
        data_s,
        data_train_s,
        data_test_s,
        dtag,
        expected_hashes,
        outdir_s,
        _log_dir_s,
        attack_suite,
        split_seed,
        model_seed,
        svd_dim,
        scale_classical,
        scale_quantum,
        max_train,
        max_test,
        q_feature_map,
        q_reps,
        q_shots,
        q_backend_method,
        q_max_iter,
        run_quantum,
        _resume,
        _dry_run,
        _keep_failed_partials,
        _env_omp_threads,
        _retries,
        pass_signal_defaults,
        _required_csv_cols,
    ) = job

    outdir = Path(outdir_s)
    data = Path(data_s) if data_s else None
    data_train = Path(data_train_s) if data_train_s else None
    data_test = Path(data_test_s) if data_test_s else None

    prefix = _run_prefix(
        protocol=protocol,
        dtag=dtag,
        split_seed=split_seed,
        model_seed=model_seed,
        svd_dim=svd_dim,
        attack_suite=attack_suite,
        scale_classical=scale_classical,
        scale_quantum=scale_quantum,
        max_train=int(max_train),
        max_test=int(max_test),
        q_feature_map=q_feature_map,
        q_reps=q_reps,
        q_shots=q_shots,
        q_backend_method=q_backend_method,
        q_max_iter=q_max_iter,
        run_quantum=run_quantum,
    )

    cmd = _build_cmd(
        python_exe=python_exe,
        protocol=protocol,
        data=data,
        data_train=data_train,
        data_test=data_test,
        outdir=outdir,
        split_seed=split_seed,
        model_seed=model_seed,
        svd_dim=svd_dim,
        attack_suite=attack_suite,
        scale_classical=scale_classical,
        scale_quantum=scale_quantum,
        max_train=int(max_train),
        max_test=int(max_test),
        q_feature_map=q_feature_map,
        q_reps=q_reps,
        q_shots=q_shots,
        q_backend_method=q_backend_method,
        q_max_iter=q_max_iter,
        run_quantum=run_quantum,
        pass_signal_defaults=pass_signal_defaults,
    )

    allow_q_wild = (not run_quantum)
    csv_pattern = _prefix_glob_pattern_for_resume(prefix, allow_q_wildcard=allow_q_wild)

    return {
        "protocol": protocol,
        "dtag": dtag,
        "split_seed": split_seed,
        "model_seed": model_seed,
        "svd_dim": svd_dim,
        "attack_suite": attack_suite,
        "scale_classical": scale_classical,
        "scale_quantum": scale_quantum,
        "max_train": int(max_train),
        "max_test": int(max_test),
        "run_quantum": bool(run_quantum),
        "q_feature_map": q_feature_map if run_quantum else "qnone",
        "q_reps": int(q_reps),
        "q_shots": int(q_shots),
        "q_backend_method": str(q_backend_method) if run_quantum else "none",
        "q_max_iter": int(q_max_iter) if run_quantum else None,
        "expected_hashes": expected_hashes,
        "prefix": prefix,
        "out_csv_glob": str(outdir / csv_pattern),
        "cmd": cmd,
    }


# ----------------------------
# Main
# ----------------------------
def main():
    ap = argparse.ArgumentParser()

    ap.add_argument("--protocol", type=str, default="id", choices=["id", "ood", "all"])
    ap.add_argument("--data", type=str, default=str(PATHS.data_dir / "cicids_subset.csv"))

    ap.add_argument("--id-data", action="append", default=[], help="Repeatable explicit ID dataset path(s).")
    ap.add_argument("--id-glob", action="append", default=[], help='Repeatable glob pattern(s) for ID datasets.')

    ap.add_argument("--data-train", type=str, default=None)
    ap.add_argument("--data-test", type=str, default=None)

    ap.add_argument("--ood-train-glob", action="append", default=[], help="Repeatable glob pattern(s) for OOD train CSVs.")
    ap.add_argument("--ood-test-glob", action="append", default=[], help="Repeatable glob pattern(s) for OOD test CSVs.")

    ap.add_argument("--outdir", type=str, default=str(PATHS.raw_dir / "hais_cicids_runs"))
    ap.add_argument("--attack-suite", type=str, default=DEFAULT_ATTACK_SUITE)

    ap.add_argument("--split-seeds", type=str, default=",".join(map(str, DEFAULT_SPLIT_SEEDS)))
    ap.add_argument("--model-seeds", type=str, default=",".join(map(str, DEFAULT_MODEL_SEEDS)))
    ap.add_argument("--dims", type=str, default=",".join(map(str, DEFAULT_DIMS)))
    ap.add_argument("--q-feature-maps", type=str, default=",".join(DEFAULT_Q_FEATURE_MAPS))

    ap.add_argument("--scale-classical", type=str, default=DEFAULT_CLASSICAL_SCALE)
    ap.add_argument("--scale-quantum", type=str, default=DEFAULT_QUANTUM_SCALE)

    ap.add_argument("--q-reps", type=int, default=1)
    ap.add_argument("--q-shots", type=int, default=1024)
    ap.add_argument("--q-backend-method", type=str, default=DEFAULT_Q_BACKEND_METHOD, choices=["statevector", "qasm"])
    ap.add_argument("--q-max-iter", type=int, default=DEFAULT_Q_MAX_ITER)

    ap.add_argument("--max-train", type=int, default=DEFAULT_MAX_TRAIN, help="Max train samples passed to runner (0=all).")
    ap.add_argument("--max-test", type=int, default=DEFAULT_MAX_TEST, help="Max test samples passed to runner (0=all).")

    ap.add_argument("--no-quantum", action="store_true", help="Run classical only (skip QSVC)")
    ap.add_argument("--run-both", action="store_true", help="Run BOTH: classic-only runs AND quantum runs.")

    ap.add_argument(
        "--classic-qscale-mode",
        type=str,
        default="fixed",
        choices=["fixed", "cli"],
        help="fixed=use DEFAULT_QUANTUM_SCALE for classic-only runs; cli=use your --scale-quantum value.",
    )

    ap.add_argument("--n-jobs", type=int, default=1, help="Parallel workers")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fail-fast", action="store_true", help="Stop immediately on first failure")

    ap.add_argument("--allow-parallel-quantum", action="store_true", help="Allow quantum runs with n_jobs>1.")
    ap.add_argument("--python", type=str, default="", help="Default: current interpreter (sys.executable)")
    ap.add_argument("--log-dir", type=str, default="", help="Default: <outdir>/_logs")
    ap.add_argument("--keep-failed-partials", action="store_true")
    ap.add_argument("--omp-threads", type=int, default=1)

    ap.add_argument("--retries", type=int, default=0, help="Retries per job after failure (default 0)")
    ap.add_argument("--max-fails", type=int, default=0, help="Stop when failures reach this (0 = no limit)")

    ap.add_argument("--pass-signal-defaults", action="store_true", help="Pass runner signal defaults explicitly.")
    ap.add_argument("--strict-ood-pairing", action="store_true", help="Fail if OOD globs don't pair cleanly.")

    ap.add_argument(
        "--required-csv-cols",
        type=str,
        default=",".join(DEFAULT_REQUIRED_CSV_COLS),
        help="Comma-separated list of columns required for a CSV to count as complete (resume safety).",
    )

    ap.add_argument(
        "--fail-summary-n",
        type=int,
        default=12,
        help="Print last N failure log paths at end of each phase (0 disables).",
    )

    ap.add_argument("--plan", action="store_true", help="Do not execute; just print plan + optionally write manifest.")
    ap.add_argument(
        "--manifest-out",
        type=str,
        default="",
        help="If set, write a JSON manifest of planned jobs to this path (implies --plan).",
    )

    args = ap.parse_args()

    protocol = str(args.protocol).lower().strip()
    outdir = Path(args.outdir)
    log_dir = Path(args.log_dir) if args.log_dir else (outdir / "_logs")
    python_exe = str(args.python).strip() if str(args.python).strip() else sys.executable

    required_csv_cols = _parse_str_list(str(args.required_csv_cols))
    fail_summary_n = int(args.fail_summary_n)

    manifest_out = Path(args.manifest_out).resolve() if str(args.manifest_out).strip() else None
    plan = bool(args.plan) or (manifest_out is not None)

    if args.ood_train_glob and not args.ood_test_glob:
        print("[WARN] You provided --ood-train-glob but no --ood-test-glob. Pairing will likely yield 0 pairs.")
    if args.ood_test_glob and not args.ood_train_glob:
        print("[WARN] You provided --ood-test-glob but no --ood-train-glob. Pairing will likely yield 0 pairs.")

    # ----------------------------
    # Build ID dataset list
    # ----------------------------
    id_datasets: List[Path] = []

    if args.id_data:
        for p in args.id_data:
            p = (p or "").strip()
            if not p:
                continue
            id_datasets.append(Path(p).resolve())

    if args.id_glob:
        id_datasets.extend(_expand_globs(args.id_glob, only_csv=True))

    if not id_datasets and str(args.data).strip():
        id_datasets.append(Path(args.data).resolve())

    id_datasets = [p for p in id_datasets if p.exists() and p.suffix.lower() == ".csv"]

    seen_id: Set[str] = set()
    uniq_id: List[Path] = []
    for p in id_datasets:
        k = _norm_path_key(p)
        if k in seen_id:
            continue
        seen_id.add(k)
        uniq_id.append(p)
    id_datasets = uniq_id

    # ----------------------------
    # Build OOD pair list
    # ----------------------------
    ood_pairs: List[Tuple[Path, Path]] = []

    data_train = Path(args.data_train).resolve() if args.data_train else None
    data_test = Path(args.data_test).resolve() if args.data_test else None
    if data_train is not None or data_test is not None:
        if data_train is None or data_test is None:
            raise SystemExit("If using --data-train/--data-test, you must provide BOTH.")
        if not data_train.exists():
            raise SystemExit(f"Missing OOD train file: {data_train}")
        if not data_test.exists():
            raise SystemExit(f"Missing OOD test file: {data_test}")
        if data_train.suffix.lower() != ".csv" or data_test.suffix.lower() != ".csv":
            raise SystemExit("OOD train/test inputs must be .csv files.")
        ood_pairs.append((data_train, data_test))

    unused_tr: List[Path] = []
    unused_te: List[Path] = []
    train_globs = args.ood_train_glob or []
    test_globs = args.ood_test_glob or []
    if train_globs or test_globs:
        trains = _expand_globs(train_globs, only_csv=True)
        tests = _expand_globs(test_globs, only_csv=True)
        pairs, unused_tr, unused_te = _pair_ood(trains, tests, strict=bool(args.strict_ood_pairing))
        ood_pairs.extend(pairs)

    seen_pair: Set[str] = set()
    uniq_pairs: List[Tuple[Path, Path]] = []
    for tr, te in ood_pairs:
        key = f"{_norm_path_key(tr)}|{_norm_path_key(te)}"
        if key in seen_pair:
            continue
        seen_pair.add(key)
        uniq_pairs.append((tr, te))
    ood_pairs = uniq_pairs

    if unused_tr or unused_te:
        if unused_tr:
            print(f"[WARN] OOD pairing: {len(unused_tr)} train file(s) unused (no matched test). Examples:")
            for p in unused_tr[:8]:
                print(f"  - {p}")
            if len(unused_tr) > 8:
                print(f"  ... ({len(unused_tr) - 8} more)")
        if unused_te:
            print(f"[WARN] OOD pairing: {len(unused_te)} test file(s) unused (no matched train). Examples:")
            for p in unused_te[:8]:
                print(f"  - {p}")
            if len(unused_te) > 8:
                print(f"  ... ({len(unused_te) - 8} more)")

        if bool(args.strict_ood_pairing):
            raise SystemExit("Strict OOD pairing enabled and some files were left unmatched. Fix patterns or filenames.")

    # ----------------------------
    # Validate protocol requirements
    # ----------------------------
    if protocol == "id" and not id_datasets:
        raise SystemExit("Protocol=id but no ID datasets found. Use --data, --id-data, or --id-glob.")
    if protocol == "ood" and not ood_pairs:
        raise SystemExit("Protocol=ood but no OOD pairs found. Use --data-train/--data-test or --ood-*-glob.")
    if protocol == "all" and (not id_datasets and not ood_pairs):
        raise SystemExit("Protocol=all but nothing to run. Provide ID and/or OOD inputs.")

    cfg = GridCfg(
        protocol=protocol,
        id_datasets=id_datasets,
        ood_pairs=ood_pairs,
        outdir=outdir,
        log_dir=log_dir,
        attack_suite=str(args.attack_suite),
        split_seeds=_parse_int_list(args.split_seeds),
        model_seeds=_parse_int_list(args.model_seeds),
        dims=_parse_int_list(args.dims),
        q_feature_maps=_parse_str_list(args.q_feature_maps),
        classical_scale=str(args.scale_classical),
        quantum_scale=str(args.scale_quantum),
        quantum_reps=int(args.q_reps),
        quantum_shots=int(args.q_shots),
        quantum_backend_method=str(args.q_backend_method),
        quantum_max_iter=int(args.q_max_iter),
        max_train=int(args.max_train),
        max_test=int(args.max_test),
        run_quantum=not bool(args.no_quantum),
        run_both=bool(args.run_both),
        classic_qscale_mode=str(args.classic_qscale_mode),
        n_jobs=int(args.n_jobs),
        resume=bool(args.resume),
        dry_run=bool(args.dry_run),
        fail_fast=bool(args.fail_fast),
        allow_parallel_quantum=bool(args.allow_parallel_quantum),
        python_exe=python_exe,
        keep_failed_partials=bool(args.keep_failed_partials),
        env_omp_threads=int(args.omp_threads),
        retries=int(args.retries),
        max_fails=int(args.max_fails),
        pass_signal_defaults=bool(args.pass_signal_defaults),
        strict_ood_pairing=bool(args.strict_ood_pairing),
        required_csv_cols=required_csv_cols,
        fail_summary_n=fail_summary_n,
        plan=plan,
        manifest_out=manifest_out,
    )

    if not cfg.split_seeds:
        raise SystemExit("No split-seeds provided.")
    if not cfg.model_seeds:
        raise SystemExit("No model-seeds provided.")
    if not cfg.dims:
        raise SystemExit("No dims provided.")
    if cfg.run_quantum and not cfg.q_feature_maps:
        raise SystemExit("No q-feature-maps provided.")
    if cfg.run_both and not cfg.run_quantum:
        print("[WARN] --run-both ignored because --no-quantum is set (quantum disabled).")

    cfg.outdir.mkdir(parents=True, exist_ok=True)
    cfg.log_dir.mkdir(parents=True, exist_ok=True)

    classic_grid = list(itertools.product(cfg.split_seeds, cfg.model_seeds, cfg.dims, ["qnone"]))
    quantum_grid = list(itertools.product(cfg.split_seeds, cfg.model_seeds, cfg.dims, cfg.q_feature_maps)) if cfg.run_quantum else []

    if not cfg.run_quantum:
        grids_to_run: List[Tuple[bool, List[Tuple[int, int, int, str]]]] = [(False, classic_grid)]
    else:
        if cfg.run_both:
            grids_to_run = [(False, classic_grid), (True, quantum_grid)]
        else:
            grids_to_run = [(True, quantum_grid)]

    classic_scale_quantum = DEFAULT_QUANTUM_SCALE if cfg.classic_qscale_mode == "fixed" else cfg.quantum_scale
    if cfg.classic_qscale_mode == "fixed" and cfg.quantum_scale != DEFAULT_QUANTUM_SCALE:
        will_run_classic = (not cfg.run_quantum) or (cfg.run_both and cfg.run_quantum)
        if will_run_classic:
            print(
                f"[INFO] classic-qscale-mode=fixed: classic runs will use scale_quantum='{DEFAULT_QUANTUM_SCALE}' "
                f"(ignoring CLI --scale-quantum='{cfg.quantum_scale}') to keep filenames/resume stable."
            )

    classic_jobs: List[Tuple] = []
    quantum_jobs: List[Tuple] = []

    def _append_job(
        *,
        protocol0: str,
        data0: Optional[Path],
        tr0: Optional[Path],
        te0: Optional[Path],
        dtag0: str,
        expected_hashes0: Dict[str, Optional[str]],
        split_seed: int,
        model_seed: int,
        dim: int,
        run_q: bool,
        fmap: str,
    ) -> None:
        scale_q = cfg.quantum_scale if run_q else classic_scale_quantum

        job = (
            str(cfg.python_exe),
            str(protocol0),
            str(data0) if data0 is not None else "",
            str(tr0) if tr0 is not None else "",
            str(te0) if te0 is not None else "",
            str(dtag0),
            dict(expected_hashes0),
            str(cfg.outdir),
            str(cfg.log_dir),
            str(cfg.attack_suite),
            int(split_seed),
            int(model_seed),
            int(dim),
            str(cfg.classical_scale),
            str(scale_q),
            int(cfg.max_train),
            int(cfg.max_test),
            str(fmap if run_q else "qnone"),
            int(cfg.quantum_reps),
            int(cfg.quantum_shots),
            str(cfg.quantum_backend_method),
            int(cfg.quantum_max_iter),
            bool(run_q),
            bool(cfg.resume),
            bool(cfg.dry_run),
            bool(cfg.keep_failed_partials),
            int(cfg.env_omp_threads),
            int(cfg.retries),
            bool(cfg.pass_signal_defaults),
            list(cfg.required_csv_cols),
        )

        assert len(job) == _JOB_TUPLE_LEN, f"Internal bug: job tuple len={len(job)} expected={_JOB_TUPLE_LEN}"
        (quantum_jobs if run_q else classic_jobs).append(job)

    def _append_id_jobs(data_path: Path) -> None:
        dtag0 = _dataset_dtag_id(data_path)
        expected_hashes0 = _dataset_full_hashes_id(data_path)
        for run_q, grid in grids_to_run:
            for (split_seed, model_seed, dim, fmap) in grid:
                _append_job(
                    protocol0="id",
                    data0=data_path,
                    tr0=None,
                    te0=None,
                    dtag0=dtag0,
                    expected_hashes0=expected_hashes0,
                    split_seed=split_seed,
                    model_seed=model_seed,
                    dim=dim,
                    run_q=bool(run_q),
                    fmap=fmap,
                )

    def _append_ood_jobs(train_path: Path, test_path: Path) -> None:
        dtag0 = _dataset_dtag_ood(train_path, test_path)
        expected_hashes0 = _dataset_full_hashes_ood(train_path, test_path)
        for run_q, grid in grids_to_run:
            for (split_seed, model_seed, dim, fmap) in grid:
                _append_job(
                    protocol0="ood",
                    data0=None,
                    tr0=train_path,
                    te0=test_path,
                    dtag0=dtag0,
                    expected_hashes0=expected_hashes0,
                    split_seed=split_seed,
                    model_seed=model_seed,
                    dim=dim,
                    run_q=bool(run_q),
                    fmap=fmap,
                )

    if cfg.protocol in ("id", "all"):
        for p in cfg.id_datasets:
            _append_id_jobs(p)

    if cfg.protocol in ("ood", "all"):
        for tr, te in cfg.ood_pairs:
            _append_ood_jobs(tr, te)

    total_jobs = len(classic_jobs) + len(quantum_jobs)

    print("\n==============================")
    print("RUN GRID CONFIG")
    print("==============================")
    print(f"Protocol:           {cfg.protocol}")
    print(f"ID datasets:        {len(cfg.id_datasets)}")
    if cfg.id_datasets:
        for p in cfg.id_datasets[:12]:
            print(f"  - {p}")
        if len(cfg.id_datasets) > 12:
            print(f"  ... ({len(cfg.id_datasets) - 12} more)")
    print(f"OOD pairs:          {len(cfg.ood_pairs)}")
    if cfg.ood_pairs:
        for (tr, te) in cfg.ood_pairs[:8]:
            print(f"  - train={tr.name} | test={te.name}")
        if len(cfg.ood_pairs) > 8:
            print(f"  ... ({len(cfg.ood_pairs) - 8} more)")
    print(f"Output:             {cfg.outdir}")
    print(f"Logs:               {cfg.log_dir}")
    print(f"Attack suite:       {cfg.attack_suite}")
    print(f"Split seeds:        {cfg.split_seeds}")
    print(f"Model seeds:        {cfg.model_seeds}")
    print(f"Dims:               {cfg.dims}")
    print(f"Max train/test:     {cfg.max_train}/{cfg.max_test}")
    print(f"Quantum enabled:    {cfg.run_quantum}")
    print(f"Run both:           {cfg.run_both and cfg.run_quantum}")
    print(f"Classic qscale mode:{cfg.classic_qscale_mode} (classic uses '{classic_scale_quantum}')")
    if cfg.run_quantum:
        print(f"Q feature maps:     {cfg.q_feature_maps}")
        print(f"Q reps/shots:       {cfg.quantum_reps}/{cfg.quantum_shots}")
        print(f"Q backend/max_iter: {cfg.quantum_backend_method}/{cfg.quantum_max_iter}")
        print(f"Scale quantum:      {cfg.quantum_scale}")
    print(f"Scale classical:    {cfg.classical_scale}")
    print(f"Python exe:         {cfg.python_exe}")
    print(f"Jobs classic:       {len(classic_jobs)}")
    print(f"Jobs quantum:       {len(quantum_jobs)}")
    print(f"Jobs total:         {total_jobs}")
    print(f"Workers requested:  {cfg.n_jobs}")
    print(f"Resume:             {cfg.resume}")
    print(f"Dry-run:            {cfg.dry_run}")
    print(f"Fail-fast:          {cfg.fail_fast}")
    print(f"Retries/job:        {cfg.retries}")
    print(f"Max fails:          {cfg.max_fails} (0=no limit)")
    print(f"OMP threads:        {cfg.env_omp_threads}")
    print(f"Pass sig defaults:  {cfg.pass_signal_defaults}")
    print(f"Strict OOD pair:    {cfg.strict_ood_pairing}")
    print(f"Req CSV cols:       {cfg.required_csv_cols}")
    print(f"Fail summary N:     {cfg.fail_summary_n}")
    print(f"Plan mode:          {cfg.plan}")
    if cfg.manifest_out is not None:
        print(f"Manifest out:       {cfg.manifest_out}")
    print("==============================\n")

    if total_jobs == 0:
        print("[OK] Nothing to run (empty job list).")
        return

    if cfg.plan:
        manifest: Dict[str, Any] = {
            "config": {
                "protocol": cfg.protocol,
                "outdir": str(cfg.outdir),
                "log_dir": str(cfg.log_dir),
                "attack_suite": cfg.attack_suite,
                "split_seeds": cfg.split_seeds,
                "model_seeds": cfg.model_seeds,
                "dims": cfg.dims,
                "max_train": int(cfg.max_train),
                "max_test": int(cfg.max_test),
                "run_quantum": cfg.run_quantum,
                "run_both": cfg.run_both and cfg.run_quantum,
                "classic_qscale_mode": cfg.classic_qscale_mode,
                "scale_classical": cfg.classical_scale,
                "scale_quantum": cfg.quantum_scale,
                "q_feature_maps": cfg.q_feature_maps,
                "q_reps": cfg.quantum_reps,
                "q_shots": cfg.quantum_shots,
                "q_backend_method": cfg.quantum_backend_method,
                "q_max_iter": cfg.quantum_max_iter,
                "required_csv_cols": cfg.required_csv_cols,
                "strict_ood_pairing": cfg.strict_ood_pairing,
            },
            "counts": {
                "classic_jobs": len(classic_jobs),
                "quantum_jobs": len(quantum_jobs),
                "total_jobs": total_jobs,
            },
            "jobs": [],
        }

        for j in classic_jobs:
            entry = _job_to_manifest_entry(j)
            entry["phase"] = "classic"
            manifest["jobs"].append(entry)
        for j in quantum_jobs:
            entry = _job_to_manifest_entry(j)
            entry["phase"] = "quantum"
            manifest["jobs"].append(entry)

        print("[PLAN] Job counts:")
        print(f"  classic: {len(classic_jobs)}")
        print(f"  quantum: {len(quantum_jobs)}")
        print(f"  total:   {total_jobs}")

        preview_n = min(20, len(manifest["jobs"]))
        print(f"\n[PLAN] Preview first {preview_n} job(s):")
        for i in range(preview_n):
            e = manifest["jobs"][i]
            print(f"{i+1:>3}/{len(manifest['jobs'])} [{e['phase']}] -> {e['out_csv_glob']}")
            print(f"      CMD: {' '.join(e['cmd'])}")

        if cfg.manifest_out is not None:
            cfg.manifest_out.parent.mkdir(parents=True, exist_ok=True)
            cfg.manifest_out.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
            print(f"\n[OK] Wrote manifest -> {cfg.manifest_out}")

        print("\n[OK] Plan complete. (No execution)")
        return

    if cfg.dry_run:
        merged_preview = classic_jobs + quantum_jobs
        max_show = min(80, len(merged_preview))
        for i in range(max_show):
            e = _job_to_manifest_entry(merged_preview[i])
            print(f"{i+1:>3}/{len(merged_preview)} -> {e.get('out_csv_glob','?')}")
            cmd = e.get("cmd", [])
            if isinstance(cmd, list):
                print(f"      CMD: {' '.join(cmd)}")
        if len(merged_preview) > max_show:
            print(f"... ({len(merged_preview) - max_show} more)")
        print("\n[OK] Dry run complete.")
        return

    ok_total = 0
    fail_total = 0
    all_fail_logs: List[str] = []

    if classic_jobs:
        ok1, fail1, fail_logs1 = _execute_jobs(
            jobs=classic_jobs,
            phase_name="Classic runs",
            n_jobs=max(1, int(cfg.n_jobs)),
            fail_fast=bool(cfg.fail_fast),
            max_fails=int(cfg.max_fails),
            fail_summary_n=int(cfg.fail_summary_n),
        )
        ok_total += ok1
        fail_total += fail1
        all_fail_logs.extend(fail_logs1)

        if cfg.fail_fast and fail1 > 0:
            print(f"\n[STOP] Fail-fast triggered after classic phase. ok={ok_total} fail={fail_total}")
            return
        if cfg.max_fails and fail_total >= cfg.max_fails:
            print(f"\n[STOP] Max-fails reached after classic phase. ok={ok_total} fail={fail_total}")
            return

    if quantum_jobs:
        effective_q_jobs = max(1, int(cfg.n_jobs))
        if effective_q_jobs > 1 and not cfg.allow_parallel_quantum:
            print("[WARN] Quantum phase with n_jobs>1 -> forcing n_jobs=1 (use --allow-parallel-quantum to override).")
            effective_q_jobs = 1

        ok2, fail2, fail_logs2 = _execute_jobs(
            jobs=quantum_jobs,
            phase_name="Quantum runs",
            n_jobs=effective_q_jobs,
            fail_fast=bool(cfg.fail_fast),
            max_fails=int(cfg.max_fails),
            fail_summary_n=int(cfg.fail_summary_n),
        )
        ok_total += ok2
        fail_total += fail2
        all_fail_logs.extend(fail_logs2)

    print(f"\n[OK] Completed. ok={ok_total} fail={fail_total}")

    if all_fail_logs and int(cfg.fail_summary_n) > 0:
        n = min(int(cfg.fail_summary_n), len(all_fail_logs))
        print(f"\n[SUMMARY] Total failures: {fail_total}. Last {n} log(s):")
        for p in all_fail_logs[-n:]:
            print(f"  - {p}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
