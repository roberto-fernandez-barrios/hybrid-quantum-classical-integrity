# 6. Results

This section evaluates whether structured perturbations can produce high-impact and low-observability failures in classical and quantum kernel models. We report three complementary quantities: performance impact, detectability, and stealth. Impact measures the degradation induced by a perturbation, detectability summarizes the response of the audit signals, and stealth combines both dimensions to highlight perturbations that are harmful while remaining weakly observed.

The analysis focuses on two protocols. The ID protocol evaluates controlled perturbations over the same distributional setting used for the clean benchmark. The OOD protocol evaluates a Tuesday-to-Wednesday split and is used as a boundary condition to assess whether the observed vulnerability profiles persist under distributional shift.

## 6.1 Clean performance is not sufficient to characterize reliability

The clean benchmark provides the baseline operating point for all models, but it does not fully characterize their behaviour under structured perturbations. The evaluated models include a classical SVC-RBF baseline and four quantum kernel variants: QSVC-Z, QSVC-PauliXZ, QSVC-PauliXYZ, and QSVC-ZZ.

Figure 1 reports clean balanced accuracy across projected dimensions. Clean performance should be interpreted only as a necessary baseline, not as evidence of robustness. The following sections show that models with comparable clean behaviour can expose substantially different vulnerability and auditability profiles under perturbation.

## 6.2 QSVC-ZZ exhibits the strongest ID vulnerability profile

Figure 2 shows the mean balanced-accuracy impact under ID attacks across projected dimensions. QSVC-ZZ consistently exhibits the largest degradation among the evaluated models. Its average impact increases from 0.0522 at dimension 8 to 0.0655 at dimension 12. In comparison, the SVC-RBF baseline remains substantially lower, between 0.0164 and 0.0193.

Relative to SVC-RBF, QSVC-ZZ reaches an impact ratio of 2.97x at dimension 8, 3.66x at dimension 10, and 3.39x at dimension 12. This indicates that the ZZ quantum feature map exposes a considerably larger vulnerability surface under controlled ID perturbations.

PauliXYZ also exceeds the classical baseline, but less strongly than ZZ. At dimension 12, QSVC-PauliXYZ reaches an impact ratio of 1.99x relative to SVC-RBF. QSVC-Z and QSVC-PauliXZ show milder profiles, with impact ratios around 1.62x at dimension 12.

## 6.3 Stealth is feature-map dependent

Figure 3 reports the mean stealth score under ID attacks. The same ranking observed for impact is also visible in stealth. QSVC-ZZ consistently has the highest stealth score across all evaluated dimensions, increasing from 0.0281 at dimension 8 to 0.0332 at dimension 12.

Figure 4 reports stealth ratios against SVC-RBF. QSVC-ZZ remains above 2x across all dimensions, with stealth ratios of 2.20x, 2.51x, and 2.33x for dimensions 8, 10, and 12 respectively. This is the strongest evidence that the observed vulnerability is not merely a performance degradation effect, but an auditability-relevant phenomenon.

The additional quantum feature maps reveal that the effect is not homogeneous across quantum kernels. QSVC-PauliXYZ shows an intermediate stealth profile, reaching 1.57x the SVC-RBF stealth score at dimension 12. QSVC-Z and QSVC-PauliXZ show similar and milder profiles, around 1.37x at dimension 12.

A sanity check confirmed that QSVC-Z and QSVC-PauliXZ produce nearly identical aggregate results under the current configuration. Their impact profiles are identical at the reported precision, while detectability and stealth differ only by negligible numerical amounts. Therefore, they should be interpreted cautiously as effectively equivalent in this setup rather than as clearly distinct robustness profiles.

## 6.4 Top stealth attacks concentrate on structured feature and covariate perturbations

Figure 5 ranks the top stealth attacks under ID evaluation. The highest-stealth cases are dominated by QSVC-ZZ, especially under feature sign flips and covariate perturbations.

The strongest cases include:

- feature_sign_flip_p_0.100
- feature_sign_flip_p_0.050
- mean_shift_pf_delta_0.100
- scaling_drift_alpha_0.050
- label_flip_prior_preserving_r_0.100

The top-ranked attacks show that QSVC-ZZ is particularly sensitive to structured feature corruption and covariate changes. These perturbations produce substantial impact while not always being proportionally reflected by the audit signals.

Prior-preserving label flips also appear among the highest-stealth attacks across several quantum feature maps. This supports the auditability-gap argument: perturbations that preserve coarse label priors may still degrade model behaviour while remaining weakly detected by standard integrity signals.

## 6.5 OOD acts as a boundary condition

Figure 6 compares ID and OOD stealth scores at projected dimension 12. OOD stealth values are substantially smaller in absolute terms for most models. This indicates that the strongest evidence for the vulnerability profile is concentrated in the controlled ID setting.

Some quantum/classical ratios under OOD are numerically large, especially for QSVC-ZZ at dimensions 10 and 12. However, these ratios arise over near-zero classical baselines. For this reason, the OOD results should be interpreted as a boundary condition rather than as the main evidence of the paper.

The conservative interpretation is that quantum-kernel vulnerability is protocol-dependent. Under ID evaluation, QSVC-ZZ exposes a strong high-impact and high-stealth profile. Under OOD evaluation, absolute stealth scores are much smaller, and relative ratios should be interpreted cautiously.

## 6.6 Summary of findings

The results support four main findings.

First, clean performance is insufficient to characterize kernel reliability. Models with acceptable clean behaviour can expose substantially different perturbation responses.

Second, QSVC-ZZ presents the strongest vulnerability and stealth profile under ID evaluation. Its impact ratio reaches up to 3.66x relative to SVC-RBF, and its stealth ratio remains above 2x across all evaluated dimensions.

Third, quantum-kernel robustness is feature-map dependent. PauliXYZ shows an intermediate vulnerability profile, while Z and PauliXZ behave nearly equivalently under the current configuration.

Fourth, the strongest auditability gaps are attack-specific. Feature sign flips, mean shifts, scaling drifts, and prior-preserving label flips produce the most relevant high-stealth cases.

Overall, the results do not support a claim that quantum kernels are universally less robust. Instead, they support a more precise claim: quantum kernel robustness and auditability are feature-map dependent, and the ZZ feature map exposes the strongest high-impact and high-stealth vulnerability profile among the evaluated kernels under controlled ID perturbations.
