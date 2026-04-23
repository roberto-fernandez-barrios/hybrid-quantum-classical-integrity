# DONE
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .base import Attack, AttackResult


@dataclass(frozen=True)
class GaussianNoiseCfg:
    sigma: float = 0.05  # noise std


class GaussianNoise(Attack):
    name = "gaussian_noise"

    def __init__(self, cfg: GaussianNoiseCfg):
        if float(cfg.sigma) < 0.0:
            raise ValueError("GaussianNoiseCfg.sigma must be >= 0")
        self.cfg = cfg

    def apply(self, X: np.ndarray, seed: int, y: Optional[np.ndarray] = None) -> AttackResult:
        X = np.asarray(X, dtype=float)
        rng = np.random.default_rng(int(seed))

        sigma = float(self.cfg.sigma)
        noise = rng.normal(loc=0.0, scale=sigma, size=X.shape)

        X_att = X + noise
        meta = {"family": "noise", "strength": sigma, "sigma": sigma}
        return AttackResult(X_att=np.asarray(X_att), y_att=y, meta=meta)
