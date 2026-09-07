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


In the paper-core perturbation suite, the mean-shift perturbation is implemented as a per-feature random shift (`mean_shift_pf`), rather than as a single global constant offset. This design probes sensitivity to structured feature-wise covariate changes.
 These perturbations test whether feature-distribution audit signals can detect input-space changes.

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




Important implementation note: the experimental configuration records `q_backend_method=statevector` for traceability, but the current `FidelityQuantumKernel` is created with `fidelity=None`. Therefore, the backend object is not force-wired into the kernel primitive. The results should be interpreted as Qiskit Machine Learning fidelity-kernel simulations under the recorded software environment, not as hardware execution or as an explicitly shot-noise-controlled backend experiment.

