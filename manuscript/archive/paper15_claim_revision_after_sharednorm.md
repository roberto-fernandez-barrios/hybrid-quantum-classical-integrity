# Claim revision after shared-normalization and quadrant analysis

## Main correction

The original stealth ratios were computed using model-local detectability normalization. This is useful for within-model ranking, but cross-model stealth ratios require shared normalization.

After recomputing detectability with shared normalization across models within each protocol, dataset tag and projected dimension, the main ordering remains stable but the cross-model stealth ratios become more conservative.

## Updated ID ratios

QSVC-ZZ impact ratios against SVC-RBF remain:

- dim=8: 2.97x
- dim=10: 3.66x
- dim=12: 3.39x

QSVC-ZZ shared-normalized stealth ratios against SVC-RBF are:

- dim=8: 1.59x
- dim=10: 1.81x
- dim=12: 1.67x

Therefore, the paper should not claim that QSVC-ZZ has more than 2x stealth under the cross-model shared-normalized metric. The safer claim is that QSVC-ZZ remains the highest-stealth model under ID evaluation, with consistently elevated shared-normalized stealth relative to SVC-RBF.

## Updated interpretation of top stealth attacks

The aggregate top-stealth ranking includes:

- feature_sign_flip
- scaling_drift
- mean_shift
- label_flip_prior_preserving

However, the quadrant analysis separates two different phenomena.

### High-impact but detectable perturbations

Scaling drift and mean shift produce strong impact but are largely observable by feature-centric signals. These should be described as damaging and detectable, not as pure stealth attacks.

### True auditability-gap perturbations

The clearest high-impact and low-detectability cases are prior-preserving target-shift perturbations. These attacks have standard feature-centric detectability equal to zero and remain weakly detected even under the full shared-normalized signal set.

## Updated main claim

We find two complementary failure modes. First, QSVC-ZZ exhibits the strongest aggregate ID vulnerability profile among the evaluated kernels, with substantially higher impact than SVC-RBF and consistently higher shared-normalized stealth. Second, the clearest auditability-gap cases are prior-preserving target-shift perturbations, which produce material impact while remaining nearly invisible to standard feature-centric integrity signals.

## Manuscript rule

Do not use the old model-local stealth ratios as the main cross-model evidence.

Use:

- impact ratios for cross-model vulnerability;
- shared-normalized stealth ratios for cross-model stealth;
- quadrant analysis for true auditability-gap cases.
