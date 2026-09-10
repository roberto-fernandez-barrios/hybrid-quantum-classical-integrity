"""Queue the 300 frozen v1.3.7 correction replay jobs."""

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

from src.experiments.run_v11_reinforcement_queue import DIMS, GATE_N_ENVIRONMENTS, MODEL_SEEDS, SPLIT_SEEDS
from src.experiments.run_v137_correction import ANALYSIS


@dataclass(frozen=True)
class CorrectionJob:
    kind: str
    gate: str
    split_seed: int
    model_seed: int
    svd_dim: int

    @property
    def stem(self) -> str:
        return f"v137__{self.kind}__{self.gate}__split{self.split_seed}__model{self.model_seed}__d{self.svd_dim}"

    def completed(self, repo: Path, out_dir: Path) -> bool:
        csv_path = repo / out_dir / f"{self.stem}.csv"
        json_path = repo / out_dir / f"{self.stem}.json"
        if not csv_path.is_file() or not json_path.is_file() or csv_path.stat().st_size == 0:
            return False
        try:
            meta = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            return False
        expected = 18 if self.kind == "gate1" else 106
        return (
            meta.get("analysis") == ANALYSIS
            and int(meta.get("schema_version", 0)) == 2
            and int(meta.get("expected_rows_per_model", 0)) == expected
        )

    def command(self, python_exe: str, out_dir: Path) -> list[str]:
        return [
            python_exe,
            "-m",
            "src.experiments.run_v137_correction",
            "--job-kind",
            self.kind,
            "--gate",
            self.gate,
            "--split-seed",
            str(self.split_seed),
            "--model-seed",
            str(self.model_seed),
            "--svd-dim",
            str(self.svd_dim),
            "--out-dir",
            out_dir.as_posix(),
        ]


def build_jobs() -> list[CorrectionJob]:
    calibrated = [
        CorrectionJob("calibrated", str(env["gate"]), split_seed, model_seed, dim)
        for env in GATE_N_ENVIRONMENTS
        for split_seed in SPLIT_SEEDS
        for model_seed in MODEL_SEEDS
        for dim in DIMS
    ]
    gate1 = [
        CorrectionJob("gate1", "gate1_id_cicids", split_seed, model_seed, dim)
        for split_seed in SPLIT_SEEDS
        for model_seed in (42, 43, 44, 45)
        for dim in DIMS
    ]
    jobs = calibrated + gate1
    if len(jobs) != 300:
        raise AssertionError(f"Expected 300 correction jobs, got {len(jobs)}")
    return jobs


def _run_job(
    job: CorrectionJob,
    repo: Path,
    out_dir: Path,
    python_exe: str,
    log_dir: Path,
    retries: int,
) -> dict[str, object]:
    log_path = log_dir / f"{job.stem}.log"
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
    started = time.time()
    attempts = 0
    while True:
        attempts += 1
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"\n===== attempt {attempts} start {time.strftime('%Y-%m-%dT%H:%M:%S')} =====\n")
            log.write(" ".join(job.command(python_exe, out_dir)) + "\n")
            log.flush()
            proc = subprocess.run(
                job.command(python_exe, out_dir), cwd=repo, env=env,
                stdout=log, stderr=subprocess.STDOUT, check=False,
            )
        ok = proc.returncode == 0 and job.completed(repo, out_dir)
        if ok or attempts > retries:
            return {
                "job": job.stem,
                "ok": bool(ok),
                "returncode": int(proc.returncode),
                "attempts": attempts,
                "seconds": round(time.time() - started, 2),
                "log": log_path.relative_to(repo).as_posix(),
            }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--n-jobs", type=int, default=4)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=Path("results/raw/paper15_v137_correction"))
    parser.add_argument("--status-out", type=Path, default=Path("results/paper_digest/paper15_v137_correction/queue_status.json"))
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    jobs = build_jobs()
    pending = [job for job in jobs if not job.completed(repo, args.out_dir)]
    print(f"[V137] planned={len(jobs)} completed={len(jobs) - len(pending)} pending={len(pending)}")
    if args.dry_run:
        for job in pending[:8]:
            print(" ".join(job.command(args.python, args.out_dir)))
        return

    log_dir = repo / "results/logs/paper15_v137_correction"
    log_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.n_jobs)) as pool:
        futures = {
            pool.submit(_run_job, job, repo, args.out_dir, args.python, log_dir, args.retries): job
            for job in pending
        }
        for done, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            results.append(result)
            print(
                f"[V137] {'OK' if result['ok'] else 'FAIL'} {done}/{len(pending)} "
                f"{result['job']} ({result['seconds']}s)",
                flush=True,
            )
    failures = [result for result in results if not result["ok"]]
    status = {
        "analysis": ANALYSIS,
        "planned_jobs": len(jobs),
        "executed_jobs": len(results),
        "failed_jobs": len(failures),
        "all_completed": all(job.completed(repo, args.out_dir) for job in jobs),
        "finished": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "jobs": [asdict(job) for job in jobs],
        "results": results,
    }
    status_path = repo / args.status_out
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(status, indent=2), encoding="utf-8", newline="\n")
    if failures or not status["all_completed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
