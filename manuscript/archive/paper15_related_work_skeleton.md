# 2. Related Work - Skeleton

This section positions the paper relative to five areas: classical kernel baselines, quantum kernel methods, robustness and perturbation evaluation, drift and integrity monitoring, and benchmark auditability.

The final version should include approximately 10-20 references. Do not leave this section as generic background; every subsection should end by explaining why the current paper needs an auditability-aware benchmark protocol.

## 2.1 Classical kernel methods and SVC baselines

Support vector classifiers with kernel functions remain a standard baseline for small- and medium-scale classification problems. The RBF kernel is especially relevant because it provides a strong nonlinear classical reference point for comparing kernel-induced feature spaces.

For this paper, the SVC-RBF model serves as the classical baseline. Its role is not to represent all classical machine-learning methods, but to provide a controlled classical kernel comparator against fidelity-based quantum kernels.

References to add:

- foundational SVM / kernel methods;
- RBF kernel classification;
- kernel methods as baselines in quantum kernel papers.

Search terms:

- support vector machines kernel methods Cortes Vapnik
- RBF kernel SVC benchmark
- kernel methods machine learning reference

Gap connection:

Existing kernel baselines usually report performance or robustness, but not whether benchmark perturbations are auditable through signal-family-specific diagnostics.

## 2.2 Quantum kernel methods and QSVC

Quantum kernel methods use quantum feature maps to embed classical data into quantum Hilbert spaces. A quantum kernel is then computed from overlaps or fidelities between quantum states. QSVC models use these kernels inside a support-vector classification framework.

The main motivation for quantum kernel evaluation is that different feature maps may induce different geometries and decision boundaries. Therefore, quantum kernel benchmarks should not collapse all quantum models into a single category. Feature-map-specific analysis is necessary.

References to add:

- quantum kernel estimation;
- Havlíček-style quantum feature maps;
- fidelity quantum kernels;
- QSVC / qiskit-machine-learning references;
- quantum kernels in classification benchmarks.

Search terms:

- quantum kernel estimation supervised learning
- quantum feature maps Havlicek
- fidelity quantum kernel QSVC
- quantum kernel machine learning review
- Qiskit Machine Learning FidelityQuantumKernel QSVC

Gap connection:

Most quantum-kernel evaluations focus on predictive performance or trainability. Fewer studies evaluate whether perturbation-induced failures are visible to benchmark audit signals.

## 2.3 Quantum feature maps and benchmark sensitivity

Quantum feature maps define how classical features are encoded into quantum circuits. Small changes in feature-map design may induce different kernel matrices and therefore different robustness profiles.

This paper compares several feature-map configurations and reports a methodological finding: under the current reps=1 Qiskit configuration, Z and PauliXZ induce identical fidelity kernels. Therefore, they should be treated as one empirical kernel profile rather than independent behaviours.

References to add:

- feature-map design in quantum machine learning;
- data re-uploading / Pauli feature maps;
- expressibility and kernel concentration;
- quantum kernel alignment or effective dimension.

Search terms:

- quantum feature map design classification
- Pauli feature map quantum kernel
- quantum kernel expressibility effective dimension
- quantum kernel alignment
- quantum kernel concentration

Gap connection:

Prior work often treats feature-map selection as a performance or expressibility question. This paper adds an auditability perspective: feature maps may also differ in vulnerability and observability under perturbation.

## 2.4 Robustness, perturbations, and label noise

Robustness evaluation studies how model performance changes under perturbations, noise, corruption, distribution shift, or label errors. Label noise and prior-preserving target shifts are particularly relevant because they may alter learned or evaluated behaviour without necessarily producing obvious changes in input-feature distributions.

This paper uses structured perturbations not as operational attacks, but as controlled probes of benchmark reliability. The perturbation families include target shift, feature corruption, covariate shift, and pipeline perturbations.

References to add:

- robustness under distribution shift;
- label noise in classification;
- covariate shift and target shift;
- corruption robustness;
- benchmark perturbation suites.

Search terms:

- machine learning robustness distribution shift survey
- label noise classification survey
- covariate shift target shift machine learning
- corruption robustness benchmark
- dataset shift machine learning

Gap connection:

Robustness studies usually ask whether performance degrades. This paper additionally asks whether that degradation is visible to the benchmark's audit signals.

## 2.5 Drift detection and integrity monitoring

Drift detection methods monitor changes between reference and current data distributions. Common approaches include statistical tests, divergence measures, maximum mean discrepancy, Kolmogorov-Smirnov tests, and score-distribution monitoring.

These signals are effective for certain perturbation families, especially covariate shifts. However, feature-centric signals may be blind to target-shift perturbations if the input distribution remains unchanged.

This paper distinguishes standard feature/score-based signals from label-aware and prediction-aware signals. The results show that no single signal family dominates across all perturbation families.

References to add:

- concept drift detection;
- data drift monitoring;
- MMD two-sample testing;
- KS tests for drift;
- prediction drift and monitoring;
- ML monitoring / data quality.

Search terms:

- concept drift detection survey
- data drift monitoring machine learning
- maximum mean discrepancy two sample test
- Kolmogorov Smirnov drift detection
- machine learning monitoring prediction drift

Gap connection:

Existing drift detection work often evaluates whether a distribution changed. This paper evaluates whether harmful benchmark perturbations are observable by different signal families.

## 2.6 Benchmark reliability, reproducibility, and auditability

Benchmark reliability depends not only on reported performance, but also on whether the evaluation protocol exposes failure modes. Reproducibility work emphasizes the importance of seeds, data splits, metrics, and transparent reporting. However, benchmark auditability requires an additional question: can harmful perturbations be detected by the available evaluation signals?

This paper proposes auditability-aware benchmarking as a way to connect robustness evaluation, drift monitoring, and reproducibility.

References to add:

- benchmark reliability;
- reproducibility in ML;
- responsible benchmarking;
- evaluation methodology;
- auditability / transparency in ML systems.

Search terms:

- machine learning benchmark reliability
- reproducibility machine learning benchmark
- responsible benchmarking machine learning
- machine learning evaluation methodology
- auditability machine learning systems

Gap connection:

Prior benchmark work often emphasizes reproducibility and performance reporting. This paper adds a signal-design perspective: benchmark conclusions should be evaluated together with the observability of perturbation-induced failures.

## 2.7 Positioning of this paper

This paper combines the above areas into a single auditability-aware evaluation protocol.

The key difference from standard robustness evaluation is that this paper jointly measures:

- performance impact;
- detectability by signal family;
- shared-normalized stealth;
- true high-impact/low-detectability cases;
- high-impact but detectable cases;
- seed-unit uncertainty.

The key difference from standard quantum-kernel benchmarking is that this paper does not ask only whether one model performs better than another. It asks whether benchmark conclusions are sensitive to perturbations and whether those perturbations are observable.

The key difference from standard drift detection is that this paper does not treat detectability as sufficient. A perturbation can be detectable but irrelevant, or harmful but weakly detected. Both axes are necessary.

## 2.8 Related Work gap statement

Existing work has studied classical kernels, quantum kernels, distribution shift, drift detection, robustness, and benchmark reproducibility. However, these areas are often treated separately.

The gap addressed by this paper is the lack of an auditability-aware benchmark protocol that jointly evaluates:

1. how much a perturbation changes benchmark conclusions;
2. whether the perturbation is visible to available audit signals;
3. which signal family detects which perturbation family;
4. whether different quantum feature maps expose different auditability profiles;
5. whether cross-model stealth comparisons are normalized on a shared scale.

This paper addresses that gap by evaluating classical and quantum kernel models under structured perturbations and proposing a benchmark protocol based on impact, detectability, shared-normalized stealth, quadrant analysis, and uncertainty reporting.
