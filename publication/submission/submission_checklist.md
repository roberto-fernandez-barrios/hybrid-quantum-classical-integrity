# IEEE TDSC submission checklist

## Scientifically closed

- [x] Central claim frozen as information-set conditional integrity auditing.
- [x] Propositions 1–2 framed as elementary support, not primary novelty.
- [x] ZZ-versus-SVC retained only as secondary, pipeline-conditional evidence.
- [x] Label intervention distinguished from statistical label shift.
- [x] Five split clusters treated as within-environment uncertainty only.
- [x] Fixed OOD environments not presented as population sampling.
- [x] Headroom, scaling, class balance and categorical-feature limits disclosed.
- [x] Quantum gate explicitly limited to ideal simulation and shot emulation.
- [x] Hash chain described as tamper-evident, not identity/non-repudiation.
- [x] ATHENA contribution bounded; no claim of complete project or WP5 coverage.
- [x] QPU, scheduling, multi-tenancy, provider security and Fleet Management excluded.
- [x] Abstract is one paragraph and within the 150--250-word working target.
- [x] Five IEEE Index Terms are supplied.
- [x] In-text citations and reference keys are bidirectionally complete.
- [x] Figures and tables are cited, captioned and reproducibly sourced.
- [x] Five evidence manifests, 44 outputs, primary count claims and the
      calibrated label-path checks verify (artifact 1.1.0).
- [x] Reinforcement gates preregistered before execution
      (`manuscript/paper15_v11_reinforcement_prereg.md`) and reported as executed.
- [x] Related work rechecked on 2026-09-06 (QML-PipeGuard, evaluation blindness).
- [x] Tests and CI include the publication-artifact verifier.
- [x] TDSC `IEEEtran` Computer Society source and separate supplement compile.
- [x] Main paper is below the 12-page final-paper planning ceiling.
- [x] Main and supplement use US Letter, two-column layout, vector figures, and
      embedded fonts.
- [x] Current route is a regular paper; no open special issue justified a
      change of claim or scope on 10 August 2026.

## Administrative actions requiring the authors

- [x] Confirm author list/order, affiliations, corresponding author and ORCIDs (2026-09-06; mirrored from the companion intrusion-detection study).
- [x] Confirm CRediT roles and competing-interest wording (all authors, 2026-09-06).
- [x] Select a software/artifact license approved by all rights holders
      (Apache-2.0 code, CC BY 4.0 evidence/documentation, manuscript excluded).
- [x] Funding statement confirmed by all authors; any extra co-funding clause
      required by the executed award is a proof-stage addition.
- [x] Repository visibility: public since 2026-09-06; `main` aligned with the
      science branch. **A LICENSE file must be added before the DOI is minted.**
- [x] `CITATION.cff` and `.zenodo.json` carry confirmed authors, licenses and
      the version DOI (2026-09-06).
- [x] Upload/publish the archive in Zenodo and insert the reserved DOI
      (`10.5281/zenodo.22550853`, artifact 1.1.0, tag `paper15-q1-v1.1.0`).
- [ ] Remove author-identifying funding/AI metadata if the journal requires it
      outside the anonymous manuscript file; retain it on the title page.
- [x] Confirm originality/not-under-review statement in the cover letter.
- [x] Disclose closely related papers/preprints with a difference statement
      (Section II-C, title page, cover letter); attach copies if the portal asks.
- [x] Replace `Anonymous Author(s)` in both LaTeX sources (done 2026-09-06).
- [ ] Recheck the TDSC portal on submission day for article type, page limit,
      biographies, template, supplement designation, and current special issues.
- [x] Obtain all-author approval of the generative-AI disclosure (system,
      sections and level of use; approved 2026-09-06).

These items are authorship, legal or external-account decisions. They do not
require new scientific experiments.

## Automated preflight immediately before upload

- [ ] Run `pwsh -File publication/tdsc/build.ps1` from the repository root.
- [ ] Run the complete test suite and artifact verifier.
- [ ] Confirm that the build reports no broken references or overfull boxes.
- [ ] Confirm that PDF hashes match `publication/tdsc/CHECKSUMS.sha256`.
- [ ] Search the active package for `DOI PENDING`, `Anonymous Author`, and any
      obsolete journal name; only deliberately unresolved administrative fields
      may remain.
- [ ] Inspect every final PDF page at submission size after author metadata is
      inserted.
