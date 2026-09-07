# 6. Discussion, Limitations, and Conclusion Draft

## 6. Discussion

The results show that benchmark reliability cannot be reduced to clean performance or perturbation robustness alone. A perturbation may be harmful while remaining weakly reflected by standard audit signals, or it may be highly detectable while producing limited practical impact. This motivates an auditability-aware view of benchmark evaluation.

### 6.1 Robustness and auditability are distinct

Robustness asks how much model behaviour changes under perturbation. Auditability asks whether that change is visible to the available diagnostic signals. This distinction explains why scaling drift and mean shift should be interpreted as damaging but observable perturbations, while prior-preserving target-shift perturbations form clearer auditability-gap cases.

### 6.2 Signal design determines what can be audited

The signal-family comparison shows that standard feature-centric signals are effective for covariate shifts but insufficient for target-shift perturbations. Label-aware and prediction-aware signals partially close this gap. Therefore, detectability should be reported by signal family rather than as a single universal score.

### 6.3 Quantum kernel behaviour should be feature-map specific

The results show that quantum-kernel behaviour should not be collapsed into a generic quantum category. QSVC-ZZ shows the strongest aggregate ID vulnerability profile, QSVC-PauliXYZ shows an intermediate profile, and QSVC-Z/PauliXZ-equivalent shows a milder profile. The supported claim is feature-map-specific, not a universal claim about quantum kernels.

### 6.4 OOD as a boundary condition

The OOD protocol is useful but should not be overinterpreted. Absolute OOD effects are much smaller than ID effects and show substantial seed-to-seed variability. Therefore, OOD is used as a boundary condition rather than as the main evidence for the paper's central claim.

## 7. Limitations

The results should be interpreted within the scope of the experimental design.

First, the experiments use a single CICIDS-derived binary classification benchmark. Additional datasets are needed before making broader claims about classical or quantum kernel auditability.

Second, the benchmark uses limited train/test sizes to make classical and quantum kernel evaluation feasible under comparable conditions.

Third, the main statistical analysis uses six paired seed units, corresponding to three split seeds and two model seeds. The paired confidence intervals support the central ID claim, but a larger seed set would provide tighter uncertainty estimates.

Fourth, the OOD protocol uses one Tuesday-to-Wednesday temporal split. OOD effects are small and variable across seeds, so they are treated as a boundary condition.

Fifth, quantum models are evaluated using fidelity quantum kernels under simulation. The results should not be interpreted as claims about real quantum hardware execution, hardware noise, shot noise, or resource requirements.

Sixth, under the current Qiskit reps=1 configuration, Z and PauliXZ induce identical fidelity kernels. This equivalence is reported explicitly and the main analysis collapses them into a single empirical profile.

Seventh, the perturbation suite is controlled but not exhaustive. Other perturbation types may expose different auditability patterns.

## 8. Conclusion

This paper introduced an auditability-aware perspective on classical and quantum kernel benchmarking. The central claim is that benchmark reliability requires more than clean performance and robustness. It also requires measuring whether harmful perturbations are visible to the available audit signals.

Using a CICIDS-derived binary classification benchmark, we evaluated an RBF-kernel SVC baseline and several QSVC configurations under structured perturbation families. The results show two complementary failure modes.

First, QSVC-ZZ exhibits the strongest aggregate ID vulnerability profile among the evaluated kernels. It shows substantially higher balanced-accuracy impact than SVC-RBF and consistently higher shared-normalized stealth. Paired seed-unit confidence intervals for the QSVC-ZZ minus SVC-RBF differences remain strictly positive across the evaluated dimensions.

Second, the clearest true auditability-gap cases are prior-preserving target-shift perturbations. These perturbations produce measurable performance impact while remaining nearly invisible to standard feature-centric signals. Conversely, scaling drift and mean shift are damaging but largely detectable.

Based on these findings, we propose an auditability-aware benchmark protocol requiring clean performance reporting, perturbation impact measurement, detectability by signal family, shared normalization for cross-model stealth, impact-detectability quadrant analysis, feature-map equivalence checks, conservative OOD interpretation, and seed-unit uncertainty estimates.

The broader implication is that robust benchmarking should answer two questions at the same time: how much does a perturbation change the conclusion, and can that change be audited?
