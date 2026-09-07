# Claude Code Review Task - Paper 1.5 Auditability Gap

You are reviewing this repository as a critical methodological reviewer.

## Mode

READ-ONLY REVIEW.

Do not edit files.
Do not create files.
Do not delete files.
Do not move files.
Do not run long experiments.
Do not install packages.
Do not format code.
Do not make commits.
Do not regenerate all results.
Do not modify the manuscript.

You may inspect files, read code, read CSV summaries, inspect figure filenames, and run lightweight commands only if necessary to understand the repository.

Your output should be a review printed in the chat/terminal, not written to disk.

## Main manuscript to review

Read first:

- `manuscript/paper15_master_manuscript_draft_v1_clean.md`

If that file does not exist, read:

- `manuscript/paper15_master_manuscript_draft_v1.md`

Also inspect:

- `manuscript/paper15_master_v1_audit_report.md`
- `manuscript/paper15_final_selected_figures.md`
- `manuscript/paper15_claim_revision_after_sharednorm.md`
- `manuscript/paper15_z_pauli_xz_equivalence_note.md`
- `manuscript/paper15_ci_statistical_support.md`
- `manuscript/paper15_ci_and_ood_disclosure_patch.md`

## Results and analysis files to inspect

Inspect:

- `results/aggregated/agg_paper_core_all_fmaps_plus_baseline.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/statistics/`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/signal_comparison/`
- `results/paper_figures/paper_core_all_fmaps_plus_baseline/`

## Code to inspect

Inspect the experimental pipeline:

- `src/experiments/run_grid.py`
- `src/experiments/run_benchmark.py`
- `src/experiments/aggregate_results.py`
- `src/experiments/make_plots.py`
- `src/experiments/signals.py`

Inspect model code:

- files related to `classical.py`
- files related to `quantum_qsvc.py`

Inspect perturbation code:

- `label_flip.py`
- `feature_sign_flip.py`
- `scaling_drift.py`
- `mean_shift.py`
- `feature_dropout.py`

Use `Get-ChildItem -Recurse src` or equivalent if paths differ.

## Central thesis

The paper is not claiming quantum advantage.

The paper is not claiming quantum models are universally worse.

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

## Known corrections already made

Please verify these corrections.

### 1. Shared normalization

Old model-local stealth ratios are no longer used as the main cross-model evidence.

Cross-model stealth uses shared-normalized detectability.

Updated QSVC-ZZ shared-normalized stealth ratios against SVC-RBF under ID:

- dim=8: 1.59x
- dim=10: 1.81x
- dim=12: 1.67x

Impact ratios remain:

- dim=8: 2.97x
- dim=10: 3.66x
- dim=12: 3.39x

### 2. Z / PauliXZ equivalence

Z and PauliXZ are treated as an equivalent kernel profile under the current reps=1 configuration.

The main paper should interpret three unique empirical quantum kernel profiles:

- QSVC-ZZ
- QSVC-PauliXYZ
- QSVC-Z/PauliXZ-equivalent

### 3. Confidence intervals

Seed-unit confidence intervals are computed over six paired seed units.

The manuscript should state that two-sided 95% confidence intervals use the Student t distribution with five degrees of freedom.

Paired ID differences QSVC-ZZ minus SVC-RBF:

Impact:

- dim=8: 0.0347, CI95 [0.0224, 0.0470]
- dim=10: 0.0437, CI95 [0.0342, 0.0532]
- dim=12: 0.0462, CI95 [0.0353, 0.0572]

Shared-normalized stealth:

- dim=8: 0.0098, CI95 [0.0045, 0.0151]
- dim=10: 0.0133, CI95 [0.0104, 0.0161]
- dim=12: 0.0143, CI95 [0.0091, 0.0194]

### 4. True auditability-gap quadrant

True auditability-gap cases are separated from high-impact but detectable perturbations.

The clearest true auditability-gap cases are prior-preserving target-shift perturbations.

Scaling drift and mean shift should be described as damaging but largely detectable.

### 5. OOD boundary condition

OOD is not the main evidence.

OOD effects are smaller and more seed-variable.

The manuscript should not claim OOD generalization.

## What I need from you

Produce a critical review with this structure:

1. Executive verdict.
2. Files inspected.
3. Is the central claim supported?
4. Are the Results consistent with the CSVs and figures?
5. Are the Methodology and Results internally consistent?
6. Are there any old claims that should be removed?
7. Is the Z/PauliXZ equivalence handled correctly?
8. Is the shared-normalized stealth framing correct?
9. Is the CI/statistical framing correct?
10. Is the OOD framing conservative enough?
11. Is the proposed auditability-aware benchmark protocol a real contribution?
12. What are the remaining blockers before submission?
13. What are minor improvements?
14. Suitability assessment:
    - workshop;
    - Q2 journal;
    - Q1 journal.
15. Exact wording changes needed.

Be strict. Assume you are reviewing for a serious ML/AI venue.

Do not focus only on missing citations. Related Work is still in skeleton form. Mention citation gaps, but focus mainly on scientific consistency and methodological defensibility.
