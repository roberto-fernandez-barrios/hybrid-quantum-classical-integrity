"""Information-aware, calibrated decision layer for the HSaaS integrity contract.

Artifact 1.3.0 (``manuscript/paper15_v13_prereg.md``; first evaluated in
artifact 1.2.0, ``manuscript/paper15_v12_policy_prereg.md``).

The layer consumes, for one audited batch,

* the information regime available to the auditor and whether it includes
  trusted aggregate and/or item-aligned references;
* the per-sensor calibrated fire flags (1.1.0 thresholds) and the
  family-calibrated regime flag (Gate F, conformal max-rank p-value);
* the exact-reference fire flag, defined only under a trusted reference and
  combining the declared aggregate and item-aligned invariants;
* the protected boundaries declared by the contract;

and returns an ``allow / hold / block`` decision with reason codes.

Policy taxonomy (``POLICY_CLASS``)
----------------------------------

* P0 ``serve_always`` -- baseline: always ``allow``.
* P1 ``union_uncalibrated`` -- uncalibrated, risk-tolerant: ``hold`` if any
  per-sensor rule of the regime fires (the 1.1.0 rule); serves otherwise,
  including under a declared residual blind region.
* P2 ``family_calibrated`` -- calibrated, risk-tolerant: ``hold`` if the
  family-calibrated regime rule fires; serves otherwise, *including under an
  explicitly declared residual blind region* (reason code
  ``allowed_with_residual_blind_region``). It is not a fail-closed policy.
* P3 ``family_calibrated_strict`` -- *sensor-coverage-complete relative to
  the declared evidence dimensions* (artifact
  1.3.1 name; the identifier is kept for compatibility with the frozen
  evidence tables): as P2, and every mandatory protected boundary that the
  regime covers neither exactly (trusted item-aligned reference) nor
  statistically (declared calibrated sensor) yields ``hold`` (reason code
  ``unverified_boundary``). It fails closed *on missing coverage*, not on
  insufficient power: a boundary that is nominally covered by a calibrated
  sensor of low power is served exactly as under P2, so P3 does not guarantee
  a minimum detection power and does not rule out an unsafe allow whenever a
  sensor exists. Abstention that depends on the validity of the calibration
  itself (out-of-support context) is outside this layer (Paper 2.5).

Three notions must not be conflated: the *contract logic* of ``src/hsaas/contracts.py``
fails closed on its invariants (a violated invariant blocks, missing mandatory
evidence holds); the *decision policy* P2 is calibrated and risk-tolerant; the
*decision policy* P3 abstains on missing coverage. ``block`` is reserved for
violations of an exact invariant against a trusted reference; ``hold`` is the
response to statistical evidence of deviation or, under P3, to a boundary the
regime does not cover. The decision composes with the four frozen HSaaS
contracts by taking the maximum in the lattice ``allow < hold < block``.

The module is pure: it performs no I/O and does not depend on the evidence
tables, so the same function serves the offline batch evaluator of Gate D and
a future service endpoint; nothing here is a deployed runtime service.
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
POLICY_CLASS: Final[dict[str, str]] = {
    "serve_always": "baseline (always serve)",
    "union_uncalibrated": "uncalibrated, risk-tolerant (1.1.0 union of per-sensor rules)",
    "family_calibrated": "calibrated, risk-tolerant (may serve under a declared residual blind region)",
    "family_calibrated_strict": "sensor-coverage-complete relative to the declared evidence dimensions, abstaining on missing coverage (a mandatory boundary without declared exact or statistical coverage => hold; no minimum-power guarantee)",
}


@dataclass(frozen=True)
class RegimeSpec:
    """What an information regime can establish about each protected boundary.

    ``coverage`` maps a boundary to one of ``exact`` (trusted aggregate or
    item-aligned reference; exact-zero null), ``calibrated`` (batch-level statistical
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
    # No exact feature-value sensor was executed. Feature coverage remains
    # calibrated; conclusion/aggregate and item identity use exact references.
    "I_XFY_trusted": RegimeSpec("I_XFY_trusted", True, {"feature": "calibrated", "prediction": "exact", "label": "exact"}),
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
    """Protected boundaries without declared exact or statistical coverage under the regime.

    Coverage is declared, not measured: a boundary covered by a calibrated
    sensor counts as covered whatever the power of that sensor.
    """

    return tuple(b for b in protected if not regime.covers(b))


def decide(
    policy: str,
    regime: RegimeSpec | str,
    evidence: Evidence,
    protected: tuple[str, ...] = BOUNDARIES,
) -> Decision:
    """Deterministic, total decision function of policy, regime and evidence.

    ``evidence.family_fire`` is the flag of the family-calibrated rule of the
    regime (artifact 1.3.0: conformal max-rank p-value <= alpha).
    """

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
