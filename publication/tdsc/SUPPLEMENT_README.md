# Supplementary material README

## Description

`paper15_tdsc_supplement.pdf` accompanies “Information-Set Conditional
Integrity Auditing for Hybrid Quantum-Classical Kernel Workflows.” It records
the prespecified experimental environments, 18-condition intervention suite,
information-set coverage matrix, deduplication rules, statistical units,
exact-statevector validation, 165-cell quantum integrity gate, executable
contract checks, and the claims-supported/claims-excluded boundary.

The supplement adds audit and reproduction detail; it does not add evidence
from a physical QPU, calibrated backend noise, scheduling, multi-tenancy,
provider security, side channels, or operational Fleet Management.

## Files and approximate size

- `supplement.tex` — editable LaTeX source;
- `paper15_tdsc_supplement.pdf` — rendered supplement, currently three US Letter
  pages;
- `CLAIMS_TRACEABILITY.md` — claim-to-artifact map;
- `publication/artifact/` — compact verification artifact, including code,
  tests, locked dependencies, derived evidence, and SHA-256 manifests.

Exact sizes and SHA-256 values are reported in `CHECKSUMS.sha256` after every
release build.

## Platform and environment

The evidence was frozen with Python 3.10.16, NumPy 2.2.6, pandas 2.3.3,
scikit-learn 1.7.2, Qiskit 2.3.0, and Qiskit Machine Learning 0.9.0. The locked
environment is `requirements-lock.txt`; the self-contained archival copy is
`publication/artifact/environment/requirements-lock.txt`.

The LaTeX sources were checked on Windows 11 with MiKTeX and `IEEEtran` 1.8b.
The Python verification and CI workflow are cross-platform.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
```

On Linux or macOS, use `.venv/bin/python` and `/` path separators.

## Fast verification and expected output

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m src.experiments.verify_publication_artifact `
  --root publication\artifact
```

The tests must pass. The verifier must exit zero and report 96 release files,
four evidence manifests, 22 manifested outputs, 3,600 expansion label rows,
2,184 positive expansion impacts, 1,440 Gate-1 label rows, and 1,276 positive
Gate-1 impacts. A hash, schema, count, or consistency mismatch causes a nonzero
exit.

## Full replay

Full replay is optional and substantially more expensive. Dataset acquisition,
staging, exact-statevector queues, evidence builders, and expected outputs are
documented in `Q1_REPRODUCTION.md`. The published datasets retain their original
licenses and are not included in the artifact.

## Contact

**[INSERT CORRESPONDING AUTHOR NAME AND EMAIL BEFORE PUBLICATION.]**
