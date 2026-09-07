# ATHENA-AEGIS auditable HSaaS demonstrator and policy layer

Status: complete local research prototype (four contracts, six scenarios)
plus the information-aware calibrated policy layer of artifacts 1.2.0/1.3.0,
evaluated offline on frozen outputs; deployment, authenticated provider
records and QPU execution remain open (Paper 2.5).

## Purpose

The demonstrator converts the paper's integrity-audit contract into an
executable service boundary. It is deliberately transport-agnostic: the audit
envelope can be returned by a CLI, batch job, or future HTTP service without
changing the contract semantics. Nothing in this repository is a deployed
runtime service.

Run it with either entry point:

```powershell
python -m src.hsaas.demo
athena-aegis-demo
```

The packaged console command is declared in `pyproject.toml`. The default run
uses one compact CICIDS cell (split 42, dimension 4, 32/32 rows) and writes a
strict manifest under `results/paper_digest/paper15_hsaas_demo/`.

## Four ordered contracts

1. **Input/preprocessing:** hashes the input arrays and the preprocessing
   declaration. A mismatch blocks the result.
2. **Circuit/kernel:** binds circuit and kernel provenance to semantic kernel
   probes and symmetry, diagonal, eigenvalue, and PSD-repair evidence.
   Semantics-preserving rewrites pass only when explicitly approved (the
   approved class of Proposition 7).
3. **Execution/result:** validates declared execution metadata, repeated-
   estimation discrepancy, and prediction provenance. Approved stochastic
   execution is held for uncertainty adjudication; it is not silently accepted.
4. **Evaluation/report:** binds item-level labels to predictions and recomputes
   balanced accuracy. A prior-preserving label change is blocked even when the
   class marginal remains identical.

Contracts form an ordered SHA-256 chain. This makes later modification
detectable, but does not authenticate the provider: a production deployment
must sign the chain and bind it to backend/job/calibration identities.

## Fail-closed logic of the contracts

The contracts fail closed on their invariants. This is a property of the
contract layer and must not be confused with the decision policies below,
of which only P3 is fail-closed.

| Contract state | Service action | Meaning |
|---|---|---|
| all `pass` | `allow` | Evidence satisfies every declared contract |
| any `review`, no `fail` | `hold` | Do not serve; obtain uncertainty/policy adjudication |
| any `fail` | `block` | Do not serve; preserve evidence and investigate |

## Prespecified scenarios and observed decisions

| Scenario | Decision | Contract result |
|---|---|---|
| Clean | `allow` | Four contracts pass |
| Approved transpilation | `allow` | Hash changes, semantic kernel and output preserved |
| Parameterized circuit mutation | `block` | Circuit provenance and semantic kernel fail |
| PSD-preserving kernel substitution | `block` | Algebra passes; trusted semantic/provenance contract fails |
| Prior-preserving label corruption | `block` | Label marginal is invariant; item-level provenance fails |
| Approved 256-shot emulator | `hold` | Stochastic kernel and repeated estimate require adjudication |

## Information-aware calibrated policy layer (artifacts 1.2.0/1.3.0)

`src/hsaas/policy.py` is a pure decision function that consumes, for one
audited batch, the information regime (`I_X`, `I_XF`, `I_Ym`, `I_XFY`,
`I_XFY_trusted`), whether a trusted item-aligned reference exists, the
per-sensor calibrated fire flags (1.1.0 thresholds), the conformal
family-calibrated regime flag (`src/integrity/family_calibration.py`, Gate F
of 1.3.0), the exact item-aligned flag (defined only under a trusted
reference) and the protected boundaries declared by the contract (feature,
prediction, label). It returns `allow / hold / block` with reason codes.

Policy taxonomy (`POLICY_CLASS`):

- P0 `serve_always` — baseline.
- P1 `union_uncalibrated` — uncalibrated, risk-tolerant: the 1.1.0 union of
  per-sensor rules.
- P2 `family_calibrated` — calibrated, risk-tolerant: `hold` if the conformal
  family rule fires; otherwise serves, *including under an explicitly declared
  residual blind region* (`allowed_with_residual_blind_region:label`). It is
  not a fail-closed policy.
- P3 `family_calibrated_strict` — strict fail-closed / abstaining: as P2, and
  an unverified mandatory boundary yields `hold` (`unverified_boundary:label`).

`block` is reserved for an exact invariant violated against a trusted
reference. The policy composes with the four contracts by the maximum in the
lattice `allow < hold < block` (`compose`); on the six frozen envelopes the
composed action reproduces the contract action in every scenario, including
the `hold` of the approved 256-shot emulator.

`src/experiments/build_q1_policy_evidence.py` evaluates the four policies
over the five regimes offline on 24,000 frozen observations (12,000 clean
draws, 1,200 near-null shams, 10,800 interventions of which 7,008 change the
reported balanced accuracy) and writes 27 tables with 12 fail-closed
consistency checks; the results are summarised in
`manuscript/paper15_v13_result_summary.md`. Key numbers (1.3.0, conformal
rule): decision false-alarm rates 0.056 / 0.058 / 0.048 / 0.053 against
0.125 / 0.203 / 0.048 / 0.259 (union); unsafe allows 4,496 / 4,365 / 7,008 /
4,390 of 7,008 for the batch-level regimes under P2 and 0 for the trusted
item-aligned regime, which however interrupts 52 % of the 1,200 benign
near-null controls (544 held, 85 blocked). The adversarial gate of 1.3.0
(`build_q1_adversarial_evidence.py`) shows that P2 serves 959–1,328 of 3,418
material rows of an attacker who preserves the batch-level fingerprint; the
trusted regime blocks all of them.

## Boundary

The prototype and the policy layer are local processes over frozen outputs:
no network authentication, signed provider record, persistence, incident
response, scheduler binding or QPU identity. Context-conditioned calibration
under non-stationarity, out-of-support abstention and recovery/fallback are
Paper 2.5.
