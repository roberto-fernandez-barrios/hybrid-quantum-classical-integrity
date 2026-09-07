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
