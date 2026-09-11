# Paper 1.5 artifact 1.3.0 — prespecified protocol: amendment A2 (family calibration), regenerated Gates F and D, and the adversarial Gate A (cluster-preserving perturbation)

Frozen on **2026-09-07**, before any regenerated Gate F/D table existed and
before any Gate A job was executed. The commit that freezes this file is
recorded in the manifests of the regenerated evidence
(`policy_evidence_manifest.json`, `adversarial_evidence_manifest.json`) by
file hash. Nothing in this protocol may change after execution except to
correct a documented implementation defect, recorded in the amendments
section with its date. Every result is published as executed.

Artifact 1.3.0 is the last scientific iteration of Paper 1.5. After it, the
article is reopened only for an objective error that invalidates a claim, an
editorial requirement of the journal, or a reviewer request.

## A2 — Amendment to the 1.2.0 protocol (`paper15_v12_policy_prereg.md`, Gate F)

**What was discovered (2026-09-07).** Two independent reviews of artifact
1.2.0 found that Proposition 5(b) is false as stated. The executed family rule
scored every calibration draw against the calibration set only (each draw
against the other 199) while the audited batch was scored against all 200
calibration draws, and fired when the audited family score exceeded the 191st
smallest calibration family score. With several sensors and tied max-rank
scores the calibration scores and the audited score are not exchangeable, so
the rank argument of the proof does not apply, and the extra `1/(n+1)`
claimed to cover the asymmetry does not. Finite counterexample: `n = 4`,
`alpha = 0.2`, three sensors with cyclic orderings over five vectors; the
executed rule fires for three of the five possible audited members
(probability 0.60 under exchangeability) against the published bound
`(n+2-k)/(n+1) = 0.40` and against `alpha`. On the frozen null draws, random
re-splits of the 400 draws of each cell into 200 calibration and 200 audited
draws (an assignment that is exchangeable by construction) give pooled firing
rates 0.052 / 0.058 / 0.040 / 0.059 for `I_X` / `I_XF` / `I_Ym` / `I_XFY`
(30 re-splits, seed 20260907): the executed rule exceeds `alpha` in the
multi-sensor regimes even when the exchangeability premise holds.

**What is invalidated.** Proposition 5(b) of artifact 1.2.0 (the bound
`alpha + 1/(n+1)`), its proof, and the attribution in Proposition 5(c), in
Section VI-B and in the limitations of the 1.2.0 manuscript of the whole
residual excess (0.061 / 0.073 / 0.048 / 0.079 against 0.05) to the
violation of exchangeability by the design (overlapping draws, calibration and
evaluation halves being different rows of one staged table). Part of that
excess is bias of the rule itself.

**What remains descriptively valid.** Every 1.2.0 number was computed
correctly for the rule as executed: the union rates 0.125 / 0.203 / 0.048 /
0.259 (independent of the family rule), the per-sensor rates of Gate N, the
structural zero firings on the label path (a consequence of the views, not of
the rule), the exact detections of the trusted regime, and the Gate D counts
under P0, P1 and P2/P3 *for the 1.2.0 rule*. They are kept in the comparison
tables of 1.3.0 under the label "1.2.0 rule (asymmetric)" and are not used for
any decision or claim of 1.3.0.

**Pre-amendment diagnostic, disclosed.** During the review session of
2026-09-07, before this amendment was written, a diagnostic script computed on
the frozen draws (i) a symmetric conformal max-rank rule with p-value
`(1 + #{calibration scores >= audited score}) / 201`, pooled false-alarm
rates 0.056 / 0.058 / 0.048 / 0.053 on 12,000 clean draws from evaluation
pools disjoint from the calibration pools (resampled draws within a pool may overlap),
and (ii) the re-split rates quoted above. These numbers were seen before the
amendment. They are recorded here so that the regenerated Gate F cannot be
presented as a blind result: the rule adopted below is that construction,
formalised and tested, and its regenerated numbers are expected to coincide
with the diagnostic. No other rule or parameter was tried.

**Rule adopted (full conformal max-rank p-value).** For a cell with `n = 200`
calibration vectors `v_1..v_n` (one value per sensor of the regime) and an
audited vector `v`, form the augmented set of `n + 1` vectors and give every
member `j` the leave-one-out family score

    U~_j = max_{s in regime} #{i != j : v_{s,i} < v_{s,j}} / n,

computed against the other `n` members of the augmented set. The conformal
p-value of the audited vector is `p = (1 + #{i <= n : U~_i >= U~_{n+1}}) / (n+1)`
and the regime fires iff `p <= alpha = 0.05` (ties count against firing). If
the `n + 1` vectors are exchangeable, `P(p <= alpha) <= floor(alpha (n+1)) / (n+1)
= 10/201 = 0.0498 <= alpha`, with no assumption on ties or continuity
(Proposition 5(b) of `manuscript/FORMAL_CORE.md`, version 1.2; the
deterministic counting statement behind it is tested exhaustively in
`tests/test_family_calibration_exhaustive.py`, including the counterexample
above). For a single sensor without ties the rule coincides with the
per-sensor rule of artifact 1.1.0 (fire iff the value exceeds the 191st
smallest calibration value). The guarantee is marginal (unconditional) over
the joint draw of calibration set and audited batch; conditional on a fixed
calibration set the false-alarm probability fluctuates around the level, and
the 200 evaluation draws of a cell share the calibration set, so pooled rates
remain descriptive and the inference unit remains the (environment, split)
cluster.

**Alternative studied (split construction).** Reference draws define the
per-sensor rank transform, a disjoint calibration set gives the null family
scores, and the audited batch is compared with those scores:
`p = (1 + #{c : U(c) >= U(v)}) / (|C| + 1)`. It is valid under the same
exchangeability premise conditional on the reference set, but uses half of
the draws for ranking and half for calibration (p-value resolution 1/101).
Decision recorded before regeneration: the full conformal rule is adopted
because it is exact with ties, uses all 200 draws and reduces to the 1.1.0
per-sensor rule; the split construction is reported once as a sensitivity
column (S1: reference = draws 01–10 of each run, calibration = draws 11–20).

**Analyses regenerated from the frozen 1.1.1 outputs (no kernel, model or
draw re-executed).**

- Gate F: per cell and regime, conformal p-values of the 200 evaluation
  draws, the 1,200 shams, the 10,800 intervened observations and the clean
  rows; false-alarm rate per cell, per (environment, split) cluster, per
  environment with five-cluster `t` intervals, and pooled; detection per
  intervention and regime; near-null control response; label-path checks.
  Three rules side by side on identical draws: union of per-sensor rules
  (1.1.0), 1.2.0 asymmetric family rule, conformal family rule (adopted); the
  split construction as S1.
- Decomposition: the pooled excess of the 1.2.0 rule over the nominal level
  is split into *rule bias* (1.2.0 rate minus conformal rate on the same
  draws) and *design effect* (conformal rate minus nominal), and both rules
  are evaluated under 30 exchangeable random re-splits of the 400 pooled
  draws of every cell (seed 20260907), where any excess of the 1.2.0 rule is
  its own bias and the conformal rule must stay at or below the level.
- E1 (`gate2_id_256`, 256-row draws from 322-row pool halves, at most one
  disjoint draw per half): never excluded. The primary aggregate is over the
  eight environments as preregistered in 1.2.0; a sensitivity aggregate over
  the seven environments other than E1 and E1 on its own are reported
  alongside, with the reason (the draws of E1 overlap almost entirely, so its
  200 draws per cell carry the information of about one independent batch per
  pool half).
- Gate D: the four policies over the five regimes on the same 24,000 frozen
  observations, with P2 and P3 using the conformal rule and P1 unchanged;
  the 1.2.0-rule versions of P2 and P3 are kept as comparison columns. Metrics
  per (regime, policy, tau in {0, 0.02, 0.05}): unsafe allow, safe allow, true
  hold, true block, false hold, false block, benign hold, benign block,
  immaterial allow, integrity-only hold/block, containment, coverage, residual
  blind material, decision false-alarm rate (clean draws; exact-zero rows for
  the trusted regime, flagged as a different denominator), benign interruption
  rate (near-null shams held or blocked; same 1,200 rows for every regime),
  non-material interruption rate (clean, benign and immaterial observations
  held or blocked over their total). Consistency checks D1–D5 of 1.2.0 with
  D3 at 2,617 material label rows.

**Results fixed before execution.** Expectations recorded now: (i) the
conformal rule lies within [0.035, 0.065] pooled in every regime, with E1 as
the only environment above 0.10; (ii) the rule bias accounts for most of the
1.2.0 excess in `I_XF` and `I_XFY` and the design effect is below 0.01 in
every regime except through E1; (iii) unsafe allows under P2 change by fewer
than 2% of the 7,008 material rows relative to the 1.2.0 rule; (iv) the label
path stays at zero firings in `I_X`, `I_XF` (3,600 rows) and `I_Ym` (1,800
prior-preserving rows) under the conformal rule, since the audited sensor
values of those rows equal the clean reference exactly and the conformal
p-value is then 1. Whatever is observed is published.

**Acceptance checks (fail-closed).** F0: frozen per-sensor thresholds
reproduced from the calibration draws. F1: conformal pooled rate at or below
the union pooled rate in every regime. F3: zero firings of the conformal `I_X`
and `I_XF` rules on the 3,600 label rows and of `I_Ym` on the 1,800
prior-preserving rows. F4: under every exchangeable re-split, the conformal
firing fraction of every cell and regime is at most `floor(0.05 * 201) / 201`
plus the pooling tolerance of one draw (the counting bound holds per
augmented set; a re-split evaluates 200 audited draws against one calibration
set, so the fraction is a mean of dependent indicators and is checked at
0.0498 + 0.01). D1–D5 as in 1.2.0.

## Gate A — adaptive cluster-preserving perturbation (adversary class F5)

**Question.** The two executed feature-side drift mechanisms (feature-wise
mean shift, scaling drift) are detected in every cell of the frozen design
because the projected features hold tight clusters of rows that a fresh clean
batch reproduces and any in-place displacement smears (`null_mass_point_profile.csv`:
in every environment some feature keeps 69–87% of the rows within 0.01
standard deviations). The adversary model of 1.2.0 names the adaptive
attacker who preserves that structure (F5) but does not execute it. What do
the batch-level regimes detect, and how much does the conclusion move, when
the same mechanisms are applied by an attacker who leaves the clustered
entries untouched?

**Threat knowledge.** The attacker holds the audited batch and knows the
batch-level sensor definitions (per-feature JSD, MMD and KS against a clean
reference batch; score and prediction sensors) and the cluster fingerprint.
It does not need the calibration draws or the thresholds and does not use
them. It cannot write the training data, the fitted model, the reference
batch, the labels or the item-aligned references.

**Perturbation algorithm (`src/attacks/cluster_preserving.py`).** On the
audited batch (after the training-fitted projection and the branch scaler,
exactly where the executed mechanisms act), per feature `j`: an entry
`x[i, j]` is *clustered* when at least `ceil(0.05 n)` rows of the batch
(itself included, never fewer than two) lie within `0.01 sd_j` of it, where
`sd_j` is the population standard deviation of feature `j` over the batch;
entries of a constant feature are all clustered. Clustered entries are left
untouched. Every other entry receives the executed mechanism unchanged:
mean shift `x + d_j`, `d_j ~ N(0, delta)` drawn once per feature with the
runner's stable attack seed; scaling drift `x (1 + alpha)`. Labels are never
touched. The window (0.01 standard deviations) and the minimum mass (5% of
the batch) are fixed from the 1.1.0 mass-point profile before execution and
are not tuned.

**Budget.** The entries outside clusters, data-determined; the perturbed
entry fraction per row is recorded and reported (`atk_perturbed_entry_fraction`).

**Strength grid (fixed).** delta, alpha in {0.02, 0.05, 0.10, 0.25, 0.50}.
The first three match the frozen suite; 0.25 and 0.50 explore whether the
attacker can buy materiality on the unclustered entries. No strength is added
or removed after execution.

**Matched controls.** The executed mechanisms at 0.02 / 0.05 / 0.10
(`mean_shift_pf_delta_*`, `scaling_drift_alpha_*`) run in the same jobs with
their frozen tags, hence with the same attack seeds as the frozen expansion.

**Environments, models, seeds, dimensions.** The eight null-calibration
environments E1–E8 with their frozen feature maps (ZZ everywhere; ZZ, Z and
PauliXYZ in E2 and E3) and sample caps (256/256 in E1, 128/128 otherwise);
SVC-RBF and the fidelity kernels; split seeds 42–46; model seeds 42, 43;
dimensions 8, 10, 12; exact-statevector engine; 240 jobs
(`src.experiments.run_v13_f5_queue`); suite `paper_f5` (clean, six matched
controls, ten adaptive conditions). Single-threaded BLAS per worker.

**Target sensors and regimes.** Batch-level `I_X` (feature JSD, MMD, KS
rejection) and `I_XF` (plus score JSD, prediction-rate shift, prediction JSD),
`I_XFY` (batch), under the union rule (1.1.0 thresholds of the same cells),
the 1.2.0 asymmetric rule and the conformal rule; exact detection under
`I_XFY*` (prediction disagreement, confusion-profile deltas; label mismatch
is zero by construction).

**Materiality endpoint.** As Gate D: `|Delta_R| > 0` primary; 0.02 and 0.05
as sensitivity; `Delta_R` recomputed as the signed change of balanced
accuracy.

**Endpoints (prespecified).**
- A1: detection rate per mechanism, strength, regime and rule, pooled over
  the eight environments (600 observations per condition and model class as
  in Gate F) and per environment; the matched controls alongside.
- A2: prediction-change rate (item-aligned disagreement > 0) and
  conclusion-change rate (material fraction) per mechanism and strength, with
  the mean signed change.
- A3: unsafe allows under P2 (conformal) and P3 in `I_X`, `I_XF`, `I_XFY`,
  and exact detection under `I_XFY*`, on the material adaptive rows; benign
  interruption is not defined for this gate (no clean draws are re-run).
- A4: evasion ratios at matched strengths: detection(F5) / detection(F2) and
  material fraction(F5) / material fraction(F2), per regime and rule.
- A5: distribution of the perturbed-entry fraction (attacker budget actually
  available) per environment, branch and dimension.

**Acceptance checks (fail-closed).** A0: 240/240 jobs complete, 16
interventions plus clean per (model, dimension, split, model seed) cell, the
frozen maps and caps. AC1: the clean rows and the six matched-control rows
reproduce the frozen expansion rows of the same (environment, dimension,
split, model seed, model, intervention) within 1e-9 in balanced accuracy,
clean balanced accuracy, the ten calibrated sensors and the prediction
disagreement (the replay is the frozen pipeline). AC2: label sensors and
label-flip rate are zero on every adaptive row (labels untouched). AC3: every
adaptive row records a frozen-entry fraction strictly between 0 and 1 or
equal to 1 (an all-frozen batch is legitimate and reported), never missing.
AC4: every material adaptive row has non-zero prediction disagreement (a
changed conclusion requires a changed prediction when labels are fixed).

**Expectations recorded before execution.** (i) At the matched strengths
0.02–0.10 the detection of F5 under `I_X` and `I_XF` falls far below the
0.98–1.00 of the matched controls; the value recorded as expectation is below
0.30. (ii) The material fraction of F5 at matched strength is below that of
F2. (iii) At 0.25 and 0.50 both detection and materiality rise; no expectation
is recorded on where detection crosses 0.5. (iv) Every material adaptive row
is blocked under `I_XFY*` (AC4 makes this structural). (v) Some adaptive rows
are served under P2 with a changed conclusion in `I_X` and `I_XF`; their
number is the primary security endpoint of the gate. Whatever is observed is
published, including a failure of (i).

**Stopping rule.** The prespecified grid is executed once. No strength,
mechanism, window, minimum mass, environment or seed is added or removed
after seeing results. A job is re-run only for an infrastructure failure
(one retry, logged); failed jobs are preserved in the queue status.

**Reporting.** The gate enters the adversary table of the main text (the F5
row changes from "discussed" to executed, with its rates), one paragraph of
the results, and the supplement in full (tables and one figure generated from
the manifested outputs).

## L3 — confusion-preserving relabeling: decision recorded

Not executed. The class is already realised by 808 of the executed label
rows (witness W1 = W10: flips with zero confusion-profile delta and zero
conclusion change). A controlled L3 gate would reproduce counterexample C1
by construction and could change no conclusion of the article: a trusted
aggregate reference is exactly blind to it (Corollary 3b), an item-aligned
reference detects it exactly, and every batch-level policy serves it as an
immaterial row, which is not an unsafe allow under the prespecified
definition. Executing it would add a table, not evidence.

## Amendments

**A3 — 2026-09-07, implementation clarification recorded before the first
builder run (no result seen).** Check F4 as frozen asked that the conformal
firing fraction stay below `floor(0.05 * 201)/201 + 0.01` in *every*
re-split. That mis-states what the counting bound guarantees: the bound
constrains the probability over exchangeable assignments, i.e. the
expectation of the firing fraction, while a single re-split evaluates 200
audited draws against one fixed calibration set and its fraction fluctuates
around the level conditionally on that set. F4 is therefore evaluated on the
mean over the 30 re-splits of every (cell, regime) with tolerance 0.02 and on
the pooled mean over the 60 cells with tolerance 0.005. The maximum
per-re-split fraction is still reported (`family_resplit_by_cell.csv`). No
other check, endpoint or parameter changed.
