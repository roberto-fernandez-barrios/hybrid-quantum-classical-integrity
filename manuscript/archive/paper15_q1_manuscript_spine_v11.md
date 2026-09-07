# Information-Set Conditional Integrity Auditing for Hybrid Quantum-Classical Kernel Workflows

Anonymous manuscript for double-anonymized review  
Target venue: *Computers & Security* (full-length research article)

## Abstract

Integrity auditing asks whether evidence exposed at a workflow boundary can
identify a consequential intervention. We formalize **information-set
conditional auditability** and link interventions, evidence regimes, sensor
families, blind regions and responses. For a fixed deterministic predictor,
evaluation-label changes leave feature and prediction statistics invariant; if
class counts are preserved, label-marginal statistics are invariant too. These
elementary results support an integrated coverage methodology rather than a
standalone theorem claim.

We evaluate an RBF support-vector classifier and three empirically distinct
fidelity-kernel profiles under 18 controlled interventions. A frozen CICIDS2017
gate and 360 exact-statevector expansion jobs cover CICIDS2017, UNSW-NB15 and
ToN-IoT, including scale and five fixed out-of-distribution settings. After
verified deduplication, the expansion contains 11,400 model-intervention
observations. All 3,600 evaluation-label observations leave features, scores and
predictions unchanged; all 1,800 prior-preserving cases also leave label
marginals unchanged. Every one of the 2,184 positive conclusion impacts changes
item-aligned joint-outcome evidence.

A separate 165-cell simulator gate shows complementary quantum-workflow
coverage: semantic controls prevent hash-only false alarms, parameterized
circuit changes are exposed, and algebraic checks miss positive-semidefinite
kernel substitution. Controlled finite-shot emulators exercise repeated
estimation. A four-contract demonstrator converts the coverage map into
hash-chained, fail-closed `allow/hold/block` decisions across six scenarios.
The contribution is the combined formalization, coverage validation, bounded
quantum layer and executable response. Heterogeneous ZZ-versus-SVC effects are
secondary. No hardware, scheduling, provider, multi-tenancy or operational
Fleet Management claim is made.

**Keywords:** hybrid quantum-classical systems; quantum machine learning;
quantum kernels; integrity auditing; observability; sensor coverage;
cybersecurity

## 1. Introduction

Hybrid quantum-classical software distributes one reported result across several
computational and evidential boundaries. Classical records are acquired,
cleaned, projected and encoded; a circuit and execution stack produce quantum
evidence; a classical learner converts a kernel or measurement into a decision;
and an evaluation layer aligns that decision with reference outcomes and reports
a metric. A plausible final number may therefore coexist with a failure in the
data, circuit, kernel, prediction, label, or reporting path. Security analyses
of hybrid systems accordingly call for lifecycle-wide controls rather than trust
in an isolated algorithm [Volya2023, Ghosh2023].

Robustness benchmarking normally collapses this chain into a performance change.
That endpoint is necessary, but it does not identify what changed or whether the
available evidence could reveal the change. A large performance loss can be easy
to diagnose because several independent sensors react. A smaller loss may be a
more serious integrity failure when it changes the reported conclusion while
every sensor available to the evaluator remains invariant. Conversely, a drift
statistic can react strongly even when the fixed decision is unchanged. Impact,
observability and response are different axes.

The distinction matters especially at the evaluation boundary. Let a deployed
predictor receive exactly the same feature batch and emit exactly the same
predictions, but let the reference labels used to score that batch be corrupted.
The reported balanced accuracy can change although the model has not degraded.
A feature monitor cannot observe the event because its input is unchanged. A
prediction monitor adds no information because the predictions are unchanged. A
label-count monitor can expose an unbalanced corruption, but a balanced exchange
of class identities leaves that marginal invariant. Detection then requires an
item-aligned comparison between outcome and prediction, independently
authenticated labels, or provenance that binds labels to items. Calling the
event simply “stealthy” suppresses the crucial qualifier: stealthy to whom, with
which evidence?

This paper makes that qualifier explicit. **Information-set conditional
auditability** evaluates an intervention relative to the evidence exposed at a
workflow boundary and to a declared sensor family. It separates changes in model
output from changes in the evidence used to evaluate that output, then records
the remaining blind region. Quantum kernels are a useful bounded demonstrator:
their workflow crosses classical preprocessing, parameterized circuit
construction, fidelity evaluation, a kernel matrix, a classical support-vector
decision and an outcome-based evaluation. The setting is quantum-specific
without requiring claims about a physical processor.

Three research questions organize the study:

- **RQ1 — conditional identifiability:** Which controlled interventions are
  observable from feature, prediction, label-marginal, item-aligned outcome and
  quantum-workflow evidence, and where are the exact blind regions?
- **RQ2 — transport of the coverage boundary:** Do the information-set blind
  regions recur across datasets, fixed ID/OOD environments, projected
  dimensions and classical/quantum kernel profiles?
- **RQ3 — quantum-boundary composition:** Do provenance, semantic, algebraic,
  repeated-estimation and output sensors provide complementary coverage, and can
  their evidence drive an executable fail-closed decision?

The contribution is one integrated package, not a claim that any constituent is
individually new:

1. a workflow formalization that separates model-output, evaluation-conclusion
   and execution-integrity effects and conditions every auditability claim on an
   information set;
2. exact blind-region statements plus an attack-to-sensor coverage method that
   distinguishes structural invariance from low empirical detector power;
3. multi-dataset and fixed-OOD validation with verified computational-unit
   deduplication and uncertainty clustered at the data-split level;
4. a bounded quantum-specific layer combining circuit/kernel provenance,
   semantic comparison, algebraic validation, repeated estimation and output
   monitoring; and
5. an executable four-contract demonstrator whose `allow/hold/block` policy
   makes the declared coverage operational at a local research-prototype level.

The paper deliberately does **not** claim that Propositions 1--2 are deep new
impossibility theorems, that contracts or hash chains originate here, or that a
particular quantum feature map is universally less robust than an RBF kernel.
The scope covers data-to-evaluation integrity and selected simulated
quantum-kernel boundaries. Quantum hardware, calibrated backend noise,
scheduling, provider-side security, multi-tenant interference and the project's
Fleet Management case study are outside the scientific claim.

## 2. Related work and positioning

### 2.1 Hybrid quantum-classical security and integrity

Volya et al. decompose classical-quantum systems into classical control,
compilation, quantum execution and measurement surfaces, showing why security
cannot be inferred from the circuit alone [Volya2023]. Surveys broaden this view
to malicious compilation, hardware faults, cloud exposure, side channels and
classical dependencies [Ghosh2023, Saki2022]. Quantum Vulnerability Factor
quantifies changes in circuit output distributions under injected faults
[Oliveira2024], and Quantum Leak demonstrates timing leakage in cloud quantum
services [Lu2025]. These studies establish the threat surface and impact metrics;
they do not make auditability conditional on the evidence exposed to a sensor.
Our empirical scope is narrower than their lifecycle, and our claim is about the
coverage argument within that scope.

The closest direct overlap is QCIVET, a concurrent 2026 preprint that models a
hybrid pipeline with explicit contracts, hash-chained audit traces and semantic
observable checks grounded in behavioural subtyping [YeniarasKarimov2026]. It
also includes calibrated-noise and real-QPU evidence that this paper does not
possess. Consequently, stage contracts, hash chains and fail-closed verification
are not claimed here as standalone novelty. The distinction is the unit of
analysis: we ask which *information set* makes a changed asset identifiable,
treat evaluation labels and conclusions as first-class boundaries, validate an
attack-to-sensor coverage map across multiple data environments, and use the
contract only to execute that map.

A second concurrent line evaluates circuit integrity with complementary
structural, interaction and behavioural scores [Ahmed2026]. It reinforces the
case against a one-metric integrity claim. Our quantum gate reaches the same
general lesson in a kernel workflow but embeds it in a wider evidence lattice
that includes classical features, predictions, item-aligned labels and the
reported benchmark conclusion. We therefore do not claim that complementarity
among circuit metrics is itself new.

### 2.2 Quantum software testing, verification and contracts

Quantum software testing addresses the oracle problem through cross-stack or
semantics-preserving variants. QDiff uses differential testing of quantum
software stacks [Wang2021]; MorphQ generates quantum-specific metamorphic
relations for Qiskit and revealed platform bugs [Paltenghi2023]; and QEMI extends
equivalence-modulo-inputs testing to Qiskit, Q# and Cirq [Luo2026]. Formal and
runtime approaches include CertiQ compiler verification [Shi2019], quantum
program logics [Ying2011, Zhou2019], projection-based runtime assertions
[Li2020], and design-by-contract proposals for quantum software
[Yamaguchi2023].

These methods verify programs, compilers or semantic relations. The benign
transpilation and common-unitary conditions in our simulator gate are therefore
negative controls, not a claim to have invented metamorphic testing. Our target
is different: to expose what a provenance hash, semantic probe, algebraic check,
repeated estimate or final prediction can and cannot establish about one hybrid
kernel workflow. The result is a sensor-coverage contract rather than a general
quantum compiler or platform tester.

### 2.3 Monitoring under incomplete or delayed labels

Classical monitoring work already makes clear that labels alter what can be
inferred. Black-box shift estimation detects and corrects label shift under
assumptions on the relationship between source and target distributions
[Lipton2018]. MLDemon combines unlabeled observations with selectively acquired
labels to monitor deployed performance [Ginart2022], and recent
uncertainty-aware monitoring likewise uses active labeling intervention
[Koebler2025]. A concurrent evidence-sufficiency preprint studies delayed ground
truth, proxy coverage and the inability of feature proxies to detect pure
concept drift when the feature distribution is unchanged [Solozobov2026].

Our intervention should not be confused with statistical label shift. It changes
the *evaluation labels attached to fixed items* while holding the input and
predictor fixed; it is a controlled integrity failure in the scoring path.
Moreover, the label source may itself be compromised, so label availability is
not enough: the audit must distinguish a trusted item-aligned outcome from an
unauthenticated marginal. The contribution is thus not the general observation
that monitoring without labels is limited, but its integration into an explicit
hybrid-workflow coverage and response contract.

### 2.4 Benchmark validity, drift sensors and quantum kernels

MMD supplies a kernel two-sample statistic [Gretton2012], while KS summaries and
Jensen-Shannon divergence provide familiar univariate and histogram views. A
non-zero raw statistic is not automatically a calibrated alarm: thresholds,
false-alarm control and power belong to a deployment-specific test. This paper
therefore uses exact equality only for constructed invariances and describes
non-invariant sensor magnitudes without treating them as operating points.

Security-oriented ML benchmarks are vulnerable to sampling, labeling, baseline,
metric and threat-model errors [Arp2022]. Quantum-kernel benchmarks add strong
dependence on feature map, data encoding, preprocessing and classical comparator
[Schnabel2025]. Work on adversarial quantum kernels and QML poisoning asks
whether an attack changes performance and whether a defense recovers it
[Montalbano2025, Kundu2024]. Our secondary ZZ-versus-SVC profile belongs in this
benchmarking context. It is retained to show that impact profiles vary by model,
not to infer a universal quantum/classical ordering.

### 2.5 Resulting gap

Table 1 summarizes the nearest-work comparison. In the search reported in the
supplementary novelty audit, we found no prior study combining the same five
elements: information-set conditioning; labels and the evaluation conclusion as
explicit integrity boundaries; exact and empirical sensor blind regions;
multi-dataset/fixed-OOD validation in quantum-kernel workflows; and an
executable fail-closed instantiation. The novelty is this combination. Removing
the conditioning would reduce the paper to another detector benchmark; removing
the quantum layer would lose the hybrid boundary; and presenting the contract or
the two propositions alone would overlap established work.

| Line of work | Evidence conditioning | Evaluation-label boundary | Quantum evidence | Validation and response |
|---|---|---|---|---|
| Hybrid threat taxonomies [Volya2023, Ghosh2023] | none | no | broad lifecycle | taxonomy; no response |
| QCIVET [YeniarasKarimov2026] | stage observables/contracts | no | calibrated noise and QPU | three applications; verification engine |
| MorphQ/QDiff/QEMI [Wang2021, Paltenghi2023, Luo2026] | semantic relations | no | software stack | cross-platform test verdicts |
| Evidence sufficiency [Solozobov2026] | proxy coverage | delayed outcomes | no | one dataset; readiness gate |
| Circuit-integrity metrics [Ahmed2026] | fixed metric layers | no | circuit metrics | circuit corpus; no response |
| **This work** | **explicit evidence partial order** | **yes** | **bounded simulator** | **3 datasets; 8 environments; local fail-closed response** |

*Table 1. Positioning against the closest lines of work. “Partial” does not
denote inferiority; it denotes a different formal object. QCIVET includes QPU
evidence beyond the scope of this paper.*

## 3. Formal framework

### 3.1 Workflow and impact loci

Let a hybrid evaluation workflow be represented by

\[
\mathcal{W}=(X, P, C, K, E, f, y, R),
\]

where `X` is the acquired feature batch, `P` is classical preprocessing, `C` is the parameterized circuit or feature map, `K` is the estimated kernel, `E` is execution metadata, `f` is the resulting predictor, `y` is reference outcome information, and `R` is the reported evaluation result.

A perturbation `a` may act on one or more elements of `W`. We distinguish:

- **model-output impact**, measured by a change in predictions or scores on aligned items;
- **benchmark-conclusion impact**, measured by a change in a reported metric or comparative conclusion;
- **execution-integrity impact**, measured by a change in circuit, kernel, or execution evidence even when the final prediction is unchanged.

The current primary performance endpoint is the balanced-accuracy conclusion impact

\[
I_R(a)=BA_{clean}-BA_a.
\]

For aligned deterministic predictions, output impact includes

\[
I_f(a)=\frac{1}{n}\sum_{i=1}^{n}\mathbf{1}\{f_a(x_i)\neq f_0(x_i)\}.
\]

When `I_R(a)>0` but `I_f(a)=0`, the measured change lies in the evaluation or label path, not in the predictor output.

### 3.2 Information regimes

We use a partially ordered family of evidence sets rather than a falsely linear
hierarchy:

- `I_X`: features or preprocessed features only;
- `I_XF`: features plus model scores or predictions, with
  \(I_X \subset I_{XF}\);
- `I_Ym`: the evaluation-label marginal or class-count vector;
- `I_XFY`: item-aligned features, predictions and reference outcomes, which
  contains both `I_XF` and the outcome marginal;
- `I_Q`: circuit, transpilation, kernel-estimation and execution evidence.

`I_Ym` is not an intermediate step between `I_XF` and `I_XFY`, and `I_Q` is a
separate workflow branch that can be joined with classical evidence. A sensor
`S` is admissible in regime `I` if it is a measurable function only of evidence
in `I`. Auditability is therefore reported as `A(a | I, S)`, never as an
unqualified property of `a`.

### 3.3 Exact observability boundaries

**Proposition 1 (feature and prediction blindness to label-only perturbations).** Let `f` be fixed and deterministic. Let `T_y` transform only the evaluation labels, so that `X'=X` and `f'(X')=f(X)`. Then every audit statistic measurable with respect to `I_X` or `I_XF` is invariant under `T_y`.

**Proof.** The complete arguments supplied to such a statistic are identical
before and after the intervention. A deterministic function evaluated on
identical arguments returns the same value. Therefore no test based only on
those arguments can distinguish the two states. \(\square\)

**Proposition 2 (label-marginal blindness under prior preservation).** If `T_y` additionally preserves the empirical class histogram, every audit statistic measurable only with respect to `I_Ym` is invariant.

**Proof.** The sufficient input to the statistic, the empirical label-count
vector, is unchanged. \(\square\)

**Corollary 1.** Detecting a prior-preserving label-only perturbation requires at least one source outside `I_X`, `I_XF`, and the label histogram: joint label-prediction evidence, item-level provenance, an independently authenticated label source, or an assumption restricting admissible label transformations.

These propositions are finite-batch statements and require no distributional asymptotics. They describe sensor capability, not attack prevalence.

### 3.4 Conditional auditability gap

For an information regime `I`, sensor family `S`, and materiality threshold `tau`, an intervention belongs to the auditability-gap set if

\[
\mathcal{G}_{I,S}(\tau)=\{a:|I_R(a)|\geq \tau \;\wedge\; S(a)=S(0)\}.
\]

The absolute endpoint covers both degradation and apparent improvement caused by
an integrity failure; the present positive-impact counts use the signed drop for
interpretability. Exact invariance is used only where the intervention supplies
it. For non-invariant signals, practical detection requires a separately
calibrated alarm rule and false-alarm budget. A min-max-normalized stealth score
may summarize a fixed experiment, but it is neither the definition of an
auditability gap nor comparable outside its frozen normalization reference.

## 4. Methodology

### 4.1 Claim hierarchy and threat model

The primary estimand is sensor coverage conditional on an evidence set. Exact
blindness under constructed label-path interventions is Tier A evidence. The
multi-dataset and fixed-OOD replication of that coverage boundary is Tier B.
Model-profile differences, including ZZ versus SVC, are Tier C descriptive
evidence and cannot override the primary result.

The study is an integrity stress test. Its manipulations are controlled
interventions, not claims about attack prevalence or operational adversary
frequency. The data-to-evaluation gates trust the training routine and fitted
model artifact while changing evaluation features, post-projection values, or
labels. The quantum-specific simulator gate additionally permits
circuit/parameter mutation and post-estimation kernel corruption. Malicious
scheduling, calibrated backend tampering, multi-tenant interference,
provider-side manipulation, side channels and physical-device execution are
outside the empirical scope.

### 4.2 Data and fixed environments

Gate 1 uses a balanced binary subset derived from CICIDS2017
[Sharafaldin2018] with 3,000 rows and
77 numeric feature columns before projection and caps training/evaluation at
128/128. The expansion adds a prespecified 256/256 CICIDS scale gate; balanced
ID subsets from UNSW-NB15 [Moustafa2015] and ToN-IoT [Alsaedi2020]; four
temporal CICIDS train-test pairs;
and one UNSW temporal pair. Expansion jobs use 128/128 except for the scale
gate. All data-to-evaluation gates report projected dimensions 8, 10 and 12.

The eight expansion environments are CICIDS2017 ID at 256/256; UNSW-NB15 and
ToN-IoT ID; CICIDS Tuesday-to-Wednesday, Tuesday-to-Friday-PortScan,
Wednesday-to-Thursday-Web and Wednesday-to-Friday-AM temporal pairs; and one
UNSW-NB15 temporal pair. The two additional ID datasets retain all quantum
profiles; the scale and temporal gates compare SVC with ZZ. “OOD” identifies a
fixed source-to-target construction, not a sampled deployment population.

These are fixed benchmark environments, not a probability sample of
deployments. Each staged table is balanced at 3,000 rows; this is useful for a
controlled audit but does not reproduce operational class prevalence.
Categorical fields are excluded. Temporal OOD pairs are interpreted separately
because several clean baselines approach chance performance, constraining the
impact that subsequent interventions can express.

### 4.3 Preprocessing and models

Numeric non-finite values are replaced during staging, and train-defined
preprocessing is applied without using evaluation labels. Each pipeline uses
TruncatedSVD fitted on its training features. The RBF SVC branch then applies a
training-fitted standardization; the fidelity-kernel branch applies its frozen
training-fitted angular scaling to \([0,2\pi]\). Interventions are applied to the
resulting evaluation representation. No hyperparameter search is performed.
Accordingly, SVC/QSVC contrasts compare complete frozen pipelines and do not
identify an isolated causal effect of kernel geometry.

The classical comparator is an RBF SVC. Quantum models use fidelity quantum
kernels with `reps=1`. Four configured feature-map labels reduce to three unique
empirical profiles because Z and PauliXZ generate identical kernel matrices
under the frozen implementation: ZZ, PauliXYZ, and Z/PauliXZ-equivalent. The
analysis therefore does not count Z and PauliXZ as independent behaviours.

Gate 1 used Qiskit Machine Learning's reference ideal evaluator
[JavadiAbhari2024]. Expansion gates use an explicitly tagged
exact-statevector evaluator that prepares each unique feature-map state once and
computes \(K(x,y)=|\langle\phi(x)|\phi(y)\rangle|^2\) by matrix multiplication,
with the same
PSD repair for symmetric blocks. Unit matrices match the reference at `1e-10`;
an end-to-end 128/128 replay preserves every discrete endpoint and integrity
signal, with a maximum `0.0001222` difference confined to ROC-AUC quantities
(one half-tie increment). This engine is an ideal-simulation optimization and
supplies no shot-noise or QPU evidence.

### 4.4 Interventions

The 18 non-clean interventions comprise three frozen severities for each of six
mechanisms:

- feature sign flip;
- feature-wise mean shift;
- scaling drift;
- feature dropout;
- random label flip;
- prior-preserving label flip.

The first four may change model input and output. The last two keep features,
scores and predictions fixed and act only on the evaluation path. The code and
archived tables retain the historical family label `target_shift`; in the paper
these rows are called *evaluation-label interventions*, because they are not the
distributional label-shift setting of [Lipton2018]. Random flips may alter the
observed label marginal; prior-preserving exchanges do not. All six mechanisms
receive equal weight in the suite average. This is a transparent engineering
profile, not an estimate of real-world threat frequency.

### 4.5 Sensor families

Feature-only evidence uses feature JSD, MMD, and the KS rejection rate. Prediction-aware evidence adds score-distribution JSD. Label-marginal evidence uses prior shift and label JSD. Joint-outcome evidence includes prediction-rate, disagreement, prediction-distribution, and confusion-profile changes.

Sensor-family results are primary. Shared min-max normalization is retained only for within-design descriptive summaries. Raw invariance is used for structural-blindness claims.

### 4.6 Experimental units, endpoints and uncertainty

Gate 1 crosses five split seeds `{42,43,44,45,46}` with four nested model/perturbation seeds `{42,43,44,45}`. The raw grid contains 7,980 rows. Because every quantum-map CSV repeats the same classical pipeline, 3,420 SVC rows are exact computational repetitions. Equality is verified across performance, impact, and signal columns before deduplication, leaving 4,560 unique model-attack observations.

The eight expansion environments cross the same five split seeds with two nested model seeds `{42,43}`. All 360 expected CSV/JSON job pairs completed. Their 13,680 raw rows contain 2,280 verified repeated SVC rows from the multi-map ID gates, leaving 11,400 unique observations. No repeated key is collapsed unless performance, impact, and raw sensor evidence agree numerically.

The primary coverage endpoints are exact raw invariance/response counts within
the prespecified design. The secondary model-profile endpoint is the
within-split difference in suite-average balanced-accuracy conclusion impact.
The split seed is its inferential unit: model-seed values are averaged within
split, giving five clusters. Two-sided 95% Student-t intervals use four degrees
of freedom. They describe resampling uncertainty inside each fixed environment;
they are not population intervals and are not adjusted for simultaneous testing.
Analyses over all 20 split-model combinations are sensitivity analyses and are
not interpreted as 20 independent external replications.

### 4.7 Quantum-specific integrity gate

A separate simulator gate isolates the quantum-workflow boundary using CICIDS, 64/64 train/evaluation rows, five split seeds, projected dimensions 4, 6, and 8, and 11 conditions, for 165 split-dimension-condition cells. The clean negative control is compared with benign level-1 transpilation; a common post-feature-map X rewrite that must preserve fidelity; data-dependent RZ mutations at strengths 0.02 and 0.10; a feature-map repetition change from one to two; asymmetric, diagonal-eroded, and symmetric PSD-preserving kernel edits; and binomial fidelity-estimation emulators at 256 and 1,024 shots.

Each cell records canonical OpenQASM 3 circuit and parameter provenance, kernel hashes, semantic kernel differences against a trusted reference, symmetry/diagonal/eigenvalue checks, repeated-estimation discrepancy, and prediction changes. The shot conditions sample exact fidelities and therefore assess the sensor contract under controlled stochastic estimation; they are not sampler-backend or QPU executions. Acceptance checks are prespecified for the clean contract, semantic-preserving controls, circuit-mutation sensitivity, algebraic fault detection, the algebraic blind region, and finite-shot repeat disagreement.

The intended countermeasure is layered: authenticated circuit and parameter provenance, an approved-transpilation policy, semantic probe kernels, algebraic validation, repeated estimation with uncertainty bounds, PSD repair as containment rather than evidence of integrity, and output monitoring. No single sensor is treated as sufficient.

### 4.8 Executable service-contract demonstrator

A local HSaaS research prototype instantiates four ordered contracts: input/preprocessing, circuit/kernel, execution/result, and evaluation/report. Each contract records evidence, violations, and review conditions in an SHA-256 chain. Only four passes yield `allow`; any review yields a fail-closed `hold`, and any violation yields `block`. The chain detects later modification but is not a provider-authenticated digital signature.

The demonstrator uses one compact CICIDS cell (split 42, dimension 4, 32/32 rows) and six prespecified scenarios: clean, approved transpilation, parameterized circuit mutation, PSD-preserving kernel substitution, prior-preserving label corruption, and an approved 256-shot binomial emulator. This experiment assesses countermeasure composition and decision logic, not predictive generalization or service throughput.

## 5. Results

### 5.1 Label-path failures expose exact sensor blind regions

All random and prior-preserving evaluation-label cells have zero prediction
disagreement: the model receives the same `X` and emits the same predictions.
Feature JSD, MMD, KS rejection, and score JSD are also exactly unchanged.
Balanced-accuracy conclusion impact is non-negative in the executed design, but
not strictly positive in every cell. Gate 1 contains 1,276 positive-impact and
164 zero-impact label observations out of 1,440; the expansion contains 2,184
positive-impact and 1,416 zero-impact observations out of 3,600. No negative
impact occurs. These are evaluation-path integrity failures when they alter the
conclusion, not robustness failures of the fixed predictor.

Prior-preserving flips additionally produce zero label-prior shift and zero
label JSD. They therefore occupy the exact blind region predicted by
Propositions 1 and 2. In Gate 1 at flip rate 0.10, their mean conclusion impacts
across evaluated model-dimension cells range from 0.0492 to 0.0633. Joint
confusion evidence reacts whenever the conclusion impact is positive, showing
that the observed gap closes when item-level outcomes are available and trusted.

The expansion reproduces these invariances without exception: all 3,600
evaluation-label rows are blind to feature-plus-prediction evidence and have
zero prediction disagreement, and all 1,800 prior-preserving rows are also blind
to label-marginal evidence. Of the 3,600 rows, 2,184 have positive conclusion
impact; every one has non-zero joint-outcome evidence. Thus the coverage
boundary, rather than an average detector score, replicates across all eight
fixed expansion environments (Figure 1).

![Empirical sensor response by information regime. Fractions are over
model/environment/seed cells; zero denotes raw invariance, not estimated
detector power, and practical alarms require separate
calibration.](figures/fig_q1_sensor_coverage.png)

Random label flips provide a useful negative control for the information-set argument. They remain invisible to feature-plus-prediction monitoring but are strongly visible to label-marginal monitoring. The perturbation has not become intrinsically less stealthy; the auditor has acquired a more informative view.

### 5.2 Suite-average model impact is feature-map specific

QSVC-ZZ has the largest mean balanced-accuracy conclusion impact in the frozen ID suite. Relative to SVC-RBF, its mean ratios are 2.524, 3.094, and 3.323 at dimensions 8, 10, and 12. Ratios are descriptive; paired differences are the inferential endpoint.

The within-split paired differences are 0.02427 (95% CI
0.01200--0.03654), 0.03289 (0.01998--0.04580) and 0.03855
(0.02773--0.04937), respectively; all five split clusters are positive at each
dimension. The corresponding ZZ/SVC impacts are 0.04019/0.01592,
0.04860/0.01571 and 0.05514/0.01659. These intervals summarize five split
clusters in one fixed environment and are not population claims.

This is a conditional property of the frozen pipelines, dataset, suite, and dimensions. It does not establish that quantum kernels are generally more vulnerable. The other quantum profiles occupy intermediate positions and confirm that "quantum" is not a homogeneous empirical category.

Across the eight expansion environments, the mean ZZ-minus-SVC difference is positive in 7/8 environments at dimension 8 and 8/8 at dimensions 10 and 12. Environment-specific 95% intervals exclude zero in 4/8, 7/8, and 5/8 environments, respectively. The means range from -0.00009 to 0.09382 at dimension 8, 0.00107 to 0.09508 at dimension 10, and 0.00403 to 0.11585 at dimension 12. This heterogeneity is shown in the fixed-environment forest plot in Figure 2; no pooled population effect is claimed.

![Environment-specific ZZ-minus-SVC mean conclusion-impact differences and 95%
t intervals over five split clusters. ID and OOD settings are shown separately;
no population pooling is
performed.](figures/fig_q1_external_forest.png)

### 5.3 Why a single stealth average is insufficient

An average over all normalized sensors mixes sensors that observe different information. Adding several structurally blind feature statistics can dilute one joint-outcome alarm; conversely, adding a label-aware signal assumes labels are available and trustworthy at audit time. Both change the scalar without changing the underlying evidence contract. For this reason the main result is the attack-to-sensor coverage matrix. Shared-normalized stealth remains a frozen-design sensitivity used to compare with the workshop artifact.

### 5.4 Cross-environment validation

All prespecified expansion gates completed with zero failed jobs. At dimension 8, seven of eight environment means for the secondary ZZ-minus-SVC profile are positive; at dimensions 10 and 12 all eight are positive. The number of environment-specific intervals excluding zero is not monotone with dimension and one OOD pair is effectively null, preventing a universal ordering claim. More importantly, the exact information-set blind regions replicate across every environment and model profile, including settings in which clean predictive performance is weak.

Clean balanced accuracy and suite-average conclusion impact correlate positively across expansion cells (`r=0.714`; exploratory), indicating substantial performance-headroom confounding in model-profile comparisons. The auditability result does not depend on this ordering: it is defined by invariance conditional on evidence and by whether a material conclusion change remains observable under a richer information regime.

### 5.5 Quantum-workflow sensor contract

All 165 prespecified cells are present and all nine acceptance checks pass under
the frozen numerical tolerance (`1e-8` for non-zero detection unless a stricter
contract check is stated). Clean cells trigger no sensor. Benign transpilation
and a common-unitary circuit rewrite change circuit and serialized-kernel
provenance while preserving semantic kernels, algebraic properties, and outputs
in every cell. They demonstrate that raw hashes require policy-aware
adjudication: provenance difference alone is not evidence of harmful semantic
change.

Every data-dependent circuit mutation changes the semantic kernel. The mild RZ mutation changes no evaluated prediction, the stronger mutation changes predictions in 2/15 cells, and increasing feature-map repetitions changes predictions in 11/15 cells. Conversely, every asymmetric and diagonal-eroded matrix is detected algebraically but changes no predictions at the tested severity. A PSD-preserving mixture remains symmetric, unit-diagonal, and positive semidefinite in all cells, so algebraic validation is exactly blind; trusted kernel provenance and semantic comparison detect all 15 substitutions, while output monitoring reacts in only 1/15.

Both stochastic estimators yield non-zero repeated-estimation discrepancy in all 15 cells. Output changes occur in 7/15 cells at 256 shots and 3/15 at 1,024 shots, with mean balanced-accuracy drops of 0.00521 and 0.00313. These are controlled binomial emulators, so the result supports repeated-estimation logic but not a claim about a physical device or calibrated noise model.

![Sensor-family response across clean and semantics-preserving controls, circuit
mutations, kernel corruptions and finite-shot emulators. Coverage is conditional
on the information exposed to each sensor; output invariance does not imply
workflow integrity.](figures/fig_q1_quantum_integrity_contract.png)

Figure 3 summarizes why these controls falsify any one-sensor security story.
Circuit hashes overreact to approved semantic equivalence, algebraic checks miss
valid-looking malicious substitutions, and output monitors miss changes before
they cross a decision boundary. The layered contract supplies complementary
coverage and makes every residual blind region explicit.

### 5.6 Executable countermeasure composition

All six service-contract envelopes verify and all eight acceptance checks pass. The clean run and explicitly approved transpilation receive `allow`: despite a circuit-hash change, the transpiled semantic-kernel difference is only `7.11e-15`, below the declared tolerance. Parameterized circuit mutation and PSD-preserving kernel substitution receive `block`; the latter remains symmetric, unit-diagonal, and positive semidefinite, confirming that the block depends on trusted semantic/provenance evidence rather than algebra alone.

Prior-preserving label corruption also receives `block` at the evaluation/report contract while its class-prior delta is exactly zero. The approved 256-shot emulator receives `hold`, not `allow`: stochastic differences and repeated-estimation evidence are expected but require uncertainty adjudication. Thus the prototype evaluates an actual response policy rather than merely enumerating sensors.

The prototype is packaged with a console entry point, tests, CI configuration,
a strict output manifest, and reviewer-facing summary table. It remains a local
process and makes no claim about network authentication, signed provider
records, persistence, incident handling, scheduling or QPU binding.

## 6. Integrity-audit contract for hybrid workflows

Every integrity claim should report seven fields:

1. **Boundary:** acquisition, preprocessing, circuit construction, transpilation, execution, kernel estimation, prediction, label, or reporting.
2. **Protected asset:** data, circuit IP, execution fidelity, kernel matrix, prediction, ground truth, or reported conclusion.
3. **Adversary or failure capability:** exactly which elements may change and which remain fixed.
4. **Information regime:** which of `I_X`, `I_XF`, `I_Ym`, `I_XFY`, and `I_Q` is available.
5. **Sensor and calibration:** raw statistic, null reference, threshold, and false-alarm budget.
6. **Coverage:** perturbations for which the sensor can react, exact blind regions, and empirical power where estimable.
7. **Response:** provenance failure, abstention, rerun, PSD repair, rollback, human adjudication, or another countermeasure.

For label-path integrity, the minimum defensive bundle is item-level label
provenance plus a joint label-prediction audit. The simulator gate evaluates the
corresponding bounded quantum-kernel bundle: circuit and parameter provenance,
transpilation-aware adjudication, semantic probes, kernel
symmetry/diagonal/PSD checks, repeated-estimation discrepancies, and a
fail-closed policy when evidence violates the contract. These controls specify
the evidence required inside the studied boundary; they do not certify any
provider or hardware boundary.

## 7. Discussion

### 7.1 Robustness and integrity are causally different

The label-path result is intentionally simple because it exposes a common category error. A performance metric can fall even though the model output is bit-for-bit unchanged. Calling that event model degradation assigns the failure to the wrong component and suggests the wrong defense. Input robustness cannot repair corrupted ground truth; provenance and joint validation can.

### 7.2 Auditability claims must name their information set

Zero response is evidence only when a sensor had access to information capable of distinguishing the states. This principle applies beyond label corruption. A circuit hash cannot detect a calibration change, a kernel PSD check cannot establish label provenance, and an output monitor cannot protect circuit confidentiality. Hybrid security therefore needs a coverage argument across boundaries rather than one global anomaly score.

### 7.3 The quantum result is a profile, not a universal ordering

QSVC-ZZ's larger suite-average impact is directionally consistent in most fixed environments, but its magnitude and interval support vary sharply across ID/OOD pairs. Clean-performance headroom, pipeline-specific scaling, and kernel geometry are entangled. A causal attribution to quantum geometry would require symmetric preprocessing controls, headroom-aware endpoints, kernel-level interventions, or a decomposition experiment. Until then the paper reports feature-map-specific profiles and avoids universal classical-versus-quantum vulnerability language.

### 7.4 Relationship to ATHENA-AEGIS

The framework provides direct evidence for ATHENA-AEGIS G3.2 (validation and
verification across the studied hybrid steps) and G3.3 (metrics, threat
identification and enforcement), and selected simulator evidence for G3.1. It
covers classical preprocessing, prediction, outcome and result interpretation;
adds bounded evidence for circuit construction, benign transpilation
equivalence, controlled kernel corruption and stochastic fidelity estimation;
and executes the resulting policy through a four-contract local prototype. The
software is therefore a research contribution towards Result 3.1 and the
manuscript supports Result 3.2; neither result is claimed complete for the whole
project.

Within WP5, a submitted or published article contributes to Task 5.2 and its
scientific-dissemination report. This paper does not implement Task 5.1 or
Result 5.1, the operational Fleet Management case study. Dataset choice and the
local HSaaS demonstrator must not be used to imply that operational use-case
coverage.

### 7.5 What the integrated contribution adds

The closest precedents each cover an important portion of the design. QCIVET
already supplies stage contracts, hash-linked traces and stronger backend/QPU
evidence [YeniarasKarimov2026]; evidence-sufficiency monitoring formalizes
limitations of proxies under delayed outcomes [Solozobov2026]; circuit-integrity
metrics and quantum software testing establish complementary quantum-side
checks [Ahmed2026, Wang2021, Paltenghi2023, Luo2026]. This paper's additional
claim is narrower but joint: the audit conclusion is indexed by the exact
information exposed, the evaluation-label path is a first-class protected
boundary, structural blind regions are separated from empirical response, the
coverage boundary is replayed across fixed dataset/OOD environments, and the
same coverage map drives a fail-closed local decision. None of the propositions,
contracts, hashes, sensors or model comparisons is presented as sufficient
novelty alone.

## 8. Limitations

First, the expansion includes three datasets and multiple temporal pairs, but these are eight fixed cybersecurity environments assembled from repository subsets. They improve transport evidence but are not a random sample of deployments, and five split clusters quantify within-environment sampling rather than population-level generalization.

Second, most gates cap training and evaluation at 128; the completed 256/256 CICIDS gate is a scale sensitivity, not evidence of large-scale quantum-kernel deployment.

Third, both the archived Qiskit reference evaluator and the accelerated exact-statevector evaluator operate in ideal simulation. The quantum-specific gate adds controlled binomial shot estimation, but not a sampler backend, device-calibrated noise, or hardware experiment.

Fourth, SVC and QSVC use their frozen pipeline-specific scalers. The study compares complete pipelines; it does not causally isolate preprocessing from kernel geometry.

Fifth, the quantum-specific gate covers controlled circuit/parameter mutation, benign transpilation equivalence, post-estimation matrix corruption, and finite-shot emulation. It does not cover malicious compiler or scheduler attacks, calibrated hardware noise, provider manipulation, multi-tenant interference, or side channels.

Sixth, exact blindness is a capability statement under the specified perturbation. It does not estimate how often such failures occur in deployment or imply malicious intent.

Seventh, min-max stealth is reference-dependent and retained only as a secondary sensitivity. A practical alarm requires null calibration, false-alarm control, and detection-power estimates.

Eighth, the HSaaS demonstrator is an executable local contract, not a deployed
network service or an authenticated provider ledger. Its hash chain is
tamper-evident but supplies neither identity nor non-repudiation. The article
does not evaluate Fleet Management, scheduling, provider security,
multi-tenancy or physical quantum execution; those topics are excluded rather
than deferred experimental claims of this study.

## 9. Conclusion

Hybrid workflow integrity cannot be reduced to a robustness number. A perturbation can change a reported conclusion without changing the model, and a detector can remain silent because the evidence it sees is mathematically invariant. We formalized this dependency through information-set conditional auditability, proved exact blind regions for label-only and prior-preserving perturbations, and reproduced those boundaries across CICIDS, UNSW-NB15, ToN-IoT, and eight fixed expansion environments. The feature-map-specific QSVC-ZZ impact profile is directionally consistent in most environments but heterogeneous and headroom-confounded, so it remains secondary and conditional.

The methodological requirement is straightforward: every integrity claim must
state the workflow boundary, information available, sensor coverage, residual
blind region and response. This turns auditability from an unqualified scalar
into a bounded evidence contract. The data-to-evaluation layer has
multi-dataset, temporal, scale and clustered evidence; the quantum-specific
simulator layer validates complementary controls; and the packaged HSaaS
prototype turns those controls into fail-closed decisions. The resulting claim
is complete for the declared research boundary and intentionally makes no
full-lifecycle, provider, Fleet Management or hardware-security claim.

## Declarations

**Funding.** Funding details are supplied on the separate title page and are
withheld from this file for double-anonymized review.

**Data and code availability.** The review artifact contains the source code,
locked environment specification, tests, compact derived tables, figures,
SHA-256 manifests and exact reproduction commands. Raw CICIDS2017, UNSW-NB15
and ToN-IoT data are not redistributed; the documentation records their public
sources and deterministic staging steps. During double-anonymized review the
archive is supplied without author-identifying metadata. The version DOI is to
be inserted in the unblinded record after archival.

**Ethics.** The study uses previously released network-security benchmark data
and performs no research involving human participants, animals or newly
collected personal data.

**Competing interests and author contributions.** These declarations are kept
on the separate title page for double-anonymized review and require confirmation
by all authors before upload.

**Declaration of generative AI and AI-assisted technologies.** During
manuscript and artifact preparation, the authors used OpenAI Codex for
literature-discovery assistance, language editing, code inspection and test
automation. The authors verified the cited primary sources, numerical claims
and generated edits and retain full responsibility for the article.

## References

[Ahmed2026] Ahmed, E., Ye, B., Shah, S. H., Akbar, M. A., & Khan, A. A.
(2026). A multi-level integrity evaluation framework for quantum circuits under
controlled anomaly injection. arXiv:2604.26430.

[Alsaedi2020] Alsaedi, A., Moustafa, N., Tari, Z., Mahmood, A., & Anwar, A.
(2020). TON_IoT telemetry dataset: A new generation dataset of IoT and IIoT for
data-driven intrusion detection systems. *IEEE Access, 8*, 165130-165150.
https://doi.org/10.1109/ACCESS.2020.3022862

[Arp2022] Arp, D., Quiring, E., Pendlebury, F., Warnecke, A., Pierazzi, F.,
Wressnegger, C., Cavallaro, L., & Rieck, K. (2022). Dos and don'ts of machine
learning in computer security. In *31st USENIX Security Symposium*, 3971-3988.

[Ghosh2023] Ghosh, S., Upadhyay, S., & Saki, A. A. (2023). A primer on
security of quantum computing. arXiv:2305.02505.

[Ginart2022] Ginart, A., Zhang, L., Zou, J., & Garg, A. (2022). MLDemon:
Deployment monitoring for machine learning systems. In *Proceedings of the 25th
International Conference on Artificial Intelligence and Statistics*, PMLR 151,
3962-3997.

[Gretton2012] Gretton, A., Borgwardt, K. M., Rasch, M. J., Scholkopf, B., &
Smola, A. (2012). A kernel two-sample test. *Journal of Machine Learning
Research, 13*, 723-773.

[JavadiAbhari2024] Javadi-Abhari, A., Treinish, M., Krsulich, K., Wood, C. J.,
Lishman, J., Gacon, J., Martiel, S., Nation, P. D., Bishop, L. S., Cross, A. W.,
& Johnson, B. R. (2024). Quantum computing with Qiskit. arXiv:2405.08810.

[Koebler2025] Koebler, D., Temme, M., Bischl, B., Casalicchio, G., & Feurer,
M. (2025). Uncertainty-aware performance monitoring of machine learning
models. In *Proceedings of the 28th International Conference on Artificial
Intelligence and Statistics*, PMLR 258.

[Kundu2024] Kundu, S., & Ghosh, S. (2024). Adversarial poisoning attack on
quantum machine learning models. arXiv:2411.14412.

[Li2020] Li, G., Zhou, L., Yu, N., Ding, Y., Ying, M., & Xie, Y. (2020).
Projection-based runtime assertions for testing and debugging quantum programs.
*Proceedings of the ACM on Programming Languages, 4*(OOPSLA), Article 150.
https://doi.org/10.1145/3428218

[Lipton2018] Lipton, Z. C., Wang, Y.-X., & Smola, A. J. (2018). Detecting and
correcting for label shift with black box predictors. In *Proceedings of the
35th International Conference on Machine Learning*, PMLR 80, 3122-3130.

[Lu2025] Lu, C., Telang, P. R., Aysu, A., & Basu, K. (2025). Quantum Leak:
Timing side-channel attacks on cloud-based quantum services. In *Proceedings of
the 2025 ACM SIGSAC Conference on Computer and Communications Security*.
https://doi.org/10.1145/3716368.3735264

[Luo2026] Luo, J., Xia, S., Zhang, F., & Zhao, J. (2026). QEMI: A quantum
software stacks testing framework via equivalence modulo inputs.
arXiv:2602.09942.

[Montalbano2025] Montalbano, G., & Banchi, L. (2025). Quantum adversarial
learning for kernel methods. *Quantum Machine Intelligence, 7*, 15.
https://doi.org/10.1007/s42484-025-00238-8

[Moustafa2015] Moustafa, N., & Slay, J. (2015). UNSW-NB15: A comprehensive
data set for network intrusion detection systems. In *2015 Military
Communications and Information Systems Conference*.
https://doi.org/10.1109/MilCIS.2015.7348942

[Oliveira2024] Oliveira, D., Giusto, E., Baheri, B., Guan, Q., Montrucchio,
B., & Rech, P. (2024). A systematic methodology to compute the quantum
vulnerability factors for quantum circuits. *IEEE Transactions on Dependable
and Secure Computing, 21*(4), 2631-2644.
https://doi.org/10.1109/TDSC.2023.3313934

[Paltenghi2023] Paltenghi, M., & Pradel, M. (2023). MorphQ: Metamorphic
testing of the Qiskit quantum computing platform. In *45th IEEE/ACM
International Conference on Software Engineering*.
https://doi.org/10.1109/ICSE48619.2023.00202

[Saki2022] Kundu, S., & Ghosh, S. (2022). Security aspects of quantum machine
learning: Opportunities, threats and defenses. In *Great Lakes Symposium on
VLSI 2022*. https://doi.org/10.1145/3526241.3530833

[Schnabel2025] Schnabel, J., & Roth, M. (2025). Quantum kernel methods under
scrutiny: A benchmarking study. *Quantum Machine Intelligence, 7*, 58.
https://doi.org/10.1007/s42484-025-00273-5

[Sharafaldin2018] Sharafaldin, I., Habibi Lashkari, A., & Ghorbani, A. A.
(2018). Toward generating a new intrusion detection dataset and intrusion
traffic characterization. In *Proceedings of ICISSP 2018*, 108-116.
https://doi.org/10.5220/0006639801080116

[Shi2019] Shi, Y., Tao, R., Li, X., Javadi-Abhari, A., Cross, A. W., Chong,
F. T., & Gu, R. (2019). CertiQ: A mostly-automated verification of a realistic
quantum compiler. arXiv:1908.08963.

[Solozobov2026] Solozobov, O. (2026). Evidence sufficiency under delayed
ground truth: Proxy monitoring for risk decision systems. arXiv:2604.15740.

[Volya2023] Volya, D., Zhang, T., Alam, N., Tehranipoor, M., & Mishra, P.
(2023). Towards secure classical-quantum systems. In *IEEE International
Symposium on Hardware Oriented Security and Trust*, 283-292.
https://doi.org/10.1109/HOST55118.2023.10133344

[Wang2021] Wang, J., Zhang, Q., Xu, G. H., & Kim, M. (2021). QDiff:
Differential testing of quantum software stacks. In *36th IEEE/ACM
International Conference on Automated Software Engineering*.
https://doi.org/10.1109/ASE51524.2021.9678792

[Yamaguchi2023] Yamaguchi, M., & Yoshioka, N. (2023). Design by contract
framework for quantum software. arXiv:2303.17750.

[YeniarasKarimov2026] Yeniaras, E., & Karimov, M. A. (2026). QCIVET: A
quantum-classical pipeline integrity framework with contract-based subtype
verification and hash-chained audit traces. arXiv:2605.13109.

[Ying2011] Ying, M. (2011). Floyd-Hoare logic for quantum programs. *ACM
Transactions on Programming Languages and Systems, 33*(6), Article 19.
https://doi.org/10.1145/2049706.2049708

[Zhou2019] Zhou, L., Yu, N., & Ying, M. (2019). An applied quantum Hoare
logic. In *40th ACM SIGPLAN Conference on Programming Language Design and
Implementation*, 1149-1162. https://doi.org/10.1145/3314221.3314584
