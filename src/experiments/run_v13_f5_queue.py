"""Paper 1.5 adversarial queue (artifact 1.3.0): Gate A, cluster-preserving perturbation.

Executes the prespecified adversarial gate recorded in
``manuscript/paper15_v13_prereg.md`` by invoking ``src.experiments.run_benchmark``
once per (environment, split seed, model seed, projected dimension) cell of
the eight null-calibration environments with the ``paper_f5`` suite: the two
executed feature-side drift mechanisms at the frozen strengths (matched
controls, identical attack seeds to the frozen expansion) and their adaptive
cluster-preserving variants on the prespecified strength grid. Every job uses
the tagged ``exact_statevector`` engine, the frozen maps and sample caps.
Re-running is safe: completed jobs are detected from their run-tag prefix and
skipped.

Usage (from the repository root):

    .venv/Scripts/python.exe -m src.experiments.run_v13_f5_queue --n-jobs 6
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from src.experiments.run_v11_reinforcement_queue import GATE_N_ENVIRONMENTS, Job, _cells, _env_job, _run_job


ATTACK_SUITE = "paper_f5"


def outdir_for(gate: str) -> str:
    return f"results/raw/paper15_v13_f5_{gate}"


def build_jobs() -> List[Job]:
    jobs: List[Job] = []
    for env in GATE_N_ENVIRONMENTS:
        outdir = outdir_for(str(env["gate"]))
        for s, m, d in _cells():
            jobs.append(
                _env_job(
                    gate_family="gateA",
                    env=env,
                    outdir=outdir,
                    split_seed=s,
                    model_seed=m,
                    svd_dim=d,
                    attack_suite=ATTACK_SUITE,
                    scale_classical="standard",
                    scale_quantum="minmax2pi",
                    svc_tune="none",
                    qsvc_tune="none",
                )
            )
    return jobs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-jobs", type=int, default=2)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--python", type=str, default=sys.executable)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--status-out",
        type=Path,
        default=Path("results/paper_digest/paper15_v13_adversarial/queue_status.json"),
    )
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    jobs = build_jobs()
    pending = [job for job in jobs if not job.completed(repo)]
    print(f"[V13-F5-QUEUE] planned={len(jobs)} completed={len(jobs) - len(pending)} pending={len(pending)}")

    log_dir = repo / "results" / "logs" / "paper15_v13_adversarial"
    log_dir.mkdir(parents=True, exist_ok=True)
    status_path = repo / args.status_out
    status_path.parent.mkdir(parents=True, exist_ok=True)

    plan = {
        "gate": "A_cluster_preserving",
        "attack_suite": ATTACK_SUITE,
        "planned_jobs": len(jobs),
        "jobs": [asdict(job) for job in jobs],
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if args.dry_run:
        for job in pending[:5]:
            print(" ".join(job.command(args.python)))
        print(json.dumps({"planned": len(jobs), "pending": len(pending)}, indent=2))
        return

    results: List[Dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=max(1, int(args.n_jobs))) as pool:
        futures = {
            pool.submit(_run_job, job, repo=repo, python_exe=args.python, log_dir=log_dir, retries=int(args.retries)): job
            for job in pending
        }
        done = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            done += 1
            state = "OK " if result["ok"] else "FAIL"
            print(f"[V13-F5-QUEUE] {state} {done}/{len(pending)} {result['job']} ({result['seconds']}s)", flush=True)

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
