# IEEE TDSC manuscript package (artifact 1.2.0)

This directory contains the submission sources for the regular-paper candidate
"Observational Indistinguishability and Integrity Blind Regions Across the
Evidence Boundaries of Hybrid Quantum-Classical Kernel Workflows". The
manuscript is formatted with `IEEEtran` in Computer Society journal mode.

## Source inventory

- `main.tex` — complete article: abstract, related work and positioning,
  observation model and blind regions, adversary and failure model,
  methodology, results, integrity-audit contract, discussion and limitations,
  conclusion, declarations;
- `supplement.tex` — formal core with proofs, experimental design, coverage
  contract, statistical units and dependence structure, exact-statevector
  validation, quantum gate, contract and policy composition, the 1.1.0 and
  1.2.0 preregistered gates in full, the secondary model-impact profile, and
  the reproduction mapping;
- `references.bib` — bibliography cited by the main article;
- `figures/` — vector figures used in the article and supplement
  (`fig_q1_calibrated_coverage.pdf`, `fig_q1_policy_decisions.pdf`,
  `fig_q1_quantum_integrity_contract.pdf`, `fig_q1_external_forest.pdf`,
  `fig_q1_sensor_coverage.pdf`);
- `tables/` — LaTeX tables and the number-macro file `policy_macros.tex`,
  all generated from the manifested CSV evidence by
  `src/experiments/make_q1_reinforcement_tables.py` and
  `src/experiments/make_q1_policy_tables.py` (never edited by hand);
- `SUPPLEMENT_README.md` — IEEE-oriented description and execution guide;
- `CLAIMS_TRACEABILITY.md` — claim-to-evidence map;
- `build.ps1` — clean, checked LaTeX build;
- `RELEASE_NOTES.md` — submission-build scope;
- `CHECKSUMS.sha256` — hashes of the rendered submission PDFs;
- `VERSION` — submission build identifier.

The cover letter, title-page metadata, AI disclosure and portal checklist are
in `publication/submission/`. Journal rules and the template audit are in
`journal/`.

## Build

Prerequisites are PowerShell 7 (`pwsh`, cross-platform), a LaTeX distribution
providing `pdflatex`, `bibtex` and `IEEEtran`, and Poppler's `pdfinfo`. From
the repository root:

```powershell
pwsh -NoProfile -File publication/tdsc/build.ps1
```

The script copies the sources into a fresh directory below `tmp/`, compiles
the main article and supplement from that clean staging directory, rejects
broken references and overfull boxes, checks the 12-page article ceiling, and
writes `output/pdf/paper15_tdsc_submission.pdf` and
`output/pdf/paper15_tdsc_supplement.pdf`. The page counts and PDF hashes of
the released build are recorded in `publication/RELEASE_STATUS.md`
(generated); any required biographies can change pagination.

## Scientific verification

Python 3.10 is the frozen reference interpreter. From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m src.experiments.verify_publication_artifact `
  --root publication\artifact
```

The verifier checks the artifact-wide SHA-256 manifest, six evidence
manifests, 65 manifested outputs, table shapes, the primary count claims
including the signed label-path counts, the calibrated label-path checks and
the policy-level claims used by the paper. Full replay instructions are in
`Q1_REPRODUCTION.md`; raw public benchmark datasets are staged by the
documented procedures and are not redistributed.

## Claim boundary

The paper establishes integrity auditability only relative to a declared view,
declared trusted references and a declared intervention class. It combines
the observation model, exact and calibrated blind regions, an explicit
adversary model, multi-dataset/fixed-OOD validation, decision-level
calibration, an end-to-end policy evaluation on frozen outputs, bounded
simulator-only quantum controls and a local fail-closed contract. It does not
establish QPU security, calibrated device-noise coverage, scheduling security,
provider integrity or attestation, multi-tenancy protection, context-conditioned
runtime calibration under non-stationarity, recovery, or operational Fleet
Management. The ZZ-versus-SVC profile is secondary evidence.

## Author actions

All authors confirmed authorship, ORCIDs, CRediT roles, competing interests,
funding wording, the AI-use disclosure and the licensing scheme on
2026-09-06; the 1.2.0 changes to the manuscript (formal core, adversary model,
policy gates, retitling) are recorded in `CHANGELOG.md` and require the
authors' re-approval of the submission package before upload. The version DOI
of 1.2.0 is inserted by the release pipeline (`publication/DOI_STATUS.md`).
