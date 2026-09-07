# Supplementary material README (artifact 1.2.0)

## Description

`paper15_tdsc_supplement.pdf` accompanies "Observational Indistinguishability
and Integrity Blind Regions Across the Evidence Boundaries of Hybrid
Quantum-Classical Kernel Workflows". It records the formal core with proofs
(Lemma 1, Propositions 1–6, Corollaries 1–2, the counterexample witnesses),
the adversary-model reading rule, the prespecified experimental environments,
the 18-condition intervention suite, the information-set coverage matrix, the
deduplication rules and the dependence structure of the statistical units,
the exact-statevector validation, the 165-cell quantum integrity gate, the
executable contract and its composition with the policy layer, the three
preregistered reinforcement gates of artifact 1.1.0 (null calibration with
disjoint clean pools, symmetric preprocessing ablation, cross-validated
tuning), the two preregistered policy gates of artifact 1.2.0 (family-wise
regime calibration; end-to-end allow/hold/block evaluation), the secondary
model-impact profile, and the claims-supported/claims-excluded boundary.

The supplement adds audit and reproduction detail; it does not add evidence
from a physical QPU, calibrated backend noise, scheduling, multi-tenancy,
provider security or attestation, side channels, or operational Fleet
Management.

## Files and size

- `supplement.tex` — editable LaTeX source; `tables/*.tex` — generated tables
  and number macros; `figures/*.pdf` — vector figures;
- `paper15_tdsc_supplement.pdf` — rendered supplement (US Letter; page count
  and SHA-256 in `publication/RELEASE_STATUS.md`);
- `CLAIMS_TRACEABILITY.md` — claim-to-artifact map;
- `publication/artifact/` — compact verification artifact, including code,
  tests, locked dependencies, derived evidence, six SHA-256 evidence
  manifests and the artifact-wide manifest.

Exact sizes and SHA-256 values are reported in `CHECKSUMS.sha256` and
`publication/RELEASE_STATUS.md` after every release build.

## Platform and environment

The evidence was frozen with Python 3.10.16, NumPy 2.2.6, pandas 2.3.3,
scikit-learn 1.7.2, Qiskit 2.3.0 and Qiskit Machine Learning 0.9.0. The
locked environment is `requirements-lock.txt`; the self-contained archival
copy is `publication/artifact/environment/requirements-lock.txt`.

The LaTeX sources were checked on Windows 11 with MiKTeX and `IEEEtran` 1.8b.
The Python verification, the dataset hash verifier and the CI workflow are
cross-platform.

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

The tests must pass (the collected count is recorded in
`publication/RELEASE_STATUS.md`). The verifier must exit zero and report six
evidence manifests, 65 manifested outputs, 3,600 expansion label rows with
2,184 lowered / 983 unchanged / 433 raised conclusions (2,617 changed), 1,440
Gate-1 label rows with 1,276 / 105 / 59, 60 calibrated cells, 7,008 material
observations over 5 regimes and 4 policies, and the number of files in the
artifact-wide manifest. A hash, schema, count or consistency mismatch causes a
non-zero exit.

## Full replay

Full replay is optional and substantially more expensive. Dataset acquisition
(official sources and expected SHA-256), staging, exact-statevector queues,
evidence builders, the 1.2.0 policy gates and expected outputs are documented
in `Q1_REPRODUCTION.md`. The published datasets retain their original
licenses and are not included in the artifact.

## Contact

Roberto Fernández-Barrios (corresponding author), Faculty of Engineering,
University of Deusto, Bilbao, Spain — roberto.fernandez.b@deusto.es.
