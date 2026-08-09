# Novelty review and claim-differentiation record

Cut-off date: 9 August 2026  
Primary claim: **information-set conditional integrity auditing** for hybrid
quantum-classical kernel workflows.

## Review question and search boundary

The review asked whether prior work already (i) defines integrity auditability
relative to the evidence exposed at a workflow boundary, (ii) derives blind
regions from that information set, (iii) maps perturbations to complementary
sensor families, and (iv) validates the mapping across data-to-evaluation and
quantum-kernel boundaries with an executable fail-closed response.

Searches combined the phrases `quantum-classical pipeline integrity`, `quantum
software contract`, `quantum circuit integrity`, `quantum software testing`,
`monitoring without labels`, `label shift`, `delayed ground truth`, `sensor
coverage`, `blind spot`, `auditability`, and `information set`. Sources were
followed through their references and forward-related records. The review used
publisher, proceedings, institutional, or arXiv primary records; non-primary
discovery pages were not used to support manuscript claims.

## Closest work and non-overlap

| Work | What it already contributes | Consequence for this paper | Remaining distinction |
|---|---|---|---|
| Yeniaras & Karimov, QCIVET (arXiv:2605.13109, 2026) | Stage contracts, hash-chained audit traces, behavioural subtyping, semantic observable checks, formal properties, calibrated-noise and QPU validation | **Direct overlap.** Do not claim contracts, hash chains, stage decomposition, or fail-closed verification alone as novel | This paper conditions auditability on the auditor's evidence, treats labels and the evaluation conclusion as first-class integrity boundaries, derives sensor blind regions, and validates their coverage across three datasets, ID/OOD settings, kernel profiles, and a quantum-kernel-specific simulator gate |
| Solozobov, *Evidence Sufficiency Under Delayed Ground Truth* (arXiv:2604.15740, 2026) | Evidence sufficiency under label latency, proxy-monitor coverage and the impossibility of observing pure concept drift from unchanged features | **Close conceptual neighbour.** Do not claim the general insight that unlabeled monitoring has blind spots | The present unit is an adversarial/fault perturbation at a hybrid workflow boundary, including corrupted evaluation labels and quantum circuit/kernel evidence; the endpoint is conditional integrity auditability rather than time-decaying governance sufficiency |
| Ahmed et al., *Multi-Level Integrity Evaluation Framework for Quantum Circuits* (arXiv:2604.26430, 2026) | Complementary structural, interaction and behavioural circuit metrics; empirical structural blind spots | **Close quantum-specific neighbour.** Do not claim that one circuit metric is insufficient | The present framework spans classical data, predictions, labels, evaluation conclusions and fidelity-kernel artifacts, and states coverage as a function of available evidence rather than a fixed three-score circuit evaluation |
| Paltenghi & Pradel, MorphQ (ICSE 2023) | Metamorphic testing of Qiskit using quantum-specific semantics-preserving transformations | Benign transpilation/common-unitary controls are not a standalone novelty | They serve as negative controls inside a broader integrity coverage contract rather than as a platform bug-finding method |
| Wang et al., QDiff (ASE 2021) | Differential testing of quantum software stacks using equivalent program variants | Cross-implementation/variant testing is prior art | This paper does not claim compiler testing; it audits evidence sufficiency for fixed workflow boundaries |
| Luo et al., QEMI (arXiv:2602.09942, 2026) | Equivalence-modulo-inputs testing of Qiskit, Q# and Cirq; compiler-stack bugs | Semantics-preserving variant generation is prior art | The present contribution is sensor coverage and response composition, not quantum stack bug discovery |
| Li et al., projection-based runtime assertions (OOPSLA 2020) | Quantum program runtime assertions | Quantum semantic checks and assertions are prior art | Assertions instantiate the quantum evidence family; they do not address evaluation-label blind regions or cross-sensor identifiability |
| Shi et al., CertiQ (2019) and quantum program logics | Compiler/program correctness proofs | Formal verification is prior art | Propositions 1--2 are supporting boundary results, not the paper's novelty claim |
| Volya et al. (HOST 2023); Ghosh et al. (2023) | Lifecycle attack surfaces of classical-quantum systems | Full-stack threat enumeration is prior art | The paper supplies a bounded, executable coverage argument for selected boundaries; it does not claim full-stack security |
| Oliveira et al., Quantum Vulnerability Factor (TDSC 2024) | Quantifies circuit-output sensitivity to injected faults | Quantum vulnerability/impact scoring is prior art | The present primary axis is whether the available evidence can observe the intervention, separated from output impact |
| Lipton et al. (ICML 2018), Ginart et al. (AISTATS 2022), Koebler et al. (AISTATS 2025) | Label-shift detection and performance monitoring with unlabeled data plus selective labels | Label availability and proxy monitoring are prior art | The paper studies integrity of the label/evaluation path itself and explicitly separates label marginals from item-level joint outcomes/provenance |
| Arp et al. (USENIX Security 2022) | Evaluation pitfalls in learning-based security, including labels, sampling, baselines and threat models | Benchmark-validity criticism is prior art | This paper formalizes one specific failure mechanism as a sensor-coverage problem and supplies executable evidence contracts |
| Schnabel & Roth (QMI 2025) and broader QKM benchmarking | Feature-map and pipeline choices materially affect QKM results | ZZ-vs-SVC is not a general scientific novelty | It remains a secondary, pipeline-specific profile and never supports a universal quantum/classical ordering |

## Frozen novelty statement

The defensible novelty is the **combination** of:

1. a workflow formalization that separates model-output, evaluation-conclusion,
   and execution-integrity effects;
2. auditability conditioned on the evidence available to the auditor;
3. exact blind-region statements and an attack-to-sensor coverage map;
4. replication of those boundaries across CICIDS2017, UNSW-NB15, ToN-IoT,
   fixed ID/OOD environments, model profiles and projected dimensions;
5. a bounded quantum-specific instantiation covering circuit provenance,
   semantic kernel comparison, algebraic checks and repeated estimation; and
6. an executable four-contract `allow/hold/block` demonstration that makes the
   coverage and residual blind regions actionable.

No individual item above is presented as sufficient novelty. Propositions 1--2
are elementary finite-batch consequences that make the information boundary
precise. The hash chain and contract mechanism are an implementation of the
framework, not a priority claim. ZZ-vs-SVC is secondary empirical context.

## Language prohibited by the evidence

- “first integrity framework for hybrid quantum-classical pipelines”;
- “complete/full-lifecycle coverage”;
- “contracts/hash chains are the main novelty”;
- “quantum kernels are more vulnerable than classical kernels”;
- “the simulator gate validates QPU, calibrated-noise, scheduling, provider,
  multi-tenant, or operational Fleet Management security”; and
- “WP5 case-study software is delivered by this paper.”

## Residual novelty risk

The literature is moving unusually quickly in 2026. QCIVET, the evidence-
sufficiency preprint, and the multi-level circuit-integrity preprint appeared
after the original workshop framing. They reduce the defensible breadth of any
claim based on contracts or complementary sensors. The revised claim remains
distinct, but the related-work comparison must be retained at submission and
rerun immediately before upload.

