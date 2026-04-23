# DONE
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .base import Attack, AttackResult


@dataclass(frozen=True)
class QuantizationCfg:
    step: float = 0.05  # quantization step size (>0)


class Quantization(Attack):
    name = "quantization"

    def __init__(self, cfg: QuantizationCfg):
        step = float(cfg.step)
        if step <= 0.0:
            raise ValueError("QuantizationCfg.step must be > 0")
        self.cfg = cfg

    def apply(self, X: np.ndarray, seed: int, y: Optional[np.ndarray] = None) -> AttackResult:
        X = np.asarray(X, dtype=float)
        step = float(self.cfg.step)

        X_att = np.round(X / step) * step
        meta = {"family": "distortion", "strength": step, "step": step}
        return AttackResult(X_att=np.asarray(X_att), y_att=y, meta=meta)
