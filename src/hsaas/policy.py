"""Information-aware, calibrated decision layer for the HSaaS integrity contract.

Artifact 1.2.0, Gate D (``manuscript/paper15_v12_policy_prereg.md``).

The layer consumes, for one audited batch,

* the information regime available to the auditor and whether it includes a
  trusted item-aligned reference;
* the per-sensor calibrated fire flags (1.1.0 thresholds) and the
  family-calibrated regime flag (Gate F);
* the exact item-aligned fire flag, defined only under a trusted reference;
* the protected boundaries declared by the contract;

and returns a fail-closed ``allow / hold / block`` decision with reason codes.

``block`` is reserved for violations of an exact invariant against a trusted
reference. ``hold`` is the response to statistical evidence of deviation or to
missing mandatory evidence. The decision composes with the four frozen HSaaS
contracts by taking the maximum in the lattice ``allow < hold < block``.

The module is pure: it performs no I/O and does not depend on the evidence
tables, so the same function serves the batch evaluator and a service
endpoint.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final


ACTION_ORDER: Final[dict[str, int]] = {"allow": 0, "hold": 1, "block": 2}
POLICIES: Final[tuple[str, ...]] = (
    "serve_always",
    "union_uncalibrated",
    "family_calibrated",
    "family_calibrated_strict",
)
BOUNDARIES: Final[tuple[str, ...]] = ("feature", "prediction", "label")


@dataclass(frozen=True)
class RegimeSpec:
    """What an information regime can establish about each protected boundary.

    ``coverage`` maps a boundary to one of ``exact`` (item-aligned trusted
    reference; exact-zero null), ``calibrated`` (batch-level statistical
    coverage), ``marginal`` (only the class marginal; structurally blind to
    prior-preserving relabeling) or ``blind`` (structurally indistinguishable).
    """

    name: str
    trusted_reference: bool
    coverage: dict[str, str]

    def covers(self, boundary: str) -> bool:
        return self.coverage.get(boundary, "blind") in ("exact", "calibrated")


REGIMES: Final[dict[str, RegimeSpec]] = {
    "I_X": RegimeSpec("I_X", False, {"feature": "calibrated", "prediction": "blind", "label": "blind"}),
    "I_XF": RegimeSpec("I_XF", False, {"feature": "calibrated", "prediction": "calibrated", "label": "blind"}),
    "I_Ym": RegimeSpec("I_Ym", False, {"feature": "blind", "prediction": "blind", "label": "marginal"}),
    "I_XFY": RegimeSpec("I_XFY", False, {"feature": "calibrated", "prediction": "calibrated", "label": "calibrated"}),
    "I_XFY_trusted": RegimeSpec("I_XFY_trusted", True, {"feature": "exact", "prediction": "exact", "label": "exact"}),
}


@dataclass(frozen=True)
class Evidence:
    """Fire flags available to the decision layer for one audited batch."""

    union_fire: bool
    family_fire: bool
    exact_fire: bool | None = None  # None when no trusted item-aligned reference exists

    def __post_init__(self) -> None:
        if self.exact_fire is not None and not isinstance(self.exact_fire, bool):
            raise TypeError("exact_fire must be a bool or None")


@dataclass(frozen=True)
class Decision:
    action: str
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.action not in ACTION_ORDER:
            raise ValueError(f"unknown action {self.action!r}")
        if not self.reasons:
            raise ValueError("a decision must carry at least one reason code")


def unverified_boundaries(regime: RegimeSpec, protected: tuple[str, ...] = BOUNDARIES) -> tuple[str, ...]:
    """Protected boundaries that the regime cannot verify exactly or statistically."""

    return tuple(b for b in protected if not regime.covers(b))


def decide(
    policy: str,
    regime: RegimeSpec | str,
    evidence: Evidence,
    protected: tuple[str, ...] = BOUNDARIES,
) -> Decision:
    """Deterministic, total decision function of policy, regime and evidence."""

    spec = REGIMES[regime] if isinstance(regime, str) else regime
    if policy not in POLICIES:
        raise ValueError(f"unknown policy {policy!r}")
    if spec.trusted_reference and evidence.exact_fire is None:
        raise ValueError("a trusted-reference regime requires an exact fire flag")
    if not spec.trusted_reference and evidence.exact_fire is not None:
        raise ValueError("exact evidence is undefined without a trusted item-aligned reference")

    if policy == "serve_always":
        return Decision("allow", ("policy_serve_always",))

    reasons: list[str] = []
    if spec.trusted_reference and evidence.exact_fire:
        reasons.append("exact_invariant_violated")
        return Decision("block", tuple(reasons))

    statistical_fire = evidence.union_fire if policy == "union_uncalibrated" else evidence.family_fire
    if statistical_fire:
        reasons.append("union_sensor_fired" if policy == "union_uncalibrated" else "family_calibrated_fired")
        return Decision("hold", tuple(reasons))

    if policy == "family_calibrated_strict":
        missing = unverified_boundaries(spec, protected)
        if missing:
            reasons.extend(f"unverified_boundary:{b}" for b in missing)
            return Decision("hold", tuple(reasons))

    residual = unverified_boundaries(spec, protected)
    if residual:
        reasons.append("allowed_with_residual_blind_region:" + "+".join(residual))
    else:
        reasons.append("all_protected_boundaries_covered")
    return Decision("allow", tuple(reasons))


def compose(contract_action: str, policy_action: str) -> str:
    """Compose the frozen contract action with the policy action (lattice maximum)."""

    for action in (contract_action, policy_action):
        if action not in ACTION_ORDER:
            raise ValueError(f"unknown action {action!r}")
    return max((contract_action, policy_action), key=lambda a: ACTION_ORDER[a])
