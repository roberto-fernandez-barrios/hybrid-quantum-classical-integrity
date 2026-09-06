"""Paper 1.5 reinforcement queue (artifact 1.1.0): Gates N, P and T.

Executes the prespecified reinforcement gates recorded in
``manuscript/paper15_v11_reinforcement_prereg.md`` by invoking
``src.experiments.run_benchmark`` once per (environment, split seed, model seed,
projected dimension) cell. Every job uses the tagged ``exact_statevector``
engine. Re-running is safe: completed jobs are detected from their run-tag
prefix and skipped.

Gate N  null calibration    ``paper_null`` suite over the eight expansion
                            environments (frozen maps and sample caps)
Gate P  preprocessing       CICIDS ID 128/128, ``paper_core``, ZZ vs SVC under
                            three scaler configurations
Gate T  tuned baselines     CICIDS ID 128/128 and UNSW temporal OOD,
                            ``paper_core``, 5-fold CV tuning of both learners

Usage (from the repository root):

    .venv/Scripts/python.exe -m src.experiments.run_v11_reinforcement_queue --gates N,P,T
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from src.experiments.run_benchmark import _dataset_tag_from_hashes, _packed_seed, sha256_file


SPLIT_SEEDS: Sequence[int] = (42, 43, 44, 45, 46)
MODEL_SEEDS: Sequence[int] = (42, 43)
DIMS: Sequence[int] = (8, 10, 12)

Q_REPS = 1
Q_SHOTS = 1024
Q_BACKEND = "exact_statevector"
Q_MAX_ITER = 1000

CICIDS_ID = "data/cicids_subset.csv"
UNSW_ID = "data/unsw_subset.csv"
TON_ID = "data/ton_iot_subset.csv"

# Gate N environments mirror the frozen expansion (``build_q1_expansion_evidence.GATES``).
GATE_N_ENVIRONMENTS: List[Dict[str, object]] = [
    {"gate": "gate2_id_256", "protocol": "id", "data": CICIDS_ID, "maps": ["zz"], "n": 256},
    {
        "gate": "gate3a_ood_tue_wed",
        "protocol": "ood",
        "data_train": "data/processed/cicids_ood_tuesday_train.csv",
        "data_test": "data/processed/cicids_ood_wednesday_test.csv",
        "maps": ["zz"],
        "n": 128,
    },
    {
        "gate": "gate3b_ood_tue_fri_portscan",
        "protocol": "ood",
        "data_train": "data/processed/cicids_ood_tuesday_train_portscan.csv",
        "data_test": "data/processed/cicids_ood_friday_portscan_test.csv",
        "maps": ["zz"],
        "n": 128,
    },
    {
        "gate": "gate3c_ood_wed_thu_webattacks",
        "protocol": "ood",
        "data_train": "data/processed/cicids_ood_wednesday_train.csv",
        "data_test": "data/processed/cicids_ood_thursday_webattacks_test.csv",
        "maps": ["zz"],
        "n": 128,
    },
    {
        "gate": "gate3d_ood_wed_fri_morning",
        "protocol": "ood",
        "data_train": "data/processed/cicids_ood_wednesday_train.csv",
        "data_test": "data/processed/cicids_ood_friday_morning_test.csv",
        "maps": ["zz"],
        "n": 128,
    },
    {"gate": "gate5a_id_unsw", "protocol": "id", "data": UNSW_ID, "maps": ["zz", "z", "pauli_xyz"], "n": 128},
    {"gate": "gate5b_id_ton_iot", "protocol": "id", "data": TON_ID, "maps": ["zz", "z", "pauli_xyz"], "n": 128},
    {
        "gate": "gate6_ood_unsw",
        "protocol": "ood",
        "data_train": "data/processed/unsw_ood_train.csv",
        "data_test": "data/processed/unsw_ood_test.csv",
        "maps": ["zz"],
        "n": 128,
    },
]

GATE_P_CONFIGS: List[Dict[str, str]] = [
    {"config": "P0_reference", "scale_classical": "standard", "scale_quantum": "minmax2pi"},
    {"config": "PA_standard_standard", "scale_classical": "standard", "scale_quantum": "standard"},
    {"config": "PB_minmax2pi_minmax2pi", "scale_classical": "minmax2pi", "scale_quantum": "minmax2pi"},
]

GATE_T_ENVIRONMENTS: List[Dict[str, object]] = [
    {"gate": "gate1_id_cicids", "protocol": "id", "data": CICIDS_ID, "maps": ["zz"], "n": 128},
    {
        "gate": "gate6_ood_unsw",
        "protocol": "ood",
        "data_train": "data/processed/unsw_ood_train.csv",
        "data_test": "data/processed/unsw_ood_test.csv",
        "maps": ["zz"],
        "n": 128,
    },
]


@dataclass
class Job:
    gate_family: str
    gate: str
    outdir: str
    protocol: str
    data: Optional[str]
    data_train: Optional[str]
    data_test: Optional[str]
    split_seed: int
    model_seed: int
    svd_dim: int
    maps: List[str]
    max_train: int
    max_test: int
    attack_suite: str
    scale_classical: str
    scale_quantum: str
    svc_tune: str
    qsvc_tune: str

    def name(self) -> str:
        return f"{self.gate_family}__{self.gate}__split{self.split_seed}__model{self.model_seed}__d{self.svd_dim}"

    def dataset_tag(self, repo: Path) -> str:
        if self.protocol == "ood":
            assert self.data_train and self.data_test
            hashes = {
                "train": sha256_file(repo / self.data_train)[:8],
                "test": sha256_file(repo / self.data_test)[:8],
                "id": "",
            }
        else:
            assert self.data
            hashes = {"train": "", "test": "", "id": sha256_file(repo / self.data)[:8]}
        return _dataset_tag_from_hashes(self.protocol, hashes)

    def run_tag_prefix(self, repo: Path) -> str:
        seed = _packed_seed(self.split_seed, self.model_seed)
        qtag = (
            f"__qmaps{'-'.join(self.maps)}__qr{Q_REPS}__qb{Q_BACKEND}"
            f"__qs{Q_SHOTS}__qmi{Q_MAX_ITER}"
        )
        return (
            f"proto{self.protocol}__{self.dataset_tag(repo)}"
            f"__seed{seed}__split{self.split_seed}__model{self.model_seed}__d{self.svd_dim}"
            f"__mt{self.max_train}__me{self.max_test}"
            f"__cmodelssvc_rbf"
            f"__cscale{self.scale_classical}__qscale{self.scale_quantum}"
            f"__atk{self.attack_suite}{qtag}"
        )

    def completed(self, repo: Path) -> bool:
        outdir = repo / self.outdir
        if not outdir.is_dir():
            return False
        prefix = self.run_tag_prefix(repo)
        for csv_path in outdir.glob(f"run__{prefix}__cfg*.csv"):
            json_path = csv_path.with_suffix(".json")
            if json_path.is_file() and csv_path.stat().st_size > 0:
                return True
        return False

    def command(self, python_exe: str) -> List[str]:
        cmd = [
            python_exe,
            "-m",
            "src.experiments.run_benchmark",
            "--svd-dim", str(self.svd_dim),
            "--outdir", self.outdir,
            "--scale-classical", self.scale_classical,
            "--scale-quantum", self.scale_quantum,
            "--attack-suite", self.attack_suite,
            "--split-seed", str(self.split_seed),
            "--model-seed", str(self.model_seed),
            "--max-train", str(self.max_train),
            "--max-test", str(self.max_test),
        ]
        if self.protocol == "ood":
            assert self.data_train and self.data_test
            cmd += ["--data-train", self.data_train, "--data-test", self.data_test]
        else:
            assert self.data
            cmd += ["--data", self.data]
        cmd += [
            "--run-quantum",
            "--q-feature-maps", ",".join(self.maps),
            "--q-reps", str(Q_REPS),
            "--q-shots", str(Q_SHOTS),
            "--q-backend-method", Q_BACKEND,
            "--q-max-iter", str(Q_MAX_ITER),
            "--svc-tune", self.svc_tune,
            "--qsvc-tune", self.qsvc_tune,
        ]
        return cmd


def _cells() -> List[tuple[int, int, int]]:
    return [(s, m, d) for s in SPLIT_SEEDS for m in MODEL_SEEDS for d in DIMS]


def _env_job(
    *,
    gate_family: str,
    env: Dict[str, object],
    outdir: str,
    split_seed: int,
    model_seed: int,
    svd_dim: int,
    attack_suite: str,
    scale_classical: str,
    scale_quantum: str,
    svc_tune: str,
    qsvc_tune: str,
) -> Job:
    n = int(env["n"])
    return Job(
        gate_family=gate_family,
        gate=str(env["gate"]),
        outdir=outdir,
        protocol=str(env["protocol"]),
        data=str(env["data"]) if env.get("data") else None,
        data_train=str(env["data_train"]) if env.get("data_train") else None,
        data_test=str(env["data_test"]) if env.get("data_test") else None,
        split_seed=split_seed,
        model_seed=model_seed,
        svd_dim=svd_dim,
        maps=[str(m) for m in env["maps"]],  # type: ignore[union-attr]
        max_train=n,
        max_test=n,
        attack_suite=attack_suite,
        scale_classical=scale_classical,
        scale_quantum=scale_quantum,
        svc_tune=svc_tune,
        qsvc_tune=qsvc_tune,
    )


def build_jobs(gates: Sequence[str]) -> List[Job]:
    jobs: List[Job] = []
    if "N" in gates:
        for env in GATE_N_ENVIRONMENTS:
            outdir = f"results/raw/paper15_v11_null_{env['gate']}"
            for s, m, d in _cells():
                jobs.append(
                    _env_job(
                        gate_family="gateN",
                        env=env,
                        outdir=outdir,
                        split_seed=s,
                        model_seed=m,
                        svd_dim=d,
                        attack_suite="paper_null",
                        scale_classical="standard",
                        scale_quantum="minmax2pi",
                        svc_tune="none",
                        qsvc_tune="none",
                    )
                )
    if "P" in gates:
        env = {"gate": "gate1_id_cicids", "protocol": "id", "data": CICIDS_ID, "maps": ["zz"], "n": 128}
        for config in GATE_P_CONFIGS:
            outdir = f"results/raw/paper15_v11_prep_{config['config']}"
            for s, m, d in _cells():
                job = _env_job(
                    gate_family="gateP",
                    env=env,
                    outdir=outdir,
                    split_seed=s,
                    model_seed=m,
                    svd_dim=d,
                    attack_suite="paper_core",
                    scale_classical=config["scale_classical"],
                    scale_quantum=config["scale_quantum"],
                    svc_tune="none",
                    qsvc_tune="none",
                )
                job.gate = f"{env['gate']}__{config['config']}"
                jobs.append(job)
    if "T" in gates:
        for env in GATE_T_ENVIRONMENTS:
            outdir = f"results/raw/paper15_v11_tuned_{env['gate']}"
            for s, m, d in _cells():
                jobs.append(
                    _env_job(
                        gate_family="gateT",
                        env=env,
                        outdir=outdir,
                        split_seed=s,
                        model_seed=m,
                        svd_dim=d,
                        attack_suite="paper_core",
                        scale_classical="standard",
                        scale_quantum="minmax2pi",
                        svc_tune="cv5",
                        qsvc_tune="cv5",
                    )
                )
    return jobs


def _run_job(job: Job, *, repo: Path, python_exe: str, log_dir: Path, retries: int) -> Dict[str, object]:
    log_path = log_dir / f"{job.name()}.log"
    env = dict(os.environ)
    env.update(
        {
            "PYTHONUNBUFFERED": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        }
    )
    attempts = 0
    started = time.time()
    while True:
        attempts += 1
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"\n===== attempt {attempts} start {time.strftime('%Y-%m-%dT%H:%M:%S')} =====\n")
            log.write(" ".join(job.command(python_exe)) + "\n")
            log.flush()
            proc = subprocess.run(
                job.command(python_exe),
                cwd=str(repo),
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
        ok = proc.returncode == 0 and job.completed(repo)
        if ok or attempts > retries:
            return {
                "job": job.name(),
                "ok": bool(ok),
                "returncode": int(proc.returncode),
                "attempts": attempts,
                "seconds": round(time.time() - started, 2),
                "log": log_path.as_posix(),
            }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gates", type=str, default="N,P,T", help="Comma-separated subset of N,P,T")
    parser.add_argument("--n-jobs", type=int, default=2)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--python", type=str, default=sys.executable)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--status-out",
        type=Path,
        default=Path("results/paper_digest/paper15_v11_reinforcement/queue_status.json"),
    )
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    gates = tuple(g.strip().upper() for g in str(args.gates).split(",") if g.strip())
    unknown = sorted(set(gates) - {"N", "P", "T"})
    if unknown:
        raise SystemExit(f"Unknown gates {unknown}; use a subset of N,P,T")

    jobs = build_jobs(gates)
    pending = [job for job in jobs if not job.completed(repo)]
    print(f"[V11-QUEUE] gates={gates} planned={len(jobs)} completed={len(jobs) - len(pending)} pending={len(pending)}")

    log_dir = repo / "results" / "logs" / "paper15_v11_reinforcement"
    log_dir.mkdir(parents=True, exist_ok=True)
    status_path = repo / args.status_out
    status_path.parent.mkdir(parents=True, exist_ok=True)

    plan = {
        "gates": list(gates),
        "planned_jobs": len(jobs),
        "jobs": [asdict(job) for job in jobs],
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if args.dry_run:
        for job in pending[:10]:
            print(" ".join(job.command(args.python)))
        print(json.dumps({"planned": len(jobs), "pending": len(pending)}, indent=2))
        return

    results: List[Dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=max(1, int(args.n_jobs))) as pool:
        futures = {
            pool.submit(
                _run_job,
                job,
                repo=repo,
                python_exe=args.python,
                log_dir=log_dir,
                retries=int(args.retries),
            ): job
            for job in pending
        }
        done = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            done += 1
            state = "OK " if result["ok"] else "FAIL"
            print(f"[V11-QUEUE] {state} {done}/{len(pending)} {result['job']} ({result['seconds']}s)", flush=True)

    failures = [r for r in results if not r["ok"]]
    plan.update(
        {
            "finished": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "executed": len(results),
            "failed": len(failures),
            "results": results,
            "all_completed": all(job.completed(repo) for job in jobs),
        }
    )
    status_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(json.dumps({"executed": len(results), "failed": len(failures), "all_completed": plan["all_completed"]}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
