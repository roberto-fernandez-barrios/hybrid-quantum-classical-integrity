# Article and supplement sources

This directory contains the publication sources for *Observational
Indistinguishability and Integrity Blind Regions in Hybrid Quantum-Classical
Workflows*, version `1.3.7`.

## Contents

- `main.tex` — article source (12-page maximum).
- `supplement.tex` — supplementary material source.
- `references.bib` — bibliography used by the article.
- `reference_audit_v1.3.4.csv` — frozen, machine-readable source audit for the
  bibliography.
- `reference_audit_v1.3.5_addendum.csv` — two bounded primary-source records
  supporting the compact authenticated-representation clarification.
- `reference_audit_v1.3.6.csv` — the closed 2026 primary-source audit for the
  two added references and one verified-but-peripheral work.
- `figures/` — vector figures used by the article and supplement.
- `tables/` — generated LaTeX tables and number macros derived from manifested
  evidence.
- `CLAIMS_TRACEABILITY.md` — mapping from manuscript claims to evidence and
  executable checks.
- `SUPPLEMENT_README.md` — detailed supplement and verification description.
- `build.ps1` — clean, checked LaTeX build.
- `CHECKSUMS.sha256` — released PDF hashes.
- `VERSION` — publication build identifier.

Administrative upload material is intentionally not part of the public
repository.

## Build

Prerequisites are PowerShell 7, a LaTeX distribution providing `pdflatex`,
`bibtex`, and `IEEEtran`, plus Poppler's `pdfinfo`. From the repository root:

```powershell
pwsh -NoProfile -File publication/tdsc/build.ps1
```

The script compiles from a clean staging directory under `tmp/`, rejects
broken references and overfull boxes, checks the article page limit, and
writes:

```text
output/pdf/paper15_tdsc_submission.pdf
output/pdf/paper15_tdsc_supplement.pdf
```

Released page totals and SHA-256 hashes are recorded in
`publication/RELEASE_STATUS.md`.

## Scientific verification

Python 3.10 is the frozen reference interpreter:

```powershell
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.venv\Scripts\python.exe -m src.experiments.verify_publication_artifact `
  --root publication\artifact
```

The verifier checks the artifact-wide manifest, eleven embedded evidence
manifests and all manifested outputs, table shapes, primary counts, declared
calibration/intervention geometry, identity responses, matched pairs, derived
summaries, and acceptance conditions.
Full replay instructions and external dataset requirements are in
`REPRODUCIBILITY.md`.

## Scope

The manuscript establishes integrity auditability relative to a declared
view, trusted references, intervention class, and frozen finite design. The
quantum experiments are simulator-based. The work does not claim physical-QPU
security, calibrated hardware-noise coverage, provider attestation,
multi-tenancy protection, production authentication, or deployed runtime
enforcement.
