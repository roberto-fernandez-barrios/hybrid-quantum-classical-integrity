# Threat-model card — Paper 1.5 / ATHENA-AEGIS

Version: 2.0 (2026-09-07; version 1.0 dated 2026-08-09)  
Scope: integrity and auditability of a hybrid quantum-classical kernel workflow.
The per-class adversary and failure model is `ADVERSARY_MODEL.md`; the formal
objects (views, trusted references, blind regions) are `FORMAL_CORE.md`. This
card is the short reference.

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
| Adaptive attacker | prior-preserving evaluation-label flip, PSD-preserving kernel substitution; discussed but not executed: confusion-preserving relabeling, cluster-preserving feature perturbation |

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
- prevalence of attacks in real deployments.

## Information regimes and blind regions

| Regime | Observes | Structural blind region demonstrated | Calibrated / exact status in the frozen design |
|---|---|---|---|
| `I_X` | features (multiset of rows) | any label-only change | family-calibrated FPR 0.061; label path 0/3,600 |
| `I_XF` | features and fixed-model outputs | any label-only change | family-calibrated FPR 0.073; label path 0/3,600 |
| `I_Ym` | label marginal | prior-preserving item-level relabeling; every feature-side change | FPR 0.048; contains nothing in this suite |
| `I_XFY` (batch) | multiset of item triples, no reference | none for material label changes (Proposition 3) but statistically undetectable: 16–43 of 2,617 | family-calibrated FPR 0.079 |
| `I_XFY*` (trusted, item-aligned) | same items against an authenticated reference | none | exact: 2,617/2,617 material label rows, 0 unsafe allows, 0 false holds |
| `I_Q` | circuit, kernel and execution evidence | composition-dependent: hashes overreact to equivalence; algebra misses PSD-preserving substitution; outputs miss sub-decision changes | 165/165 cells |

No "stealth" claim is valid without naming one of these regimes and the
references it trusts.

## Detection and response policy

The policy layer composes calibrated sensors, the regime, the
trusted-reference status, materiality and the declared residual blind region
into `allow / hold / block`, and composes with the four ordered HSaaS
contracts by the maximum in `allow < hold < block`:

- `block` only for an exact invariant violated against a trusted reference;
- `hold` for statistical evidence of deviation (family-calibrated rule) or for
  missing mandatory evidence (strict policy: an unverified protected boundary);
- `allow` otherwise, with the residual blind region declared in the reason
  code.

PSD repair is containment for numerical validity, not proof that the original
kernel was trustworthy. A raw hash mismatch is evidence for adjudication, not
automatic proof of harmful semantics.

## Claims supported

- Auditability is a property of (intervention class, view, trusted references).
- Structural blind regions are monotone under refinement and closed exactly by
  added evidence that separates the class.
- Material label-path interventions always change the confusion matrix and
  are separable in the joint view; a trusted aggregate reference of the same
  batch detects them exactly, item identity needs an item-aligned reference,
  and no verifier whose evidence the adversary can rewrite certifies
  authenticity (Proposition 6).
- Per-sensor calibration does not calibrate the decision; family calibration
  restores a decision-level budget at a small detection cost.
- The unsafe-allow count is set by the information regime; only the trusted
  item-aligned regime serves none of the materially changed results.

## Claims not supported

- universal superiority or vulnerability of quantum models;
- QPU security, calibrated-noise robustness or provider integrity;
- production readiness of the local HSaaS demonstrator;
- population-level incident rates or deployment-wide detector power;
- that the exchangeability premise of the calibration holds in deployment.

## Residual validation gates (outside this article)

1. Signed provider/job/calibration provenance and key-management threat model.
2. Malicious transpiler/scheduler and physical-layout scenarios.
3. Calibrated noisy-backend and QPU campaign with repeated jobs and multiple
   calibration windows.
4. Multi-tenant and side-channel tests.
5. Context-conditioned runtime calibration under non-stationarity, with
   out-of-support abstention and recovery/fallback evaluation.
6. Network deployment, authentication, persistence and incident-response tests.
