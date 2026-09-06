# src/attacks/sham.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np


@dataclass(frozen=True)
class AttackResult:
    X_att: np.ndarray
    y_att: np.ndarray
    meta: Dict[str, Any]


@dataclass(frozen=True)
class IdentityAttackCfg:
    strength: float = 0.0


class IdentityAttack:
    """
    Null control.

    It should produce no change in X or y. Used as a sham baseline for
    calibrating detectability.
    """

    def __init__(self, cfg: Optional[IdentityAttackCfg] = None):
        self.cfg = cfg or IdentityAttackCfg()

    def apply(self, X: np.ndarray, seed: int = 0, y: Optional[np.ndarray] = None) -> AttackResult:
        X_att = np.asarray(X).copy()
        y_att = np.asarray(y).copy() if y is not None else np.array([], dtype=int)

        return AttackResult(
            X_att=X_att,
            y_att=y_att,
            meta={
                "family": "sham",
                "priority_group": "sham",
                "strength_nominal": float(self.cfg.strength),
                "strength_eff": 0.0,
                "sham_type": "identity",
                "n_samples": int(X_att.shape[0]),
                "n_features": int(X_att.shape[1]) if X_att.ndim == 2 else 0,
            },
        )


@dataclass(frozen=True)
class TinyGaussianNoiseCfg:
    sigma: float = 0.001


class TinyGaussianNoise:
    """
    Near-null feature perturbation.

    It adds tiny Gaussian noise, intended to represent harmless numerical
    variation rather than a meaningful attack.
    """

    def __init__(self, cfg: Optional[TinyGaussianNoiseCfg] = None):
        self.cfg = cfg or TinyGaussianNoiseCfg()

        if float(self.cfg.sigma) < 0.0:
            raise ValueError(f"TinyGaussianNoiseCfg.sigma must be >= 0, got {self.cfg.sigma}")

    def apply(self, X: np.ndarray, seed: int = 0, y: Optional[np.ndarray] = None) -> AttackResult:
        X_ref = np.asarray(X)
        X_att = X_ref.copy().astype(float, copy=False)
        y_att = np.asarray(y).copy() if y is not None else np.array([], dtype=int)

        rng = np.random.default_rng(int(seed))
        sigma = float(self.cfg.sigma)

        if sigma > 0.0 and X_att.size > 0:
            noise = rng.normal(loc=0.0, scale=sigma, size=X_att.shape)
            X_att = X_att + noise
            mean_abs_delta = float(np.mean(np.abs(noise)))
            max_abs_delta = float(np.max(np.abs(noise)))
        else:
            mean_abs_delta = 0.0
            max_abs_delta = 0.0

        return AttackResult(
            X_att=X_att,
            y_att=y_att,
            meta={
                "family": "sham",
                "priority_group": "sham",
                "strength_nominal": float(sigma),
                "strength_eff": float(mean_abs_delta),
                "sigma": float(sigma),
                "sham_type": "tiny_gaussian_noise",
                "mean_abs_delta": float(mean_abs_delta),
                "max_abs_delta": float(max_abs_delta),
                "n_samples": int(X_att.shape[0]),
                "n_features": int(X_att.shape[1]) if X_att.ndim == 2 else 0,
            },
        )


@dataclass(frozen=True)
class TinyScalingDriftCfg:
    alpha: float = 0.001


class TinyScalingDrift:
    """
    Near-null scaling perturbation.

    X_att = X * (1 + alpha)

    Intended as a harmless numerical drift control.
    """

    def __init__(self, cfg: Optional[TinyScalingDriftCfg] = None):
        self.cfg = cfg or TinyScalingDriftCfg()

    def apply(self, X: np.ndarray, seed: int = 0, y: Optional[np.ndarray] = None) -> AttackResult:
        X_ref = np.asarray(X)
        X_att = X_ref.copy().astype(float, copy=False)
        y_att = np.asarray(y).copy() if y is not None else np.array([], dtype=int)

        alpha = float(self.cfg.alpha)

        if X_att.size > 0:
            before = X_att.copy()
            X_att = X_att * (1.0 + alpha)
            delta = X_att - before
            mean_abs_delta = float(np.mean(np.abs(delta)))
            max_abs_delta = float(np.max(np.abs(delta)))
        else:
            mean_abs_delta = 0.0
            max_abs_delta = 0.0

        return AttackResult(
            X_att=X_att,
            y_att=y_att,
            meta={
                "family": "sham",
                "priority_group": "sham",
                "strength_nominal": float(abs(alpha)),
                "strength_eff": float(mean_abs_delta),
                "alpha": float(alpha),
                "sham_type": "tiny_scaling_drift",
                "mean_abs_delta": float(mean_abs_delta),
                "max_abs_delta": float(max_abs_delta),
                "n_samples": int(X_att.shape[0]),
                "n_features": int(X_att.shape[1]) if X_att.ndim == 2 else 0,
            },
        )

@dataclass(frozen=True)
class CleanResampleCfg:
    """
    pool_half: which disjoint half of the clean held-out pool to draw from
               ("calibration" or "evaluation").
    draw_index: 1-based index of the draw; only used for traceability.
    """

    pool_half: str = "calibration"
    draw_index: int = 1


class CleanResample:
    """
    Null-distribution control: an independent clean evaluation batch.

    ``IdentityAttack`` returns exactly the reference batch, so every sensor
    delta is exactly zero and no null distribution is obtained. This control
    instead draws ``n = len(X)`` rows by simple random sampling without
    replacement from the designated half of a clean held-out pool that the
    runner supplies (rows never used for training or for the frozen
    evaluation batch, transformed with the same training-fitted
    preprocessing). The calibration and evaluation halves are disjoint, so
    thresholds calibrated on one half can be evaluated on the other.
    """

    needs_pool = True

    def __init__(self, cfg: Optional[CleanResampleCfg] = None):
        self.cfg = cfg or CleanResampleCfg()
        if self.cfg.pool_half not in ("calibration", "evaluation"):
            raise ValueError(
                f"CleanResampleCfg.pool_half must be 'calibration' or 'evaluation', got {self.cfg.pool_half!r}"
            )

    def apply(
        self,
        X: np.ndarray,
        seed: int = 0,
        y: Optional[np.ndarray] = None,
        pool: Optional[Dict[str, Any]] = None,
    ) -> AttackResult:
        if pool is None:
            raise ValueError("CleanResample requires the runner to supply a clean held-out pool")

        X_pool = np.asarray(pool["X"])
        y_pool = np.asarray(pool["y"]).astype(int)
        half_idx = np.asarray(pool[f"{self.cfg.pool_half}_idx"], dtype=int)
        n = int(np.asarray(X).shape[0])

        if X_pool.ndim != 2 or X_pool.shape[0] != len(y_pool):
            raise ValueError("Clean pool X/y shapes are inconsistent")
        if len(half_idx) < n:
            raise ValueError(
                f"Clean pool half '{self.cfg.pool_half}' has {len(half_idx)} rows; "
                f"cannot draw {n} rows without replacement"
            )

        rng = np.random.default_rng(int(seed))
        sel = np.sort(rng.choice(half_idx, size=n, replace=False))

        X_att = X_pool[sel].copy()
        y_att = y_pool[sel].copy()

        return AttackResult(
            X_att=X_att,
            y_att=y_att,
            meta={
                "family": "null_control",
                "priority_group": f"null_{self.cfg.pool_half}",
                "strength_nominal": 0.0,
                "strength_eff": 0.0,
                "sham_type": "clean_resample",
                "pool_half": str(self.cfg.pool_half),
                "draw_index": int(self.cfg.draw_index),
                "n_pool_half": int(len(half_idx)),
                "n_pool_total": int(len(y_pool)),
                "n_samples": int(n),
                "n_features": int(X_att.shape[1]) if X_att.ndim == 2 else 0,
                "pos_rate_draw": float(np.mean(y_att)) if n > 0 else 0.0,
                "pool_sampling": "simple_random_without_replacement",
            },
        )
