# Method-geometry audit for the v1.3.5 decision

Audit date: 2026-09-09 (Europe/Madrid)  
Audited checkout: `bb96f73c851574867c224c819d512a1d6d124179`  
Frozen scientific release: `paper15-q1-v1.3.4` (`c2381f4`)  
Scope: the calibration/intervention geometry question M1 only. No new gate was executed during this audit.

## Verdict

**M1 is real for the batch-level calibrated sensors.** The frozen runner uses a fixed, benchmark-protected evaluation batch as the reference. A clean-resample null row compares that fixed reference with a different clean batch drawn from a held-out pool, whereas a feature-side intervention row compares the fixed reference with an edited version of the reference batch itself. Thus the statistic implementation is the same, but the statistical relationship between its two arguments is not: the clean-resample draws are unpaired and the interventions are same-item edits.

This finding does not invalidate the reported clean-resample false-action estimates for their declared geometry, the exact same-item identity result, the structural label-only blind regions, or any theorem. It does mean that the original feature-side detection rates, including Gate A, conflate the evaluated dataset's cluster structure, same-item editing geometry, and any monitor-aware reduction. A geometry-aligned sensitivity is therefore required before submission.

## Exact code path

1. `src/experiments/run_benchmark.py` loads the frozen split, selects `te_idx`, and places all other evaluation-side rows in `X_pool_raw`/`y_pool_raw`. It partitions that pool into calibration and evaluation halves with the split seed.
2. `src/attacks/sham.py::CleanResample.apply` draws `len(X)` rows without replacement from the designated pool half. Each draw is distinct from the fixed evaluation batch, although different draws from the same half may overlap.
3. `src/experiments/run_benchmark.py::_run_model` sets `X_ref = X_tr_f`, but the calibrated `*_vs_clean_eval` sensors use `X_te_f` (and its predictions/scores/labels) as their reference. Every attack object receives `X_te_f, y_te_f`.
4. For a clean resample, the current arrays are a fresh `(X_b,y_b)` from the pool. For every ordinary feature intervention, the current arrays are `(T(X_te_f),y_te_f)`. For Identity, current equals the fixed evaluation arrays exactly.
5. `src/experiments/build_q1_reinforcement_evidence.py::_thresholds` pools the 20 calibration draws over the ten `(split_seed,model_seed)` runs into 200 draws per `(environment,dimension,model)` and calibrates the listed distributional sensors. `_fire_matrix(..., item_aligned=True)` then applies those thresholds to same-item intervention rows from the frozen expansion evidence.
6. `src/experiments/build_q1_adversarial_evidence.py::score_gate_a` applies the same clean-resample calibration vectors and thresholds to the same-item matched-control and adaptive Gate A rows.

In notation, for fixed frozen evaluation batch `E` and a held-out clean draw `B`:

- frozen null: `S_null = s(E, B)`;
- frozen feature intervention: `S_attack = s(E, T(E))`;
- exact identity control: `S_identity = s(E, E)`.

The first two expressions use the same sensor function but not the same sampling/editing geometry.

## Sensor audit

| sensor | calibration reference | calibration current | attack reference | attack current | paired/unpaired | geometry matched? | consequence |
|---|---|---|---|---|---|---|---|
| `integrity_jsd_vs_clean_eval` | fixed `X_te_f` feature distributions | clean-resample `X_b` feature distributions | fixed `X_te_f` feature distributions | `T(X_te_f)` feature distributions | null unpaired; attack same-item, distributional statistic | **No** | Detection can include sensitivity to editing a clustered empirical measure rather than only a clean-vs-intervened change under resampling. |
| `integrity_mmd_vs_clean_eval` | fixed `X_te_f` feature multiset | clean-resample `X_b` feature multiset | fixed `X_te_f` feature multiset | `T(X_te_f)` feature multiset | null unpaired; attack same-item, distributional statistic | **No** | The unbiased RBF MMD is computed consistently, but its two samples have different dependence/overlap relationships across null and attack. |
| `integrity_ks_reject05_vs_clean_eval` | fixed `X_te_f`, feature by feature | clean-resample `X_b` | fixed `X_te_f`, feature by feature | `T(X_te_f)` | null unpaired; attack same-item, distributional statistic | **No** | Tight repeated/near-repeated values in `X_te_f` can make a very small in-place edit separate empirical CDF mass that a fresh clean batch preserves. |
| `integrity_score_jsd_vs_clean_eval` | scores `f(X_te_f)` | scores `f(X_b)` | scores `f(X_te_f)` | scores `f(T(X_te_f))` | null unpaired; attack same-item, distributional statistic | **No** | Score-response rates inherit the same reference/current geometry mismatch. |
| `integrity_pred_pos_rate_shift` | positive prediction rate on `X_te_f` | positive prediction rate on `X_b` | positive prediction rate on `X_te_f` | positive prediction rate on `T(X_te_f)` | null unpaired; attack same-item, aggregate statistic | **No** | The rate statistic is aggregate, but null variability and intervention response arise from different batch relationships. |
| `integrity_pred_jsd` | predicted-class distribution on `X_te_f` | predicted-class distribution on `X_b` | predicted-class distribution on `X_te_f` | predicted-class distribution on `T(X_te_f)` | null unpaired; attack same-item, aggregate statistic | **No** | Same consequence as prediction-rate shift. It is not an item-wise comparison despite receiving arrays in row order. |
| `integrity_label_prior_shift` | label rate on `y_te_f` | label rate on `y_b` | label rate on `y_te_f` | label rate on `y_eval` | null unpaired; feature attacks preserve the same labels | **No** for calibration geometry; not relevant to feature-side response | For feature attacks this score is exactly zero. Label-only structural results do not need to be rerun for M1. |
| `integrity_label_jsd` | label distribution on `y_te_f` | label distribution on `y_b` | label distribution on `y_te_f` | label distribution on `y_eval` | null unpaired; feature attacks preserve the same labels | **No** for calibration geometry; not relevant to feature-side response | For feature attacks this score is exactly zero. |
| `integrity_confusion_profile_l1` | aggregate PMF of `(y_te_f,f(X_te_f))` | aggregate PMF of `(y_b,f(X_b))` | aggregate PMF of `(y_te_f,f(X_te_f))` | aggregate PMF of `(y_eval,f(X_eval))` | null unpaired; attack same-item at input level, aggregate statistic | **No** | The aggregate joint-outcome response inherits both label-composition and feature-edit geometry differences. |
| `integrity_confusion_profile_jsd` | aggregate PMF of `(y_te_f,f(X_te_f))` | aggregate PMF of `(y_b,f(X_b))` | aggregate PMF of `(y_te_f,f(X_te_f))` | aggregate PMF of `(y_eval,f(X_eval))` | null unpaired; attack same-item at input level, aggregate statistic | **No** | Same consequence as the L1 confusion-profile response. |
| `integrity_pred_disagreement` | not calibrated on clean resamples | not defined item-wise because `X_b` has different item identities | predictions on `X_te_f` | predictions on `T(X_te_f)` | exact same-item | **Yes within its declared exact item-aligned mode** | Correctly excluded from the batch-level clean-resample null; exact zero under Identity and positive only when an item's prediction changes. |
| `integrity_confusion_profile_l1_delta`, `integrity_confusion_profile_jsd_delta` | declared exact trusted aggregate, not calibrated on unaligned draws | not used as a clean-resample null | trusted clean same-batch aggregate | current same-batch aggregate | same-batch aggregate | **Yes within the declared trusted-reference mode** | Exact-zero reference semantics are separate from the calibrated batch-level sensitivity. |
| `label_flip_rate` | not calibrated on clean resamples | item correspondence unavailable | `y_te_f` | same-item `y_eval` | exact same-item | **Yes within its declared exact item-aligned mode** | Zero for every feature-side intervention; label-only blind-region claims remain structural and outside the new gate. |

## Attack/control construction audit

| construction | frozen input/current construction | relationship to calibrated null |
|---|---|---|
| `CleanResample` | `X_b,y_b` sampled from a held-out pool half; reference remains fixed `X_te_f,y_te_f` | This **is** the unpaired clean-resample null geometry. |
| `IdentityAttack` | exact copies `X_te_f,y_te_f` | Same-item exact control, deliberately distinct from clean resampling. All calibrated scores, prediction disagreement, confusion-profile deltas and label response are zero in all 600 published identity rows (maximum absolute value `0`). |
| `TinyGaussianNoise` (`sigma=0.001`) | independent entry-wise noise added to `X_te_f`; labels copied | Same-item edit; geometry does **not** match the unpaired null. |
| `TinyScalingDrift` (`alpha=0.001`) | `X_te_f * 1.001`; labels copied | Same-item edit; geometry does **not** match the unpaired null. |
| `MeanShift` | one seeded normal offset per feature added to every row of `X_te_f`; labels unchanged | Same-item edit; geometry does **not** match the unpaired null. |
| `ScalingDrift` | `X_te_f * (1+alpha)`; labels unchanged | Same-item edit; geometry does **not** match the unpaired null. |
| `FeatureDropout` | seeded entry mask on `X_te_f`, filled by the attacked batch's per-feature median; labels unchanged | Same-item edit; geometry does **not** match the unpaired null. |
| Gate A matched controls | frozen MeanShift and ScalingDrift on `X_te_f` | Same mismatch as the corresponding original mechanisms. |
| Gate A cluster-preserving variants | cluster mask learned from `X_te_f`; only nonclustered entries of that same batch are edited | Same-item, monitor-aware edit; geometry does **not** match the unpaired null. Its comparison with matched controls isolates the adaptive mask only within the frozen same-item design. |

## Terminology and scope consequences

- The published approximately 5% quantity is a **clean-resample false-action rate**, not an identity false-positive rate.
- The IdentityAttack result is a **paired identity response**. It is exactly zero for the sensors whose definitions are meaningful under exact same-item equality.
- The original construction remains a valid, design-specific benchmark: a protected clean same-item-set reference for attacked batches, with clean resampling used to quantify clean batch variation. The issue is comparability of the null and intervention geometries for a general sensitivity claim, not a code arithmetic error.
- The authorized follow-up must keep the original evidence untouched and add a separate sensitivity in which, for each fresh clean draw `B`, the clean statistic `s(E,B)` is paired with `s(E,T(B))`. This keeps the statistical unit, fixed reference, batch size, preprocessing, and draw construction unchanged; only `B` versus `T(B)` changes.

## Immutability check at audit time

All 96 files currently under `publication/artifact/evidence/` are byte-identical to the corresponding blobs in `paper15-q1-v1.3.4` (SHA-256 comparison, 0 missing and 0 changed). No historical evidence or manifest was modified by this audit.
