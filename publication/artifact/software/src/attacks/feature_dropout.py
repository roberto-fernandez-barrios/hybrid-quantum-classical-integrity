# DONE
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .base import Attack, AttackResult


@dataclass(frozen=True)
class FeatureDropoutCfg:
    p: float = 0.05               # probability to drop each entry
    strategy: str = "median"      # "median" | "mean"


class FeatureDropout(Attack):
    name = "feature_dropout"

    def __init__(self, cfg: FeatureDropoutCfg):
        p = float(cfg.p)

        if not (0.0 <= p <= 1.0):
            raise ValueError("FeatureDropoutCfg.p must be in [0,1]")

        if cfg.strategy not in ("median", "mean"):
            raise ValueError(
                "FeatureDropoutCfg.strategy must be 'median' or 'mean'"
            )

        self.cfg = cfg

    def apply(
        self,
        X: np.ndarray,
        seed: int,
        y: Optional[np.ndarray] = None,
    ) -> AttackResult:

        X_att = np.asarray(X, dtype=float).copy()
        rng = np.random.default_rng(int(seed))

        # -------------------------
        # Robust stats preparation
        # -------------------------
        # Convert inf / -inf → NaN
        X_att[~np.isfinite(X_att)] = np.nan

        p = float(self.cfg.p)

        # Mask of dropped entries
        mask = rng.random(X_att.shape) < p

        # -------------------------
        # Fill strategy
        # -------------------------
        if self.cfg.strategy == "median":
            fill = np.nanmedian(X_att, axis=0)
        else:
            fill = np.nanmean(X_att, axis=0)

        # Columns fully NaN → replace with 0
        fill = np.nan_to_num(
            fill,
            nan=0.0,
            posinf=0.0,
            neginf=0.0,
        )

        # -------------------------
        # Apply dropout
        # -------------------------
        X_att = np.where(mask, fill[None, :], X_att)

        meta = {
            "family": "pipeline",
            "strength": p,
            "p": p,
            "strategy": self.cfg.strategy,
            "drop_frac": float(mask.mean()),
            "n_dropped": int(mask.sum()),
        }

        return AttackResult(
            X_att=np.asarray(X_att),
            y_att=y,
            meta=meta,
        )
