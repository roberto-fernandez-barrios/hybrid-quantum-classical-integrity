# ATHENA-AEGIS auditable HSaaS demonstrator

Status: complete local research prototype; deployment and provider/QPU
authentication remain open.

## Purpose

The demonstrator converts the paper's integrity-audit contract into an
executable service boundary. It is deliberately transport-agnostic: the audit
envelope can be returned by a CLI, batch job, or future HTTP service without
changing the contract semantics.

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
   Semantics-preserving rewrites pass only when explicitly approved.
3. **Execution/result:** validates declared execution metadata, repeated-
   estimation discrepancy, and prediction provenance. Approved stochastic
   execution is held for uncertainty adjudication; it is not silently accepted.
4. **Evaluation/report:** binds item-level labels to predictions and recomputes
   balanced accuracy. A prior-preserving label change is blocked even when the
   class marginal remains identical.

Contracts form an ordered SHA-256 chain. This makes later modification
detectable, but does not authenticate the provider: a production deployment
must sign the chain and bind it to backend/job/calibration identities.

## Fail-closed policy

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

All eight acceptance checks pass, including verification of all six hash
chains. The result is exported to
`manuscript/tables/hsaas_contract_summary.csv` for reviewer inspection.

## Security boundary

This prototype evaluates ideal-statevector kernels and one binomial shot
emulator. It is not an HTTP deployment, a digital-signature system, a calibrated
noise study, or a QPU run. The remaining operational tier must add:

- authentication/authorization and signed manifests;
- backend, provider, job, calibration, layout, scheduling, and timestamp binding;
- noisy-backend and QPU replay;
- multi-tenant and provider-side fault scenarios;
- persistence, incident response, rollback, and retention policies.

Within that boundary, the demonstrator is evidence for ATHENA Result 3.1: it
turns the paper's sensor taxonomy into an executable, tested, fail-closed
software contract rather than leaving countermeasures as prose alone.
