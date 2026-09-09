# Version 1.3.5 geometry-aligned sensitivity: preregistered protocol

Frozen on **2026-09-09 at 14:42:40+02:00 (Europe/Madrid)**, after the code-only audit in `manuscript/METHOD_GEOMETRY_AUDIT_v135.md` established M1 and before any geometry-aligned intervention result was generated. The Git commit that freezes this file is the preregistration commit and will be recorded, without modifying this file, in the sensitivity manifest and release provenance.

This is the only new experiment authorized for version 1.3.5. It is a targeted sensitivity analysis. It does not replace or alter the original frozen design or any v1.3.4 evidence.

## 1. Question and stopping rule

The frozen design calibrated its batch-level sensors on `s(E,B)`, where `E` is the protected frozen evaluation batch and `B` is a distinct clean-resample batch, but evaluated feature interventions with `s(E,T(E))`. This gate asks whether the feature-side and Gate A conclusions persist when the intervention is instead evaluated as `s(E,T(B))` for the same fresh `B` whose clean statistic is `s(E,B)`.

The design below is executed once. No dataset, environment, split, model, feature map, kernel, preprocessing choice, sensor, intervention, strength, seed, batch size, rule, endpoint or reporting subset may be added, removed or tuned after results are seen. Infrastructure failures may be retried without changing configuration. A result that weakens or contradicts the original account is reported as such; there is no follow-up gate.

## 2. Frozen inputs and environments

The sensitivity uses all eight environments of Gates N and A, not an outcome-selected subset.

| environment | protocol and frozen data | max train/test | evaluated models/maps |
|---|---|---:|---|
| `gate2_id_256` | CICIDS ID, `data/cicids_subset.csv` | 256/256 | SVC-RBF; QSVC-ZZ r1 |
| `gate3a_ood_tue_wed` | CICIDS Tuesday train / Wednesday test | 128/128 | SVC-RBF; QSVC-ZZ r1 |
| `gate3b_ood_tue_fri_portscan` | CICIDS Tuesday-PortScan train / Friday-PortScan test | 128/128 | SVC-RBF; QSVC-ZZ r1 |
| `gate3c_ood_wed_thu_webattacks` | CICIDS Wednesday train / Thursday-WebAttacks test | 128/128 | SVC-RBF; QSVC-ZZ r1 |
| `gate3d_ood_wed_fri_morning` | CICIDS Wednesday train / Friday-morning test | 128/128 | SVC-RBF; QSVC-ZZ r1 |
| `gate5a_id_unsw` | UNSW-NB15 ID frozen staged table | 128/128 | SVC-RBF; QSVC-ZZ r1; QSVC-Z r1; QSVC-PauliXYZ r1 |
| `gate5b_id_ton_iot` | ToN-IoT ID frozen staged table | 128/128 | SVC-RBF; QSVC-ZZ r1; QSVC-Z r1; QSVC-PauliXYZ r1 |
| `gate6_ood_unsw` | UNSW temporal train/test frozen tables | 128/128 | SVC-RBF; QSVC-ZZ r1 |

Frozen projected dimensions are `8, 10, 12`; split seeds are `42, 43, 44, 45, 46`; model seeds are `42, 43`. The 240 `(environment,dimension,split_seed,model_seed)` jobs and their model/map membership are identical to Gates N and A. Dataset paths and SHA-256 hashes must match the frozen run metadata before a job is accepted.

The environment remains Python 3.10.16, NumPy 2.2.6, pandas 2.3.3, scikit-learn 1.7.2, Qiskit 2.3.0 and Qiskit Machine Learning 0.9.0 under the repository lock files. BLAS thread counts are fixed to one per worker. The quantum path remains the ideal exact-statevector fidelity kernel with the already evaluated feature maps. No QPU, shots/noise study or new circuit is introduced.

## 3. Frozen split, model and preprocessing replay

For every job, the runner reproduces the existing pipeline exactly:

1. load the frozen ID or OOD split with the split seed;
2. select the frozen training and evaluation indices using the packed `(split_seed,model_seed)` sequence;
3. define `E` as the frozen evaluation batch and define the held-out clean pool as the remaining evaluation-side rows;
4. partition that pool into calibration/evaluation halves with the split seed;
5. fit the frozen branch scaler on the selected training rows only: `StandardScaler` for SVC-RBF and `MinMaxScaler(0,2pi)` for every QSVC;
6. reconstruct SVC-RBF and QSVC objects with the frozen hyperparameters and model seed.

The repository did not persist the predictor objects. Their reconstruction is a **deterministic replay of the frozen configuration**, not retraining for model selection: no hyperparameter search, changed training set or new model is allowed. Before any aligned intervention row from a replay is accepted, its clean `E` metrics and the selected clean draw's published null statistics must match the corresponding frozen raw outputs within `1e-9` (with paired NaNs treated as equal).

## 4. Statistical unit and aligned geometry

Let `c=(environment,dimension,split_seed,model_seed,model)` identify a frozen model cell. Let `E_c` be its protected frozen evaluation batch. Let `C_{c,k}`, `k=1..20`, be the clean draws from the calibration half and `B_{c,k}`, `k=1..20`, the clean draws from the disjoint evaluation half, constructed by the existing `CleanResample` seeds and without-replacement sampling within each draw.

The frozen calibration statistics remain:

`V^cal_{c,k} = s(E_c, C_{c,k}),  k=1..20`.

Pooling over the five split seeds and two model seeds gives the existing 200 calibration vectors per `(environment,dimension,model)`. All 20 evaluation draws remain the clean-resample false-action evaluation:

`V^clean_{c,k} = s(E_c, B_{c,k}),  k=1..20`.

To retain the frozen intervention sample size of one attacked batch per model cell, the aligned intervention batch is fixed before results as **evaluation draw 01**:

`B_c := B_{c,1}`,

`V^attack_{c,a} = s(E_c, T_a(B_c))`.

Its paired clean comparator is the already defined `V^clean_{c,1}=s(E_c,B_c)`. Therefore calibration, clean evaluation and intervention scoring use the same statistical unit, the same fixed reference relationship and the same batch construction. Only the current batch changes from clean `B_c` to intervened `T_a(B_c)`. This produces exactly one aligned observation per original model cell and intervention: 600 observations per intervention over all environments, matching Gate A's original sample size.

The original design `s(E_c,T_a(E_c))` remains frozen and is reported separately. It is never overwritten or silently pooled with `s(E_c,T_a(B_c))`.

## 5. Identity and clean-resample controls

Two estimands are kept separate.

**Exact paired identity response.** For `T_identity(B_c)=B_c`, compute the meaningful same-item statistics as `s(B_c,B_c)`. JSD, MMD, KS statistic/rejection, score JSD, prediction-rate shift/JSD/disagreement, label-rate shift/JSD/mismatch and confusion-profile L1/JSD must be exactly zero within numerical tolerance `1e-12`.

**Clean-resample false-action response.** The 200 calibration and 200 evaluation draws per `(environment,dimension,model)` remain `s(E_c,C_{c,k})` and `s(E_c,B_{c,k})`. Their firing rate is called the **clean-resample false-action rate**, never an identity false-positive rate.

As an implementation equality check, scoring `s(E_c,T_identity(B_c))` must reproduce `s(E_c,B_c)` within `1e-12`; this equality is not reported as an exact-zero identity statistic.

## 6. Frozen sensors and decision rules

No sensor is added. The batch-level calibrated vector is:

- feature: `integrity_jsd_vs_clean_eval`, `integrity_mmd_vs_clean_eval`, `integrity_ks_reject05_vs_clean_eval`;
- prediction/score: `integrity_score_jsd_vs_clean_eval`, `integrity_pred_pos_rate_shift`, `integrity_pred_jsd`;
- label marginal: `integrity_label_prior_shift`, `integrity_label_jsd`;
- joint outcome: `integrity_confusion_profile_l1`, `integrity_confusion_profile_jsd`.

Per-sensor thresholds are the existing 191st order statistics of the 200 calibration draws at `alpha=0.05`. The adopted family decision is the existing full-conformal Max-Rank construction over the declared sensor family, with ties against firing and fire iff `p<=0.05`. The uncorrected union is retained descriptively because it is part of the frozen reporting; the superseded asymmetric 1.2.0 family rule is not an endpoint of this sensitivity.

The principal feature regimes are `I_X` (three feature sensors) and `I_XF` (feature plus prediction/score sensors). `I_Ym` and batch `I_XFY` are retained for completeness but are not used to infer feature-intervention efficacy because their clean-resample label composition can fire independently of the feature edit.

Same-item exact sensors are computed relative to `B_c` for `T_a(B_c)`: prediction disagreement, label mismatch and confusion-profile L1/JSD deltas. They are reported separately and are not inserted into the unpaired clean-resample calibration family.

## 7. Frozen interventions and seeds

No intervention is new; all objects, tags, strengths and seed derivations come from the existing runner.

- near-null: `sham_tiny_gaussian_sigma_0.001`, `sham_tiny_scaling_alpha_0.001`;
- mean shift: `mean_shift_pf_delta_{0.020,0.050,0.100}`;
- scaling drift: `scaling_drift_alpha_{0.020,0.050,0.100}`;
- feature dropout: `feature_dropout_p_{0.020,0.050,0.100}`, median fill;
- Gate A adaptive mean shift: `cluster_preserving_mean_shift_delta_{0.020,0.050,0.100,0.250,0.500}`;
- Gate A adaptive scaling: `cluster_preserving_scaling_alpha_{0.020,0.050,0.100,0.250,0.500}`.

The nonadaptive mean-shift and scaling rows at 0.02/0.05/0.10 are Gate A's matched controls. The cluster window (`0.01` batch standard deviations), minimum mass (`5%`, never fewer than two rows), constant-feature behavior and unmodified-label rule are frozen. Cluster membership is recomputed on the fresh `B_c`, as required by the existing attack definition. Each intervention uses `_stable_attack_seed(model_seed, attack_tag)`, exactly as in the frozen runner. No additional random seed is introduced.

Label-only attacks are not rerun. Their structural blind regions and exact-reference conclusions do not depend on M1.

## 8. Frozen endpoints and summaries

All endpoints are descriptive; there is no new bootstrap, hypothesis test, F1/AUC endpoint or post-hoc cutoff.

1. **Clean and identity:** per-sensor and per-regime clean-resample false-action rates; maximum absolute exact paired identity response; equality of aligned identity-copy and clean statistics.
2. **Aligned feature response:** per intervention, environment, branch, regime and adopted rule: `n`, `n_fire`, detection/response rate and the four paired clean/attack states (neither fires, clean only, attack only, both). `attack only` is the intervention-associated escalation count; it supplements rather than replaces the raw response rate.
3. **Materiality:** signed conclusion change `Delta_R = BA(B_c,y_c)-BA(T_a(B_c),y_c)`, absolute materiality at `|Delta_R|>0` (numerical tolerance `1e-12`), and the existing descriptive sensitivities at `0.02` and `0.05`. Prediction disagreement is computed item-wise between `f(B_c)` and `f(T_a(B_c))`.
4. **Near-null:** the two frozen near-null interventions, kept separate from clean resampling and exact identity.
5. **Gate A by strength:** control and adaptive response/materiality profiles for both mechanisms; all five adaptive strengths reported.
6. **Matched Gate A comparison:** at 0.02/0.05/0.10, aggregate each `(environment,split_seed,mechanism,strength,regime)` over its frozen dimensions, model seeds and available models. Report how many cells have adaptive response below, equal to or above the matched control, together with material-cell counts and pooled response/materiality. No numerical survival threshold is introduced.

The gate answers only Q1--Q7 in the task statement. It distinguishes descriptively:

- the change between original `s(E,T(E))` and aligned `s(E,T(B))` as a design-geometry effect, without a causal population claim;
- the clean-draw and attacked-batch cluster mass/frozen-entry summaries as dataset cluster structure;
- the matched control/adaptive contrast within the aligned geometry as the monitor-aware component.

These components may interact. The gate does not claim a causal decomposition beyond the matched constructions it directly evaluates.

## 9. Qualitative interpretation fixed before results

Gate A is described as corroborated by the sensitivity if the cluster-preserving variant reduces response relative to its matched control consistently across a substantial proportion of the environment/split/strength cells while retaining material conclusion changes. Exact reproduction of the original `0.96--1.00` to `0.01--0.66` ranges is neither required nor expected. The report will give the full counts and proportions rather than invent a numerical cutoff for “substantial.”

If the direction is mixed, concentrated in only part of the grid, or accompanied by little materiality, the verdict is `PARTIAL`. If the aligned comparison does not show a defensible, repeated reduction with materiality, the verdict is `NO`. Wording in the abstract and manuscript follows the observed verdict. No parameter or subset will be changed to improve it.

The sentence “calibration controls false actions but does not guarantee coverage against a monitor-aware attacker” is retained only if the aligned results show both (i) controlled clean-resample false-action behavior under the declared calibration construction and (ii) materially altered adaptive rows that evade the calibrated feature regime in the aligned design.

## 10. Fail-closed checks

The builder/verifier must reject the evidence package unless all applicable checks pass:

- the eight environments, 240 jobs, seeds, dimensions, model/map membership, data hashes, batch caps, scalers, hyperparameters and exact-statevector backend match the frozen metadata;
- every selected `B_c` is exactly `clean_resample_eval_01` under the frozen seed and pool partition;
- replayed clean `E_c` metrics and `s(E_c,B_c)` match the frozen raw row within `1e-9`;
- every observation declares `reference_geometry=fixed_frozen_E`, `current_geometry=fresh_eval_draw_01` or `intervened_fresh_eval_draw_01`, and the implementation arguments agree with that declaration;
- calibration/current and attack/current batch sizes agree within each cell;
- exact paired identity scores are at most `1e-12`, and aligned identity-copy equals the clean row within `1e-12`;
- all feature interventions preserve `y_c`; their paired label-statistic changes are zero;
- all attack tags, strengths and stable attack seeds match this preregistration;
- matched control/adaptive pairs exist for both mechanisms at 0.02/0.05/0.10 in every expected cell;
- all five adaptive strengths exist in every expected cell;
- every summary is recomputable from the manifested observation table with no missing cells;
- the preregistration file hash and preregistration commit are recorded;
- all 96 prior evidence files remain byte-identical to v1.3.4. The baseline evidence-tree SHA-256 is `0c3b001eae6a25c76566a1ca03c49332027e6edc49dc684e1552f972fe21a9d7`.

## 11. Output contract

New evidence is written only to `publication/artifact/evidence/geometry_sensitivity/` and is never merged into a historical evidence directory. Required files are:

- `geometry_audit.csv`;
- `geometry_observations.csv` (manifested cell-level source for verification);
- `geometry_null_response.csv`;
- `geometry_attack_detection.csv`;
- `geometry_near_null.csv`;
- `geometry_gateA_by_strength.csv`;
- `geometry_gateA_summary.csv`;
- `geometry_sensitivity_manifest.json`;
- corresponding LaTeX macros in the TDSC tables directory.

The manifest records input/output hashes, row counts, expected cells, replay status, all fail-closed checks, the preregistration hash and commit, and the unchanged old-evidence tree hash. The release report must state `OLD SCIENTIFIC EVIDENCE MODIFIED: 0` and the exact number of new sensitivity evidence files.

## 12. Interpretation boundaries

The original benchmark geometry is described neutrally as a **design-specific calibration geometry**: protected clean same-item-set comparisons for attacked batches and clean resampling for the null. This sensitivity tests transport to aligned fresh-batch interventions; it does not rewrite the original evidence.

No core theorem, proposition, threat class, dataset, model family, kernel, feature map, attack, title or primary structural experiment is changed by this gate. The final scientific version, if the gate executes successfully, is v1.3.5 and is described as a targeted methodological sensitivity amendment.
