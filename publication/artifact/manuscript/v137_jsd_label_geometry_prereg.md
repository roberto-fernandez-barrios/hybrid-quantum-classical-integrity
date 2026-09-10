# Version 1.3.7: preregistered JSD correction and label-geometry closure

Frozen on **2026-09-10 at 20:22:28+02:00 (Europe/Madrid)** after the historical, pre-correction audit commit `641f84abebacce64e372180705fd1b69efc65ef5` and before any corrected JSD value or geometry-aligned label result was generated. The commit that first contains this file is the preregistration commit. Its SHA and commit timestamp will be recorded in both new evidence manifests without editing this file.

The historical audit had already established that the continuous-histogram JSD can return NaN when the current support lies wholly outside reference-only finite edges; it had also inventoried published NaNs and existing decisions. No corrected sensor output, aligned label intervention, corrected decision count, sensor ablation, or headline delta was known when this protocol was frozen.

This is a corrective scientific release, classified as **sensor-correction and label-geometry closure**. It does not overwrite or reinterpret any v1.3.6-or-earlier evidence. The work executes once under the stopping rule below; there is no second gate and no preventive v1.3.8.

## 1. Questions and stopping rule

The authorized questions are only:

1. What values and decisions change when the histogram-support defect in feature JSD and score JSD is corrected coherently?
2. What batch-level statistical response do the six existing label interventions have when their intervention geometry is aligned with the frozen clean-resample geometry?
3. Which declared sensor contributes to each response, and what survives a frozen-observation-only descriptive ablation that removes the prespecified KS-reject coordinate?
4. Which headline quantities change, and which structural, exact-reference, model, dataset, and quantum claims remain invariant?

No dataset, environment, split, row, model, feature map, kernel, preprocessing choice, sensor family, intervention, strength, seed, batch size, calibration draw, rule, endpoint, materiality definition, or reporting subset may be added, removed, selected, or tuned after results are seen. Infrastructure failures may be retried with the identical configuration and must be logged. A documented implementation bug in the new runner may be amended before rerun; any amendment must identify the failing check and preserve the failed output. Otherwise every result is published as executed, including weakened conclusions.

## 2. Frozen datasets and hashes

Only the existing staged inputs below may be read. The full raw/staged provenance remains `publication/DATASET_HASHES_v1.3.6.json`; that file and every historical manifest are immutable.

| path | SHA-256 |
|---|---|
| `data/cicids_subset.csv` | `8c8771f4e348bcbd6a58c8e215ba143d6f98a4a7a341d0e991bb8f3c211a9588` |
| `data/unsw_subset.csv` | `6292a46b03eef422acd660f68b5c76c3e04118a63d617a8e5f5b755450078780` |
| `data/ton_iot_subset.csv` | `cc6a61e9a3c294b5520cb59e8874c12929d1a91acca92f06c1ca868a5768c01b` |
| `data/processed/cicids_ood_tuesday_train.csv` | `649b5ffb6a09a89cb28f021ef8878ed990d0c5c2f2283fe1394f9b5e88a500e9` |
| `data/processed/cicids_ood_wednesday_test.csv` | `c82af0bab09f10ac46dd078c5dbab4f46e8a67fb5602dbedf4cdc3faf5a73c6d` |
| `data/processed/cicids_ood_tuesday_train_portscan.csv` | `649b5ffb6a09a89cb28f021ef8878ed990d0c5c2f2283fe1394f9b5e88a500e9` |
| `data/processed/cicids_ood_friday_portscan_test.csv` | `0e535a9942a24bb09d7b04b1d3e3e2714a182ed3f4b7d62711ef329d2d392b11` |
| `data/processed/cicids_ood_wednesday_train.csv` | `c82af0bab09f10ac46dd078c5dbab4f46e8a67fb5602dbedf4cdc3faf5a73c6d` |
| `data/processed/cicids_ood_thursday_webattacks_test.csv` | `3ec6a4d7c4b363d436088f064c43b1a0cffd72efd5825ab2a12ea1096c233674` |
| `data/processed/cicids_ood_friday_morning_test.csv` | `5c44b321468f72c3a4ef0f51135629092d253b02b7746cae64b5905a2fe89dd5` |
| `data/processed/unsw_ood_train.csv` | `993984caf61b9e60a68d9722fae9564edbd3ea91f8e2204b3ce13c26f612c350` |
| `data/processed/unsw_ood_test.csv` | `b9107599e6510ae5116d26ac952283814d80f8fdba775977893c2879a3c6cee0` |

Every job fails before model reconstruction if its applicable dataset hash differs. No CICIDS deduplication or restaging is authorized.

## 3. Frozen environments, cells, batches, and software

The corrected calibrated replay and label geometry cover all eight existing Gate N/F/A environments and all reproducible model cells, never an outcome-selected subset.

| environment | protocol/data | batch cap | frozen models/maps |
|---|---|---:|---|
| `gate2_id_256` (E1) | CICIDS ID | 256 | SVC-RBF; QSVC-ZZ r1 |
| `gate3a_ood_tue_wed` | CICIDS Tuesday/Wednesday | 128 | SVC-RBF; QSVC-ZZ r1 |
| `gate3b_ood_tue_fri_portscan` | CICIDS Tuesday/Friday-PortScan | 128 | SVC-RBF; QSVC-ZZ r1 |
| `gate3c_ood_wed_thu_webattacks` | CICIDS Wednesday/Thursday-WebAttacks | 128 | SVC-RBF; QSVC-ZZ r1 |
| `gate3d_ood_wed_fri_morning` | CICIDS Wednesday/Friday-morning | 128 | SVC-RBF; QSVC-ZZ r1 |
| `gate5a_id_unsw` | UNSW-NB15 ID | 128 | SVC-RBF; QSVC-ZZ, Z, PauliXYZ r1 |
| `gate5b_id_ton_iot` | ToN-IoT ID | 128 | SVC-RBF; QSVC-ZZ, Z, PauliXYZ r1 |
| `gate6_ood_unsw` | UNSW temporal OOD | 128 | SVC-RBF; QSVC-ZZ r1 |

Projected dimensions are exactly `8, 10, 12`; split seeds are `42, 43, 44, 45, 46`; model seeds are `42, 43`. There are 240 `(environment,dimension,split_seed,model_seed)` jobs and 600 model cells after map membership. E1 is the only 256-row environment; every other environment uses 128 rows. Any E1-versus-rest comparison is descriptive and cannot identify a batch-size effect because batch size, environment, pool overlap, and null behavior are confounded.

The replay environment is the frozen Python 3.10.16 lock: NumPy 2.2.6, pandas 2.3.3, SciPy 1.15.3, scikit-learn 1.7.2, Qiskit 2.3.0, Qiskit Aer 0.17.2, and Qiskit Machine Learning 0.9.0. BLAS thread counts are one per worker. The quantum branch remains an ideal exact-statevector fidelity-kernel instantiation; the recorded `shots=1024` configuration is metadata for the existing interface and is not a new finite-shot, noise, QPU, or hardware experiment.

## 4. Frozen split, preprocessing, and model reconstruction

For every job, use the original loader, packed seed, stratified training/evaluation index selection, held-out evaluation-side pool, and split-seed pool permutation. Fit the branch scaler on selected training rows only: `StandardScaler` for SVC-RBF and `MinMaxScaler(0,2pi)` for QSVC. No imputation, feature selection, resplit, or normalization changes.

SVC-RBF is reconstructed with `C=1`, `gamma="scale"`, `tol=1e-3`, shrinking enabled, no class weights, no probabilities, and unlimited iterations. QSVC is reconstructed with the cell's frozen feature map, one repetition, exact-statevector fidelity kernel, `C=1`, `tol=1e-3`, no class weights or probabilities, model seed as the Qiskit seed, and `max_iter=1000`. Reconstruction is deterministic replay, not model selection or tuning. Clean predictions, continuous scores, balanced accuracy, selected batch identities, and every sensor unaffected by the correction must reproduce the corresponding frozen row within `1e-9` before a job is accepted.

## 5. Corrected continuous-histogram JSD

The correction applies identically to `integrity_jsd_vs_clean_eval` and `integrity_score_jsd_vs_clean_eval`; feature JSD remains the arithmetic mean of per-feature divergences.

For each one-dimensional comparison:

1. retain finite observations and independently clip the reference and current samples to their own frozen quantiles `(0.005,0.995)`, exactly as before;
2. require both resulting samples to be non-empty;
3. construct exactly 40 shared bins with `numpy.histogram_bin_edges` from the clipped reference sample; NumPy's deterministic finite expansion for a constant reference is accepted;
4. replace the first edge by `-inf` and the last edge by `+inf`, leaving all interior reference-derived cut points unchanged;
5. call `numpy.histogram(..., density=False)` for both samples, require nonnegative finite counts and positive total mass, and divide each count vector by its own total to form PMFs `p` and `q`;
6. report `scipy.spatial.distance.jensenshannon(p,q)**2` with the SciPy default natural-log base. Thus the divergence is finite in `[0,ln(2)]`, identical inputs give zero up to floating-point tolerance, and fully separated support gives a high response rather than NaN. No pseudocount, current-to-reference clipping, density normalization over infinite bin widths, or ad hoc fallback is used.

The shared bins make the PMF-level divergence symmetric in `p,q`; the reference-anchored raw-sample procedure is intentionally directional as a drift sensor because its interior edges are defined by the declared reference. Empty/nonfinite-only inputs, invalid edges, zero histogram mass, or a nonfinite final divergence raise a validation error.

The old implementation remains identifiable through the v1.3.6 tag. A separately named legacy-reproduction entry point may retain audited-NaN-to-`-inf` behavior solely to reproduce prior releases. Every current conformal, split-conformal, augmented-score, and evidence-generation path must reject any NaN or infinity in calibration or audited sensor matrices; a current sensor NaN is never silently converted to “never fire.”

## 6. Frozen sensors, calibration, and rules

No sensor is added or removed. The calibrated coordinates remain:

- feature: feature JSD, MMD, and KS reject fraction;
- prediction: score JSD, prediction-rate shift, and prediction marginal JSD;
- label marginal: label-prior shift and label JSD;
- joint outcome: confusion-profile L1 and confusion-profile JSD.

The regimes remain `I_X` (feature), `I_XF` (feature plus prediction), `I_Ym` (label marginal), and `I_XFY` (all ten coordinates). The same-item exact aggregate and item-aligned sensors remain separate from these families.

The calibration observations are exactly the same 20 `clean_resample_calibration_01..20` draws per model cell, pooled over five split seeds and two model seeds into 200 vectors per `(environment,dimension,model)`. The 200 evaluation vectors per cell remain the same `clean_resample_eval_01..20` draws. “Frozen calibration” means the same rows, pool halves, seeds, and alpha; feature-JSD and score-JSD coordinates are rederived using the corrected definition. Every other calibration coordinate must be bitwise or numerically equal within `1e-12` to its frozen value. Per-sensor thresholds remain the 191st order statistics at `alpha=0.05` but are recomputed from those corrected coordinates where applicable.

The adopted family rule remains the full-conformal max-rank p-value with ties against firing and fire iff `p<=0.05`. The executed primary design remains descriptive because its exchangeability premise is violated; the theorem remains conditional on exchangeability. The union of the prespecified per-sensor rules remains a descriptive comparison. The v1.2 asymmetric rule remains legacy comparison only. The prior re-split sensitivity is not rerun or promoted to primary.

KS remains in every primary family. Its dominance is reported, not optimized away. A descriptive “without KS” ablation may be computed only from the same frozen/corrected per-sensor observations by removing `integrity_ks_reject05_vs_clean_eval` from `I_X`, `I_XF`, and `I_XFY` and applying the same max-rank/threshold rules. It is secondary, reported regardless of result, and cannot replace or select the primary narrative. No new KS variant is authorized.

## 7. JSD-dependent replay contract

Only quantities downstream of feature JSD or score JSD are rederived. The replay covers:

- the 26,400 frozen null/calibration/evaluation/sham observations used by Gate N/F;
- the 10,800 frozen `paper_core` intervention observations and their policy decisions;
- the 9,600 original-geometry Gate A intervention observations;
- the 13,200 v1.3.5 aligned feature-geometry observations;
- the 4,560 legacy Gate1 unique observations needed to audit sensor-decomposition/shared-normalization consequences.

The same datasets, rows, splits, models, predictions, attacks, strengths, attack seeds, calibration draws, and geometries are used. Outputs are new v1.3.7 evidence and delta tables; `gate1/`, `expansion/`, `reinforcement/`, `policy/`, `adversarial/`, and `geometry_sensitivity/` are never modified. Every corrected row records a stable old-row identifier, previous and corrected JSD values, previous and corrected per-sensor fires, family fires, union fires, and the reason for change.

The corrected replay reports every already-existing feature intervention: label flip and prior-preserving label flip, feature sign flip, mean shift, scaling drift, and feature dropout at `0.02,0.05,0.10`; identity; the two near-null controls at `0.001`; and the existing Gate A cluster-preserving mean/scaling variants at `0.02,0.05,0.10,0.25,0.50`. This list does not create a new attack or strength; it identifies the frozen rows whose downstream decisions are rederived.

## 8. Label-side aligned geometry

Let `c=(environment,dimension,split_seed,model_seed,model)`, `E_c` be the frozen evaluation batch, `C_{c,k}` the frozen calibration draws, and `B_c=clean_resample_eval_01` the same evaluation-half draw selected by v1.3.5. Calibration is `s(E_c,C_{c,k})`; the aligned clean comparator is `s(E_c,B_c)`; an aligned label intervention is

`s(E_c,T_y(B_c))`,

instead of the original `s(E_c,T_y(E_c))`.

`X_B`, predictions `f(X_B)`, and continuous scores are unchanged by the label intervention. Only labels are passed to the existing attack implementation. Each attack uses `_stable_attack_seed(model_seed, attack_tag)` exactly as in the frozen runner. The six and only six label attacks are:

- Bernoulli label flip `label_flip_r_{0.020,0.050,0.100}`;
- paired prior-preserving label flip `label_flip_prior_preserving_r_{0.020,0.050,0.100}`.

The existing Bernoulli construction, paired permutation without replacement, rounding, class-balance cap, budgets, metadata, and effective strengths are unchanged. Applying the fixed algorithm and seed to `B_c` may select different item identities than applying it to `E_c`; that is the intended geometry change, not a new attack. There are exactly `600 x 6 = 3,600` aligned label observations.

For each row record the original published response, the JSD-corrected original-geometry response, and the JSD-corrected aligned response for every sensor, union, conformal family, p-value, materiality, environment, model, strength, and attack class. Do not add item-aligned trusted sensors to a calibration family.

Separately compute constructive same-batch quantities between `(B_c,y_B,f(X_B))` and `(B_c,T_y(y_B),f(X_B))`: label mismatch, label-prior/label-JSD change, and confusion-profile L1/JSD change. A row that exactly preserves a declared aggregate remains exactly invisible to that aggregate within `1e-12`; a changed item label remains visible to the item-aligned label-mismatch check. These constructive checks are not statistical family responses and are not new structural theorems.

## 9. Endpoints, policy, decomposition, and MDE description

The label analysis answers only:

- whether original `11/2617` conformal and `43/2617` union material-label responses change under aligned geometry, and in which direction;
- the detected fraction of aggregate-separable material label interventions;
- whether structural aggregate-blind rows remain exactly invisible to the corresponding exact aggregate;
- changes in derived Gate F/D policy counts and materially altered results served;
- conclusions invariant under the geometry change.

Materiality remains the absolute signed balanced-accuracy change with primary threshold `>1e-12` and descriptive thresholds `0.02` and `0.05`. For aligned label rows it compares balanced accuracy on `(B_c,y_B)` with balanced accuracy on `(B_c,T_y(y_B))`. There is no F1/AUC endpoint, outcome-selected subset, bootstrap, new test, or power guarantee.

Sensor decomposition reports, for each existing mechanism and strength as applicable: feature JSD, MMD, KS statistic/reject fraction, score JSD, prediction marginal, label marginal, confusion L1, and confusion JSD. Required highlighted rows are tiny Gaussian, tiny scaling, mean shift, scaling drift, sign flip, dropout, Gate A matched controls, and Gate A adaptive variants. Report per-sensor response/firing and the primary family response, then the frozen-observation-only without-KS ablation.

An analytical/descriptive minimum observable confusion-profile L1 change may be derived from the frozen per-cell threshold and exact count lattice only when no additional distributional assumption is needed. It must be labeled an implied discrete threshold, not a statistical-power guarantee. If a requested derivation needs stronger assumptions, it is omitted. No intensity or batch-size sweep is run.

Gate F and D use the existing rule-to-policy mapping and the existing P0/P1/P2/P3 policies. P3 remains structurally sensor-coverage-complete with respect to declared evidence dimensions; coverage existence is not statistical power. “Cost” denotes stress-control interruption, not deployed operational cost. P2 is not presented as a deployable risk guarantee.

## 10. Required new evidence and immutability

New JSD evidence is written only below `publication/artifact/evidence/jsd_correction/`, including the already frozen historical audit and at minimum:

- `jsd_historical_nan_audit.csv`;
- `jsd_corrected_observations.csv`;
- `jsd_correction_deltas.csv`;
- `jsd_sensor_decomposition.csv`;
- `jsd_without_ks_ablation.csv`;
- `jsd_mde_description.csv` if the exact derivation is valid;
- `headline_delta.csv`;
- `jsd_correction_manifest.json`.

New label evidence is written only below `publication/artifact/evidence/label_geometry_sensitivity/`:

- `label_geometry_observations.csv`;
- `label_geometry_detection.csv`;
- `label_geometry_material.csv`;
- `label_geometry_policy_effect.csv`;
- `label_geometry_summary.csv`;
- `label_geometry_manifest.json`.

Manifests record all input/output SHA-256 hashes, row counts, the preregistration hash/commit/timestamp, dataset hashes, software contract, geometries, checks, and historical evidence tree IDs. The final report must state `V1.3.6 EVIDENCE MODIFIED: 0`, `V1.3.5 GEOMETRY EVIDENCE MODIFIED: 0`, and the exact count and hashes of new v1.3.7 files.

## 11. Headline audit fixed before results

`headline_delta.csv` and the final report compare v1.3.6, corrected-original v1.3.7 where meaningful, and final aligned v1.3.7. The audit includes, even when unchanged: feature detection ranges; near-null response; original and aligned Gate A; label `11/2617` and `43/2617`; `4496/7008`; `4390/7008`; `28--39%`; policy served/held/blocked counts; `3.25 pp`; every quantum count; every exact trusted-reference count; structural blind counts; and all numerator/denominator macros referenced by the main text or supplement. Each row gives claim, old value, new value, delta, reason, and source.

## 12. Fail-closed acceptance checks

The builders/verifiers abort unless all applicable checks pass:

1. dataset hashes, 240 jobs, 600 model cells, environments, maps, dimensions, seeds, batch caps, scalers, hyperparameters, and backend match this file;
2. clean rows, model predictions/scores, non-JSD sensors, attack metadata, budgets, and materiality reproduce frozen values within their declared tolerances before corrected rows are accepted;
3. corrected feature and score JSD are deterministic and finite for every valid finite input; no JSD NaN or infinity reaches current family calibration;
4. regression cases cover identical, fully disjoint, partially disjoint, constant-shifted, and degenerate-reference samples, PMF-level symmetry, and deterministic output;
5. the same frozen calibration/evaluation draw identifiers occur exactly once with no new draw or resplit;
6. the original, corrected-original, and aligned geometries are labeled and never pooled silently;
7. all six label attack tags exist in every expected model cell, with no other label attack or strength;
8. feature/prediction coordinates of an aligned label row equal its clean `s(E,B)` coordinates; exact same-batch aggregate-blind rows have zero response in the preserved aggregate; item label mismatch detects every nonzero flip;
9. all decisions, p-values, policy actions, decompositions, without-KS rows, and headline deltas recompute from manifested observations;
10. the preregistration file is byte-identical to its freezing commit;
11. the Git blobs under `publication/artifact/evidence/` at tag `paper15-q1-v1.3.6`, and under `publication/artifact/evidence/geometry_sensitivity/` at tag `paper15-q1-v1.3.5`, remain unchanged.

## 13. Interpretation boundary

Structural blind regions, Propositions 1--7, the R0/M0/C hierarchy, reference lattice, root-of-trust analysis, and exact C1 acceptance results are not reopened. Label-only structural results remain exactly as stated. The new label gate is a finite-design statistical sensitivity, not a theorem. Constructive exact aggregate/item/hash checks remain a third, separate evidential category.

No new dataset, environment, model, map, kernel, attack, intensity, hyperparameter, model selection, calibration campaign, KS variant, baseline, theorem, lattice, policy, endpoint, QPU/noise study, deployment experiment, or literature campaign is authorized. After successful verification, release, and green public CI, the work stops unless an objective reproducible error, portal requirement, editor request, or real reviewer request appears.
