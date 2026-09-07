# Paper 1.5 assembly plan - Auditability gap paper

## Working title

Auditability Gaps in Classical and Quantum Kernel Benchmarks under Structured Perturbations

Alternative title:

Beyond Robustness: Measuring Auditability Gaps in Classical and Quantum Kernel Benchmarks

## Central thesis

This paper does not claim universal quantum advantage or universal quantum fragility.

The central thesis is:

High-impact, low-observability perturbations can materially alter benchmark conclusions while being weakly reflected by standard integrity or drift signals. Therefore, benchmark evaluation should measure not only robustness, but also auditability.

## Final core claim

We find two complementary failure modes.

First, QSVC-ZZ exhibits the strongest aggregate ID vulnerability profile among the evaluated kernels, with substantially higher impact than SVC-RBF and consistently higher shared-normalized stealth.

Second, the clearest auditability-gap cases are prior-preserving target-shift perturbations, which produce material impact while remaining nearly invisible to standard feature-centric integrity signals.

## Final paper structure

### Abstract

Status: missing.

Needs to summarize:

- benchmark reliability problem;
- auditability gap definition;
- classical/quantum kernel comparison;
- structured perturbation suite;
- main findings:
  - QSVC-ZZ strongest ID vulnerability profile;
  - Z/PauliXZ equivalence;
  - prior-preserving target shift is the clearest true auditability gap;
  - standard feature-centric signals are blind to target shift;
  - covariate shifts are damaging but detectable;
  - proposed auditability-aware benchmark protocol.

### 1. Introduction

Status: missing.

Needs to explain:

- clean benchmark scores are not enough;
- robustness alone is not enough;
- auditability gap = impact + low observability;
- why this matters for classical and quantum kernel benchmarks;
- what the paper does and does not claim;
- contributions.

Suggested contributions:

C1. Define and operationalize auditability gap as a joint impact-detectability concept.

C2. Evaluate classical and quantum kernel models under structured perturbation families.

C3. Show that QSVC-ZZ has the strongest ID vulnerability profile among evaluated kernels, supported by paired seed-unit confidence intervals.

C4. Show that prior-preserving target-shift perturbations are the clearest true auditability-gap cases because standard feature-centric signals are blind to them.

C5. Propose an auditability-aware benchmark protocol requiring impact, detectability-by-signal-family, shared normalization, and quadrant analysis.

### 2. Related Work

Status: missing.

Needs subsections:

- Quantum kernel methods and QSVC.
- Classical kernel baselines.
- Robustness evaluation and distribution shift.
- Drift and integrity monitoring.
- Benchmark auditability and reproducibility.
- Gap in prior work: robustness is usually measured separately from observability.

Needs citations later.

### 3. Problem Formulation

Status: partially covered in methodology.

Source files:

- `manuscript/paper15_methodology_audit_protocol.md`
- `manuscript/paper15_claim_revision_after_sharednorm.md`

Needs to define formally:

- clean benchmark;
- perturbation;
- impact;
- detectability;
- stealth;
- auditability gap;
- difference between robustness and auditability.

Recommended equations:

impact(a) = M_clean - M_perturbed(a)

detectability(a) = aggregate normalized audit signal response

stealth(a) = impact(a) × (1 - detectability(a))

Important note:

For cross-model comparisons, use shared-normalized detectability.

### 4. Methodology

Status: drafted.

Main source:

- `manuscript/paper15_methodology_audit_protocol.md`

Must include:

- threat model;
- ID/OOD protocols;
- models;
- perturbation families;
- impact metrics;
- detectability signals;
- shared normalization;
- stealth definition;
- quadrant analysis;
- statistical analysis;
- limitations of experimental scope.

Important additions:

- Mention Z/PauliXZ equivalence clearly.
- State that OOD is a boundary condition.
- State that statevector simulation is not hardware evidence.

### 5. Results

Status: drafted but needs revision after Claude/shared-normalization changes.

Sources:

- `manuscript/paper15_results_section_draft.md`
- `manuscript/paper15_signal_comparison_subsection.md`
- `manuscript/paper15_claim_revision_after_sharednorm.md`
- `manuscript/paper15_ci_statistical_support.md`
- `manuscript/paper15_z_pauli_xz_equivalence_note.md`

Required Results subsections:

#### 5.1 Clean performance is not sufficient to characterize reliability

Use clean performance as baseline only.

Figure candidate:

- existing clean performance figure if available.

#### 5.2 QSVC-ZZ has the strongest ID impact profile

Use updated impact evidence:

- impact ratios vs SVC:
  - dim 8: 2.97x
  - dim 10: 3.66x
  - dim 12: 3.39x

Use CI evidence:

- ZZ-SVC impact paired difference:
  - dim 8: 0.0347, CI95 [0.0224, 0.0470]
  - dim 10: 0.0437, CI95 [0.0342, 0.0532]
  - dim 12: 0.0462, CI95 [0.0353, 0.0572]

Main figure:

- `fig12_id_impact_ci_unique_kernel_profiles.png`

#### 5.3 Shared-normalized stealth confirms elevated ZZ auditability risk

Use shared-normalized stealth, not old model-local ratios.

Shared-normalized stealth ratios ZZ vs SVC:

- dim 8: 1.59x
- dim 10: 1.81x
- dim 12: 1.67x

Use CI evidence:

- ZZ-SVC shared stealth paired difference:
  - dim 8: 0.0098, CI95 [0.0045, 0.0151]
  - dim 10: 0.0133, CI95 [0.0104, 0.0161]
  - dim 12: 0.0143, CI95 [0.0091, 0.0194]

Main figure:

- `fig13_id_sharednorm_stealth_ci_unique_kernel_profiles.png`

#### 5.4 Quantum feature-map behaviour is not homogeneous

Use unique empirical profiles:

- QSVC-ZZ
- QSVC-PauliXYZ
- QSVC-Z/PauliXZ-equivalent

Do not claim four distinct quantum feature maps.

Use:

- `manuscript/paper15_z_pauli_xz_equivalence_note.md`

Figure candidates:

- `fig2_v2_id_attack_impact_unique_kernel_profiles.png`
- `fig3_v2_id_sharednorm_stealth_unique_kernel_profiles.png`
- `fig4_v2_id_sharednorm_stealth_ratio_unique_kernel_profiles.png`

But prefer CI figures in main text and move non-CI v2 figures to supplementary if space is limited.

#### 5.5 True auditability-gap cases differ from high-impact detectable perturbations

Use quadrant analysis.

Main claim:

- prior-preserving target shift is the clearest high-impact/low-detectability case;
- scaling drift and mean shift are damaging but detectable.

Source:

- `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/true_auditability_gap_highimpact_lowdetect_sharednorm.csv`
- `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/highimpact_highdetect_sharednorm.csv`

Main figure:

- `fig11_id_auditability_map_sharednorm.png`

#### 5.6 Standard and label-aware signals capture different failure modes

Use signal comparison.

Main claim:

- standard signals are blind to target shift;
- label/prediction-aware signals partially close that gap;
- feature-centric signals work better for covariate shift;
- no single signal family dominates.

Source:

- `manuscript/paper15_signal_comparison_subsection.md`

Figure candidates:

- `fig9_detectability_old_vs_full_by_family_id.png`
- `fig8_standard_vs_full_detectability_id.png`
- `fig10_top12_standard_signal_blindspots.png`

Prefer Figure 9 in main paper.

#### 5.7 OOD as a boundary condition

Use conservative wording.

Claim:

- OOD absolute stealth values are much smaller;
- many CIs include zero;
- do not claim broad OOD generalization;
- OOD supports the boundary-condition framing.

### 6. Proposed Auditability-Aware Benchmark Protocol

Status: drafted.

Source:

- `manuscript/paper15_proposed_auditability_protocol.md`

This should be one of the main contributions.

Must include checklist:

1. Report clean performance by model and dimension.
2. Report perturbation impact by family.
3. Report detectability by signal family.
4. Use shared normalization for cross-model stealth.
5. Compute stealth but also plot impact vs detectability.
6. Separate true auditability gaps from high-impact detectable perturbations.
7. Report feature-map equivalences.
8. Treat single OOD pair as boundary condition.
9. Report seed-unit confidence intervals.

### 7. Discussion

Status: missing.

Needs to discuss:

- Why QSVC-ZZ may expose stronger perturbation sensitivity.
- Why target-shift perturbations are invisible to feature-centric signals.
- Why the finding is not "quantum is bad".
- Why auditability is complementary to robustness.
- Why benchmark reporting should include signal-family coverage.

### 8. Limitations

Status: partly drafted in methodology.

Needs final dedicated section.

Limitations:

- single dataset;
- n=128 train/test;
- six seed units;
- single OOD pair;
- statevector simulation;
- no hardware noise;
- Z/PauliXZ equivalence;
- perturbation suite is controlled and not exhaustive;
- stealth metric depends on signal design.

### 9. Conclusion

Status: missing.

Needs to restate:

- auditability gap concept;
- QSVC-ZZ strongest ID vulnerability profile;
- target shift as clearest true auditability gap;
- signal-family reporting;
- proposed auditability-aware protocol.

## Main figures

Recommended main figures:

1. Clean performance by model/dim.
2. `fig12_id_impact_ci_unique_kernel_profiles.png`
3. `fig13_id_sharednorm_stealth_ci_unique_kernel_profiles.png`
4. `fig11_id_auditability_map_sharednorm.png`
5. Signal-family detectability figure:
   - `fig9_detectability_old_vs_full_by_family_id.png`
6. OOD boundary figure:
   - `fig7_id_vs_ood_stealth_dim12.png`

Optional main/supplementary:

- `fig4_v2_id_sharednorm_stealth_ratio_unique_kernel_profiles.png`
- `fig6_top12_id_stealth_attacks.png`

## Supplementary figures

Recommended supplementary:

- old model-local stealth figures;
- full top-20 stealth list;
- heatmaps;
- computational cost figures;
- Z/PauliXZ circuit equivalence note;
- per-family attack tables;
- full OOD tables.

## Files already created

- `manuscript/paper15_results_checkpoint.md`
- `manuscript/paper15_final_selected_figures.md`
- `manuscript/paper15_results_section_draft.md`
- `manuscript/paper15_signal_comparison_subsection.md`
- `manuscript/paper15_claim_revision_after_sharednorm.md`
- `manuscript/paper15_z_pauli_xz_equivalence_note.md`
- `manuscript/paper15_ci_statistical_support.md`
- `manuscript/paper15_methodology_audit_protocol.md`
- `manuscript/paper15_proposed_auditability_protocol.md`

## Critical rules for manuscript writing

Do not write:

- quantum advantage;
- quantum models are worse;
- attacks on banks;
- falsifying quantum benchmarks;
- stealth ratio >2x under shared normalization;
- four independent quantum feature maps;
- OOD generalization.

Write:

- feature-map-specific vulnerability profile;
- auditability-aware benchmark evaluation;
- high-impact/low-detectability perturbations;
- signal-family-specific detectability;
- shared-normalized stealth;
- Z/PauliXZ-equivalent profile;
- OOD boundary condition.

## Submission readiness

Experimental core: strong enough for a serious paper.

Still missing before submission:

1. Abstract.
2. Introduction.
3. Related Work.
4. Final Results rewrite using shared-normalization and CIs.
5. Discussion.
6. Limitations.
7. Conclusion.
8. Reference integration.
9. Final figure numbering and captions.
