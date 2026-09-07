# Statistical support after seed-unit CI analysis

## Main finding

Seed-unit confidence intervals were computed over six paired seed units.

The key ID comparison is QSVC-ZZ minus SVC-RBF.

## Paired ID differences: impact

- dim=8:  mean difference = 0.0347, CI95 [0.0224, 0.0470]
- dim=10: mean difference = 0.0437, CI95 [0.0342, 0.0532]
- dim=12: mean difference = 0.0462, CI95 [0.0353, 0.0572]

All impact confidence intervals are strictly positive.

## Paired ID differences: shared-normalized stealth

- dim=8:  mean difference = 0.0098, CI95 [0.0045, 0.0151]
- dim=10: mean difference = 0.0133, CI95 [0.0104, 0.0161]
- dim=12: mean difference = 0.0143, CI95 [0.0091, 0.0194]

All shared-normalized stealth confidence intervals are strictly positive.

## Interpretation

The central ID claim is statistically supported under the current seed design. QSVC-ZZ shows consistently higher impact and higher shared-normalized stealth than SVC-RBF across all evaluated dimensions.

## OOD interpretation

OOD confidence intervals are much wider relative to the observed means and frequently include zero. This supports treating OOD as a boundary condition rather than as the main evidence.

## Manuscript wording

Use:

"Under ID evaluation, paired seed-unit comparisons show that QSVC-ZZ has consistently higher impact and shared-normalized stealth than SVC-RBF across all evaluated dimensions. The 95% confidence intervals for the ZZ-SVC paired differences remain strictly positive for both impact and shared-normalized stealth."

Avoid:

"The result generalizes under OOD."

The OOD claim should remain conservative.
