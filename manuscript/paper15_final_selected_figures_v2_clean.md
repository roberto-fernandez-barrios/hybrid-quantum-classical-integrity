
# Final selected figures - clean v2

This document supersedes older figure-selection notes that referenced model-local stealth ratios.

Do not use:

- `fig5_id_stealth_ratio_vs_svc.png`
- `fig3_id_stealth_by_model_dim.png` as the main stealth evidence
- any caption claiming that QSVC-ZZ remains above 2x stealth across all dimensions

The main paper should use shared-normalized and CI-based figures.

## Clean operating point

Status:
Reported as Table 1 in the manuscript. No clean performance figure is used in the workshop-ready version.

Purpose:
Reports the clean operating point. Clean performance is a baseline, not reliability evidence.

## Main Figure 2 - ID impact with confidence intervals

File:
`fig12_id_impact_ci_unique_kernel_profiles.png`

Purpose:
Shows ID balanced-accuracy impact with 95% seed-unit confidence intervals across unique empirical kernel profiles.

Main claim:
QSVC-ZZ has consistently higher impact than SVC-RBF across dimensions 8, 10, and 12.

## Main Figure 3 - ID shared-normalized stealth with confidence intervals

File:
`fig13_id_sharednorm_stealth_ci_unique_kernel_profiles.png`

Purpose:
Shows ID shared-normalized stealth with 95% seed-unit confidence intervals.

Main claim:
QSVC-ZZ remains the highest shared-normalized stealth profile under ID evaluation, with positive paired differences relative to SVC-RBF.

## Main Figure 4 - Auditability map

File:
`fig11_id_auditability_map_sharednorm.png`

Purpose:
Separates true high-impact/low-detectability auditability-gap cases from high-impact but detectable perturbations.

Main claim:
Prior-preserving target-shift perturbations are the clearest true auditability-gap cases.

## Main Figure 5 - Signal-family detectability

Preferred file:
`fig9_detectability_old_vs_full_by_family_id.png`

Purpose:
Shows that standard feature-centric signals and label/prediction-aware signals capture different failure modes.

Main claim:
Standard signals are blind to target-shift perturbations but effective for covariate shifts.

## Main Figure 6 - OOD boundary condition

File:
`fig7_v2_id_vs_ood_sharednorm_stealth_dim12_unique_profiles_ci.png`

Purpose:
Reports absolute ID vs OOD shared-normalized stealth at dimension 12 with confidence intervals.

Main claim:
OOD effects are smaller and more seed-variable, so OOD is treated as a boundary condition.

## Supplementary figures

Recommended supplementary figures:

- `fig2_v2_id_attack_impact_unique_kernel_profiles.png`
- `fig3_v2_id_sharednorm_stealth_unique_kernel_profiles.png`
- `fig4_v2_id_sharednorm_stealth_ratio_unique_kernel_profiles.png`
- `fig8_standard_vs_full_detectability_id.png`
- `fig10_top12_standard_signal_blindspots.png`
- full attack heatmaps
- computational cost figures
- Z/PauliXZ equivalence diagnostics
