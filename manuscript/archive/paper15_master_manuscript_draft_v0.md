<!--
Paper 1.5 master manuscript draft v0

Working title:
Auditability Gaps in Classical and Quantum Kernel Benchmarks under Structured Perturbations

Status:
This is an assembled draft, not the final submission version.

Known TODOs:
- Replace Related Work placeholders with real citations.
- Harmonize figure numbering.
- Add final captions.
- Check equation formatting in target journal template.
- Reduce repetition between Methodology and Proposed Protocol.
- Add references.
- Polish language.
- Confirm all figure filenames.
-->

# Auditability Gaps in Classical and Quantum Kernel Benchmarks under Structured Perturbations


# Abstract and Introduction

TODO: Missing source file `paper15_abstract_introduction_draft.md`.


# 2. Related Work

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


# 3. Problem Formulation

This paper studies benchmark reliability through three quantities: impact, detectability, and stealth.

Let \(M_{\mathrm{clean}}\) denote the clean benchmark metric and \(M_{\mathrm{perturbed}}(a)\) the same metric under perturbation \(a\). The primary impact metric is balanced-accuracy impact:

\[
\mathrm{Impact}(a) = M_{\mathrm{clean}} - M_{\mathrm{perturbed}}(a)
\]

A perturbation is considered harmful when it produces positive impact.

Detectability measures how strongly the perturbation is reflected by audit signals. We distinguish standard feature/score-based signals from label-aware and prediction-aware signals. For cross-model comparison, raw signal responses are normalized using a shared reference across models within each protocol, dataset tag, and projected dimension.

The shared-normalized stealth score is defined as:

\[
\mathrm{Stealth}(a) = \mathrm{Impact}(a) \times (1 - \mathrm{Detectability}_{\mathrm{shared}}(a))
\]

This score is high when a perturbation is both harmful and weakly detected. However, scalar stealth alone is not sufficient. Therefore, the analysis also uses an impact-detectability quadrant to separate true high-impact/low-detectability auditability gaps from high-impact but detectable perturbations.

The paper uses the term auditability gap for perturbations that produce material impact while remaining weakly reflected by available audit signals. This framing is methodological and defensive: the goal is to improve benchmark reporting, not to propose operational attacks.


# 4. Methodology

This section describes the experimental protocol used to evaluate robustness and auditability in classical and quantum kernel benchmarks. The goal is not to study adversarial optimization or deployment-time attacks, but to evaluate whether structured perturbations can alter benchmark conclusions while remaining weakly reflected by standard integrity signals.

## 4.1 Threat model and auditability setting

We consider a benchmark-audit setting in which a trained model is evaluated under clean and perturbed conditions. A perturbation is considered relevant when it produces a measurable degradation in model behaviour or changes the interpretation of the benchmark result.

The central object of study is the auditability gap: a perturbation may be harmful while being weakly observable by the available audit signals. Therefore, a benchmark should not only measure how much performance degrades, but also how clearly the perturbation is reflected by integrity, drift, label-aware, and prediction-aware signals.

This work does not frame the perturbations as operational attack recipes. Instead, they are used as controlled probes to study methodological reliability. The purpose is defensive: to identify which perturbation families are visible to standard benchmark diagnostics and which require additional audit signals.

## 4.2 Data and protocols

The experiments use a CICIDS-derived binary classification benchmark prepared for equivalent classical and quantum-kernel evaluation. All models are evaluated after projection to a fixed low-dimensional feature space, enabling direct comparison between the classical RBF kernel baseline and quantum kernel models.

Two protocols are used.

### ID protocol

The in-distribution protocol evaluates controlled perturbations in the same distributional setting used for the clean benchmark. This protocol is the main source of evidence because it isolates perturbation effects under controlled conditions.

### OOD protocol

The out-of-distribution protocol evaluates a Tuesday-to-Wednesday split. It is used as a boundary condition to assess whether vulnerability profiles persist under temporal distribution shift. Since this protocol uses a single OOD pair, OOD results are interpreted conservatively and are not used as the main evidence for the paper's central claim.

## 4.3 Models and feature maps

The classical baseline is an SVC with an RBF kernel.

The quantum models are QSVC classifiers based on fidelity quantum kernels. The evaluated feature-map configurations are:

- ZZFeatureMap
- ZFeatureMap
- PauliFeatureMap with XZ paulis
- PauliFeatureMap with XYZ paulis

A circuit-level sanity check showed that, under the current Qiskit configuration with reps=1, the Z and PauliXZ configurations induce identical fidelity kernel matrices. Therefore, the main analysis interprets the quantum results as three unique empirical kernel profiles:

- QSVC-ZZ
- QSVC-PauliXYZ
- QSVC-Z/PauliXZ-equivalent

The PauliXZ configuration is retained for transparency and reproducibility, but it is not interpreted as an independent feature-map behaviour in the main conclusions.

## 4.4 Perturbation families

The benchmark evaluates structured perturbations grouped into four main families.

### Target shift

Target-shift perturbations modify labels while preserving or altering coarse label statistics. The most important case for auditability is the prior-preserving label flip, which can affect model conclusions while leaving label-prior statistics unchanged.

### Corruption

Corruption perturbations alter feature values or feature signs. Feature sign flips are used to test sensitivity to structured feature corruption.

### Covariate shift

Covariate-shift perturbations modify the input distribution through scaling or mean-shift transformations. These perturbations test whether feature-distribution audit signals can detect input-space changes.

### Pipeline perturbations

Pipeline perturbations emulate changes in feature availability or preprocessing, such as feature dropout. These perturbations test whether benchmark conclusions are sensitive to changes in the feature-processing pipeline.

## 4.5 Impact metrics

Impact measures the degradation induced by a perturbation relative to the corresponding clean evaluation.

The primary impact metric is balanced-accuracy impact:

impact = clean balanced accuracy - perturbed balanced accuracy

Balanced accuracy is used because it is more informative than raw accuracy under class imbalance. ROC-AUC and positive-class F1 impact are computed as secondary metrics, but the main analysis focuses on balanced-accuracy impact.

## 4.6 Detectability signals

Detectability summarizes how strongly the perturbation is reflected by audit signals. Two signal groups are distinguished.

### Standard feature/score-based signals

The standard signal group contains feature-distribution and score-drift diagnostics:

- feature-distribution Jensen-Shannon divergence
- maximum mean discrepancy
- Kolmogorov-Smirnov rejection rate
- score-drift Jensen-Shannon divergence

These signals are expected to be effective for covariate and feature-distribution changes.

### Label-aware and prediction-aware signals

The second signal group contains label-aware and prediction-aware diagnostics:

- label-prior shift
- label-distribution Jensen-Shannon divergence
- predicted-positive-rate shift
- prediction-disagreement rate
- prediction-distribution Jensen-Shannon divergence
- confusion-profile L1 shift
- confusion-profile Jensen-Shannon divergence

These signals are designed to expose perturbations that are not necessarily visible in the input-feature distribution, especially target-shift and prediction-behaviour changes.

## 4.7 Shared normalization of detectability

For within-model inspection, detectability can be normalized locally. However, cross-model stealth comparisons require a shared normalization reference. Otherwise, identical raw signals may receive different normalized values depending on the model-specific normalization range.

Therefore, the main cross-model analysis uses shared signal normalization. For each protocol, dataset tag, and projected dimension, raw audit signals are normalized jointly across models. The model identifier is deliberately excluded from the normalization group.

This shared normalization is used for cross-model stealth ratios and for the final auditability map.

## 4.8 Stealth score

Stealth combines impact and detectability. A perturbation is considered more stealthy when it produces high impact while remaining weakly detected.

The shared-normalized stealth score is defined as:

stealth = impact × (1 - shared-normalized detectability)

where impact is balanced-accuracy impact and detectability is the shared-normalized aggregate detectability score.

This definition intentionally penalizes perturbations that are highly damaging but also highly observable. Therefore, stealth should be interpreted jointly with the impact-detectability scatter rather than only as a scalar ranking.

## 4.9 Auditability quadrant analysis

To distinguish true auditability-gap cases from merely high-impact perturbations, an impact-detectability quadrant analysis is performed.

The high-impact threshold is defined as the 75th percentile of ID balanced-accuracy impact. The low-detectability threshold is defined as the 25th percentile of ID shared-normalized detectability.

A true auditability-gap case is defined as a perturbation satisfying:

- impact greater than or equal to the high-impact threshold;
- detectability lower than or equal to the low-detectability threshold.

This separates high-impact/low-detectability perturbations from high-impact but detectable perturbations. In the current results, prior-preserving target-shift perturbations form the clearest auditability-gap cases, while scaling and mean-shift perturbations are high-impact but largely detectable.

## 4.10 Statistical analysis

The main statistical summaries are computed over six paired seed units. Each seed unit corresponds to a split/model-seed configuration. For each protocol, model, projected dimension, and seed unit, metrics are averaged across perturbations. Mean values and 95% confidence intervals are then computed over seed units.

For the central ID comparison, paired differences between QSVC-ZZ and SVC-RBF are computed for each projected dimension. The confidence intervals for the paired differences are used to assess whether QSVC-ZZ consistently exceeds the classical baseline in impact and shared-normalized stealth.

The OOD results are reported with the same statistical machinery, but they are interpreted as a boundary condition because the absolute effects are small and confidence intervals frequently include zero.

## 4.11 Reproducibility controls

The experimental runner stores raw outputs, aggregated summaries, configuration information, dataset hashes, model identifiers, attack identifiers, and seed information. Aggregated tables and paper-ready figures are generated from saved CSV files rather than from manually copied values.

The main paper uses:

- shared-normalized summaries for cross-model stealth comparisons;
- unique empirical kernel profiles after collapsing the Z/PauliXZ equivalence;
- seed-unit confidence intervals for ID impact and shared-normalized stealth;
- quadrant analysis for identifying true auditability-gap cases.

## 4.12 Methodological limitations

The experimental design has several limitations.

First, the feature-map comparison is performed at projected dimensions 8, 10, and 12. The original ZZ analysis includes dimensions 4, 6, 8, 10, and 12.

Second, the OOD protocol uses a single Tuesday-to-Wednesday temporal split. Therefore, OOD results are not used as the main evidence for the paper's central claim.

Third, quantum models are evaluated with fidelity kernels under statevector simulation. The results should not be interpreted as claims about hardware execution or hardware noise.

Fourth, the train/test sizes are intentionally limited to make classical and quantum-kernel evaluation feasible under equivalent conditions. The conclusions should therefore be interpreted as controlled benchmark evidence rather than large-scale deployment evidence.

Fifth, Z and PauliXZ induce identical kernels under the current reps=1 configuration. This equivalence is reported explicitly and the main feature-map interpretation is based on three unique empirical kernel profiles.

These limitations do not invalidate the auditability-gap analysis, but they define the scope of the conclusions.


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


# 6. Proposed Auditability-Aware Benchmark Protocol

The previous results show that robustness alone is insufficient to characterize benchmark reliability. A perturbation may degrade performance while being either clearly observable or weakly reflected by the available audit signals. Conversely, some perturbations may be highly detectable but not especially damaging. For this reason, benchmark evaluation should report impact and detectability jointly.

We propose an auditability-aware benchmark protocol designed for classical and quantum kernel evaluation. The protocol is defensive and methodological: it is intended to help researchers identify when benchmark conclusions are sensitive to perturbations that are not adequately captured by standard integrity or drift signals.

## 6.1 Principle 1: Report clean performance as a baseline, not as reliability evidence

Clean performance is necessary but not sufficient. A model can perform well under clean evaluation while exposing a large vulnerability surface under structured perturbations.

Therefore, clean accuracy, balanced accuracy, ROC-AUC, and F1 should be reported only as the baseline operating point. They should not be interpreted as evidence of benchmark reliability unless accompanied by perturbation impact and detectability analysis.

## 6.2 Principle 2: Disaggregate models and feature maps

For quantum-kernel benchmarks, results should not be collapsed into a single "quantum" category. Different quantum feature maps may induce different kernel geometries and therefore different robustness and auditability profiles.

The benchmark should report results by concrete model configuration. If two feature-map configurations induce identical or empirically indistinguishable kernels, this equivalence should be reported explicitly. In the current study, Z and PauliXZ induce identical fidelity kernels under the reps=1 configuration, so the main feature-map interpretation is based on three unique empirical profiles: ZZ, PauliXYZ, and Z/PauliXZ-equivalent.

## 6.3 Principle 3: Evaluate perturbation families, not only isolated perturbations

A benchmark should include perturbations from multiple families because different perturbation families are captured by different audit signals.

At minimum, an auditability-aware benchmark should include:

- target-shift perturbations;
- feature corruption perturbations;
- covariate-shift perturbations;
- pipeline or preprocessing perturbations.

The current results show that this distinction is essential. Prior-preserving target-shift perturbations create the clearest high-impact and low-detectability cases, while scaling and mean-shift perturbations are damaging but largely detectable by feature-centric signals.

## 6.4 Principle 4: Measure impact explicitly

For each perturbation, the benchmark should measure performance degradation relative to the corresponding clean baseline.

The primary impact metric should be robust to class imbalance. In this work, balanced-accuracy impact is used as the main metric:

impact = clean balanced accuracy - perturbed balanced accuracy

ROC-AUC impact and positive-class F1 impact can be reported as secondary metrics.

A perturbation should not be called relevant only because it changes the input distribution. It should also be assessed by its effect on model behaviour.

## 6.5 Principle 5: Measure detectability by signal family

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

## 6.6 Principle 6: Use shared normalization for cross-model detectability

When detectability scores are compared across models, signal normalization must use a shared reference. If normalization is performed separately for each model, identical raw signal values may map to different normalized detectability scores, making cross-model stealth ratios difficult to interpret.

For cross-model comparisons, we recommend normalizing audit signals jointly across models within the same protocol, dataset tag, and projected dimension. The model identifier should not be included in the normalization group.

Model-local normalization can still be useful for within-model diagnostic ranking, but shared normalization should be used for cross-model stealth claims.

## 6.7 Principle 7: Compute stealth, but do not rely on stealth alone

A scalar stealth score is useful for ranking perturbations, but it should not be the only evidence for an auditability gap.

We define shared-normalized stealth as:

stealth = impact × (1 - shared-normalized detectability)

This penalizes perturbations that are highly detectable. However, if impact is very large, a perturbation may still rank highly even when detectability is also substantial.

Therefore, stealth rankings should always be accompanied by an impact-detectability map.

## 6.8 Principle 8: Separate true auditability gaps from damaging but detectable perturbations

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

## 6.9 Principle 9: Treat OOD as a boundary condition unless multiple OOD settings are tested

OOD evaluation is important, but a single OOD split should not be overinterpreted. If only one temporal or file-based OOD pair is evaluated, OOD should be reported as a boundary condition rather than as evidence of broad generalization.

In this work, the Tuesday-to-Wednesday OOD protocol shows much smaller absolute stealth effects, and confidence intervals frequently include zero. This supports a conservative interpretation: the strongest evidence is concentrated in the controlled ID audit setting.

## 6.10 Principle 10: Report uncertainty

Impact and stealth should be reported with uncertainty estimates. At minimum, seed-unit confidence intervals should be provided for the main model comparisons.

In the current study, paired seed-unit confidence intervals show that QSVC-ZZ has consistently higher ID impact and shared-normalized stealth than SVC-RBF across dimensions 8, 10, and 12. Reporting these intervals is essential because several observed differences are small in absolute value.

## 6.11 Recommended reporting checklist

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

## 6.12 Summary

The main methodological recommendation is that benchmark reliability should be evaluated using three axes:

- performance under clean evaluation;
- robustness under perturbation;
- auditability of the perturbation response.

A benchmark that reports only clean performance and robustness may miss high-impact perturbations that leave weak evidence in standard audit signals. Conversely, a benchmark that reports only drift or integrity signals may overemphasize detectable distribution changes that do not materially affect conclusions.

The proposed protocol addresses this by requiring joint reporting of impact, detectability, stealth, and signal-family coverage. This is especially important for quantum-kernel benchmarks, where different feature maps can induce different vulnerability profiles and where collapsing all configurations under a single "quantum" label can obscure the relevant behaviour.


# 7. Discussion, Limitations, and Conclusion

TODO: Missing source file `paper15_discussion_limitations_conclusion_draft.md`.
