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


## Addendum — recheck on 6 September 2026

The searches above were repeated on 6 September 2026 (arXiv, publisher
records, forward citations of QCIVET). Four records appeared after or were
missed by the 9 August cut-off and are now cited or positioned:

| Work | What it contributes | Consequence for this paper |
|---|---|---|
| Yeniaras, *QML-PipeGuard: Drift-Aware Behavioral Fingerprinting for QML Pipeline Integrity* (arXiv:2605.25066, 24 May 2026) | Informationally complete observable contract; drift-aware tolerance that absorbs benign calibration change; channel-substitution detection on IBM Heron r2 (`ibm_fez`); shot-complexity bound | **Closest quantum-specific neighbour after QCIVET.** Added to §II and Table 1. Its unit is the quantum channel; it does not model the evaluation-label path, provenance, or multi-environment coverage. Do not claim "calibrated tolerance on real hardware" as novelty in this or any follow-up paper without citing it |
| Bajaj, *Evaluation Blindness: How Silent Measurement Failures Corrupt AI Systems from Training to Deployment* (arXiv:2608.02786, 3 Aug 2026) | Defines evaluation blindness (measurement indistinguishable from healthy state while failing); six-class taxonomy over 50 incidents; failure-budget framing | **Conceptual neighbour of the central term.** Added to §II and Table 1. Qualitative and classical; no information-regime formalization, exact blind regions, coverage validation, or executable response |
| Deng, *Runtime Calibration as State-Trajectory Feedback Control in Quantum-Classical Workflows* (arXiv:2605.11860, 12 May 2026) | When to recalibrate during variational workloads under drift; feedback control under wall-clock budget | Not cited here (out of scope: no integrity claim). Relevant to the planned operational follow-up |
| Qurator (arXiv:2604.05505, Apr 2026) | Scheduling hybrid workflows across heterogeneous cloud providers | Not cited here (scheduling excluded). Relevant to the planned operational follow-up |

Companion work by the authors is now disclosed in a dedicated subsection
(§II-C) with an explicit non-overlap statement: target-domain certificates
(Zenodo 10.5281/zenodo.21776862; submitted to EPJ Quantum Technology),
conditional validity of quantum event classifiers (arXiv:2609.02781), and
candidate comparability before promotion (Zenodo 10.5281/zenodo.22239106).

The frozen novelty statement is unchanged. The recheck must be repeated on the
day of upload.


## Addendum — recheck on 7 September 2026 (artifact 1.2.0)

The claim was reformulated for 1.2.0 as: *characterization of observational
indistinguishability and integrity blind regions across the evidence
boundaries of hybrid quantum-classical workflows, including the
evaluation-label path as a protected boundary, with explicit trusted-reference
assumptions, multi-environment validation and executable, calibrated,
fail-closed policy composition.* The search was widened beyond quantum machine
learning to the lines that already establish that detectability depends on the
monitor's information, so that the article does not sell that insight as
novelty and positions itself against them explicitly.

| Line / work | What it already contributes | Consequence for this paper | Remaining distinction |
|---|---|---|---|
| Pasqualetti, Dörfler, Bullo (IEEE TAC 2013); Teixeira, Shames, Sandberg, Johansson (Automatica 2015); Liu, Ning, Reiter (CCS 2009 / TISSEC 2011) | Undetectable / stealthy attacks defined through the observability of the monitored dynamics; attack space by knowledge, disclosure and disruption resources; false-data injections in the estimator's range space | **The general insight "detectability is information-relative" is prior art.** Cited in §II-A and Table 1; the introduction states it explicitly | Object is an evidence chain of a learning workflow, blind regions derived from views rather than linear dynamics, evaluation labels as a protected boundary, trusted reference made explicit as exact-versus-statistical separation, coverage composed into a calibrated decision |
| Bai, Pasqualetti, Gupta (Automatica 2017); Urbina et al. (CCS 2016); Giraldo et al. (ACM CSUR 2018) | ε-stealthy attacks and detectability–impact trade-offs; limiting impact of stealthy attacks; physics-based detection as the question of which residuals can be formed | Cited; the unsafe-allow / false-hold trade-off of Gate D is the analogue in this setting | Batch-level versus reference-anchored auditors; no linear-system model |
| Sha (IEEE Software 2001, Simplex); Leucker & Schallhart (JLAP 2009, runtime verification); Kim & Spafford (CCS 1994, Tripwire) | Runtime assurance by switching to a verified controller; runtime verification against specifications; integrity checking against stored trusted digests | Cited in §II-A and Table 1; the fail-closed `hold` and the hash chain have this lineage | The decision is conditioned on the information regime and on a calibrated family statistic, with a measured unsafe-allow endpoint |
| Northcutt, Athalye, Mueller (NeurIPS D&B 2021) | Pervasive label errors in test sets change benchmark rankings | Cited in §II-B: labels are a quality problem in prior work | Here the label path is an asset under intervention and availability is separated from trust |
| Peltonen, Stirbu, Mikkonen, Pautasso, *Toward Standardized Quantum Provenance* (arXiv:2608.08272, 8 Aug 2026) | Cross-provider provenance schema and OpenAPI contract; no attestation or signatures | Cited in §II-C. Relevant to Paper 2.5 (provider/context evidence) | This paper's provenance is a trusted reference in the formal model, not a schema |
| Tippett (1931); Westfall & Young (1993); Vovk, Gammerman, Shafer (2005) | Minimum-p combination; resampling-based max-statistic family-wise calibration; conformal order-statistic thresholds under exchangeability | Cited for Proposition 5; **no novelty is claimed for the family-wise calibration method** | Its application as the decision-level budget of an information regime, evaluated end to end, and the measured violation of exchangeability by overlapping draws |
| QCIVET (arXiv:2605.13109), QML-PipeGuard (arXiv:2605.25066), Ahmed et al. (arXiv:2604.26430), Bajaj (arXiv:2608.02786), Solozobov (arXiv:2604.15740) | As recorded on 9 August and 6 September 2026 | Positions unchanged; the sentence "We found no previous study…" was removed and replaced by a positive delimitation ("prior work addresses A/B/C; this work differs in D/E/F") | Unchanged |

No new work was found (arXiv, publisher records, forward citations of QCIVET
and QML-PipeGuard, searches on "evaluation integrity", "label integrity",
"observability" + "monitoring" + "machine learning", "quantum provenance",
"runtime assurance" + "quantum") that formalizes blind regions of a learning
workflow's evidence chain with the evaluation-label path as a protected
boundary and explicit trusted references, or that evaluates an
information-aware calibrated fail-closed policy end to end. The frozen novelty
statement is updated to the reformulated claim above; the recheck must be
repeated on the day of upload.


## Addendum — recheck on 7 September 2026 (artifact 1.3.0, final closure)

Searches repeated (arXiv listings and web search) for: conformal anomaly
detection with family-wise or trials-factor calibration (2026 preprints
found: `nonconform`, arXiv:2605.13642, a software package for conformal
anomaly detection with FDR control; conformal calibration and the
look-elsewhere effect in new-physics anomaly searches, arXiv:2606.13780;
adaptive conformal anomaly detection with time-series foundation models,
arXiv:2604.20122); quantum machine-learning pipeline integrity and provenance
(QML-PipeGuard, arXiv:2605.25066, already positioned; nothing newer on
evaluation-label integrity or blind regions). None of these formalizes blind
regions of a learning workflow's evidence chain, treats the evaluation-label
path as a protected boundary, or measures fingerprint-preserving adaptive
evasion against a family-wise calibrated multi-sensor audit. The three 2026
conformal preprints are complementary applications of the same order-statistic
theory that the article cites through Vovk, Gammerman and Shafer (2005),
Laxhammar and Falkman (2015), Bates et al. (2023) and Angelopoulos and Bates
(2023); they are not added to the reference list because they do not change
the argument and the article is at the page ceiling.

Frozen novelty statement for 1.3.0 (supersedes the 1.2.0 wording in one
point): the conformal family rule is an application of known conformal
p-value theory to the multi-sensor audit decision; the article claims its
placement in the view lattice, the exact decision-level level under a stated
premise, and the measured decomposition of the earlier rule's excess into rule
bias and design effect, not a new statistical rule. The adaptive
cluster-preserving attacker is claimed as the executed instance of sensor
insufficiency against an adaptive adversary within the same lattice, not as a
general evasion bound. The recheck must be repeated on the day of upload.

## Addendum — VAMP (artifact 1.3.1, 7 September 2026)

Evaluated: J. W. Stokes, P. England and K. Kane, "Preventing machine learning
poisoning attacks using authentication and provenance," MILCOM 2021, pp.
181–188 (arXiv:2105.10051), which proposes VAMP, an extension of the AMP
media-provenance manifests to machine learning: datasets, software components,
trained models and evaluation sets are signed and bound by provenance
manifests so that a poisoned or substituted artifact fails authentication.

Verdict: relevant and added to §II-B and to the positioning table. What it
protects: the integrity and origin of the artifacts as objects, through
cryptographic authentication rooted in a signing infrastructure. It is the
closest prior work on authenticating evaluation sets and it is exactly the
"uncontrolled root" that Proposition 6 requires. What it does not ask, and
this article adds: which interventions stay indistinguishable to an auditor
who lacks that root (information-relative blind regions), whether an
aggregate or an item-level reference suffices for a given integrity notion
(conclusion versus identity), whether a passing substitution changes the
reported conclusion (materiality), how to calibrate the decision when only a
statistical baseline exists (conformal family rule), and what an adaptive
attacker can hide from a calibrated sensor (Gate A). No artificial difference
is constructed: the article states that a VAMP-style manifest is one way to
instantiate the trusted references it assumes, and the positioning table
credits VAMP with the provider/authentication evidence this work lacks.
