from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Paths:
    data_dir: Path = ROOT / "data"
    results_dir: Path = ROOT / "results"
    raw_dir: Path = ROOT / "results" / "raw"
    agg_dir: Path = ROOT / "results" / "agg"

PATHS = Paths()