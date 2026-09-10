#!/usr/bin/env python3
"""Verify the staged benchmark tables (and, when present, the raw sources) by SHA-256.

Cross-platform, standard library only. The expected hashes are read from the
staging reports that the dataset scripts wrote when the frozen evidence was
produced. In a clean clone without those ignored local reports, the verifier
falls back to ``publication/DATASET_HASHES_v1.3.6.json`` and reports the
declared files as optional MISSING unless ``--require-raw`` or
``--require-staged`` is selected:

* ``data/cicids_subset.prep_report.json``, ``data/unsw_subset.prep_report.json``,
  ``data/ton_iot_subset.prep_report.json`` (ID subsets; ``output.sha256`` and
  ``source.file_sha256``);
* ``data/processed/*.prep_report.json`` (OOD pairs; ``hashes.train_sha256`` /
  ``hashes.test_sha256`` and ``source.train_file_sha256`` /
  ``source.test_file_sha256``);
* ``data/raw/staging/stage_report.json`` (UNSW-NB15 / ToN-IoT staging;
  ``dst_sha256`` and ``src_sha256``).

Staged tables that exist are always checked. Raw source files are checked when
they exist under ``data/raw/cicids2017/MachineLearningCVE/``,
``data/raw/unsw_nb15/Training and Testing Sets/`` and ``data/raw/ton_iot/``;
missing raw files are reported as MISSING and only fail the run with
``--require-raw``. Any hash mismatch fails the run (exit code 1).

Usage (repository root)::

    python scripts/verify_datasets.py [--require-raw] [--require-staged] [--repo-root PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RAW_CICIDS = Path("data/raw/cicids2017/MachineLearningCVE")
RAW_UNSW = Path("data/raw/unsw_nb15/Training and Testing Sets")
RAW_TON = Path("data/raw/ton_iot")
STAGING = Path("data/raw/staging")

ID_REPORTS = {
    "data/cicids_subset.prep_report.json": ("data/cicids_subset.csv", RAW_CICIDS),
    "data/unsw_subset.prep_report.json": ("data/unsw_subset.csv", STAGING / "unsw_nb15"),
    "data/ton_iot_subset.prep_report.json": ("data/ton_iot_subset.csv", STAGING / "ton_iot"),
}
OOD_REPORTS = {
    "data/processed/cicids_ood_tuesday_vs_wednesday.prep_report.json": (
        "data/processed/cicids_ood_tuesday_train.csv",
        "data/processed/cicids_ood_wednesday_test.csv",
        RAW_CICIDS,
    ),
    "data/processed/cicids_ood_tuesday_vs_friday_portscan.prep_report.json": (
        "data/processed/cicids_ood_tuesday_train_portscan.csv",
        "data/processed/cicids_ood_friday_portscan_test.csv",
        RAW_CICIDS,
    ),
    "data/processed/cicids_ood_wednesday_vs_thursday_webattacks.prep_report.json": (
        "data/processed/cicids_ood_wednesday_train.csv",
        "data/processed/cicids_ood_thursday_webattacks_test.csv",
        RAW_CICIDS,
    ),
    "data/processed/cicids_ood_wednesday_vs_friday_morning.prep_report.json": (
        "data/processed/cicids_ood_wednesday_train.csv",
        "data/processed/cicids_ood_friday_morning_test.csv",
        RAW_CICIDS,
    ),
    "data/processed/unsw_ood_train_vs_test.prep_report.json": (
        "data/processed/unsw_ood_train.csv",
        "data/processed/unsw_ood_test.csv",
        STAGING / "unsw_nb15",
    ),
}
STAGE_REPORT = STAGING / "stage_report.json"
FROZEN_HASH_MANIFEST = Path("publication/DATASET_HASHES_v1.3.6.json")
STAGE_SOURCES = {
    "unsw_train": RAW_UNSW / "UNSW_NB15_training-set.csv",
    "unsw_test": RAW_UNSW / "UNSW_NB15_testing-set.csv",
    "ton_iot": RAW_TON / "train_test_network.csv",
}
STAGE_TARGETS = {
    "unsw_train": STAGING / "unsw_nb15" / "unsw_train.csv",
    "unsw_test": STAGING / "unsw_nb15" / "unsw_test.csv",
    "ton_iot": STAGING / "ton_iot" / "ton_network.csv",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Check:
    def __init__(self, kind: str, path: Path, expected: str) -> None:
        self.kind = kind  # "staged" | "raw"
        self.path = path
        self.expected = expected
        self.observed = ""
        self.status = "MISSING"

    def run(self, root: Path) -> None:
        full = root / self.path
        if not full.is_file():
            self.status = "MISSING"
            return
        self.observed = sha256_file(full)
        self.status = "OK" if self.observed == self.expected else "MISMATCH"


def _load(root: Path, rel: str) -> dict | None:
    path = root / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _frozen_manifest_checks(root: Path) -> list[Check]:
    path = root / FROZEN_HASH_MANIFEST
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or payload.get("release") != "1.3.6":
        raise ValueError(f"unsupported dataset-hash manifest metadata: {path}")
    checks: list[Check] = []
    seen: set[str] = set()
    for entry in payload.get("files", []):
        kind = entry.get("kind")
        rel = entry.get("path")
        digest = str(entry.get("sha256", "")).lower()
        if kind not in {"raw", "staged"} or not rel:
            raise ValueError(f"invalid dataset-hash manifest entry: {entry!r}")
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError(f"invalid SHA-256 for {rel}")
        if rel in seen:
            raise ValueError(f"duplicate dataset path in frozen manifest: {rel}")
        seen.add(rel)
        checks.append(Check(kind, Path(rel), digest))
    if not checks:
        raise ValueError(f"empty dataset-hash manifest: {path}")
    return checks


def collect_checks(root: Path) -> tuple[list[Check], list[str]]:
    checks: list[Check] = []
    notes: list[str] = []

    for rel, (staged, raw_dir) in ID_REPORTS.items():
        report = _load(root, rel)
        if report is None:
            notes.append(f"report not found: {rel}")
            continue
        checks.append(Check("staged", Path(staged), report["output"]["sha256"]))
        for name, digest in report.get("source", {}).get("file_sha256", {}).items():
            # CICIDS ID sources are raw files; UNSW/ToN ID sources are staged tables.
            kind = "raw" if raw_dir == RAW_CICIDS else "staged"
            checks.append(Check(kind, raw_dir / name, digest))

    for rel, (train, test, raw_dir) in OOD_REPORTS.items():
        report = _load(root, rel)
        if report is None:
            notes.append(f"report not found: {rel}")
            continue
        checks.append(Check("staged", Path(train), report["hashes"]["train_sha256"]))
        checks.append(Check("staged", Path(test), report["hashes"]["test_sha256"]))
        source = report.get("source", {})
        kind = "raw" if raw_dir == RAW_CICIDS else "staged"
        for name, digest in source.get("train_file_sha256", {}).items():
            checks.append(Check(kind, raw_dir / name, digest))
        for name, digest in source.get("test_file_sha256", {}).items():
            checks.append(Check(kind, raw_dir / name, digest))

    stage = _load(root, STAGE_REPORT.as_posix())
    if stage is None:
        notes.append(f"report not found: {STAGE_REPORT.as_posix()}")
    else:
        for key, entry in stage.items():
            if key in STAGE_TARGETS:
                checks.append(Check("staged", STAGE_TARGETS[key], entry["dst_sha256"]))
            if key in STAGE_SOURCES:
                checks.append(Check("raw", STAGE_SOURCES[key], entry["src_sha256"]))

    # Deduplicate identical (path, expected) pairs while preserving order.
    seen: set[tuple[str, str]] = set()
    unique: list[Check] = []
    for check in checks:
        key = (check.path.as_posix(), check.expected)
        if key in seen:
            continue
        seen.add(key)
        unique.append(check)
    frozen = _frozen_manifest_checks(root)
    if not unique and frozen:
        return frozen, [f"using frozen public hash manifest: {FROZEN_HASH_MANIFEST.as_posix()}"]
    if unique and frozen:
        live_set = {(check.kind, check.path.as_posix(), check.expected) for check in unique}
        frozen_set = {(check.kind, check.path.as_posix(), check.expected) for check in frozen}
        if live_set != frozen_set:
            notes.append("ERROR: local staging-report hashes differ from the frozen public manifest")
    return unique, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--require-raw", action="store_true", help="Fail when a raw source file is missing")
    parser.add_argument("--require-staged", action="store_true", help="Fail when a staged table is missing")
    args = parser.parse_args()
    root = args.repo_root.resolve()

    try:
        checks, notes = collect_checks(root)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for check in checks:
        check.run(root)

    width = max((len(c.path.as_posix()) for c in checks), default=20)
    print(f"{'kind':6} {'file':{width}} {'status':8} expected / observed")
    for check in checks:
        observed = check.observed[:16] if check.observed else "-"
        print(f"{check.kind:6} {check.path.as_posix():{width}} {check.status:8} {check.expected[:16]} / {observed}")
    for note in notes:
        print(f"note: {note}")

    n_ok = sum(c.status == "OK" for c in checks)
    n_mismatch = sum(c.status == "MISMATCH" for c in checks)
    missing_raw = sum(c.status == "MISSING" and c.kind == "raw" for c in checks)
    missing_staged = sum(c.status == "MISSING" and c.kind == "staged" for c in checks)
    print(f"summary: {n_ok} OK, {n_mismatch} MISMATCH, {missing_staged} staged MISSING, {missing_raw} raw MISSING")

    failed = n_mismatch > 0 or any(note.startswith("ERROR:") for note in notes)
    if args.require_raw and missing_raw:
        failed = True
    if args.require_staged and missing_staged:
        failed = True
    if not checks:
        print("error: no staging report found; nothing verified", file=sys.stderr)
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
