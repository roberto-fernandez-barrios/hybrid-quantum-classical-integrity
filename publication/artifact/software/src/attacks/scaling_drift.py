# DONE
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .base import Attack, AttackResult


@dataclass(frozen=True)
class ScalingDriftCfg:
    alpha: float = 0.1  # scaling drift


class ScalingDrift(Attack):
    name = "scaling_drift"

    def __init__(self, cfg: ScalingDriftCfg):
        self.cfg = cfg

    def apply(self, X: np.ndarray, seed: int, y: Optional[np.ndarray] = None) -> AttackResult:
        X = np.asarray(X, dtype=float)
        alpha = float(self.cfg.alpha)

        X_att = X * (1.0 + alpha)
        meta = {"family": "covariate_shift", "strength": abs(alpha), "alpha": alpha}
        return AttackResult(X_att=np.asarray(X_att), y_att=y, meta=meta)


# Backwards-compatible alias (if old code referenced PostProcessPerturbation)
PostProcessPerturbationCfg = ScalingDriftCfg
PostProcessPerturbation = ScalingDrift
