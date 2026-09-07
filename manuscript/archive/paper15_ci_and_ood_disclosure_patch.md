# CI and OOD disclosure patch

## Confidence interval methodology

The manuscript should explicitly state how confidence intervals were computed.

Use the following wording:

"Confidence intervals are computed over six paired seed units, corresponding to three data split seeds crossed with two model seeds. For each protocol, model, projected dimension, and seed unit, metrics are first averaged across perturbations. We then report two-sided 95% confidence intervals over seed units using the Student t distribution with five degrees of freedom."

For paired QSVC-ZZ minus SVC-RBF comparisons, use:

"Paired differences are computed by matching QSVC-ZZ and SVC-RBF results by split seed and model seed. Two-sided 95% confidence intervals are then computed over the six paired differences using a Student t distribution with five degrees of freedom."

## OOD interpretation

The OOD protocol should be framed even more conservatively.

Use the following wording:

"The OOD protocol is used as a boundary condition rather than as a generalization claim. Absolute OOD effects are substantially smaller than ID effects and show high seed-to-seed variability. In particular, some OOD effects are driven by individual seed units, and confidence intervals frequently include zero. Therefore, OOD results are reported to delimit the scope of the ID findings, not to establish broad temporal robustness or auditability conclusions."

## Figure 7 correction

The old ID-vs-OOD figure should be replaced by:

`fig7_v2_id_vs_ood_sharednorm_stealth_dim12_unique_profiles_ci.png`

This figure uses:

- unique empirical kernel profiles;
- shared-normalized stealth;
- absolute stealth values, not unstable OOD ratios;
- 95% seed-unit confidence intervals.

Avoid interpreting OOD ratios against SVC-RBF because the SVC-RBF OOD denominator is close to zero.
