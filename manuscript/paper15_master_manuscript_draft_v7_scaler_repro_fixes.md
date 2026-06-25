# Auditability Gaps in Classical and Quantum Kernel Benchmarks under Structured Perturbations


# Abstract

Benchmark reliability is commonly assessed through clean performance and, sometimes, robustness under perturbation. However, these quantities do not capture whether harmful perturbations are observable by the audit signals available to the evaluator. This paper studies this missing dimension through the notion of an auditability gap: a setting in which a perturbation produces material performance impact while remaining weakly reflected by standard integrity or drift signals.

We evaluate this problem in classical and quantum kernel benchmarks using a CICIDS-derived binary classification setting [Sharafaldin2018]. The experimental protocol compares an RBF-kernel SVC against fidelity-kernel QSVC models under structured perturbation families, including target shift, feature corruption, covariate shift, and pipeline perturbations. We measure impact, detectability, and shared-normalized stealth.

The results show two complementary failure modes. First, under controlled in-distribution evaluation, QSVC-ZZ exhibits the strongest aggregate vulnerability profile among the evaluated kernels, with impact ratios of 2.97x to 3.66x and shared-normalized stealth ratios of 1.59x to 1.81x relative to SVC-RBF. Second, the clearest true auditability-gap cases are prior-preserving target-shift perturbations, which produce measurable impact while remaining nearly invisible to standard feature-centric signals. Based on these findings, we propose an auditability-aware benchmark protocol requiring joint reporting of impact, detectability by signal family, shared-normalized stealth, quadrant analysis, and uncertainty estimates.

# 1. Introduction

Machine-learning benchmarks are often interpreted through clean performance metrics such as accuracy, balanced accuracy, ROC-AUC, or F1 score. While these metrics are necessary, they are not sufficient to establish benchmark reliability. A model can perform well under clean evaluation and still be sensitive to structured perturbations. Conversely, a perturbation can be highly visible in drift signals without materially changing the benchmark conclusion.

This distinction is especially important when benchmarks are used to compare different model families. In classical and quantum kernel evaluation, conclusions are often drawn from performance differences across kernels, feature maps, and projected dimensions. If a benchmark conclusion can be altered by a perturbation that is not clearly reflected by standard integrity signals, then the issue is not only robustness. It is also auditability.

We use the term auditability gap to describe this failure mode. An auditability gap occurs when a perturbation has high impact but low observability. Impact measures how much a perturbation changes model behaviour or performance relative to the clean benchmark. Detectability measures how strongly the perturbation is reflected by audit signals. A perturbation is most concerning when it produces measurable degradation while remaining weakly detected.

This paper studies auditability gaps in classical and quantum kernel benchmarks. The goal is not to prove that quantum models are universally better or worse than classical models. Instead, the objective is methodological: to evaluate whether benchmark conclusions are robust and auditable under controlled perturbation families.

Quantum kernel methods are a natural setting for this analysis because different feature maps can induce different kernel geometries. Therefore, quantum kernel benchmarks should not collapse all quantum models into a single category. A feature-map-specific analysis is required. In this work, we compare an RBF-kernel SVC baseline against QSVC configurations based on fidelity quantum kernels. A circuit-level sanity check shows that, under the current reps=1 configuration, Z and PauliXZ induce identical fidelity kernels. Therefore, the main feature-map interpretation is based on three unique empirical quantum kernel profiles: ZZ, PauliXYZ, and Z/PauliXZ-equivalent.

The experimental protocol evaluates structured perturbations grouped into target shift, feature corruption, covariate shift, and pipeline perturbations. This grouping is central because not all perturbations are captured by the same audit signals. Feature-centric signals are expected to detect input-distribution changes, while label-aware and prediction-aware signals are needed to expose target-shift and behavioural changes.

The results show that clean performance alone is insufficient to characterize benchmark reliability. Under controlled in-distribution evaluation, QSVC-ZZ exhibits the strongest aggregate vulnerability profile among the evaluated kernels. Its balanced-accuracy impact relative to SVC-RBF is 2.97x, 3.66x, and 3.39x at projected dimensions 8, 10, and 12. With shared normalization, QSVC-ZZ also remains the highest-stealth model under ID evaluation, with shared-normalized stealth ratios of 1.59x, 1.81x, and 1.67x relative to SVC-RBF. Paired seed-unit confidence intervals confirm that the ZZ-SVC differences are strictly positive for both impact and shared-normalized stealth across all evaluated dimensions.

The clearest true auditability-gap cases are prior-preserving target-shift perturbations. These perturbations produce measurable impact while standard feature-centric signals remain blind to them. Conversely, scaling drift and mean shift are damaging but largely detectable, showing that impact and detectability must be interpreted jointly.

The contributions are as follows.

First, we define and operationalize the auditability gap as a joint impact-detectability problem for kernel benchmarks.

Second, we evaluate classical and quantum kernel models under a structured perturbation suite covering target shift, corruption, covariate shift, and pipeline perturbations.

Third, we show that QSVC-ZZ has the strongest controlled ID vulnerability profile among the evaluated kernels, with statistically supported positive paired differences relative to SVC-RBF.

Fourth, we show that prior-preserving target-shift perturbations are the clearest true auditability-gap cases because they remain nearly invisible to standard feature-centric signals.

Fifth, we propose an auditability-aware benchmark protocol requiring signal-family-specific detectability reporting, shared normalization for cross-model stealth, impact-detectability quadrant analysis, and uncertainty estimates.


# 2. Related Work

This section positions the paper relative to classical kernel methods, quantum kernel learning, robustness and perturbation evaluation, drift detection, label noise, and benchmark reproducibility. The central gap is that these areas usually study performance, robustness, or distributional monitoring separately, whereas this paper evaluates benchmark reliability through the joint lens of impact and detectability.

## 2.1 Classical kernel methods and SVC baselines

Support vector classifiers and kernel methods are standard tools for nonlinear supervised learning. The RBF-kernel SVC is a strong classical baseline because it defines a nonlinear similarity function without requiring an explicit finite-dimensional feature expansion [CortesVapnik1995, ScholkopfSmola2002].

In this paper, SVC-RBF is not intended to represent all classical machine-learning models. Its role is to provide a controlled classical kernel comparator against fidelity-based quantum kernels. This choice makes the comparison more focused: the study evaluates kernel-induced decision behaviour under perturbation rather than comparing unrelated model families.

However, classical kernel baselines are usually evaluated through clean predictive performance or robustness metrics. They are less often evaluated by asking whether harmful perturbations are observable by benchmark audit signals. This motivates the auditability-aware extension proposed here.

## 2.2 Quantum kernel methods and QSVC

Quantum kernel methods encode classical data into quantum states and compute similarities through quantum-state overlaps or fidelities. Havlíček et al. introduced quantum-enhanced feature spaces as a route to supervised learning with quantum kernels [Havlicek2019]. Later work has emphasized that many supervised quantum models can be understood through a kernel-method perspective, where the data-encoding map is the central modelling choice [Schuld2021].

QSVC models are a natural experimental setting for this paper because they reuse the support-vector classification framework while replacing the classical kernel with a fidelity quantum kernel. This makes the comparison with SVC-RBF conceptually direct. The implementation also follows the Qiskit Machine Learning ecosystem, which provides `FidelityQuantumKernel` and QSVC abstractions for quantum-kernel experiments [QiskitML2025, Qiskit2024].

Most quantum-kernel studies focus on predictive performance, trainability, expressivity, or the possibility of quantum advantage [Havlicek2019, Schuld2021, HuangKuengPreskill2021]. This paper addresses a different question: whether benchmark conclusions under quantum kernels are auditable when structured perturbations alter evaluation behaviour.

## 2.3 Quantum feature maps and benchmark sensitivity

Quantum feature maps determine how classical inputs are embedded into quantum Hilbert space [Havlicek2019, Schuld2021, HuangKuengPreskill2021]. Consequently, the feature map can substantially affect the induced kernel matrix and the resulting classifier behaviour. This makes feature-map-specific reporting essential in quantum-kernel benchmarking.

Prior work often treats feature-map choice as a question of expressivity, trainability, or potential quantum advantage [Schuld2021, HuangKuengPreskill2021]. The present study evaluates several feature-map configurations but reports a key equivalence: under the current Qiskit reps=1 configuration, Z and PauliXZ induce identical fidelity kernels. Therefore, the main interpretation uses three unique empirical quantum kernel profiles: ZZ, PauliXYZ, and Z/PauliXZ-equivalent.

This is relevant to prior work because quantum-kernel benchmarking often treats feature-map choice as a performance or expressivity issue. Here, feature maps are also evaluated through auditability: whether perturbation-induced failures are visible to benchmark signals.

## 2.4 Robustness, perturbations, and benchmark stress testing

Robustness evaluation studies how model performance changes under noise, corruptions, distribution shift, or other perturbations. Benchmarking under common corruptions has been used to evaluate whether models remain reliable under non-adversarial perturbations [HendrycksDietterich2019]. This paper follows the same general philosophy of controlled stress testing, while acknowledging that the present setting differs from image-corruption robustness because it evaluates classical and quantum kernel benchmarks rather than neural image classifiers.

The key difference is that this paper does not only ask whether a perturbation degrades performance. It also asks whether the perturbation is detectable. This separates damaging-but-observable perturbations from true high-impact/low-detectability auditability gaps.

## 2.5 Dataset shift, target shift, and label noise

Dataset shift occurs when the train and test distributions differ. Prior work distinguishes covariate shift, label shift, and concept shift as different mechanisms of distributional change [MorenoTorres2012]. Label noise and target-side perturbations have also been widely studied as sources of degraded classification performance [FrenayVerleysen2014].

These distinctions are central to this paper because different shift types are visible to different audit signals. Feature-distribution signals are naturally suited to covariate shift. They are less suited to prior-preserving target-shift perturbations, where the input distribution may remain unchanged while benchmark labels or behavioural conclusions change.

This is why the paper separates target shift, corruption, covariate shift, and pipeline perturbations instead of treating all perturbations as one generic robustness condition.

## 2.6 Drift detection and integrity monitoring

Drift detection and two-sample testing methods aim to detect whether reference and current distributions differ. Maximum mean discrepancy is a common kernel-based statistic for comparing distributions [Gretton2008]. Concept-drift surveys further emphasize that changing data-generating processes require monitoring and adaptation over time [Zliobaite2014].

The auditability problem studied here is related but not identical. Drift detection asks whether a distribution changed. Benchmark auditability asks whether a harmful perturbation is visible to available audit signals. A perturbation can be visible but not harmful, or harmful but weakly visible. Therefore, impact and detectability must be reported jointly.

## 2.7 Benchmark reliability, documentation, and reproducibility

Reproducibility work in machine learning emphasizes that results should be supported by transparent reporting of data, seeds, metrics, code, and experimental conditions [Pineau2020]. Dataset and model documentation frameworks such as datasheets and model cards similarly argue that evaluation artefacts should report intended use, limitations, and evaluation context [Gebru2021, Mitchell2019].

This paper extends that reporting mindset to perturbation auditability. A benchmark should not only document what data and models were used. It should also report which perturbation families were tested, which audit signals were measured, which signal families detected which perturbations, and which harmful perturbations remained weakly observable.

## 2.8 Positioning and gap

Existing work has studied classical kernels, quantum kernels, robustness, dataset shift, drift detection, label noise, and reproducibility. However, these areas are usually treated separately.

The gap addressed by this paper is the lack of an auditability-aware benchmark protocol that jointly reports:

1. how much a perturbation changes benchmark conclusions;
2. whether the perturbation is visible to available audit signals;
3. which signal family detects which perturbation family;
4. whether different quantum feature maps expose different auditability profiles;
5. whether cross-model stealth comparisons are normalized on a shared scale;
6. whether the main findings are supported by seed-unit uncertainty estimates.

This paper addresses that gap by evaluating classical and quantum kernel models under structured perturbations and by proposing a benchmark protocol based on impact, detectability, shared-normalized stealth, quadrant analysis, and uncertainty reporting.


# 3. Problem Formulation

This paper studies benchmark reliability through three quantities: impact, detectability, and stealth.

Let \(M_{\mathrm{clean}}\) denote the clean benchmark metric and \(M_{\mathrm{perturbed}}(a)\) the same metric under perturbation \(a\). The primary impact metric is balanced-accuracy impact:

\[
\mathrm{Impact}(a) = M_{\mathrm{clean}} - M_{\mathrm{perturbed}}(a)
\]

Detectability measures how strongly the perturbation is reflected by audit signals. For cross-model comparison, raw signal responses are normalized using a shared reference across models within each protocol, dataset tag, and projected dimension.

The shared-normalized stealth score is defined as:

\[
\mathrm{Stealth}(a) = \mathrm{Impact}(a) \times (1 - \mathrm{Detectability}_{\mathrm{shared}}(a))
\]

This formulation is a first-order heuristic that combines impact and observability into a single scalar. It is not derived from a formal information-theoretic framework and should be interpreted as a ranking and diagnostic tool rather than as an absolute measure of concealment.

The paper uses the term auditability gap for perturbations that produce material impact while remaining weakly reflected by available audit signals.


# 4. Methodology

This section describes the experimental protocol used to evaluate robustness and auditability in classical and quantum kernel benchmarks. The goal is not to study adversarial optimization or deployment-time attacks, but to evaluate whether structured perturbations can alter benchmark conclusions while remaining weakly reflected by standard integrity signals.

## 4.1 Threat model and auditability setting

We consider a benchmark-audit setting in which a trained model is evaluated under clean and perturbed conditions. A perturbation is considered relevant when it produces a measurable degradation in model behaviour or changes the interpretation of the benchmark result.

The central object of study is the auditability gap: a perturbation may be harmful while being weakly observable by the available audit signals. Therefore, a benchmark should not only measure how much performance degrades, but also how clearly the perturbation is reflected by integrity, drift, label-aware, and prediction-aware signals.

This work does not provide operational perturbation instructions. Instead, they are used as controlled probes to study methodological reliability. The purpose is defensive: to identify which perturbation families are visible to standard benchmark diagnostics and which require additional audit signals.

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

Covariate-shift perturbations modify the input distribution through scaling or mean-shift transformations.


In the paper-core perturbation suite, the mean-shift perturbation is implemented as a per-feature random shift (`mean_shift_pf`), rather than as a single global constant offset. Each feature receives an independent additive shift drawn from a normal distribution with mean 0 and standard deviation equal to the absolute value of the nominal shift parameter, |delta|. This design produces both positive and negative feature-level changes and probes sensitivity to structured feature-wise covariate changes. These perturbations test whether feature-distribution audit signals can detect input-space changes.

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

The corrected shared-normalized tables used in the manuscript are archived derived artefacts under `results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/`. They are verified by `src/experiments/verify_sharednorm_artifacts.py`, which checks the reported QSVC-ZZ versus SVC-RBF impact and shared-normalized stealth ratios. The aggregate CSV also contains historical model-local detectability columns whose normalization metadata includes `model`; those model-local columns reproduce the retracted model-local stealth ratios and are not used for the manuscript's cross-model shared-normalized claims.


The aggregate detectability score is computed as the arithmetic mean of the available normalized signal responses. Standard feature/score-based detectability is computed as the mean of the normalized standard signals, while full detectability is computed as the mean across the standard, label-aware, and prediction-aware normalized signals.


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

For the central ID comparison, paired differences between QSVC-ZZ and SVC-RBF are computed for each projected dimension by matching seed units. Confidence intervals are computed as two-sided 95% intervals using the Student t distribution with five degrees of freedom, corresponding to six paired seed units. These intervals are used to assess whether QSVC-ZZ consistently exceeds the classical baseline in impact and shared-normalized stealth.

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

Third, quantum models are evaluated with fidelity kernels under simulated fidelity-kernel evaluation. The results should not be interpreted as claims about hardware execution or hardware noise.

Fourth, the train/test sizes are intentionally limited to make classical and quantum-kernel evaluation feasible under equivalent conditions. The conclusions should therefore be interpreted as controlled benchmark evidence rather than large-scale deployment evidence.

Fifth, Z and PauliXZ induce identical kernels under the current reps=1 configuration. This equivalence is reported explicitly and the main feature-map interpretation is based on three unique empirical kernel profiles.

These limitations do not invalidate the auditability-gap analysis, but they define the scope of the conclusions.


## 4.13 Additional reproducibility and statistical disclosures

The main experiments use data split seeds 42, 43, and 44 crossed with model seeds 42 and 43, yielding six paired seed units. Confidence intervals are computed as two-sided 95% intervals over seed units using the Student t distribution with five degrees of freedom. These confidence intervals are unadjusted for multiple comparisons and are reported to support directional consistency across dimensions rather than as formal multiple-hypothesis tests.

The SVC-RBF baseline uses C=1.0, gamma='scale', and the RBF kernel. The QSVC models use fidelity quantum kernels with reps=1 and simulated fidelity-kernel evaluation. The quantum feature-map configurations are ZZ, Z, PauliXZ, and PauliXYZ, with Z and PauliXZ interpreted as an equivalent empirical kernel profile under the current configuration.

The maximum training and test sample sizes are both 128 in the main paper-core experiments. Projected dimensions 8, 10, and 12 are used for the final feature-map comparison, while the original ZZ analysis also includes dimensions 4 and 6.

The stealth score is a first-order heuristic that combines impact and observability into a single scalar. It is not derived from a formal information-theoretic framework and should be interpreted as a ranking and diagnostic tool rather than as an absolute measure of concealment.

The quadrant thresholds used to identify high-impact and low-detectability cases are empirical quartile thresholds. The high-impact threshold is the 75th percentile of ID impact, and the low-detectability threshold is the 25th percentile of ID shared-normalized detectability. These thresholds are used to separate the tail of high-impact perturbations from the bulk distribution. The qualitative separation between prior-preserving target shift and covariate perturbations is also visible from the raw signal-family behaviour.

The prior-preserving label-flip perturbation modifies evaluation labels and is interpreted as a controlled benchmark-label perturbation. Its role is to test whether benchmark conclusions can be altered through target-side perturbations that are not visible to feature-centric signals.


## 4.14 Dataset characteristics

The ID benchmark uses `data/cicids_subset.csv`, containing 3000 instances, 77 feature columns before projection, and a balanced binary label distribution with 1500 samples per class.

The OOD protocol uses `data/processed/cicids_ood_tuesday_train.csv` as the reference/training file and `data/processed/cicids_ood_wednesday_test.csv` as the current/evaluation file. Both contain 3000 instances, 78 feature columns before projection, and a balanced binary label distribution with 1500 samples per class.

The OOD dataset files contain 78 feature columns before projection, compared with 77 feature columns in the ID benchmark. This difference reflects the preprocessing used to construct the ID and OOD benchmark files. It does not affect the final model comparison because both protocols are projected to the same low-dimensional spaces (8, 10, or 12 dimensions) before model training and evaluation.

The main feature-map comparison uses projected dimensions 8, 10, and 12 after dimensionality reduction. The original ZZ analysis also includes dimensions 4 and 6. The main paper-core runs use a maximum of 128 training samples and 128 test samples per run to keep classical and quantum kernel evaluations comparable and computationally feasible.


## 4.15 Software environment

The experiments were run with the following software environment:

- Python: 3.10.16
- NumPy: 2.2.6
- pandas: 2.3.3
- scikit-learn: 1.7.2
- Qiskit: 2.3.0
- Qiskit Aer: 0.17.2
- qiskit-machine-learning: 0.9.0

The SVC-RBF baseline uses C=1.0, gamma='scale', and the RBF kernel. The QSVC models use `FidelityQuantumKernel`, reps=1, simulated fidelity-kernel evaluation, and the feature-map configurations ZZ, Z, PauliXZ, and PauliXYZ. Z and PauliXZ are interpreted as one equivalent empirical kernel profile under this configuration.

The SVC-RBF baseline uses StandardScaler preprocessing, fitted on the training split and applied to the corresponding test split. The QSVC models use MinMaxScaler to the range [0, 2π], referred to as minmax2pi, because the evaluated quantum feature maps encode inputs as angular variables. Therefore, the comparison should be interpreted as a comparison between the complete classical and quantum kernel pipelines used in the experiments, including their required preprocessing.

The paper-core experiments were run with `q_max_iter=1000`, passed explicitly as `--q-max-iter 1000` to the runner script. This overrides the code default of 2000. The value 1000 is confirmed from the 168 JSON sidecar files stored with the paper-core outputs. Other code defaults should not be interpreted as the configuration used for the reported paper-core runs.




Important implementation note: the experimental configuration records `q_backend_method=statevector` for traceability, but the current `FidelityQuantumKernel` is created with `fidelity=None`. Therefore, the backend object is not force-wired into the kernel primitive. The results should be interpreted as Qiskit Machine Learning fidelity-kernel simulations under the recorded software environment, not as hardware execution or as an explicitly shot-noise-controlled backend experiment.


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

# Main result table

Table 1. ID comparison between SVC-RBF and QSVC-ZZ using shared-normalized stealth.

| dim | SVC impact | ZZ impact | impact ratio | ZZ-SVC impact diff CI95 | SVC stealth | ZZ stealth | stealth ratio | ZZ-SVC stealth diff CI95 |
|---:|---:|---:|---:|---|---:|---:|---:|---|
| 8 | 0.0176 | 0.0522 | 2.97x | 0.0347 [0.0224, 0.0470] | 0.0161 | 0.0256 | 1.59x | 0.0098 [0.0045, 0.0151] |
| 10 | 0.0164 | 0.0602 | 3.66x | 0.0437 [0.0342, 0.0532] | 0.0152 | 0.0275 | 1.81x | 0.0133 [0.0104, 0.0161] |
| 12 | 0.0193 | 0.0655 | 3.39x | 0.0462 [0.0353, 0.0572] | 0.0178 | 0.0297 | 1.67x | 0.0143 [0.0091, 0.0194] |

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


# 7. Discussion

The results show that benchmark reliability cannot be reduced to clean performance or perturbation robustness alone. A perturbation may be harmful while remaining weakly reflected by standard audit signals, or it may be highly detectable while producing limited practical impact. This motivates an auditability-aware view of benchmark evaluation.

## 7.1 Robustness and auditability are distinct

Robustness asks how much model behaviour changes under perturbation. Auditability asks whether that change is visible to the available diagnostic signals. This distinction explains why scaling drift and mean shift should be interpreted as damaging but observable perturbations, while prior-preserving target-shift perturbations form clearer auditability-gap cases.

## 7.2 Signal design determines what can be audited

The signal-family comparison shows that standard feature-centric signals are effective for covariate shifts but insufficient for target-shift perturbations. Label-aware and prediction-aware signals partially close this gap. Therefore, detectability should be reported by signal family rather than as a single universal score.

## 7.3 Quantum kernel behaviour should be feature-map specific

The results show that quantum-kernel behaviour should not be collapsed into a generic quantum category. QSVC-ZZ shows the strongest aggregate ID vulnerability profile, QSVC-PauliXYZ shows an intermediate profile, and QSVC-Z/PauliXZ-equivalent shows a milder profile. The supported claim is feature-map-specific, not a universal claim about quantum kernels.

## 7.4 OOD as a boundary condition

The OOD protocol is useful but should not be overinterpreted. Absolute OOD effects are much smaller than ID effects and show substantial seed-to-seed variability. Therefore, OOD is used as a boundary condition rather than as the main evidence for the paper's central claim.

# 8. Limitations

The results should be interpreted within the scope of the experimental design.

First, the experiments use a single CICIDS-derived binary classification benchmark. Additional datasets are needed before making broader claims about classical or quantum kernel auditability.

Second, the benchmark uses limited train/test sizes to make classical and quantum kernel evaluation feasible under comparable conditions.

Third, the main statistical analysis uses six paired seed units, corresponding to three split seeds and two model seeds. The paired confidence intervals support the central ID claim, but a larger seed set would provide tighter uncertainty estimates.

Fourth, the OOD protocol uses one Tuesday-to-Wednesday temporal split. OOD effects are small and variable across seeds, so they are treated as a boundary condition.

Fifth, quantum models are evaluated using fidelity quantum kernels under simulation. The results should not be interpreted as claims about real quantum hardware execution, hardware noise, shot noise, or resource requirements.

Sixth, under the current Qiskit reps=1 configuration, Z and PauliXZ induce identical fidelity kernels. This equivalence is reported explicitly and the main analysis collapses them into a single empirical profile.

Seventh, the perturbation suite is controlled but not exhaustive. Other perturbation types may expose different auditability patterns.

Eighth, the SVC-RBF and QSVC pipelines use different preprocessing scalers: StandardScaler for SVC-RBF and MinMaxScaler to [0, 2π] for QSVC. This asymmetry is necessary because the evaluated quantum feature maps encode inputs as angular variables. However, it means that identical covariate-shift and corruption perturbations are applied within different preprocessing regimes. The reported impact and stealth ratios should therefore be interpreted as comparisons between the evaluated end-to-end kernel pipelines, not as isolated comparisons of kernel functions under identical numeric preprocessing.

# 9. Conclusion

This paper introduced an auditability-aware perspective on classical and quantum kernel benchmarking. The central claim is that benchmark reliability requires more than clean performance and robustness. It also requires measuring whether harmful perturbations are visible to the available audit signals.

Using a CICIDS-derived binary classification benchmark, we evaluated an RBF-kernel SVC baseline and several QSVC configurations under structured perturbation families. The results show two complementary failure modes.

First, QSVC-ZZ exhibits the strongest aggregate ID vulnerability profile among the evaluated kernels. It shows substantially higher balanced-accuracy impact than SVC-RBF and consistently higher shared-normalized stealth. Paired seed-unit confidence intervals for the QSVC-ZZ minus SVC-RBF differences remain strictly positive across the evaluated dimensions.

Second, the clearest true auditability-gap cases are prior-preserving target-shift perturbations. These perturbations produce measurable performance impact while remaining nearly invisible to standard feature-centric signals. Conversely, scaling drift and mean shift are damaging but largely detectable.

Based on these findings, we propose an auditability-aware benchmark protocol requiring clean performance reporting, perturbation impact measurement, detectability by signal family, shared normalization for cross-model stealth, impact-detectability quadrant analysis, feature-map equivalence checks, conservative OOD interpretation, and seed-unit uncertainty estimates.

The broader implication is that robust benchmarking should answer two questions at the same time: how much does a perturbation change the conclusion, and can that change be audited?


# References

[CortesVapnik1995]
Cortes, C., & Vapnik, V. (1995). Support-vector networks. Machine Learning, 20, 273-297.

[ScholkopfSmola2002]
Schölkopf, B., & Smola, A. J. (2002). Learning with Kernels: Support Vector Machines, Regularization, Optimization, and Beyond. MIT Press.

[Havlicek2019]
Havlíček, V., Córcoles, A. D., Temme, K., Harrow, A. W., Kandala, A., Chow, J. M., & Gambetta, J. M. (2019). Supervised learning with quantum-enhanced feature spaces. Nature, 567, 209-212.

[Schuld2021]
Schuld, M. (2021). Supervised quantum machine learning models are kernel methods. arXiv:2101.11020.

[HuangKuengPreskill2021]
Huang, H.-Y., Kueng, R., & Preskill, J. (2021). Information-theoretic bounds on quantum advantage in machine learning. arXiv:2101.02464.

[Qiskit2024]
Javadi-Abhari, A., et al. (2024). Quantum computing with Qiskit. arXiv:2405.08810.

[QiskitML2025]
Sahin, M. E., et al. (2025). Qiskit Machine Learning: an open-source library for quantum machine learning tasks at scale on quantum hardware and classical simulators. arXiv:2505.17756.

[HendrycksDietterich2019]
Hendrycks, D., & Dietterich, T. (2019). Benchmarking Neural Network Robustness to Common Corruptions and Perturbations. arXiv:1903.12261.

[MorenoTorres2012]
Moreno-Torres, J. G., Raeder, T., Alaiz-Rodríguez, R., Chawla, N. V., & Herrera, F. (2012). A unifying view on dataset shift in classification. Pattern Recognition, 45(1), 521-530.

[FrenayVerleysen2014]
Frénay, B., & Verleysen, M. (2014). Classification in the presence of label noise: a survey. IEEE Transactions on Neural Networks and Learning Systems, 25(5), 845-869.

[Gretton2008]
Gretton, A., Borgwardt, K. M., Rasch, M. J., Schölkopf, B., & Smola, A. J. (2008). A kernel method for the two-sample problem. arXiv:0805.2368.

[Zliobaite2014]
Žliobaitė, I., Bifet, A., Pechenizkiy, M., & Bouchachia, A. (2014). A survey on concept drift adaptation. ACM Computing Surveys, 46(4), Article 44.

[Pineau2020]
Pineau, J., Vincent-Lamarre, P., Sinha, K., Larivière, V., Beygelzimer, A., d'Alché-Buc, F., Fox, E., & Larochelle, H. (2020). Improving reproducibility in machine learning research. arXiv:2003.12206.

[Gebru2021]
Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. Communications of the ACM, 64(12), 86-92.

[Mitchell2019]
Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model Cards for Model Reporting. Proceedings of FAT* 2019.

[Sharafaldin2018]
Sharafaldin, I., Lashkari, A. H., & Ghorbani, A. A. (2018). Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization. Proceedings of ICISSP 2018.
