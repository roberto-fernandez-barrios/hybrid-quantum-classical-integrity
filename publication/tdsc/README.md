# IEEE TDSC manuscript package

This directory contains the submission sources for the regular-paper candidate
“Information-Set Conditional Integrity Auditing for Hybrid Quantum-Classical
Kernel Workflows.” The manuscript is formatted with
`IEEEtran` in Computer Society journal mode.

## Source inventory

- `main.tex` — complete article: abstract, related work, formal model, Methods,
  Results, integrity-audit contract, Discussion, Limitations, and Conclusion;
- `supplement.tex` — experimental design, intervention and sensor matrices,
  exact-statevector validation, contract detail, and reproduction mapping;
- `references.bib` — bibliography cited by the main article;
- `figures/` — the four vector figures used in the article (three frozen 1.0.0
  figures plus `fig_q1_calibrated_coverage.pdf` from the reinforcement gates);
- `SUPPLEMENT_README.md` — IEEE-oriented description and execution guide;
- `CLAIMS_TRACEABILITY.md` — claim-to-evidence map;
- `build.ps1` — clean, checked LaTeX build;
- `RELEASE_NOTES.md` — submission-build scope and known administrative gates;
- `CHECKSUMS.sha256` — hashes of the rendered submission PDFs.

The active cover letter, title-page template, AI disclosure, and portal
checklist are in `publication/submission/`. Journal rules and the template audit
are in `journal/`.

## Build

Prerequisites are PowerShell 7, a LaTeX distribution providing `pdflatex`,
`bibtex`, `IEEEtran`, and Poppler's `pdfinfo`. From the repository root:

```powershell
pwsh -NoProfile -File publication/tdsc/build.ps1
```

The script copies the sources into a fresh directory below `tmp/`, compiles the
main article and supplement from that clean staging directory, rejects broken
references and overfull boxes, checks the article page ceiling, and writes:

- `output/pdf/paper15_tdsc_submission.pdf`
- `output/pdf/paper15_tdsc_supplement.pdf`

The rc1 anonymous build was nine main-paper pages plus three supplement pages
on US Letter; rc2 adds the author block, Section II-C, the calibrated-coverage
paragraph and figure, and a supplement section, and compiles to 10 main-paper pages plus
6 supplement pages (2026-09-06). Any required biographies can change pagination.

## Scientific verification

Python 3.10 is the frozen reference interpreter. From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m src.experiments.verify_publication_artifact `
  --root publication\artifact
```

The verifier checks the artifact-wide SHA-256 manifest, four evidence
manifests, 22 manifested outputs, table shapes, and the count claims used by the
paper. Full replay instructions remain in `Q1_REPRODUCTION.md`; raw public
benchmark datasets are staged by the documented procedures and are not
redistributed.

## Claim boundary

The paper establishes integrity auditability only relative to declared evidence
at a declared boundary. It combines formalization, exact blind regions, sensor
coverage, multi-dataset/fixed-OOD validation, bounded simulator-only quantum
controls, and a local fail-closed contract. It does not establish QPU security,
calibrated device-noise coverage, scheduling security, provider integrity,
multi-tenancy protection, or operational Fleet Management. The ZZ-versus-SVC
profile is secondary evidence, not the headline result.

## Required author actions

The scientific package is closed (artifact 1.1.0). Author order, affiliations,
ORCIDs and corresponding author were confirmed on 2026-09-06. Submission
remains administratively blocked until the authors confirm and insert:

1. CRediT roles (proposed on the title page);
2. competing interests and approval of the AI-use disclosure;
3. the verbatim funding/co-funding formula from the executed award;
4. artifact/software license and repository visibility;
5. related-work disclosures required by the IEEE portal; and
6. the public Zenodo version DOI.

Do not publish a DOI by inference; the repository is public and needs a LICENSE
file before archival.
