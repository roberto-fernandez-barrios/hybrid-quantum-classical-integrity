# 7. Proposed Auditability-Aware Benchmark Protocol

The previous results show that robustness alone is insufficient to characterize benchmark reliability. A perturbation may degrade performance while being either clearly observable or weakly reflected by the available audit signals. Conversely, some perturbations may be highly detectable but not especially damaging. For this reason, benchmark evaluation should report impact and detectability jointly.

We propose an auditability-aware benchmark protocol designed for classical and quantum kernel evaluation. The protocol is defensive and methodological: it is intended to help researchers identify when benchmark conclusions are sensitive to perturbations that are not adequately captured by standard integrity or drift signals.

## 7.1 Principle 1: Report clean performance as a baseline, not as reliability evidence

Clean performance is necessary but not sufficient. A model can perform well under clean evaluation while exposing a large vulnerability surface under structured perturbations.

Therefore, clean accuracy, balanced accuracy, ROC-AUC, and F1 should be reported only as the baseline operating point. They should not be interpreted as evidence of benchmark reliability unless accompanied by perturbation impact and detectability analysis.

## 7.2 Principle 2: Disaggregate models and feature maps

For quantum-kernel benchmarks, results should not be collapsed into a single "quantum" category. Different quantum feature maps may induce different kernel geometries and therefore different robustness and auditability profiles.

The benchmark should report results by concrete model configuration. If two feature-map configurations induce identical or empirically indistinguishable kernels, this equivalence should be reported explicitly. In the current study, Z and PauliXZ induce identical fidelity kernels under the reps=1 configuration, so the main feature-map interpretation is based on three unique empirical profiles: ZZ, PauliXYZ, and Z/PauliXZ-equivalent.

## 7.3 Principle 3: Evaluate perturbation families, not only isolated perturbations

A benchmark should include perturbations from multiple families because different perturbation families are captured by different audit signals.

At minimum, an auditability-aware benchmark should include:

- target-shift perturbations;
- feature corruption perturbations;
- covariate-shift perturbations;
- pipeline or preprocessing perturbations.

The current results show that this distinction is essential. Prior-preserving target-shift perturbations create the clearest high-impact and low-detectability cases, while scaling and mean-shift perturbations are damaging but largely detectable by feature-centric signals.

## 7.4 Principle 4: Measure impact explicitly

For each perturbation, the benchmark should measure performance degradation relative to the corresponding clean baseline.

The primary impact metric should be robust to class imbalance. In this work, balanced-accuracy impact is used as the main metric:

impact = clean balanced accuracy - perturbed balanced accuracy

ROC-AUC impact and positive-class F1 impact can be reported as secondary metrics.

A perturbation should not be called relevant only because it changes the input distribution. It should also be assessed by its effect on model behaviour.

## 7.5 Principle 5: Measure detectability by signal family

Detectability should not be treated as a single monolithic quantity. Different signal families capture different failure modes.

We recommend reporting at least two signal groups.

### Standard feature/score-based signals

These include:

- feature-distribution JSD;
- MMD;
- KS rejection rate;
- score-drift JSD.

These signals are especially useful for detecting covariate-shift and input-distribution changes.

### Label-aware and prediction-aware signals

These include:

- label-prior shift;
- label-distribution JSD;
- predicted-positive-rate shift;
- prediction-disagreement rate;
- prediction-distribution JSD;
- confusion-profile shift.

These signals are necessary for target-shift and behavioural perturbations that may not be visible in the feature distribution.

The current results show why this matters: standard signals are blind to target-shift perturbations on average, while label-aware and prediction-aware signals partially close this gap. Conversely, covariate shifts are better detected by standard feature-centric signals.

## 7.6 Principle 6: Use shared normalization for cross-model detectability

When detectability scores are compared across models, signal normalization must use a shared reference. If normalization is performed separately for each model, identical raw signal values may map to different normalized detectability scores, making cross-model stealth ratios difficult to interpret.

For cross-model comparisons, we recommend normalizing audit signals jointly across models within the same protocol, dataset tag, and projected dimension. The model identifier should not be included in the normalization group.

Model-local normalization can still be useful for within-model diagnostic ranking, but shared normalization should be used for cross-model stealth claims.

## 7.7 Principle 7: Compute stealth, but do not rely on stealth alone

A scalar stealth score is useful for ranking perturbations, but it should not be the only evidence for an auditability gap.

We define shared-normalized stealth as:

stealth = impact × (1 - shared-normalized detectability)

This penalizes perturbations that are highly detectable. However, if impact is very large, a perturbation may still rank highly even when detectability is also substantial.

Therefore, stealth rankings should always be accompanied by an impact-detectability map.

## 7.8 Principle 8: Separate true auditability gaps from damaging but detectable perturbations

The benchmark should explicitly distinguish two cases:

### True auditability gap

A true auditability-gap perturbation has:

- high impact;
- low detectability.

These are the most concerning cases because they can alter benchmark conclusions while leaving weak evidence in audit signals.

### High-impact but detectable perturbation

A high-impact but detectable perturbation has:

- high impact;
- high or moderate detectability.

These perturbations are still important for robustness evaluation, but they are less problematic from an auditability perspective because the audit signals provide evidence of the change.

In the current study, prior-preserving target-shift perturbations form the clearest true auditability-gap cases. Scaling drift and mean shift produce strong impact but are largely detectable, so they should be interpreted as damaging but observable.

## 7.9 Principle 9: Treat OOD as a boundary condition unless multiple OOD settings are tested

OOD evaluation is important, but a single OOD split should not be overinterpreted. If only one temporal or file-based OOD pair is evaluated, OOD should be reported as a boundary condition rather than as evidence of broad generalization.

In this work, the Tuesday-to-Wednesday OOD protocol shows much smaller absolute stealth effects, and confidence intervals frequently include zero. This supports a conservative interpretation: the strongest evidence is concentrated in the controlled ID audit setting.

## 7.10 Principle 10: Report uncertainty

Impact and stealth should be reported with uncertainty estimates. At minimum, seed-unit confidence intervals should be provided for the main model comparisons.

In the current study, paired seed-unit confidence intervals show that QSVC-ZZ has consistently higher ID impact and shared-normalized stealth than SVC-RBF across dimensions 8, 10, and 12. Reporting these intervals is essential because several observed differences are small in absolute value.

## 7.11 Recommended reporting checklist

An auditability-aware benchmark should report:

1. Clean performance by model and dimension.
2. Perturbation impact by model, dimension, and attack family.
3. Detectability by signal family.
4. Shared-normalized stealth for cross-model comparison.
5. Impact-detectability quadrant analysis.
6. Top true auditability-gap perturbations.
7. High-impact but detectable perturbations.
8. Feature-map equivalences or collapsed kernel profiles.
9. OOD results as boundary conditions when only one OOD pair is used.
10. Seed-unit confidence intervals for main comparisons.

## 7.12 Summary

The main methodological recommendation is that benchmark reliability should be evaluated using three axes:

- performance under clean evaluation;
- robustness under perturbation;
- auditability of the perturbation response.

A benchmark that reports only clean performance and robustness may miss high-impact perturbations that leave weak evidence in standard audit signals. Conversely, a benchmark that reports only drift or integrity signals may overemphasize detectable distribution changes that do not materially affect conclusions.

The proposed protocol addresses this by requiring joint reporting of impact, detectability, stealth, and signal-family coverage. This is especially important for quantum-kernel benchmarks, where different feature maps can induce different vulnerability profiles and where collapsing all configurations under a single "quantum" label can obscure the relevant behaviour.
