# DONE
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np


@dataclass(frozen=True)
class AttackResult:
    X_att: np.ndarray
    y_att: Optional[np.ndarray] = None
    meta: Dict[str, Any] = field(default_factory=dict)


class Attack:
    """
    Stable attack interface.

    Convention:
      - X is always attacked (X_att returned).
      - y may be attacked (y_att returned); if y_att is None => use original y.
      - meta SHOULD include:
          * family: str
          * strength: float (or numeric proxy)
    """
    name: str = "base"

    def apply(self, X: np.ndarray, seed: int, y: Optional[np.ndarray] = None) -> AttackResult:
        raise NotImplementedError
