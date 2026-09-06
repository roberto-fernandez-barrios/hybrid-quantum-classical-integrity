# Information-set conditional integrity auditing

Reproducibility artifact for Paper 1.5:
*Information-Set Conditional Integrity Auditing for Hybrid Quantum-Classical
Kernel Workflows*.

The central claim is deliberately bounded: **integrity auditability is
conditional on the evidence exposed at the audited workflow boundary**. An
evaluation-label intervention can change a reported conclusion while features,
scores and predictions remain exactly invariant; a prior-preserving exchange is
also invisible to label-marginal sensors. Item-aligned trusted outcomes or
provenance are required to close that blind region.

The article's novelty is the integrated package of formalization, exact blind
regions, sensor-coverage mapping, multi-dataset/fixed-OOD validation, a bounded
quantum-kernel integrity layer and an executable fail-closed contract. The two
elementary propositions, hash chaining, contracts and ZZ-versus-SVC comparison
are not presented as standalone novelty.

## Frozen evidence

| Gate | Design | Evidence used in the manuscript |
|---|---|---|
| CICIDS Gate 1 | 7,980 raw rows; 4,560 unique observations; 5 split x 4 nested model seeds | exact label-path blind regions and secondary within-split ZZ-SVC profile |
| Expansion | 360/360 jobs; 13,680 raw rows; 11,400 unique observations; 8 fixed environments | replication over CICIDS2017, UNSW-NB15, ToN-IoT, scale and temporal OOD |
| Quantum integrity | 165/165 cells; 9/9 acceptance checks | semantic, provenance, algebraic, repeated-estimation and output coverage |
| HSaaS contract | 6/6 scenarios; 8/8 acceptance checks | hash-chained four-contract `allow/hold/block` policy |
| Reinforcement (1.1.0) | 390/390 preregistered jobs; null calibration over 8 environments (alpha = 0.05 per sensor, 200 calibration and 200 disjoint evaluation draws per cell), 3 preprocessing configurations, 2 tuned environments | calibrated false-alarm/detection rates, symmetric-preprocessing and tuned-baseline sensitivity of the secondary ZZ-SVC profile |

The expansion contains 3,600 evaluation-label observations. All 3,600 leave
feature/prediction evidence and predictions invariant; all 1,800
prior-preserving observations also leave label marginals invariant. There are
2,184 positive balanced-accuracy conclusion impacts, and all 2,184 have
non-zero item-aligned joint-outcome evidence. A fail-closed verifier recomputes
these counts from the released derived tables.

## Manuscript and reviewer files

- `publication/tdsc/main.tex` — submission-oriented IEEE TDSC manuscript;
- `publication/tdsc/supplement.tex` — experimental and reproducibility detail;
- `publication/tdsc/README.md` — clean-build and submission-package guide;
- `manuscript/paper15_q1_manuscript_spine_v11.md` — frozen Markdown source from
  which the TDSC article was developed;
- `manuscript/NOVELTY_REVIEW_2026-08-09.md` — claim-specific literature and
  overlap audit through 9 August 2026, with the 6 September 2026 recheck;
- `manuscript/paper15_v11_reinforcement_prereg.md` — frozen protocol of the
  three reinforcement gates (null calibration, preprocessing ablation, tuned
  baselines);
- `manuscript/ATHENA_DEUSTO_TRACEABILITY.md` — bounded project
  requirement-to-evidence mapping;
- `manuscript/THREAT_MODEL_CARD.md` — threat and trust assumptions;
- `Q1_REPRODUCTION.md` — exact commands and evidence tiers;
- `publication/` — submission files, compact evidence artifact, hashes and DOI
  status.

Build the current 10-page main article and 6-page supplement (rc2) with:

```powershell
pwsh -NoProfile -File publication/tdsc/build.ps1
```

## Quick verification

Python 3.10 is the reference interpreter.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m src.experiments.verify_publication_artifact `
  --root publication\artifact
```

The final command validates five embedded evidence manifests, 44 manifested
outputs, CSV row counts, SHA-256 hashes, the primary label-boundary counts and
the calibrated label-path consistency checks. It exits non-zero on any mismatch.

Linux/macOS users can replace `.\.venv\Scripts\python.exe` with
`.venv/bin/python` and use `/` path separators.

## Rebuilding the evidence

The compact artifact supports result verification without recomputing quantum
kernels. Full replay starts from the public benchmark datasets and follows
`Q1_REPRODUCTION.md`:

```powershell
.\.venv\Scripts\python.exe -m src.experiments.build_q1_gate1_evidence
pwsh -NoProfile -ExecutionPolicy Bypass -File .\run_paper15_q1_exact_queue.ps1
.\.venv\Scripts\python.exe -m src.experiments.build_q1_expansion_evidence
.\.venv\Scripts\python.exe -m src.experiments.run_quantum_integrity_gate
.\.venv\Scripts\python.exe -m src.hsaas.demo
.\.venv\Scripts\python.exe -m src.experiments.run_v11_reinforcement_queue --gates N,P,T
.\.venv\Scripts\python.exe -m src.experiments.build_q1_reinforcement_evidence
.\.venv\Scripts\python.exe -m src.experiments.make_q1_reinforcement_figures
.\.venv\Scripts\python.exe -m src.experiments.assemble_publication_artifact
```

The reinforcement gates were preregistered in
`manuscript/paper15_v11_reinforcement_prereg.md` before execution; their
results are summarised in `manuscript/paper15_v11_reinforcement_result_summary.md`.

The exact-statevector engine is an ideal-simulation acceleration. The 256/1,024
shot conditions are binomial fidelity-estimation emulators. Neither is evidence
from a QPU or calibrated backend.

## Scientific boundary

This release studies data-to-evaluation integrity and selected simulated
quantum-kernel boundaries. It does not study or claim:

- physical QPU behaviour or device-calibrated noise;
- malicious scheduling, multi-tenancy or provider-side security;
- production authentication, non-repudiation or incident operations;
- operational Fleet Management.

Within ATHENA-AEGIS it supplies strong but bounded evidence for G3.2/G3.3,
selected simulator evidence for G3.1, a local research prototype towards Result
3.1, and a publication contribution to WP5 Task 5.2. It does not cover WP5 Task
5.1 or Result 5.1.

## Version, funding and citation

Artifact version: `1.1.0` (frozen 1.0.0 evidence, tag `paper15-q1-v1.0.0`, plus
the preregistered reinforcement gates; the 1.1.0 submission tag is created only
after all-author approval).

This work was supported by the Spanish State Research Agency (AEI) through
ATHENA-AEGIS, project `PID2024-155693NB-C43`.

Author metadata, CRediT roles, license choice and the version DOI require final
author confirmation before public archival. The machine-readable templates are
`CITATION.cff.in` and `.zenodo.json.in`; current archival status is recorded in
`publication/DOI_STATUS.md`.
