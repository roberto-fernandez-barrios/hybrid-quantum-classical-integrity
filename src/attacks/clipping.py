# DONE
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .base import Attack, AttackResult


@dataclass(frozen=True)
class ClippingCfg:
    # clip to [low_q, high_q] percentiles per feature (e.g., (1.0, 99.0) or (5.0, 95.0))
    low_q: float = 1.0
    high_q: float = 99.0


class Clipping(Attack):
    name = "clipping"

    def __init__(self, cfg: ClippingCfg):
        if not (0.0 <= cfg.low_q < cfg.high_q <= 100.0):
            raise ValueError("ClippingCfg requires 0 <= low_q < high_q <= 100")
        self.cfg = cfg

    def apply(self, X: np.ndarray, seed: int, y: Optional[np.ndarray] = None) -> AttackResult:
        X = np.asarray(X, dtype=float)

        lo = np.nanpercentile(X, float(self.cfg.low_q), axis=0)
        hi = np.nanpercentile(X, float(self.cfg.high_q), axis=0)
        hi = np.maximum(hi, lo)  # avoid degenerate ranges

        X_att = np.clip(X, lo, hi)

        # Total clipped tails (%) => higher = more aggressive
        clip_tail = float(self.cfg.low_q + (100.0 - self.cfg.high_q))
        window = float(self.cfg.high_q - self.cfg.low_q)

        meta = {
            "family": "distortion",
            "strength": clip_tail,
            "low_q": float(self.cfg.low_q),
            "high_q": float(self.cfg.high_q),
            "clip_tail": clip_tail,
            "window": window,
        }
        return AttackResult(X_att=np.asarray(X_att), y_att=y, meta=meta)
