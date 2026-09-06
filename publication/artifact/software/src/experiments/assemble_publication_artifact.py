"""Assemble the compact publication artifact under ``publication/artifact``.

The artifact is derived deterministically from the repository: derived
evidence directories (with their embedded manifests), reviewer-facing manuscript
documents, figures and tables, the environment lock, and a snapshot of the
source and tests. Raw benchmark data and heavy raw results are never copied.
After copying, an artifact-wide ``ARTIFACT_MANIFEST.sha256`` is written and the
independent verifier is expected to pass on the result.

Usage (repository root):

    .venv/Scripts/python.exe -m src.experiments.assemble_publication_artifact
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


EVIDENCE_DIRS = {
    "gate1": "results/paper_digest/paper15_q1_gate1_id_seeds_20_q1",
    "expansion": "results/paper_digest/paper15_q1_expansion",
    "quantum_integrity": "results/paper_digest/paper15_q1_quantum_integrity_gate",
    "hsaas": "results/paper_digest/paper15_hsaas_demo",
    "reinforcement": "results/paper_digest/paper15_v11_reinforcement",
}

MANUSCRIPT_FILES = [
    "manuscript/paper15_q1_manuscript_spine_v11.md",
    "manuscript/NOVELTY_REVIEW_2026-08-09.md",
    "manuscript/ATHENA_DEUSTO_TRACEABILITY.md",
    "manuscript/THREAT_MODEL_CARD.md",
    "manuscript/paper15_v11_reinforcement_prereg.md",
    "manuscript/paper15_v11_reinforcement_result_summary.md",
    "publication/Q1_HOSTILE_REVIEW_AUDIT.md",
    "publication/TDSC_HOSTILE_REVIEW_AUDIT.md",
    "Q1_REPRODUCTION.md",
    "output/pdf/paper15_tdsc_submission.pdf",
    "output/pdf/paper15_tdsc_supplement.pdf",
]

ENVIRONMENT_FILES = ["pyproject.toml", "requirements-dev.txt", "requirements-lock.txt"]
SKIP_DIR_NAMES = {"__pycache__", ".pytest_cache"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _copy_tree(src: Path, dst: Path) -> int:
    count = 0
    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(src).parts) or path.suffix == ".pyc":
            continue
        target = dst / path.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        count += 1
    return count


def _readme(version: str, counts: dict[str, int], size_mb: float) -> str:
    return f"""# Paper 1.5 compact review artifact — version {version}

This directory is the self-contained, derived-evidence artifact for
*Information-Set Conditional Integrity Auditing for Hybrid Quantum-Classical
Kernel Workflows*.

It contains no raw benchmark dataset. The {size_mb:.0f} MB package includes the
TDSC manuscript and supplement PDFs, the frozen Markdown source, figures, figure
source tables, environment lock, source/tests snapshot, {counts['manifests']}
evidence manifests and all {counts['manifested_outputs']} outputs referenced by
those manifests.

Version 1.1.0 adds the preregistered reinforcement gates (null calibration of
non-invariant sensors with disjoint clean pools, symmetric preprocessing
ablation, cross-validated tuning of both learners). The 1.0.0 evidence, counts
and claims are unchanged.

## Verify without recomputation

From the unpacked artifact directory:

```powershell
python -m pip install pandas==2.3.3
python software\\src\\experiments\\verify_publication_artifact.py --root .
```

The verifier checks every embedded manifest, all manifested outputs, their
SHA-256 hashes and row counts, the primary label-boundary counts (3,600 / 2,184
expansion and 1,440 / 1,276 Gate 1), the calibrated label-path consistency
checks of the reinforcement gate, and every file listed in
`ARTIFACT_MANIFEST.sha256`. Any changed byte, row count, acceptance check or
primary count causes a non-zero exit.

## Layout

- `evidence/` — derived CSV/JSON evidence and embedded SHA-256 contracts
  (`gate1`, `expansion`, `quantum_integrity`, `hsaas`, `reinforcement`);
- `manuscript/` — TDSC PDFs, frozen source, novelty audit, threat model,
  preregistration, reinforcement summary, figures and tables;
- `environment/` — Python 3.10 dependency lock and packaging metadata;
- `software/` — exact Python source and tests snapshot used for version {version}.

See `manuscript/Q1_REPRODUCTION.md` for dataset staging and experiment replay.
Exact-statevector evaluation and binomial-shot emulation are not QPU evidence.
"""


def assemble(repo: Path, out: Path, version: str) -> dict[str, object]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    copied = 0
    for name, source in EVIDENCE_DIRS.items():
        src = repo / source
        if not src.is_dir():
            raise FileNotFoundError(f"Evidence directory missing: {src}")
        copied += _copy_tree(src, out / "evidence" / name)

    manuscript_out = out / "manuscript"
    manuscript_out.mkdir(parents=True)
    for rel in MANUSCRIPT_FILES:
        src = repo / rel
        if not src.is_file():
            raise FileNotFoundError(f"Manuscript file missing: {src}")
        shutil.copy2(src, manuscript_out / src.name)
        copied += 1
    copied += _copy_tree(repo / "manuscript" / "figures", manuscript_out / "figures")
    copied += _copy_tree(repo / "manuscript" / "tables", manuscript_out / "tables")

    env_out = out / "environment"
    env_out.mkdir(parents=True)
    for rel in ENVIRONMENT_FILES:
        shutil.copy2(repo / rel, env_out / rel)
        copied += 1

    copied += _copy_tree(repo / "src", out / "software" / "src")
    copied += _copy_tree(repo / "tests", out / "software" / "tests")

    shutil.copy2(repo / "CHANGELOG.md", out / "CHANGELOG.md")
    (out / "VERSION").write_text(version + "\n", encoding="utf-8")

    # Counts for the README come from the embedded manifests.
    manifests = sorted(out.rglob("*_manifest.json"))
    manifested_outputs = sum(len(json.loads(m.read_text(encoding="utf-8")).get("outputs", {})) for m in manifests)
    size_mb = sum(p.stat().st_size for p in out.rglob("*") if p.is_file()) / 1e6
    (out / "README.md").write_text(_readme(version, {"manifests": len(manifests), "manifested_outputs": manifested_outputs}, size_mb), encoding="utf-8")

    lines = []
    for path in sorted(p for p in out.rglob("*") if p.is_file()):
        rel = path.relative_to(out).as_posix()
        if rel == "ARTIFACT_MANIFEST.sha256":
            continue
        lines.append(f"{_sha256(path)}  {rel}")
    (out / "ARTIFACT_MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {"version": version, "files": len(lines), "manifests": len(manifests), "manifested_outputs": manifested_outputs, "size_mb": round(size_mb, 1)}
    print(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=Path("publication/artifact"))
    parser.add_argument("--version", type=str, default=None, help="Defaults to the repository VERSION file")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    version = args.version or (repo / "VERSION").read_text(encoding="utf-8").strip()
    assemble(repo, (repo / args.out).resolve() if not args.out.is_absolute() else args.out, version)


if __name__ == "__main__":
    main()
