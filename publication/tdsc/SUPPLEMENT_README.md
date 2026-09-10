# Supplementary material README (release 1.3.7; corrective evidence separated)

## Description

`paper15_tdsc_supplement.pdf` accompanies "Observational Indistinguishability
and Integrity Blind Regions in Hybrid Quantum-Classical Workflows". It
records the formal core with proofs
(Lemma 1, Propositions 1–7, Corollaries 1–3, the counterexample witnesses,
the remark on metrics other than balanced accuracy, the primitive/derived
state semantics and the finite-shot counterexample of Proposition 7(iii)
introduced by the 1.3.1 correction), the adversary-model
reading rule, the prespecified experimental environments with their dataset
weights, the 18-condition intervention suite, the information-set coverage
matrix, the deduplication rules and the dependence structure of the
statistical units, the exact-statevector validation (including the exact
replay check of the adversarial gate), the 165-design-cell quantum integrity gate
read through the view lattice, the executable contract and its composition
with the policy layer, the three preregistered reinforcement gates of
artifact 1.1.0, the two policy gates of artifact 1.2.0 regenerated in 1.3.0
with the conformal family rule (with the asymmetric 1.2.0 rule as comparison,
the decomposition of its excess into rule bias and design effect, E1
reported separately, the split construction as sensitivity, and the complete
decision counts with the interruption summary over the prespecified near-null
stress controls), the preregistered
frozen adversarial Gate A in full, the preregistered v1.3.5 feature-side
geometry-aligned sensitivity, the v1.3.7 JSD correction and label-side aligned
geometry sensitivity, the sensor decomposition and frozen-only without-KS
ablation, the secondary model-impact profile, and the
claims-supported/claims-excluded boundary.

The supplement adds audit and reproduction detail; it does not add evidence
from a physical QPU, calibrated backend noise, scheduling, multi-tenancy,
provider security or attestation, side channels, deployed runtime services,
or operational Fleet Management.

## Files and size

- `supplement.tex` — editable LaTeX source; `tables/*.tex` — generated tables
  and number macros; `figures/*.pdf` — vector figures;
- `paper15_tdsc_supplement.pdf` — rendered supplement (US Letter; page count
  and SHA-256 in `publication/RELEASE_STATUS.md`);
- `CLAIMS_TRACEABILITY.md` — claim-to-artifact map;
- `publication/artifact/` — compact verification artifact, including code,
  tests, locked dependencies, derived evidence, eleven SHA-256 evidence
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
`publication/RELEASE_STATUS.md`); they include the exhaustive counting-bound
tests of the conformal rule, the five-vector counterexample to the 1.2.0
rule, the brute-force checks of the formal core, the intervention-semantics
and finite-shot tests and the manuscript consistency gates. The verifier
must exit zero and report eleven evidence manifests and all manifested outputs,
3,600 expansion label rows with 2,184 lowered / 983 unchanged / 433 raised
conclusions (2,617 changed), 1,440 Gate-1 label rows with 1,276 / 105 / 59,
60 calibrated cells, 7,008 material observations over 5 regimes and 4
policies, the conformal level 10/201 respected under the exchangeable
re-splits, the corrected trusted-regime interruption decomposition (85 gross exact
blocks, 44 overlaps, 41 net additions; total 617), 16 adversarial conditions
with an exact replay of the matched
controls, 13,200 geometry-sensitivity observations across eight environments
and 22 interventions, exact identity response, geometry declarations,
matched-control/adaptive pairs and recomputed summaries, 64,560 corrected
JSD-dependent observation rows and 3,600 aligned label rows, and the number of
files in the artifact-wide manifest. A hash,
schema, count or consistency mismatch causes a non-zero exit.

## Full replay

Full replay is optional and substantially more expensive. Dataset acquisition
(official sources and expected SHA-256), staging, exact-statevector queues,
evidence builders, the policy gates, the adversarial gate and expected
outputs are documented in `REPRODUCIBILITY.md`. The published datasets retain
their original licenses and are not included in the artifact.

## Contact

Roberto Fernández-Barrios (corresponding author), Faculty of Engineering,
University of Deusto, Bilbao, Spain — roberto.fernandez.b@deusto.es.
