# Claude Code Review Task V4 - Full Repository Hard Review

You are reviewing the full repository as a strict methodological reviewer.

## Mode

READ-ONLY REVIEW.

Do not edit files.
Do not create files.
Do not delete files.
Do not move files.
Do not install packages.
Do not run long experiments.
Do not regenerate results.
Do not make commits.
Do not format the manuscript.
Do not modify the repository.

You may inspect files, read source code, read CSVs, inspect figure filenames, and run lightweight read-only commands to verify claims.

Output your review in the chat/terminal only.

## Main manuscript to inspect

Read first:

- `manuscript/paper15_master_manuscript_draft_v3_refs_seeded.md`

This is the current main manuscript.

Also inspect:

- `manuscript/paper15_master_manuscript_draft_v2.md`
- `manuscript/paper15_master_v2_quick_audit.md`
- `manuscript/paper15_related_work_draft_with_refs.md`
- `manuscript/paper15_reference_seed_list.md`
- `manuscript/paper15_dataset_characteristics.md`
- `manuscript/paper15_reproducibility_details.md`
- `manuscript/paper15_final_selected_figures_v2_clean.md`
- `manuscript/paper15_claim_revision_after_sharednorm.md`
- `manuscript/paper15_z_pauli_xz_equivalence_note.md`
- `manuscript/paper15_ci_statistical_support.md`
- `manuscript/paper15_ci_and_ood_disclosure_patch.md`

## Results and statistics to inspect

Inspect:

- `results/aggregated/agg_paper_core_all_fmaps_plus_baseline.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/statistics/`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/signal_comparison/`
- `results/paper_figures/paper_core_all_fmaps_plus_baseline/`

In particular verify:

- `table_model_vs_svc_ratios_sharednorm.csv`
- `ci_paired_differences_zz_minus_svc_id.csv`
- `ci_per_seed_unique_kernel_profiles.csv`
- `ood_seed_variability_unique_kernel_profiles.csv`
- `true_auditability_gap_highimpact_lowdetect_sharednorm.csv`
- `highimpact_highdetect_sharednorm.csv`
- `summary_signal_comparison_by_family.csv`

## Code to inspect

Inspect the experimental code and actual paths. Do not assume paths from earlier prompts are correct.

Find and inspect:

- run grid / benchmark scripts
- aggregation scripts
- plotting scripts
- signal/integrity computation
- classical SVC implementation
- QSVC implementation
- perturbation implementations:
  - label flip
  - prior-preserving label flip
  - feature sign flip
  - scaling drift
  - mean shift
  - feature dropout

## Central thesis

The paper does not claim quantum advantage.

The paper does not claim quantum models are universally worse.

The paper is not an operational attack paper.

The intended claim is:

Benchmark reliability should measure not only clean performance and robustness, but also auditability. A perturbation can be harmful while remaining weakly reflected by standard integrity or drift signals.

The key concept is:

auditability gap = high impact + low observability

## Current final claim

The intended final claim is:

We find two complementary failure modes.

First, QSVC-ZZ exhibits the strongest aggregate ID vulnerability profile among the evaluated kernels, with substantially higher impact than SVC-RBF and consistently higher shared-normalized stealth.

Second, the clearest auditability-gap cases are prior-preserving target-shift perturbations, which produce measurable impact while remaining nearly invisible to standard feature-centric integrity signals.

## Known fixes already applied

Please verify whether these are truly fixed.

### B1. Related Work

The previous Related Work skeleton has been replaced by:

- `paper15_related_work_draft_with_refs.md`
- `paper15_reference_seed_list.md`

Check whether the references are appropriate, whether key areas are missing, and whether any citation claim is inaccurate or too weak.

Do not require perfect BibTeX yet, but judge whether the Related Work is now acceptable as a serious draft.

### B2. Seeds

The manuscript should disclose:

- data split seeds: 42, 43, 44
- model seeds: 42, 43
- six paired seed units

Check whether this is stated clearly.

### B3. Figure guide

The old figure document contained a retracted claim that QSVC-ZZ stealth was above 2x.

The new figure guide is:

- `paper15_final_selected_figures_v2_clean.md`

Check that old model-local figures are deprecated and that the main figures use shared-normalized and CI-based results.

### B4. Dataset characteristics

The manuscript should report:

- ID dataset: 3000 instances, 77 feature columns before projection, balanced 1500/1500
- OOD Tuesday reference/training file: 3000 instances, 78 feature columns before projection, balanced 1500/1500
- OOD Wednesday current/evaluation file: 3000 instances, 78 feature columns before projection, balanced 1500/1500
- max_train = 128
- max_test = 128
- projected dimensions: 8, 10, 12 for final comparison

Check whether these details are present and sufficient.

### B5. Hyperparameters and software

The manuscript should report:

- SVC-RBF: C=1.0, gamma='scale'
- QSVC: FidelityQuantumKernel, reps=1, statevector simulation
- Python 3.10.16
- NumPy 2.2.6
- pandas 2.3.3
- scikit-learn 1.7.2
- Qiskit 2.3.0
- Qiskit Aer 0.17.2
- qiskit-machine-learning 0.9.0

Check whether this is present and enough for reproducibility.

## Specific things to verify

1. Are old model-local stealth ratios fully removed from the main manuscript?
2. Are the corrected shared-normalized stealth ratios used consistently?
   - 1.59x
   - 1.81x
   - 1.67x
3. Are the impact ratios used correctly?
   - 2.97x
   - 3.66x
   - 3.39x
4. Is the Z/PauliXZ equivalence handled correctly?
5. Are confidence intervals described correctly?
   - two-sided 95%
   - Student t
   - five degrees of freedom
   - six paired seed units
6. Are multiple-comparison limitations acknowledged?
7. Is OOD framed as a boundary condition?
8. Are true auditability-gap cases separated from high-impact detectable perturbations?
9. Is the stealth formula appropriately qualified as a heuristic?
10. Is prior-preserving label flip described clearly as an evaluation-label perturbation?
11. Does the proposed auditability-aware benchmark protocol look like a real contribution?
12. Are there contradictions between:
    - master manuscript;
    - figure guide;
    - CSVs;
    - code;
    - supplementary notes?

## Output format

Give a strict review with these sections:

1. Executive verdict.
2. Files inspected.
3. Are B1-B5 now fixed?
4. Central claim assessment.
5. Results-vs-CSV consistency.
6. Methodology/code consistency.
7. Figure-selection consistency.
8. Related Work assessment.
9. Remaining hard blockers.
10. Remaining soft issues.
11. Exact wording changes needed.
12. Submission suitability:
    - workshop;
    - Q2 journal;
    - Q1 journal.
13. Final recommendation.

Be strict. Do not praise unless justified. If the paper is still not ready, say exactly why.
