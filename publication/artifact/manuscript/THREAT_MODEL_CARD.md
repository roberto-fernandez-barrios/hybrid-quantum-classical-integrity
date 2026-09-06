# Threat-model card — Paper 1.5 / ATHENA-AEGIS

Version: 1.0 (2026-08-09)  
Scope: integrity and auditability of a hybrid quantum-classical kernel workflow.

## System and protected conclusion

The system transforms an intrusion-detection dataset into a reported model
evaluation through acquisition, preprocessing/projection, quantum feature-map
construction, transpilation, fidelity-kernel estimation, classical SVC
decision, reference labels, and metric/report generation.

The primary protected asset is not only the prediction. It is the evidentiary
chain supporting the reported conclusion: *which model produced which output
from which data, circuit, kernel estimate, labels, and execution context*.

## Trust boundaries

| Boundary | Protected assets | Current evidence |
|---|---|---|
| B1 Acquisition/input | rows, feature schema, source identity | Data hashes, schema and preprocessing manifest |
| B2 Preprocessing | imputer/SVD/scaler state and transformed features | Train-fit policy, configuration and array hashes |
| B3 Circuit design | feature map, parameters and intended semantics | Canonical OpenQASM 3 and parameter provenance; semantic probes |
| B4 Transpilation | approved rewrite and semantic preservation | Benign transpilation differential; circuit and kernel comparison |
| B5 Execution/estimation | backend mode, shots, repeated estimates | Ideal statevector plus binomial estimator emulator |
| B6 Kernel/post-processing | matrix identity and mathematical validity | Hash, semantic delta, symmetry, diagonal, eigenvalue and repair evidence |
| B7 Prediction | predicted class, score and model identity | Prediction hashes, disagreement and score evidence |
| B8 Evaluation/report | labels, joint outcomes and reported metrics | Label provenance, joint hash and metric recomputation |

## Adversary/failure capabilities evaluated

- feature corruption and preprocessing drift;
- random and prior-preserving evaluation-label corruption;
- data-dependent circuit-parameter mutation and feature-map replacement;
- semantics-preserving circuit rewrites as negative controls;
- asymmetric, diagonal-eroded and symmetric PSD-preserving kernel edits;
- stochastic fidelity-estimation error under controlled binomial emulation;
- stale or altered evidence after execution, detected by the contract hash chain.

These interventions model integrity failures. They are not all asserted to be
realistic malicious exploits, and their presence does not imply attacker intent.

## Trusted computing base

The current artifact trusts:

- the local Python/Qiskit/scikit-learn runtime and host operating system;
- the reference input artifact and preprocessing declaration;
- the reference circuit/kernel probes used for comparison;
- SHA-256 collision resistance;
- item-level ground-truth provenance when that evidence is declared available;
- the code that constructs and verifies the audit envelope.

The hash chain is tamper-evident only. Because it is not digitally signed, a
party controlling both the artifact and verifier could replace the complete
chain. Provider authentication is therefore outside the demonstrated claim.

## Explicitly excluded capabilities

- compromise of the operating system, Python runtime or verifier;
- malicious provider identity, forged calibration/job metadata or key theft;
- scheduler attacks, physical mapping attacks and unapproved compiler passes;
- calibrated device noise, crosstalk, multi-tenant interference and QPU faults;
- timing/power/network side channels and circuit confidentiality attacks;
- denial of service, availability, billing and access-control threats;
- prevalence of attacks in real deployments.

## Information regimes and exact blind regions

| Regime | Observes | Structural blind region demonstrated |
|---|---|---|
| `I_X` | features | Any label-only change |
| `I_XF` | features and fixed-model outputs | Any label-only change |
| `I_Y` | label marginal | Prior-preserving item-level label changes |
| `I_XFY` | item-level features, outputs and labels | Closes the tested label-path blind region if provenance is trusted |
| `I_Q` | circuit, kernel and execution evidence | Depends on composition: hashes overreact to equivalence; algebra misses PSD-preserving substitution; outputs miss sub-decision changes |

No “stealth” claim is valid without naming one of these information regimes.

## Detection and response policy

The HSaaS demonstrator evaluates four ordered contracts. The response is:

- `allow` only if all contracts pass;
- `hold` if evidence is expected but requires adjudication, such as approved
  stochastic estimation within its bound;
- `block` if any contract violates provenance, semantics, algebra, execution,
  label or reporting requirements.

PSD repair is containment for numerical validity, not proof that the original
kernel was trustworthy. A raw hash mismatch is evidence for adjudication, not
automatic proof of harmful semantics.

## Security and scientific claims supported

- Auditability is conditional on the information exposed at a boundary.
- Model-output impact and evaluation-conclusion impact have different loci.
- Complementary sensors close different blind regions; no single score is a
  workflow-wide security certificate.
- The tested fail-closed composition distinguishes approved equivalence,
  actionable violations and uncertainty review in a local prototype.

## Claims not supported

- universal superiority or vulnerability of quantum models;
- QPU security, calibrated-noise robustness or provider integrity;
- production readiness of the local HSaaS demonstrator;
- population-level incident rates or deployment-wide detector power.

## Residual validation gates

1. Signed provider/job/calibration provenance and key-management threat model.
2. Malicious transpiler/scheduler and physical-layout scenarios.
3. Calibrated noisy-backend and QPU campaign with repeated jobs.
4. Multi-tenant and side-channel tests.
5. Threshold calibration, false-alarm budgets and detection-power analysis
   (partially addressed in artifact 1.1.0 within the frozen simulator design:
   null-calibrated thresholds at alpha = 0.05 with disjoint clean pools;
   context-conditioned operational calibration remains open).
6. Network deployment, authentication, persistence and incident-response tests.
