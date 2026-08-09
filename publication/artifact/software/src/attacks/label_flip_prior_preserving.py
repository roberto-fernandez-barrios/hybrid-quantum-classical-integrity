# src/attacks/label_flip_prior_preserving.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np


@dataclass(frozen=True)
class LabelFlipPriorPreservingCfg:
    """
    Label-flip attack that preserves the global class prior as much as possible.

    Meaning of r:
      Approximate fraction of total labels to flip.

    Implementation:
      - flips k positives -> negative
      - flips k negatives -> positive
      - total flipped labels = 2k
      - therefore class prior remains unchanged when both classes are available
    """

    r: float = 0.05
    positive_label: int = 1
    negative_label: int = 0
    min_pairs: int = 0


@dataclass(frozen=True)
class AttackResult:
    X_att: np.ndarray
    y_att: np.ndarray
    meta: Dict[str, Any]


class LabelFlipPriorPreserving:
    """
    Prior-preserving target perturbation.

    This attack is important for the auditability-gap paper because a normal
    label_flip can be detected by label prior shift. This variant changes labels
    while keeping the positive/negative prior almost identical, making it a
    stronger test of label-aware auditability.
    """

    def __init__(self, cfg: Optional[LabelFlipPriorPreservingCfg] = None):
        self.cfg = cfg or LabelFlipPriorPreservingCfg()

        if not (0.0 <= float(self.cfg.r) <= 1.0):
            raise ValueError(f"LabelFlipPriorPreservingCfg.r must be in [0, 1], got {self.cfg.r}")

        if int(self.cfg.positive_label) == int(self.cfg.negative_label):
            raise ValueError("positive_label and negative_label must be different.")

        if int(self.cfg.min_pairs) < 0:
            raise ValueError("min_pairs must be >= 0.")

    def apply(self, X: np.ndarray, seed: int = 0, y: Optional[np.ndarray] = None) -> AttackResult:
        if y is None:
            raise ValueError("LabelFlipPriorPreserving requires y.")

        X_att = np.asarray(X).copy()
        y_ref = np.asarray(y).astype(int).reshape(-1)
        y_att = y_ref.copy()

        if X_att.shape[0] != y_att.shape[0]:
            raise ValueError(
                f"X and y length mismatch: X has {X_att.shape[0]} rows, y has {y_att.shape[0]}"
            )

        n = int(y_att.shape[0])
        pos_label = int(self.cfg.positive_label)
        neg_label = int(self.cfg.negative_label)

        pos_idx = np.flatnonzero(y_att == pos_label)
        neg_idx = np.flatnonzero(y_att == neg_label)

        n_pos = int(pos_idx.size)
        n_neg = int(neg_idx.size)

        prior_before = float(np.mean(y_att == pos_label)) if n > 0 else float("nan")

        if n == 0 or n_pos == 0 or n_neg == 0 or float(self.cfg.r) <= 0.0:
            prior_after = float(np.mean(y_att == pos_label)) if n > 0 else float("nan")
            return AttackResult(
                X_att=X_att,
                y_att=y_att,
                meta={
                    "family": "target_shift",
                    "priority_group": "core",
                    "strength_nominal": float(self.cfg.r),
                    "strength_eff": 0.0,
                    "r": float(self.cfg.r),
                    "n_samples": int(n),
                    "n_pos": int(n_pos),
                    "n_neg": int(n_neg),
                    "n_flip_1_to_0": 0,
                    "n_flip_0_to_1": 0,
                    "n_flipped_total": 0,
                    "prior_before": prior_before,
                    "prior_after": prior_after,
                    "prior_abs_delta": abs(prior_after - prior_before)
                    if np.isfinite(prior_before) and np.isfinite(prior_after)
                    else float("nan"),
                    "limited_by_class_balance": 0,
                },
            )

        # r is total flip fraction. Since we flip pairs, each direction gets half.
        target_total_flips = int(round(float(self.cfg.r) * float(n)))
        target_pairs = int(target_total_flips // 2)

        if self.cfg.min_pairs > 0 and float(self.cfg.r) > 0.0:
            target_pairs = max(target_pairs, int(self.cfg.min_pairs))

        max_pairs = int(min(n_pos, n_neg))
        k = int(min(target_pairs, max_pairs))

        rng = np.random.default_rng(int(seed))

        flip_pos_to_neg = rng.choice(pos_idx, size=k, replace=False) if k > 0 else np.array([], dtype=int)
        flip_neg_to_pos = rng.choice(neg_idx, size=k, replace=False) if k > 0 else np.array([], dtype=int)

        y_att[flip_pos_to_neg] = neg_label
        y_att[flip_neg_to_pos] = pos_label

        n_flip_1_to_0 = int(flip_pos_to_neg.size)
        n_flip_0_to_1 = int(flip_neg_to_pos.size)
        n_flipped_total = int(n_flip_1_to_0 + n_flip_0_to_1)

        prior_after = float(np.mean(y_att == pos_label)) if n > 0 else float("nan")
        strength_eff = float(n_flipped_total / n) if n > 0 else 0.0

        return AttackResult(
            X_att=X_att,
            y_att=y_att,
            meta={
                "family": "target_shift",
                "priority_group": "core",
                "strength_nominal": float(self.cfg.r),
                "strength_eff": float(strength_eff),
                "r": float(self.cfg.r),
                "n_samples": int(n),
                "n_pos": int(n_pos),
                "n_neg": int(n_neg),
                "n_flip_1_to_0": int(n_flip_1_to_0),
                "n_flip_0_to_1": int(n_flip_0_to_1),
                "n_flipped_total": int(n_flipped_total),
                "prior_before": float(prior_before),
                "prior_after": float(prior_after),
                "prior_abs_delta": float(abs(prior_after - prior_before)),
                "limited_by_class_balance": int(k < target_pairs),
            },
        )