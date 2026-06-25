# Abstract and Introduction Draft

## Abstract

Benchmark reliability is commonly assessed through clean performance and, sometimes, robustness under perturbation. However, these quantities do not capture whether harmful perturbations are observable by the audit signals available to the evaluator. This paper studies this missing dimension through the notion of an auditability gap: a setting in which a perturbation produces material performance impact while remaining weakly reflected by standard integrity or drift signals.

We evaluate this problem in classical and quantum kernel benchmarks using a CICIDS-derived binary classification setting [Sharafaldin2018]. The experimental protocol compares an RBF-kernel SVC against fidelity-kernel QSVC models under structured perturbation families, including target shift, feature corruption, covariate shift, and pipeline perturbations. We measure impact, detectability, and shared-normalized stealth.

The results show two complementary failure modes. First, under controlled in-distribution evaluation, QSVC-ZZ exhibits the strongest aggregate vulnerability profile among the evaluated kernels, with impact ratios of 2.97x to 3.66x and shared-normalized stealth ratios of 1.59x to 1.81x relative to SVC-RBF. Second, the clearest true auditability-gap cases are prior-preserving target-shift perturbations, which produce measurable impact while remaining nearly invisible to standard feature-centric signals. Based on these findings, we propose an auditability-aware benchmark protocol requiring joint reporting of impact, detectability by signal family, shared-normalized stealth, quadrant analysis, and uncertainty estimates.

## 1. Introduction

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
