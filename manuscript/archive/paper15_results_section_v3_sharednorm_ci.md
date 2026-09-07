# 5. Results

This section evaluates whether structured perturbations can produce high-impact and low-observability failures in classical and quantum kernel benchmarks. We report three complementary quantities: performance impact, detectability, and stealth. Impact measures degradation relative to clean evaluation. Detectability summarizes the response of audit signals. Stealth combines both dimensions and is used to identify perturbations that are harmful while remaining weakly observed.

The results are interpreted under two protocols. The ID protocol provides the main controlled audit setting. The OOD protocol, based on a Tuesday-to-Wednesday split, is used as a boundary condition and is interpreted conservatively.

Unless stated otherwise, cross-model stealth comparisons use shared-normalized detectability. This avoids model-local normalization artifacts and makes stealth values comparable across models within the same protocol, dataset tag, and projected dimension.

## 5.1 Clean performance is necessary but not sufficient

Clean benchmark performance defines the operating point of each model, but it does not establish benchmark reliability. A model may perform well under clean evaluation while remaining vulnerable to structured perturbations. Conversely, a perturbation may be visible in audit signals without materially altering the benchmark conclusion.

Therefore, clean performance is treated as a baseline rather than as evidence of robustness or auditability. The remaining results evaluate how model conclusions change under perturbation and whether those changes are reflected by audit signals.

## 5.2 QSVC-ZZ shows the strongest ID impact profile

Under controlled ID evaluation, QSVC-ZZ exhibits the strongest aggregate impact profile among the evaluated kernels. Relative to SVC-RBF, its mean balanced-accuracy impact is higher across all evaluated projected dimensions.

The impact ratios of QSVC-ZZ against SVC-RBF are:

- dim=8: 2.97x
- dim=10: 3.66x
- dim=12: 3.39x

This effect is supported by paired seed-unit confidence intervals. The paired QSVC-ZZ minus SVC-RBF impact differences are:

- dim=8: 0.0347, CI95 [0.0224, 0.0470]
- dim=10: 0.0437, CI95 [0.0342, 0.0532]
- dim=12: 0.0462, CI95 [0.0353, 0.0572]

All confidence intervals are strictly positive. This supports the claim that QSVC-ZZ is consistently more affected than the classical RBF baseline under the controlled ID perturbation suite.

Recommended figure:

- `fig12_id_impact_ci_unique_kernel_profiles.png`

## 5.3 Shared-normalized stealth remains highest for QSVC-ZZ

The original model-local stealth ratios were replaced by shared-normalized stealth ratios for cross-model comparison. Under shared normalization, QSVC-ZZ remains the highest-stealth model under ID evaluation, although the cross-model ratios are more conservative than under model-local normalization.

The shared-normalized stealth ratios of QSVC-ZZ against SVC-RBF are:

- dim=8: 1.59x
- dim=10: 1.81x
- dim=12: 1.67x

The paired QSVC-ZZ minus SVC-RBF shared-normalized stealth differences are:

- dim=8: 0.0098, CI95 [0.0045, 0.0151]
- dim=10: 0.0133, CI95 [0.0104, 0.0161]
- dim=12: 0.0143, CI95 [0.0091, 0.0194]

All confidence intervals are strictly positive. The absolute stealth differences are modest, ranging from approximately 0.010 to 0.014, but they are consistent across dimensions and remain positive despite the fact that QSVC-ZZ perturbations are also more detectable on average.

This distinction is important: QSVC-ZZ is not stealthier because it is less observable in all cases. Rather, its impact is sufficiently higher that its net shared-normalized stealth remains elevated relative to SVC-RBF.

Recommended figure:

- `fig13_id_sharednorm_stealth_ci_unique_kernel_profiles.png`

## 5.4 Quantum kernel behaviour is feature-map dependent

The evaluated quantum configurations do not form a homogeneous group. QSVC-ZZ, QSVC-PauliXYZ, and QSVC-Z/PauliXZ-equivalent show different aggregate vulnerability profiles.

A circuit-level sanity check showed that Z and PauliXZ induce identical fidelity kernels under the current Qiskit reps=1 configuration. Therefore, they are not interpreted as independent feature-map behaviours. The main feature-map comparison is based on three unique empirical quantum kernel profiles:

- QSVC-ZZ
- QSVC-PauliXYZ
- QSVC-Z/PauliXZ-equivalent

The resulting hierarchy under ID evaluation is consistent:

- QSVC-ZZ shows the strongest impact and shared-normalized stealth.
- QSVC-PauliXYZ shows an intermediate profile.
- QSVC-Z/PauliXZ-equivalent shows a milder profile.

This supports a feature-map-specific interpretation: robustness and auditability should not be attributed to a single generic "quantum" category.

Recommended figures:

- `fig2_v2_id_attack_impact_unique_kernel_profiles.png`
- `fig3_v2_id_sharednorm_stealth_unique_kernel_profiles.png`
- `fig4_v2_id_sharednorm_stealth_ratio_unique_kernel_profiles.png`

These figures can be used as supplementary if the CI figures are used as the main evidence.

## 5.5 True auditability-gap cases differ from high-impact detectable perturbations

A scalar stealth ranking alone is insufficient to distinguish true auditability gaps from high-impact perturbations that are also highly detectable. To address this, we perform an impact-detectability quadrant analysis using shared-normalized detectability.

The high-impact threshold is defined as the 75th percentile of ID impact. The low-detectability threshold is defined as the 25th percentile of ID shared-normalized detectability.

Under this criterion, the clearest true auditability-gap cases are prior-preserving target-shift perturbations. These cases have balanced-accuracy impacts in the range of approximately 0.055 to 0.063 while maintaining very low shared-normalized detectability, approximately 0.015 to 0.018 in the selected high-impact/low-detectability set. Their standard feature-centric detectability is zero.

In contrast, scaling drift and mean shift produce high impact but are largely detectable. For example, high-impact scaling-drift cases reach detectability values around 0.74 to 0.81. These perturbations are damaging, but they are not the clearest auditability-gap cases because audit signals strongly reflect them.

Therefore, the paper distinguishes two failure modes:

1. High-impact but detectable perturbations, such as scaling drift and mean shift.
2. True auditability-gap perturbations, dominated by prior-preserving target shift.

Recommended figure:

- `fig11_id_auditability_map_sharednorm.png`

## 5.6 Signal-family analysis explains the auditability gap

The signal-family comparison shows why the auditability gap appears. Standard feature-centric signals are effective for covariate-shift perturbations but are blind to target-shift perturbations.

Under ID evaluation, the standard feature/score signal group has zero average detectability for target-shift perturbations. Label-aware and prediction-aware signals partially close this gap. Conversely, covariate shifts are strongly detected by standard feature-centric signals but less strongly captured by label-aware and prediction-aware signals.

This means that no single signal family dominates across all perturbation families. Robust benchmark auditing should report detectability by signal family rather than relying on a single aggregate drift score.

This finding is central to the methodological contribution: the auditability gap is not only a robustness issue, but also a signal-design issue.

Recommended figure:

- `fig9_detectability_old_vs_full_by_family_id.png`

Supplementary candidates:

- `fig8_standard_vs_full_detectability_id.png`
- `fig10_top12_standard_signal_blindspots.png`

## 5.7 OOD acts as a boundary condition

The OOD protocol is interpreted conservatively. Absolute OOD effects are substantially smaller than ID effects, and several confidence intervals include zero. Therefore, OOD results are not used as the main evidence for the central claim.

The seed-level OOD analysis also shows substantial variability. For QSVC-ZZ at dimension 12, the mean OOD impact is 0.0126, but the values vary strongly across seed units:

- split=42|model=42: impact 0.0484
- split=42|model=43: impact 0.0217
- split=43|model=42: impact 0.0001
- split=43|model=43: impact 0.0000
- split=44|model=42: impact 0.0054
- split=44|model=43: impact 0.0000

The corresponding OOD impact standard deviation is 0.0194, larger than the mean itself. This indicates that the OOD effect is driven by individual seed units rather than being stable across seeds.

This reinforces the boundary-condition interpretation. The OOD protocol is useful for delimiting the controlled ID findings, but it is not sufficiently replicated to support broad distributional claims.

Recommended figure:

- `fig7_v2_id_vs_ood_sharednorm_stealth_dim12_unique_profiles_ci.png`

## 5.8 Summary of findings

The Results support the following conclusions.

First, under controlled ID evaluation, QSVC-ZZ has the strongest aggregate vulnerability profile among the evaluated kernels. This is supported by impact ratios, shared-normalized stealth ratios, and paired seed-unit confidence intervals.

Second, quantum kernel behaviour is feature-map dependent. The evaluated configurations collapse into three unique empirical kernel profiles: ZZ, PauliXYZ, and Z/PauliXZ-equivalent.

Third, the clearest true auditability-gap cases are prior-preserving target-shift perturbations. These perturbations produce measurable balanced-accuracy impact while remaining nearly invisible to standard feature-centric signals.

Fourth, damaging perturbations are not always stealthy. Scaling drift and mean shift produce large impact but are largely detectable.

Fifth, signal design matters. Standard feature-centric signals detect covariate shift but miss target shift, while label-aware and prediction-aware signals partially close that gap.

Sixth, OOD results should be interpreted conservatively. The OOD protocol shows smaller and highly variable effects and is therefore used as a boundary condition rather than as primary evidence.

Together, these findings support the proposed auditability-aware benchmark protocol: benchmark reliability should be evaluated through clean performance, perturbation impact, signal-family-specific detectability, shared-normalized stealth, quadrant analysis, and uncertainty reporting.
