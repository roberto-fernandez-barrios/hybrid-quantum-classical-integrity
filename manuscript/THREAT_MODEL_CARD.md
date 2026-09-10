# Threat-model card — Paper 1.5 / ATHENA-AEGIS

Version: 3.3 (2026-09-09; terminology aligned in corrective release 1.3.4;
artifact 1.3.2 audited reference semantics and
gross/net trusted-cost distinction; 3.1 was the 1.3.1 reference taxonomy, P3 name and
definition, trusted-cost decomposition, quantum kernel notions; version 3.0 of
the same day for 1.3.0; version 2.0 for 1.2.0; version 1.0 dated 2026-08-09)  
Scope: integrity and auditability of a hybrid quantum-classical kernel workflow.
The per-class adversary and failure model is `ADVERSARY_MODEL.md`; the formal
objects (views, trusted references, blind regions, the quantum lattice) are
`FORMAL_CORE.md`. This card is the short reference.

## System and protected conclusion

The system transforms an intrusion-detection dataset into a reported model
evaluation through acquisition, preprocessing/projection, quantum feature-map
construction, transpilation, fidelity-kernel estimation, classical SVC
decision, reference labels, and metric/report generation.

The primary protected asset is the evidentiary chain supporting the reported
conclusion: *which model produced which output from which data, circuit,
kernel estimate, labels, and execution context*. The evaluation-label path is
a protected boundary in its own right.

## Trust boundaries

| Boundary | Protected assets | Evidence in the frozen artifact |
|---|---|---|
| B1 Acquisition/input | rows, feature schema, source identity | Data hashes, schema and preprocessing manifest |
| B2 Preprocessing | imputer/SVD/scaler state and transformed features | Train-fit policy, configuration and array hashes |
| B3 Circuit design | feature map, parameters and intended semantics | Canonical OpenQASM 3 and parameter provenance; semantic probes |
| B4 Transpilation | approved rewrite and semantic preservation | Benign transpilation differential; circuit and kernel comparison |
| B5 Execution/estimation | backend mode, shots, repeated estimates | Ideal statevector plus binomial estimator emulator |
| B6 Kernel/post-processing | matrix identity and mathematical validity | Hash, semantic delta, symmetry, diagonal, eigenvalue and repair evidence |
| B7 Prediction | predicted class, score and model identity | Prediction hashes, disagreement and score evidence |
| B8 Evaluation/report | labels, joint outcomes and reported metrics | Label provenance, joint hash, metric recomputation, signed conclusion change |

## Classes of intervention (see `ADVERSARY_MODEL.md` for each executed class)

| Class | Executed mechanisms |
|---|---|
| Fault robustness | mean shift, scaling drift, feature dropout with imputation, near-null shams, binomial shot emulation, approved transpilation and common-unitary rewrite |
| Integrity corruption | random evaluation-label flip, feature sign flip, asymmetric and diagonal-eroded kernel edits |
| Adversarial attack | data-dependent circuit-parameter mutation, feature-map repetition change, post-hoc envelope edit |
| Adaptive attacker | prior-preserving evaluation-label flip, PSD-preserving kernel substitution, **cluster-preserving mean shift and scaling drift (Gate A, 1.3.0)**; realised but not executed as a suite: confusion-preserving relabeling (808 rows) |

None of these is asserted to be a realistic exploit or an estimate of
prevalence; each is a controlled intervention with a declared class.

## Trusted computing base and roots

The frozen artifact trusts:

- the local Python/Qiskit/scikit-learn runtime and host operating system;
- the training data, the training routine and the fitted model artifact;
- the reference input artifact and preprocessing declaration;
- the reference circuit/kernel probes used for comparison;
- SHA-256 collision resistance;
- the item-level label reference $y^{\star}$ **only where the regime
  $\mathcal I_{XFY}^{\star}$ is declared**; label availability alone is not
  trust;
- the code that constructs and verifies the audit envelope.

Every "exact" claim is conditional on the corresponding root being outside
the intervention class (Proposition 6 of `FORMAL_CORE.md`). The hash chain is
tamper-evident only: a party controlling both the artifact and the verifier
can replace the complete chain, so provider authentication and
non-repudiation are outside the demonstrated claim.

## Explicitly excluded capabilities (Paper 2.5 or other ATHENA components)

- compromise of the operating system, Python runtime or verifier;
- malicious provider identity, forged calibration/job metadata, key theft and
  real provider attestation;
- scheduler attacks, physical mapping attacks and unapproved compiler passes
  on real hardware;
- calibrated device noise, crosstalk, multi-tenant interference and QPU faults;
- timing/power/network side channels and circuit confidentiality attacks;
- denial of service, availability, billing and access-control threats;
- adaptive attackers with a model of the sensors other than the executed
  cluster-preserving one;
- prevalence of attacks in real deployments.

## Information regimes and blind regions

| Regime | Observes | Structural blind region demonstrated | Calibrated / exact status in the frozen design (conformal rule, 1.3.0) |
|---|---|---|---|
| `I_X` | features (multiset of rows) | any label-only change | conformal decision FPR 0.056; label path 0/3,600; cluster-preserving drift detected in 0.01–0.56 at matched strengths |
| `I_XF` | features and fixed-model outputs | any label-only change | conformal FPR 0.058; label path 0/3,600; cluster-preserving drift 0.06–0.66 |
| `I_Ym` | label marginal | prior-preserving item-level relabeling; every feature-side change | FPR 0.048; zero containment; 5,450 residual-blind material cases at the structural endpoint |
| `I_XFY` (batch) | multiset of item triples; Class-A statistical aggregate comparison against the clean same-item-set benchmark oracle, without item pairing | none for material label changes (Proposition 3) but statistically undetectable: 11–43 of 2,617 | conformal FPR 0.053; benchmark protection is not deployed authentication |
| `I_XFY*` (trusted, same-batch) | deployed-authenticated aggregate (B) and item-aligned (C) references | none | exact: 2,617/2,617 material label rows and every material adaptive row; 0 materially altered audit results served; 0 violations on 1,200 exact-zero rows; 629/1,200 near-null interruptions, including 85 gross exact blocks but only 39 net additional interruptions versus batch `I_XFY`/P2 |
| `I_Q` | circuit, kernel and execution evidence | class-dependent (Proposition 7): on circuit-side interventions hashes overreact to approved equivalence; on post-processing interventions algebra misses a PSD-preserving substitution of the observed kernel, which the circuit hash and the semantic probe cannot see either; outputs miss sub-decision changes; under finite-shot estimation exact equality is not an acceptance criterion | 165/165 cells |

Reference profiles separate provenance (historical, benchmark-protected,
deployed authenticated), granularity (aggregate, item-aligned) and decision
(statistical, exact). The A/B/C shorthand is not one-dimensional: A is a
statistically thresholded aggregate comparison and in the executed suite uses
a clean same-item-set benchmark oracle without pairing; B is a trusted
aggregate same-batch exact invariant; C is a trusted item-aligned same-batch
exact invariant. No "stealth" claim is valid without naming one of these regimes
and the references it trusts, and "no reference" is never the right
description of a batch-level auditor.

## Detection and response policy

The policy layer composes the conformal family rule, the regime, the
trusted-reference status, materiality and the declared residual blind region
into `allow / hold / block`, and composes with the four ordered HSaaS
contracts by the maximum in `allow < hold < block`:

- `block` only for an exact invariant violated against a trusted reference;
- `hold` for statistical evidence of deviation (conformal rule) or, under the
  sensor-coverage-complete policy P3 (relative to the declared evidence dimensions), for a mandatory protected boundary
  without declared exact or statistical coverage;
- `allow` otherwise; the calibrated risk-tolerant policy P2 declares the
  residual blind region in the reason code and serves.

The contracts fail closed on their invariants; P2 is not fail-closed; P3
fails closed on missing coverage only and guarantees no minimum detection
power (where every boundary is covered it coincides with P2). Abstention
conditioned on the validity of the calibration itself (out-of-support
context) is outside this layer (Paper 2.5). The conformal rule's finite-sample
level (10/201 under exchangeability) is marginal; the executed design
violates the premise and the observed rates (0.056 / 0.058 / 0.048 / 0.053)
are reported as executed. PSD repair is containment for numerical validity,
not proof that the original kernel was trustworthy. A raw hash mismatch is
evidence for adjudication, not automatic proof of harmful semantics.

## Claims supported

- Auditability is a property of (intervention class, view, trusted references).
- Structural blind regions are monotone under refinement and closed exactly by
  added evidence that separates the class.
- Material label-path interventions always change the confusion matrix and
  are separable in the joint view; a trusted aggregate reference of the same
  batch detects them exactly, item identity needs an item-aligned reference,
  and no verifier whose evidence the adversary can rewrite certifies
  authenticity (Proposition 6).
- Per-sensor calibration does not calibrate the decision; the conformal family
  rule does, with a finite-sample level that is exact under exchangeability
  (observed 0.048–0.058 in the executed, non-exchangeable design); the 1.2.0
  rule had a false guarantee and most of its excess was rule bias.
- The count of materially altered audit results served (the CSV compatibility
  variable is `unsafe_allow`) is set by the information regime; “unsafe” here
  does not mean allowing a malicious network event. Only the trusted
  same-batch regime serves none, at a measured near-null cost: 629/1,200
  total, 85 gross exact-reference blocks, and 39 net additional interruptions
  over batch `I_XFY`/P2 after 46 overlapping cases are removed.
- An adaptive attacker who preserves the cluster fingerprint evades the
  calibrated batch-level sensors while keeping 83–91 % of the conclusion
  changes; only a reference closes that region.
- The quantum branch is an instance of the same view lattice, class by class
  (Proposition 7); under finite-shot estimation exact equality with the ideal
  kernel is not an acceptance criterion and the discrepancy needs a calibrated
  null.

## Claims not supported

- universal superiority or vulnerability of quantum models;
- QPU security, calibrated-noise robustness or provider integrity;
- production readiness or deployment of the local HSaaS demonstrator;
- population-level incident rates or deployment-wide detector power;
- that the exchangeability premise of the calibration holds in deployment, or
  a conditional guarantee given a calibration set.

## Residual validation gates (outside this article)

1. Signed provider/job/calibration provenance and key-management threat model.
2. Malicious transpiler/scheduler and physical-layout scenarios.
3. Calibrated noisy-backend and QPU campaign with repeated jobs and multiple
   calibration windows.
4. Multi-tenant and side-channel tests; confidentiality exposure assessment.
5. Context-conditioned runtime calibration under non-stationarity, with
   out-of-support abstention and recovery/fallback evaluation.
6. Network deployment, authentication, persistence and incident-response tests.
