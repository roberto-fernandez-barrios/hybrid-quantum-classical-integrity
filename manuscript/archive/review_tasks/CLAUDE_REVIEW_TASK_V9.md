# Claude Code Review Task V9 - Workshop-Ready Final Check

You are reviewing the current workshop-ready manuscript and repository as a strict reviewer.

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

- `manuscript/paper15_master_manuscript_draft_v9_workshop_ready.md`

Also inspect:

- `manuscript/paper15_master_v9_workshop_ready_audit.md`
- `manuscript/paper15_clean_performance_table.md`
- `manuscript/paper15_attack_suite_table.md`
- `manuscript/paper15_sharednorm_reproducibility_note.md`
- `src/experiments/verify_sharednorm_artifacts.py`
- `manuscript/paper15_reference_list_v2.md`
- `manuscript/paper15_final_selected_figures_v2_clean.md`
- `manuscript/paper15_reproducibility_details.md`

## Results/statistics to verify

Inspect:

- `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/table_model_vs_svc_ratios_sharednorm.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/summary_by_model_dim_protocol_sharednorm.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/statistics/ci_paired_differences_zz_minus_svc_id.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/statistics/ood_seed_variability_unique_kernel_profiles.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/true_auditability_gap_highimpact_lowdetect_sharednorm.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/highimpact_highdetect_sharednorm.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/signal_comparison/summary_signal_comparison_by_family.csv`
- `results/aggregated/agg_paper_core_all_fmaps_plus_baseline.csv`

## Current state

The manuscript now includes:

1. Clean performance table.
2. Formal main result table with separated CI columns.
3. Attack-suite table with 18 perturbations.
4. Five embedded figures with captions.
5. Exact abstract ratios:
   - impact: 2.97x, 3.66x, 3.39x;
   - shared-normalized stealth: 1.59x, 1.81x, 1.67x.
6. q_shots=1024 clarified as traceability, not operative hardware-shot setting.
7. SVC StandardScaler and QSVC MinMaxScaler [0, 2π] disclosed.
8. Scaler asymmetry acknowledged as a limitation.
9. q_max_iter=1000 verified from 168 JSON files.
10. Shared-normalized ratios verified from archived shared_norm artefacts.
11. Aggregate CSV model-local detectability columns explicitly excluded from final shared-normalized claims.
12. OOD framed as a boundary condition.
13. Z/PauliXZ equivalence handled.
14. Statevector/backend wording qualified.
15. Related Work no longer skeleton and all references cited.
16. Stealth formula explicitly qualified as a first-order diagnostic heuristic.
17. Confidence intervals described as unadjusted for multiple comparisons.

## Central claim

The intended final claim is:

We find two complementary failure modes.

First, QSVC-ZZ exhibits the strongest aggregate ID vulnerability profile among the evaluated kernels, with substantially higher impact than SVC-RBF and consistently higher shared-normalized stealth.

Second, the clearest auditability-gap cases are prior-preserving target-shift perturbations, which produce measurable impact while remaining nearly invisible to standard feature-centric integrity signals.

## Review questions

1. Is the manuscript now workshop-ready?
2. Are there any remaining hard blockers for workshop submission?
3. Are there any remaining hard blockers for Q2 journal submission?
4. Are the tables, ratios, confidence intervals, CSVs, and figures consistent?
5. Is the shared-normalized artefact explanation acceptable?
6. Is the model-local vs shared-normalized distinction clear enough?
7. Are methodology/code/results internally consistent?
8. Are there remaining overclaims?
9. What exact wording changes are still required?
10. What should be done before Q2/Q1 submission?

## Output format

Give a strict review with:

1. Executive verdict.
2. Files inspected.
3. Remaining hard blockers.
4. Remaining soft issues.
5. Claim support assessment.
6. Methodology/code/results consistency.
7. Table and figure assessment.
8. Reproducibility assessment.
9. Related Work assessment.
10. Submission suitability:
    - workshop;
    - Q2 journal;
    - Q1 journal.
11. Exact required wording changes.
12. Final recommendation.

Be strict. Do not praise unless justified.
