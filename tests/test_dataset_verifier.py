"""Regression tests for clean-clone dataset-hash verification."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "publication" / "DATASET_HASHES_v1.3.6.json"


def test_public_dataset_hash_manifest_is_complete() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = payload["files"]
    assert payload["schema_version"] == 1
    assert payload["release"] == "1.3.6"
    assert len(entries) == 24
    assert len({entry["path"] for entry in entries}) == len(entries)
    assert all(entry["kind"] in {"raw", "staged"} for entry in entries)
    assert all(len(entry["sha256"]) == 64 for entry in entries)


def test_clean_clone_falls_back_to_public_hash_manifest(tmp_path: Path) -> None:
    target = tmp_path / "publication" / MANIFEST.name
    target.parent.mkdir(parents=True)
    shutil.copy2(MANIFEST, target)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_datasets.py"), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    output = proc.stdout + proc.stderr
    assert proc.returncode == 0, output
    assert "using frozen public hash manifest" in output
    assert "nothing verified" not in output
    assert "MISMATCH" in output and "0 MISMATCH" in output
