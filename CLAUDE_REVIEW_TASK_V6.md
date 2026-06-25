# Claude Code Review Task V6 - Pre-Submission Hard Review

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

- `manuscript/paper15_master_manuscript_draft_v6_claude_fixes.md`

Also inspect:

- `manuscript/paper15_master_v6_claude_fixes_audit.md`
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
  - mean shift / mean_shift_pf
  - feature dropout

## Current fixed state

Previous blockers addressed:

1. Related Work is no longer a skeleton.
2. Section 2.3 has citations.
3. Sharafaldin2018 is cited for the CICIDS-derived benchmark.
4. HuangKuengPreskill2021 is cited in the text.
5. All references are cited at least once according to a multi-citation-aware audit.
6. A formal main result table has been added.
7. Dataset characteristics are reported.
8. Seeds are reported.
9. Model hyperparameters and software versions are reported.
10. Statevector wording has been qualified because the backend is not force-wired into FidelityQuantumKernel.
11. Signal aggregation is described as the arithmetic mean of normalized signal responses.
12. mean_shift_pf is described as a per-feature random shift drawn from a normal distribution with mean 0 and standard deviation |delta|.
13. The 77 vs 78 pre-projection feature-column difference between ID and OOD files is disclosed and explained.
14. q_max_iter has been inferred from 168 JSON files and is consistently 1000.
15. Old model-local stealth ratio claims are removed.
16. Z/PauliXZ equivalence is explicitly handled.
17. OOD is framed as a boundary condition, not as generalization.

## Central claim

The intended final claim is:

We find two complementary failure modes.

First, QSVC-ZZ exhibits the strongest aggregate ID vulnerability profile among the evaluated kernels, with substantially higher impact than SVC-RBF and consistently higher shared-normalized stealth.

Second, the clearest auditability-gap cases are prior-preserving target-shift perturbations, which produce measurable impact while remaining nearly invisible to standard feature-centric integrity signals.

## Specific checks

1. Is the central claim supported by the current manuscript, CSVs, figures, and code?
2. Are the corrected ratios and confidence intervals consistent with the CSVs?
3. Is the formal result table correct?
4. Are all previous blockers genuinely fixed?
5. Does the statevector/backend wording still overclaim anywhere?
6. Is signal aggregation described clearly and consistently with code?
7. Is mean_shift_pf described correctly and consistently with code?
8. Is q_max_iter now reported correctly?
9. Is the 77 vs 78 feature-column difference handled adequately?
10. Is the OOD framing conservative enough?
11. Is the stealth formula sufficiently qualified as a heuristic?
12. Is prior-preserving label flip clearly framed as an evaluation-label perturbation and not an operational attack?
13. Does the proposed auditability-aware benchmark protocol constitute a real contribution?
14. Are there contradictions between manuscript, code, CSVs, supplementary notes, and figure guide?
15. What remains as a hard blocker before:
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
7. Results/table/CSV consistency.
8. Related Work and references assessment.
9. Figure selection assessment.
10. Reproducibility assessment.
11. Submission suitability:
    - workshop;
    - Q2 journal;
    - Q1 journal.
12. Exact required wording changes.
13. Final recommendation.

Be strict. Do not praise unless justified. If the paper is not ready, say exactly why.
