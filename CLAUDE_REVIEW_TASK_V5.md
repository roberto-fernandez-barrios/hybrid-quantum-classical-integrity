# Claude Code Review Task V5 - Post Citation Fix Hard Review

You are reviewing the current manuscript and repository as a strict methodological reviewer.

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

You may inspect files, read source code, read CSVs, inspect figure filenames, and run lightweight read-only commands only.

Output your review in the chat/terminal only.

## Main manuscript

Read first:

- `manuscript/paper15_master_manuscript_draft_v5_citationfix.md`

Also inspect:

- `manuscript/paper15_master_v5_citationfix_audit.md`
- `manuscript/paper15_reference_list_v2.md`
- `manuscript/paper15_related_work_draft_with_refs_v2.md`
- `manuscript/paper15_final_selected_figures_v2_clean.md`
- `manuscript/paper15_main_result_table.md`
- `manuscript/paper15_dataset_characteristics.md`
- `manuscript/paper15_reproducibility_details.md`

## Results/statistics to verify

Inspect:

- `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/table_model_vs_svc_ratios_sharednorm.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/statistics/ci_paired_differences_zz_minus_svc_id.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/statistics/ci_per_seed_unique_kernel_profiles.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/statistics/ood_seed_variability_unique_kernel_profiles.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/true_auditability_gap_highimpact_lowdetect_sharednorm.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/highimpact_highdetect_sharednorm.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/signal_comparison/summary_signal_comparison_by_family.csv`

## Code paths to inspect

Find and inspect the actual files for:

- classical SVC implementation
- QSVC implementation
- signal/integrity computation
- run_benchmark
- run_grid
- attack implementations:
  - label flip
  - prior-preserving label flip
  - feature sign flip
  - scaling drift
  - mean shift
  - feature dropout

## Current state

Previous blockers addressed:

1. Related Work is no longer a skeleton.
2. Section 2.3 now has citations.
3. Sharafaldin2018 is cited for the CICIDS-derived benchmark.
4. HuangKuengPreskill2021 is cited in the text.
5. References are no longer labelled as a seed list.
6. A formal main result table has been added.
7. Dataset characteristics are reported.
8. Seeds are reported.
9. Model hyperparameters and software versions are reported.
10. Statevector wording has been qualified because the backend is not force-wired into FidelityQuantumKernel.
11. Signal aggregation is described as the arithmetic mean of normalized signal responses.
12. mean_shift_pf is described as a per-feature random shift.
13. Old model-local stealth ratio claims are removed.
14. Z/PauliXZ equivalence is explicitly handled.

## Central claim

The intended final claim is:

We find two complementary failure modes.

First, QSVC-ZZ exhibits the strongest aggregate ID vulnerability profile among the evaluated kernels, with substantially higher impact than SVC-RBF and consistently higher shared-normalized stealth.

Second, the clearest auditability-gap cases are prior-preserving target-shift perturbations, which produce measurable impact while remaining nearly invisible to standard feature-centric integrity signals.

## Check these specifically

1. Are all references cited at least once?
2. Is Section 2.3 now adequately cited?
3. Is Sharafaldin2018 cited where the CICIDS-derived benchmark is introduced?
4. Are there any uncited references?
5. Does the statevector/backend wording still overclaim?
6. Is the formal result table correct and sufficient?
7. Are the CSV values consistent with the manuscript?
8. Does Methodology describe signal aggregation clearly?
9. Does Methodology describe mean_shift_pf clearly?
10. Is OOD still framed conservatively?
11. Is the stealth formula sufficiently qualified as a heuristic?
12. Is the proposed auditability protocol still a real contribution?
13. Are there any contradictions between manuscript, code, CSVs, and figure guide?
14. What remains as a hard blocker before:
    - workshop submission;
    - Q2 journal;
    - Q1 journal?

## Output format

Give a strict review with:

1. Executive verdict.
2. Files inspected.
3. Remaining hard blockers.
4. Remaining soft issues.
5. Claim support assessment.
6. Methodology/code consistency.
7. Result table assessment.
8. Related Work and references assessment.
9. Figure selection assessment.
10. Submission suitability:
    - workshop;
    - Q2 journal;
    - Q1 journal.
11. Exact required wording changes.
12. Final recommendation.

Be strict. Do not praise unless justified.
