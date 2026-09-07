# Final selected figures for Paper 1.5

## Main figures

### Figure 1 - Clean performance
Candidate:
`clean_balacc_by_model_svd__metric_bal_acc_mean__proto_id__dtag_id8c8771f4.png`

Purpose:
Show that clean performance is not enough to characterize model reliability.

### Figure 2 - ID attack impact
File:
`fig2_id_attack_impact_by_model_dim.png`

Purpose:
Show that QSVC-ZZ suffers the strongest average attack impact under ID evaluation.

### Figure 3 - ID stealth
File:
`fig3_id_stealth_by_model_dim.png`

Purpose:
Show the central auditability result: QSVC-ZZ has the largest stealth profile, while other quantum feature maps are milder.

### Figure 4 - Stealth ratio against SVC-RBF
File:
`fig5_id_stealth_ratio_vs_svc.png`

Purpose:
Quantify how much larger the stealth profile is relative to the classical RBF baseline. QSVC-ZZ remains above 2x across all evaluated dimensions.

### Figure 5 - Top stealth attacks
Preferred file:
`fig6_top12_id_stealth_attacks.png`

Fallback:
`fig6_top20_id_stealth_attacks.png`

Purpose:
Show that the strongest stealth cases are dominated by QSVC-ZZ and structured feature/covariate perturbations.

### Figure 6 - ID vs OOD boundary condition
File:
`fig7_id_vs_ood_stealth_dim12.png`

Purpose:
Show that absolute stealth scores are much smaller under OOD evaluation, supporting the interpretation that the strongest evidence is protocol-dependent and concentrated in ID.

## Supplementary figures

### Supplementary S1 - Impact ratio against SVC-RBF
File:
`fig4_id_impact_ratio_vs_svc.png`

Purpose:
Support the impact-side counterpart of the stealth ratio result.

### Supplementary S2 - Per-model heatmaps
Files:
`heatmap_stealth_by_model__metric_stealth_score_mean__*.png`

Purpose:
Detailed per-model attack-level inspection.

### Supplementary S3 - Cost figures
Files:
`time_cost_train_infer_by_model_dim__*.png`
`time_cost_audit_by_model_dim__*.png`

Purpose:
Document computational cost.

## Additional signal-comparison figures

### Figure 8 - Standard vs full detectability
File:
`fig8_standard_vs_full_detectability_id.png`

Purpose:
Shows how the full detectability score differs from the standard feature/score-based signal group under ID attacks.

### Figure 9 - Signal-family detectability by attack family
File:
`fig9_detectability_old_vs_full_by_family_id.png`

Purpose:
Shows that different perturbation families are captured by different signal groups. Standard signals detect covariate shift better, while full detectability improves target-shift and corruption coverage.

### Figure 10 - Standard-signal blindspots
File:
`fig10_top12_standard_signal_blindspots.png`

Purpose:
Ranks high-stealth cases when only standard detectability signals are used. This supports the need for label-aware and prediction-aware audit signals.

### Figure 11 - ID auditability map with shared normalization
File:
`fig11_id_auditability_map_sharednorm.png`

Purpose:
Separates high-impact/low-detectability auditability-gap cases from high-impact but detectable perturbations. This figure supports the distinction between true auditability-gap attacks, dominated by prior-preserving target shift, and damaging but observable covariate perturbations such as scaling drift and mean shift.

## Revised main figures after Z/PauliXZ equivalence

The main paper should use the v2 figures based on unique empirical kernel profiles:

### Revised Figure 2
File:
`fig2_v2_id_attack_impact_unique_kernel_profiles.png`

Purpose:
Reports ID attack impact after collapsing the equivalent Z/PauliXZ profile.

### Revised Figure 3
File:
`fig3_v2_id_sharednorm_stealth_unique_kernel_profiles.png`

Purpose:
Reports shared-normalized stealth after collapsing the equivalent Z/PauliXZ profile.

### Revised Figure 4
File:
`fig4_v2_id_sharednorm_stealth_ratio_unique_kernel_profiles.png`

Purpose:
Reports cross-model shared-normalized stealth ratios against SVC-RBF. These replace the previous model-local stealth ratio figure.

## Confidence-interval figures

### Figure 12 - ID impact with confidence intervals
File:
`fig12_id_impact_ci_unique_kernel_profiles.png`

Purpose:
Reports ID balanced-accuracy impact with 95% seed-unit confidence intervals. This figure supports the claim that QSVC-ZZ has consistently higher impact than SVC-RBF.

### Figure 13 - ID shared-normalized stealth with confidence intervals
File:
`fig13_id_sharednorm_stealth_ci_unique_kernel_profiles.png`

Purpose:
Reports ID shared-normalized stealth with 95% seed-unit confidence intervals. The QSVC-ZZ minus SVC-RBF paired differences remain positive across all evaluated dimensions.

## Revised OOD boundary figure

### Figure 7 v2 - ID vs OOD shared-normalized stealth with CIs
File:
`fig7_v2_id_vs_ood_sharednorm_stealth_dim12_unique_profiles_ci.png`

Purpose:
Replaces the previous ID-vs-OOD figure. It reports absolute shared-normalized stealth values for the unique empirical kernel profiles at dimension 12, with 95% seed-unit confidence intervals. This avoids unstable OOD ratio interpretation when the SVC-RBF OOD denominator is close to zero.

Recommended interpretation:
OOD is used as a boundary condition. Absolute OOD effects are smaller and more variable than ID effects, so OOD results should not be used as the main evidence for the central claim.
