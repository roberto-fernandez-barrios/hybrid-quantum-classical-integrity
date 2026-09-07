# Paper 1.5 - Results checkpoint

## Status

The main experimental phase is complete.

The paper now includes:

- SVC-RBF baseline.
- QSVC-ZZ.
- QSVC-Z.
- QSVC-PauliXZ.
- QSVC-PauliXYZ.
- ID protocol.
- OOD protocol.
- dimensions 8, 10, 12 for all feature-map comparison.
- dimensions 4, 6, 8, 10, 12 for the original ZZ analysis.
- attack families: target shift, corruption, covariate shift, pipeline perturbations.
- metrics: impact, detectability, stealth.

## Main result

Quantum-kernel robustness is feature-map dependent.

The ZZ feature map exposes the strongest high-impact and high-stealth vulnerability profile under ID evaluation.

## ID evidence

Against SVC-RBF, QSVC-ZZ obtains:

- dim=8: impact ratio 2.97x, stealth ratio 2.20x.
- dim=10: impact ratio 3.66x, stealth ratio 2.51x.
- dim=12: impact ratio 3.39x, stealth ratio 2.33x.

PauliXYZ is also above the classical baseline, but less strongly than ZZ.

Z and PauliXZ are nearly equivalent in the current setup.

## OOD evidence

OOD effects are much smaller in absolute value.

Some ratios are large, especially for ZZ at dim 10 and dim 12, but they arise over near-zero classical baselines. Therefore, OOD is treated as a boundary condition, not as the main claim.

## Top stealth behaviour

The highest stealth cases are dominated by QSVC-ZZ under ID.

The strongest attacks are:

- feature_sign_flip_p_0.100
- feature_sign_flip_p_0.050
- mean_shift_pf_delta_0.100
- scaling_drift_alpha_0.050
- label_flip_prior_preserving_r_0.100

The first group indicates feature/covariate vulnerability, especially in ZZ.
The label-prior preserving attacks support the auditability-gap narrative because they can produce impact with low detectability.

## Conservative claim

The paper does not claim that quantum kernels are universally less robust.

The defensible claim is:

Quantum kernel robustness and auditability are feature-map dependent. Under controlled ID evaluation, the ZZ quantum kernel exhibits the strongest high-impact and high-stealth vulnerability profile among the evaluated kernels, while alternative quantum feature maps show milder or effectively equivalent profiles. Under OOD evaluation, absolute stealth values are substantially reduced, indicating that the phenomenon is protocol-dependent.

## Role in the thesis

This paper reinforces the thesis by showing that trustworthy quantum machine learning requires robustness and auditability analysis beyond clean accuracy and generalization. It naturally motivates the next paper on kernel-aware drift monitoring and adaptation.
