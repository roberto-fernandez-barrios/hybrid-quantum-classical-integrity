# Paper 1.5 reinforcement gates — prespecified protocol (artifact 1.1.0)

Frozen on **2026-09-06** before any reinforcement job was executed. This file
is the internal preregistration for the three sensitivity gates added on top of
the frozen 1.0.0 evidence. The central claim, the abstract counts, and the
1.0.0 tables are not modified by these gates. Nothing in this protocol may be
changed after execution except to correct a documented implementation defect,
which must be recorded below with its date.

## Common settings

- Quantum evaluator: `exact_statevector` (ideal fidelity kernel); one
  feature-map repetition; no shot emulation.
- Split seeds 42–46; nested model seeds 42, 43; projected dimensions 8, 10, 12.
- Preprocessing, sensors, signal parameters and intervention suite identical to
  the frozen expansion unless a gate states otherwise.
- Primary inference unit: split cluster after averaging nested model seeds;
  two-sided 95% Student-$t$ intervals with four degrees of freedom; no
  population or multiplicity-adjusted claim.
- Fail-closed builder: a gate with a missing job, a mismatched design, or a
  failed acceptance check produces no evidence manifest.
- Rule: every result is published as executed, including any reduction or
  reversal of the secondary ZZ-minus-SVC profile.

## Gate N — null calibration of non-invariant sensors

**Question.** Within the frozen design, what false-alarm rate and detection rate
do the non-invariant sensors achieve at a fixed nominal level, and does the
exact blind region survive calibration?

**Environments.** The eight expansion environments E1–E8 with their frozen
feature maps (ZZ everywhere; ZZ, Z and PauliXYZ additionally in E2 and E3) and
sample caps (256/256 in E1, 128/128 otherwise).

**Null draws.** For each run, the clean pool is the set of evaluation-side raw
rows not selected into the frozen evaluation batch (900 − n in ID protocols,
3,000 − n in OOD protocols). The pool is transformed with the same training-
fitted projection and the same training-fitted scaler as the frozen run. A
permutation seeded by the split seed divides the pool into a **calibration
half** and an **evaluation half**. Each null draw is a simple random sample
without replacement of n rows from one half; the draw seed is the runner's
stable attack seed for the draw tag. Draws are `clean_resample_calib_01..20`
(calibration half) and `clean_resample_eval_01..20` (evaluation half). The
benign controls `sham_identity`, `sham_tiny_gaussian_sigma_0.001` and
`sham_tiny_scaling_alpha_0.001` are included as specificity controls; identity
is a sanity check of exact invariance only and contributes nothing to the null.

**Calibrated sensors.** Feature regime: `integrity_jsd_vs_clean_eval`,
`integrity_mmd_vs_clean_eval`, `integrity_ks_reject05_vs_clean_eval`.
Prediction-aware: `integrity_score_jsd_vs_clean_eval`. Label marginal:
`integrity_label_prior_shift`, `integrity_label_jsd`. Joint outcome:
`integrity_pred_pos_rate_shift`, `integrity_pred_jsd`,
`integrity_confusion_profile_l1`, `integrity_confusion_profile_jsd`.
`integrity_pred_disagreement` is item-aligned; its null is exactly zero by
construction and it is reported through exact invariance, not calibration.

**Threshold rule.** For each (environment, dimension, model) cell, calibration
values are pooled over the five split seeds and two model seeds
(n_cal = 200). The threshold is the ⌈(n_cal + 1)(1 − α)⌉-th smallest
calibration value with α = 0.05 (the 191st of 200). A sensor fires when its
value is strictly greater than the threshold. Thresholds are computed once,
from calibration draws only, and frozen before any attacked row is examined.

**Evaluation.** Empirical false-alarm rate = fraction of evaluation draws that
fire, per sensor and per regime (a regime fires if any of its sensors fires).
Detection rate = fraction of frozen `paper_core` observations (from
`expansion_unique_observations.csv`, matched on environment, dimension and
model) that fire, per intervention and per regime.

**Prespecified endpoints.**
1. N1: empirical false-alarm rate per sensor and regime on the evaluation half,
   reported against nominal α = 0.05 with its binomial 95% interval.
2. N2: calibrated detection rate of the feature and feature-plus-prediction
   regimes on evaluation-label interventions must be exactly 0 (consistency
   with Propositions 1–2). This is an acceptance check.
3. N3: calibrated detection rate of the joint-outcome regime on
   evaluation-label interventions with positive conclusion impact.
4. N4: calibrated detection rate of each regime on the four feature-side
   mechanisms, by strength.
5. N5: benign-control firing rates for the two near-null shams.

**Disclosed limitations fixed in advance.** Simple random null draws let class
counts vary, whereas the frozen batch is stratified; the label-marginal null
therefore reflects natural batch variability. In E1 (n = 256) each pool half
holds 322 rows, so successive draws overlap heavily and the null variability is
understated; E1 calibrated rates are reported as indicative. Thresholds are
pooled across split seeds of the same staged table. None of this is
context-conditioned or conformal runtime calibration, which remains outside
this article.

## Gate P — symmetric preprocessing ablation

**Question.** Does the secondary ZZ-minus-SVC conclusion-impact profile depend
on the branch-specific scalers used in the frozen pipelines?

**Environment.** CICIDS2017 ID, 128/128, `paper_core`, ZZ and SVC only.

**Configurations.** P0 reference `standard`/`minmax2pi` (SVC/QSVC; re-executed
with the exact engine so that all three configurations share tooling); PA
`standard`/`standard`; PB `minmax2pi`/`minmax2pi`.

**Endpoints.** Within-split ZZ-minus-SVC mean suite-average conclusion-impact
difference with cluster interval per configuration and dimension; clean
balanced accuracy per model and configuration; exact label-path invariance
counts, which must hold in every configuration (acceptance check).

## Gate T — tuned baselines

**Question.** Does the secondary profile survive when both learners are tuned
by cross-validation on training rows only?

**Environments.** CICIDS2017 ID 128/128 and one OOD environment selected by the
rule *"the frozen expansion OOD environment with the highest mean clean SVC
balanced accuracy over dimensions"*. Evaluated on the frozen 1.0.0 tables
before execution: UNSW temporal OOD (E8, `gate6_ood_unsw`) at 0.7526; the four
CICIDS temporal pairs lie between 0.4849 and 0.4927. **Selected: E8.**

**Tuning.** SVC-RBF: C ∈ {0.1, 1, 10, 100} × γ ∈ {"scale", 0.01, 0.1, 1.0}.
QSVC: C ∈ {0.1, 1, 10, 100} on the precomputed training fidelity kernel.
StratifiedKFold with 5 folds, shuffle, random_state = model seed; scoring =
balanced accuracy; ties resolved towards the smallest C, then grid order for γ.
Both learners are tuned symmetrically. Evaluation rows are never used.

**Endpoints.** As in Gate P, plus the distribution of selected hyperparameters.
Exact label-path invariance must hold (acceptance check).

## Reporting boundary

The gates enter the supplement as sensitivity analyses and the main text as a
short calibrated-coverage paragraph and an updated limitation statement. They
do not change the abstract counts, the primary blind-region claims, or the
scope exclusions (QPU, calibrated noise, scheduling, provider security,
multi-tenancy, Fleet Management).

## Amendments

**A1 — 2026-09-06, implementation clarification.** Recorded after the queue had
started and after a dry run of the Gate N builder on the three environments
completed at that time (E1, E4, E5), before any Gate P or Gate T result existed.
The dry run showed that the item-aligned sensor `integrity_pred_disagreement`
is undefined on clean null draws: a fresh batch contains different items, so an
item-wise comparison with the reference predictions is not a null realization
and fired in 92% of evaluation draws. The protocol already stated that this
sensor is reported through exact invariance rather than calibration; the
clarification is that **regime unions on null draws include the calibrated
distributional sensors only** (the *batch-level auditor*, who receives a new
batch without item correspondence), and that **item-aligned detection is
reported separately with the exact zero threshold** (the *item-aligned
auditor*, who can compare the same items against trusted references:
prediction disagreement, confusion-profile deltas, and item-level label
mismatch). Thresholds, α, draw counts, the calibration/evaluation partition and
endpoints N1–N5 are unchanged. The distinction is the one the article already
draws between distributional evidence and item-aligned trusted outcomes.
