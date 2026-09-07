# Paper 1.5 artifact 1.2.0 — prespecified protocol for the policy-level calibration and end-to-end decision gates

Frozen on **2026-09-07** before any analysis of the two gates below was run.
This file is the internal preregistration for artifact 1.2.0. It consumes only
outputs that already exist in the frozen 1.1.1 evidence (`null_unique_observations.csv`,
`null_calibration_thresholds.csv`, `expansion_unique_observations.csv`,
`hsaas_audit_envelopes.jsonl`); **no kernel, model, or draw is re-executed**.
The frozen 1.0.0 counts (3,600 / 1,800 / 2,184; 1,440 / 720 / 1,276; 165/165;
6/6) and the 1.1.0 per-sensor thresholds are inputs, not endpoints, and are not
modified. Nothing in this protocol may change after execution except to
correct a documented implementation defect, which must be recorded in the
amendments section with its date.

## Motivation recorded before analysis

Artifact 1.1.0 calibrated each of ten distributional sensors at a nominal
per-sensor level $\alpha = 0.05$ and reported the batch-level regime rule
"fire if any sensor of the regime fires". That rule is not calibrated at the
regime level: the observed unions were 0.125 ($\mathcal I_X$, 3 sensors),
0.203 ($\mathcal I_{XF}$, 6), 0.048 ($\mathcal I_{Y_m}$, 2, perfectly
dependent), 0.259 ($\mathcal I_{XFY}$, 10). Gate N therefore established that
the exact blind regions survive calibration, but it did not supply a decision
rule with a controlled false-alarm budget. In addition, the Clopper–Pearson
intervals of 1.1.0 treat the 200 draws of a cell as independent Bernoulli
trials, whereas the draws are overlapping subsets of one pool half; those
intervals are descriptive, not inferential. Gate F and Gate D below correct
both points using the existing draws.

## Common settings

- Cells: the 60 (environment, dimension, model) cells of Gate N with their
  frozen 200 calibration draws and 200 disjoint evaluation draws.
- Per-sensor thresholds: the frozen 1.1.0 values in
  `null_calibration_thresholds.csv` (191st of 200 calibration values, fire if
  value $>$ threshold). They are reused unchanged.
- Nominal level: $\alpha = 0.05$ **per decision** (per regime rule), not per
  sensor.
- Inferential unit for false-alarm rates: the **(environment, split-seed)
  cluster**. Within a cell the 200 draws come from ten overlapping pool halves
  (five split seeds $\times$ two model seeds; the partition seed is the split
  seed) and are not independent. Rates pooled over draws are reported as
  descriptive; intervals are two-sided 95% Student-$t$ intervals over the five
  split clusters of an environment (four degrees of freedom), after averaging
  the two model seeds, three dimensions and the models of the cell. No
  multiplicity adjustment; no population claim.
- Calibration draws are used only to set thresholds; evaluation draws are used
  only to measure false alarms. This separation is retained from Gate N.
- Fail-closed builder: a failed consistency check produces no manifest.
- Rule: every result is published as executed.

## Gate F — family-wise (policy-level) calibration of each information regime

**Question.** Can the batch-level regime rule be calibrated to the nominal
$\alpha$ at the level of the decision, using the existing calibration draws,
and what does the calibrated rule cost in detection relative to the
uncalibrated union?

**Statistic.** For sensor $s$ and cell $c$, let $F_{s,c}$ be the empirical
distribution of the 200 calibration values. For a draw with sensor vector $v$,
define the calibration rank score $u_s(v) = \#\{\text{calibration values of } s
\text{ strictly below } v_s\} / 200$, and for regime $R$ the family score
$U_R(v) = \max_{s \in R} u_s(v)$ (equivalently one minus the minimum
calibration $p$-value over the family; Tippett combination). Ties count
against firing.

**Threshold.** For each cell and regime, the family threshold $q_{R,c}$ is
the $\lceil 201 \times 0.95 \rceil = 191$st smallest of the 200 calibration
values of $U_R$. The regime fires when $U_R > q_{R,c}$. The threshold is
computed from calibration draws only and frozen before any evaluation draw or
intervened observation is scored. For a regime with a single sensor the rule
coincides with the per-sensor rule of Gate N up to ties.

**Endpoints (prespecified).**
1. F1: empirical false-alarm rate of the family-calibrated rule per regime on
   the 12,000 evaluation draws (descriptive pooled rate) and per environment
   with five-split-cluster $t$ intervals, alongside the uncalibrated union
   rule of Gate N on the same draws. Expectation recorded before analysis:
   the family rule lies near 0.05 in every regime while the union rule stays
   at its 1.1.0 values; E1 remains indicative only.
2. F2: calibrated detection rate of the family rule per intervention and
   regime on the frozen `paper_core` observations of the same cells,
   alongside the union rule, so that the cost of calibration (lost
   detections) is explicit.
3. F3: label-path consistency: the family-calibrated $\mathcal I_X$ and
   $\mathcal I_{XF}$ rules must fire zero times on all 3,600 evaluation-label
   observations and the family-calibrated $\mathcal I_{Y_m}$ rule zero times
   on the 1,800 prior-preserving observations. These are consistency checks
   (Propositions 1–2 make every sensor value in those regimes identical to its
   clean reference, so the score is at the null point).

## Gate D — end-to-end decision evaluation on frozen outputs

**Question.** When sensors, calibrated thresholds, the information regime,
the trusted-reference status, a materiality threshold and the declared
residual blind region are composed into a single `allow/hold/block` decision,
how many observations with material conclusion impact would each policy
serve, and at what false-hold cost?

**Observation set (fixed).** Four classes, all already frozen:
- **clean**: the 12,000 clean evaluation draws (batch-level, no item
  correspondence to the reference batch);
- **benign in-place variation**: the 1,200 near-null shams (Gaussian
  $\sigma = 0.001$ and scaling $\alpha = 0.001$; identity shams are exact
  zeros and are excluded from rates but counted);
- **intervened**: the 10,800 frozen `paper_core` observations of the eight
  Gate N environments (feature and label interventions, item-aligned to the
  reference batch).
Gate 1 rows are not used (their environment has no null draws).

**Materiality.** An intervened observation is *material* when the reported
balanced accuracy changes: $|\Delta_R| > 0$ (primary; equals 1,534 apparent
improvements plus 5,474 drops in the frozen table, 7,008 rows, of which 2,184
are label-path rows). Sensitivity: $|\Delta_R| \ge 0.02$ and $\ge 0.05$.
Intervened rows with $\Delta_R = 0$ are *integrity violations without
conclusion impact* and are reported separately; they are never counted as
unsafe allows.

**Information regimes evaluated.** $\mathcal I_X$, $\mathcal I_{XF}$,
$\mathcal I_{Y_m}$, $\mathcal I_{XFY}$ (batch-level, no reference), and
$\mathcal I_{XFY}^{\star}$ (item-aligned against a trusted reference:
prediction disagreement, confusion-profile deltas, item-level label mismatch
with exact-zero null, plus the batch-level sensors). For clean draws the
item-aligned sensors are undefined; under $\mathcal I_{XFY}^{\star}$ the
clean class is represented by the 600 frozen clean rows and the 600 identity
shams, whose item-aligned sensors are exactly zero, so the false-alarm rate of
the exact sensors is zero by construction and only the batch-level component
can fire.

**Policies (fixed before analysis).**
- P0 `serve_always`: always `allow` (baseline).
- P1 `union_uncalibrated`: `block` if a trusted item-aligned invariant is
  violated (only in $\mathcal I_{XFY}^{\star}$); else `hold` if any
  per-sensor-calibrated sensor of the regime fires (the 1.1.0 rule); else
  `allow`.
- P2 `family_calibrated`: as P1 with the Gate F family rule in place of the
  union. This is the proposed calibrated, information-aware policy.
- P3 `family_calibrated_strict`: as P2, but `allow` additionally requires that
  every protected boundary declared by the contract (feature, prediction,
  label path) is covered by the regime either exactly or by a calibrated
  sensor; if the label boundary is declared protected and the regime has no
  label evidence ($\mathcal I_X$, $\mathcal I_{XF}$) or only marginal evidence
  ($\mathcal I_{Y_m}$, blind to prior-preserving changes), the decision is
  `hold` with reason `unverified_boundary`. This is the fail-closed reading of
  information-set conditionality.

`block` is reserved for exact invariant violations under a trusted reference;
`hold` is the response to statistical evidence or missing evidence. The
composition with the four frozen HSaaS contracts is `max` in the lattice
`allow < hold < block`; it is demonstrated on the six frozen envelopes
without re-running them.

**Endpoints (prespecified).** For each policy, regime and materiality
threshold:
- unsafe allow: material observations decided `allow` (primary endpoint);
- safe allow: clean draws, benign shams and non-material intervened
  observations decided `allow`;
- false hold/block: clean draws decided `hold`/`block` (decision false-alarm
  rate under the null); benign-variation hold/block reported separately;
- true hold/block: material observations decided `hold` or `block`;
- integrity-only hold/block: non-material intervened observations decided
  `hold`/`block`;
- residual blind cases: material observations that are structurally
  indistinguishable from the reference under the regime (label-path rows in
  $\mathcal I_X$/$\mathcal I_{XF}$; prior-preserving rows in $\mathcal I_{Y_m}$);
- coverage: fraction of material observations that are not residual blind
  cases;
- containment: true hold/block divided by material observations;
- operational cost of the union rule: false-hold rate of P1 minus P2 and the
  corresponding difference in containment.

**Consistency checks (acceptance, fail-closed).**
- D1: P0 unsafe allows equal the number of material observations in every
  regime.
- D2: under $\mathcal I_X$ and $\mathcal I_{XF}$, every policy except P3
  allows every label-path observation (structural blindness reproduced by the
  decision layer); under P3 every such observation is held.
- D3: under $\mathcal I_{XFY}^{\star}$, P1–P3 block every material label-path
  observation (2,184/2,184) and every intervened row with a non-zero
  item-aligned delta.
- D4: the decision function is deterministic and total: every observation
  receives exactly one decision with at least one reason code.
- D5: composed decisions on the six frozen envelopes reproduce the frozen
  contract actions when the policy component is `allow`.

**Reporting.** Every table and figure of the two gates is generated from the
manifested outputs; no number is typed by hand. The gates enter the main text
as one calibrated-policy subsection and one end-to-end decision table/figure,
and the supplement in full.

## Amendments

None at freeze time.

**A1 — 2026-09-07, implementation defect found on the first builder run,
before any endpoint was read.** The frozen file (commit `2c2e54a`, SHA-256
`ce623133b6c59ae7c8ccb22b10dfbb56886727a3d4dfba0726e4b133273d8232`) stated
that the 7,008 material rows under the primary definition $|\Delta_R| > 0$
contain 2,184 label-path rows, and check D3 hard-coded that count. The
1.0.0/1.1.0 column `impact_bal_acc` is the *positive part*
$\max(\mathrm{BA}_0 - \mathrm{BA}_a, 0)$ ("harm only" in the runner), so the
2,184 rows are the label-path rows whose balanced accuracy *decreased*. Under
the prespecified signed definition the frozen expansion also contains 433
label-path rows whose balanced accuracy *increased* (apparent improvement)
and 983 rows with no change; the material label-path count is therefore
2,617, and Gate 1 has 1,276 / 105 / 59 (decreased / unchanged / increased).
The manuscript sentence "no negative impact occurs" in 1.1.1 referred to the
clipped column and is corrected in 1.2.0. Check D3 is corrected to: under
$\mathcal I_{XFY}^{\star}$, P1–P3 block every material label-path
observation (all 2,617), of which the 2,184 decreased-accuracy rows are a
subset, and every intervened row with a non-zero item-aligned delta. The
materiality definition, the policies, the endpoints and every other check are
unchanged.

**A2 — 2026-09-07 (artifact 1.3.0), recorded in `paper15_v13_prereg.md`.** The
family rule of Gate F as specified above (calibration draws scored against the
calibration set, audited batch against all 200, threshold at the 191st smallest
calibration score) is asymmetric and its stated finite-sample guarantee was
false. It is replaced by the full conformal max-rank p-value; the regenerated
Gates F and D and the decomposition of the 1.2.0 excess are specified in the
1.3.0 protocol. The 1.2.0 numbers remain descriptively valid for the rule as
executed and are kept as comparison columns.
