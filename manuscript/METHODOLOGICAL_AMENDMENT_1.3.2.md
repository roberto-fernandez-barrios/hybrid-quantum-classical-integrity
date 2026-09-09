# Methodological amendment 1.3.2 — audited reference semantics

## Scope and decision

Version 1.3.2 is a controlled methodological/editorial correction of 1.3.1.
The experimental evidence remains frozen at artifact 1.3.0. No benchmark,
job, model, kernel, seed, dataset, attack, threshold, workload, QPU execution,
or experimental calibration was rerun.

**Repair B was selected.** A complete historical-only Level-A reconstruction
is not available in the frozen outputs: the feature family contains
training-reference JSD/MMD/KS variants, but the selected prediction, label
marginal and joint-outcome families have no complete prespecified historical
counterparts. Substituting a post-hoc subset would change the studied sensor
family and would not instantiate all four batch regimes.

> 1.3.2 does not alter experimental results; it corrects the epistemic
> taxonomy so that Level A accurately describes the statistical
> same-batch/untrusted comparisons actually executed.

Here “untrusted” means “not demonstrated as authenticated evidence available
to a deployed auditor.” The clean arrays were protected from mutation by the
executed benchmark attack API, so they are a benchmark-protected oracle. That
experimental protection is not a deployment authentication result.

## Audited implementation chain

1. `run_benchmark.py` creates an intervened evaluation batch from
   `X_te_f/y_te_f` and retains the clean arrays outside the attack mutation.
2. The selected Class-A feature, prediction, label-marginal and confusion
   sensors compare aggregate current values with aggregate values computed
   from those clean arrays. They use the same item set but do not use item
   correspondence.
3. Frozen calibration scores turn sensor values into per-family firing flags.
4. Gate D builds `union_fire`, `family_fire`, and `exact_fire`.
5. `src/hsaas/policy.py` consumes only those flags and the declared regime. It
   consumes neither `X_te_f/y_te_f` nor a clean same-item batch.
6. Producing the Class-A scores upstream nevertheless requires the reference
   asset identified by the audit. A deployment must supply and protect that
   asset or reduce the associated integrity claim.

## Reference classes

Reference provenance, granularity and decision semantics are separate axes:

- Level/Class A: statistically thresholded aggregate comparison; the
  reference may be historical or a benchmark-protected clean same-item set.
  The executed selected sensors use the latter, without item pairing and
  without a demonstrated deployed authentication mechanism.
- Level/Class B: deployed-trusted aggregate same-batch reference with an
  exact invariant. It is sufficient for the protected aggregate and, for a
  conclusion that is a function of that aggregate, conclusion integrity.
- Level/Class C: deployed-trusted item-aligned same-batch reference with an
  exact invariant. It is required for item-identity integrity.

The generated authoritative mapping is
`results/paper_digest/paper15_v132_amendment/sensor_reference_audit.csv`.
It is derived directly from the selected sensor lists and runner semantics.

## Frozen-only derived checks

The amendment builder reads existing Gate D and Gate A CSVs and writes only
derived audit tables:

- trusted cost: 85 gross exact-reference blocks; 46 overlap with batch
  `I_XFY`/P2 interruptions; 39 net additional interruptions out of 1,200
  near-null rows (3.25 percentage points);
- adaptive profile: materiality, family-rule detection and P2 material served
  rate for both mechanisms at every preregistered strength;
- sensor audit: current value, reference value, pairing, same-item-set status,
  benchmark protection, deployed authentication and compatible class.

The builder performs nine assertions before writing its manifest. The four
release-critical editorial facts—contiguous corollaries, gross versus net
trusted cost, aggregate plus per-strength adaptive reporting, and zero
`I_Ym` containment with 5,450 residual-blind material cases—also have
permanent regression tests.

## Scientific consequence

The correction narrows no structural theorem and changes no result row. It
removes the false implication that the executed batch sensors were purely
historical and the equally false implication that using the same item set in
the benchmark established a deployed trusted anchor. The constructive claim
is minimum evidence granularity relative to the integrity claim, not novelty
of storing a reference.
