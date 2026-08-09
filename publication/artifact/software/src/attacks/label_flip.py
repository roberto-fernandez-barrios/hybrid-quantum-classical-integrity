# DONE
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .base import Attack, AttackResult


@dataclass(frozen=True)
class LabelFlipCfg:
    r: float = 0.05  # flip rate


class LabelFlip(Attack):
    name = "label_flip"

    def __init__(self, cfg: LabelFlipCfg):
        r = float(cfg.r)
        if not (0.0 <= r <= 1.0):
            raise ValueError("LabelFlipCfg.r must be in [0,1]")
        self.cfg = cfg

    def apply(self, X: np.ndarray, seed: int, y: Optional[np.ndarray] = None) -> AttackResult:
        if y is None:
            raise ValueError("LabelFlip requires y (labels).")

        rng = np.random.default_rng(int(seed))
        r = float(self.cfg.r)

        y0 = np.asarray(y).astype(int)
        uniq = np.unique(y0)
        if not set(uniq.tolist()).issubset({0, 1}):
            raise ValueError(f"LabelFlip assumes binary labels in {{0,1}}; got unique={uniq}")

        flip = rng.random(y0.shape[0]) < r
        y_att = y0.copy()
        y_att[flip] = 1 - y_att[flip]

        meta = {
            "family": "target_shift",
            "strength": r,
            "r": r,
            "n_flipped": int(flip.sum()),
            "flip_frac": float(flip.mean()),
        }
        return AttackResult(X_att=np.asarray(X), y_att=np.asarray(y_att), meta=meta)
