"""Workflow state with primitive and derived artifacts, intervention semantics and the three kernel notions.

Artifact 1.3.1 (formal correction; no new evidence). This module is the
executable counterpart of Section 1 of ``manuscript/FORMAL_CORE.md``:

* a workflow state is a tuple of *primitive* (stored) artifacts
  ``(X, P, C, E, xi, g, f, y)`` and of *derived* artifacts recomputed from
  them by the workflow: ``X_tilde = P(X)``, ``K_sem = Phi(C)`` (ideal semantic
  kernel induced by the circuit on the probe set), ``K_hat = est(K_sem, E, xi)``
  (finite-shot estimate produced by execution), ``K_obs = g(K_hat)`` (kernel
  object delivered downstream after estimation, transmission and
  post-processing), ``y_hat = f(X_tilde, K_obs)`` and ``R = r(y_hat, y)``;
* an intervention overwrites a declared set of nodes (primitive or derived),
  keeps every node that is not a descendant of an overwritten node fixed, and
  recomputes the descendants of the overwritten nodes through the workflow
  with the retained estimation randomness ``xi``;
* the class of an intervention is read off the overwritten nodes:
  circuit-side (``C``: may change ``K_sem``), estimation/execution variation
  (``E`` or ``xi``: ``K_sem`` fixed, ``K_hat`` changes), post-processing or
  kernel substitution (``g`` or ``K_obs``: ``K_sem`` and ``K_hat`` fixed,
  ``K_obs`` changes), label-only (``y``: only ``R`` is recomputed) and
  feature-side (``X``, ``P`` or ``X_tilde``).

The module also contains the finite-shot arithmetic behind Proposition 7(iii):
for an honest binomial estimate of a fidelity ``p`` from ``N`` shots the event
``K_hat == K_0`` has probability ``C(N, Np) p^{Np} (1-p)^{N-Np}`` when ``Np``
is an integer and zero otherwise, so the exact-equality rule has false-alarm
probability ``1 - Pr[K_hat = K_0]``, which is large in general but is not
universally one (``p = 1/2``, ``N = 2`` gives ``1/2``).

The module is pure and depends on nothing but the standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from math import comb, isclose
from typing import Any, Callable, Final, Mapping, Sequence


PRIMITIVE_NODES: Final[tuple[str, ...]] = ("X", "P", "C", "E", "xi", "g", "f", "y")
DERIVED_NODES: Final[tuple[str, ...]] = ("X_tilde", "K_sem", "K_hat", "K_obs", "y_hat", "R")
NODES: Final[tuple[str, ...]] = PRIMITIVE_NODES + DERIVED_NODES

# Direct parents of every derived node; the order of DERIVED_NODES is a topological order.
PARENTS: Final[dict[str, tuple[str, ...]]] = {
    "X_tilde": ("P", "X"),
    "K_sem": ("C",),
    "K_hat": ("K_sem", "E", "xi"),
    "K_obs": ("g", "K_hat"),
    "y_hat": ("f", "X_tilde", "K_obs"),
    "R": ("y_hat", "y"),
}

INTERVENTION_CLASSES: Final[dict[str, tuple[str, ...]]] = {
    "circuit_side": ("C",),
    "estimation_variation": ("E", "xi"),
    "post_processing": ("g", "K_obs"),
    "label_only": ("y",),
    "feature_side": ("X", "P", "X_tilde"),
}


def descendants(nodes: Sequence[str]) -> frozenset[str]:
    """Every derived node that depends, directly or transitively, on one of ``nodes``."""

    unknown = [n for n in nodes if n not in NODES]
    if unknown:
        raise KeyError(f"unknown workflow nodes: {unknown}")
    out: set[str] = set()
    for node in DERIVED_NODES:  # topological order
        if node in nodes or any(p in out or p in nodes for p in PARENTS[node]):
            if node not in nodes:
                out.add(node)
    return frozenset(out)


@dataclass(frozen=True)
class Workflow:
    """The maps that turn primitive artifacts into derived ones."""

    preprocess: Callable[[Any, Any], Any]  # (P, X) -> X_tilde
    semantic_kernel: Callable[[Any], Any]  # Phi: C -> K_sem
    estimate: Callable[[Any, Any, Any], Any]  # (K_sem, E, xi) -> K_hat
    post_process: Callable[[Any, Any], Any]  # (g, K_hat) -> K_obs
    predict: Callable[[Any, Any, Any], Any]  # (f, X_tilde, K_obs) -> y_hat
    conclude: Callable[[Any, Any], Any]  # (y_hat, y) -> R

    def compute(self, node: str, values: Mapping[str, Any]) -> Any:
        if node == "X_tilde":
            return self.preprocess(values["P"], values["X"])
        if node == "K_sem":
            return self.semantic_kernel(values["C"])
        if node == "K_hat":
            return self.estimate(values["K_sem"], values["E"], values["xi"])
        if node == "K_obs":
            return self.post_process(values["g"], values["K_hat"])
        if node == "y_hat":
            return self.predict(values["f"], values["X_tilde"], values["K_obs"])
        if node == "R":
            return self.conclude(values["y_hat"], values["y"])
        raise KeyError(node)


@dataclass(frozen=True)
class State:
    """A workflow state: primitive artifacts plus the derived artifacts the workflow computed from them."""

    workflow: Workflow
    values: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_primitives(cls, workflow: Workflow, **primitives: Any) -> "State":
        missing = [n for n in PRIMITIVE_NODES if n not in primitives]
        extra = [n for n in primitives if n not in PRIMITIVE_NODES]
        if missing or extra:
            raise ValueError(f"primitives must be exactly {PRIMITIVE_NODES}; missing {missing}, extra {extra}")
        values = dict(primitives)
        for node in DERIVED_NODES:
            values[node] = workflow.compute(node, values)
        return cls(workflow, values)

    def __getitem__(self, node: str) -> Any:
        return self.values[node]

    def intervene(self, **overrides: Any) -> "State":
        """Overwrite the given nodes, keep every non-descendant fixed and recompute the descendants.

        A derived node may be overwritten directly (a feature attack on
        ``X_tilde``, a kernel substitution on ``K_obs``); its own parents are
        then left untouched, which is what makes the intervention class
        explicit.
        """

        if not overrides:
            raise ValueError("an intervention must overwrite at least one node")
        changed = tuple(overrides)
        to_recompute = descendants(changed)
        values = dict(self.values)
        values.update(overrides)
        for node in DERIVED_NODES:
            if node in to_recompute:
                values[node] = self.workflow.compute(node, values)
        return replace(self, values=values)

    def changed_nodes(self, other: "State", *, equal: Callable[[Any, Any], bool] | None = None) -> frozenset[str]:
        eq = equal or (lambda a, b: a == b)
        return frozenset(n for n in NODES if not eq(self.values[n], other.values[n]))


def intervention_class(overridden: Sequence[str]) -> str:
    """Name the intervention class of an override set; mixed sets are ``mixed``."""

    matches = [name for name, nodes in INTERVENTION_CLASSES.items() if any(n in nodes for n in overridden)]
    if len(matches) == 1:
        return matches[0]
    return "mixed" if matches else "other"


# ---------------------------------------------------------------------------
# Proposition 7(iii): exact equality under finite-shot estimation
# ---------------------------------------------------------------------------


def binomial_equality_probability(p: float, shots: int) -> float:
    """``Pr[X/N = p]`` for ``X ~ Binomial(N, p)``: zero unless ``N p`` is an integer."""

    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if shots < 1:
        raise ValueError("shots must be a positive integer")
    k = round(p * shots)
    if not isclose(k, p * shots, rel_tol=0.0, abs_tol=1e-12):
        return 0.0
    return comb(shots, k) * (p ** k) * ((1.0 - p) ** (shots - k))


def finite_shot_equality_probability(fidelities: Sequence[float], shots: int) -> float:
    """``Pr[K_hat = K_0]`` for independent binomial estimates of the kernel entries ``fidelities``."""

    prob = 1.0
    for p in fidelities:
        prob *= binomial_equality_probability(p, shots)
        if prob == 0.0:
            return 0.0
    return prob


def exact_equality_false_alarm(fidelities: Sequence[float], shots: int) -> float:
    """False-alarm probability of ``fire iff K_hat != K_0`` for an honest finite-shot estimate.

    Equals ``1 - Pr[K_hat = K_0]``: it depends on the discrete support of the
    estimator, may be large or equal to one, and is not universally one.
    """

    return 1.0 - finite_shot_equality_probability(fidelities, shots)
