# DONE
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .base import Attack, AttackResult


@dataclass(frozen=True)
class FeatureSignFlipCfg:
    p: float = 0.05


class FeatureSignFlip(Attack):
    """
    Random sign flip on feature entries (proxy for bitflip-like corruption).
    """
    name = "feature_sign_flip"

    def __init__(self, cfg: FeatureSignFlipCfg):
        p = float(cfg.p)
        if not (0.0 <= p <= 1.0):
            raise ValueError("FeatureSignFlipCfg.p must be in [0,1]")
        self.cfg = cfg

    def apply(self, X: np.ndarray, seed: int, y: Optional[np.ndarray] = None) -> AttackResult:
        X = np.asarray(X, dtype=float)
        rng = np.random.default_rng(int(seed))

        p = float(self.cfg.p)
        mask = rng.random(X.shape) < p

        X_att = X.copy()
        X_att[mask] = -X_att[mask]

        meta = {
            "family": "corruption",
            "strength": p,
            "p": p,
            "n_flipped": int(mask.sum()),
            "flip_frac": float(mask.mean()),
        }
        return AttackResult(X_att=np.asarray(X_att), y_att=y, meta=meta)


# Backwards-compatible alias (if old code referenced OutcomeCorruption)
OutcomeCorruptionCfg = FeatureSignFlipCfg
OutcomeCorruption = FeatureSignFlip
