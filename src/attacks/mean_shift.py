# DONE
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .base import Attack, AttackResult


@dataclass(frozen=True)
class MeanShiftCfg:
    delta: float = 0.05          # additive shift magnitude (or std if per_feature=True)
    per_feature: bool = False    # if True → random per-feature shifts


class MeanShift(Attack):
    name = "mean_shift"

    def __init__(self, cfg: MeanShiftCfg):
        self.cfg = cfg

    def apply(
        self,
        X: np.ndarray,
        seed: int,
        y: Optional[np.ndarray] = None,
    ) -> AttackResult:

        X = np.asarray(X, dtype=float)
        delta = float(self.cfg.delta)

        # -------------------------
        # Global mean shift
        # -------------------------
        if not self.cfg.per_feature:
            X_att = X + delta

            meta = {
                "family": "covariate_shift",
                "strength": abs(delta),         # effective == nominal in global shift
                "strength_nominal": abs(delta), # keep for uniformity
                "delta": delta,
                "per_feature": False,
            }

            return AttackResult(
                X_att=np.asarray(X_att),
                y_att=y,
                meta=meta,
            )

        # -------------------------
        # Per-feature random shift
        # -------------------------
        rng = np.random.default_rng(int(seed))

        # Random offsets per feature: N(0, |delta|)
        dvec = rng.normal(
            loc=0.0,
            scale=abs(delta),
            size=(X.shape[1],),
        )

        X_att = X + dvec

        # Effective magnitude (RMS of applied shift)
        strength_eff = float(np.sqrt(np.mean(dvec ** 2))) if dvec.size else 0.0

        meta = {
            "family": "covariate_shift",

            # IMPORTANT:
            # For per-feature shifts, strength should reflect what was actually applied.
            "strength": strength_eff,

            # Nominal target magnitude (useful for grouping by config)
            "strength_nominal": abs(delta),

            # Also keep explicit effective magnitude
            "strength_eff": strength_eff,

            "delta": delta,
            "per_feature": True,
            "dvec_mean": float(np.mean(dvec)) if dvec.size else 0.0,
            "dvec_std": float(np.std(dvec)) if dvec.size else 0.0,
        }

        return AttackResult(
            X_att=np.asarray(X_att),
            y_att=y,
            meta=meta,
        )
