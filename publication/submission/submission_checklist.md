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
- [x] Four evidence manifests, 22 outputs and primary count claims verify.
- [x] Tests and CI include the publication-artifact verifier.
- [x] TDSC `IEEEtran` Computer Society source and separate supplement compile.
- [x] Main paper is below the 12-page final-paper planning ceiling.
- [x] Main and supplement use US Letter, two-column layout, vector figures, and
      embedded fonts.
- [x] Current route is a regular paper; no open special issue justified a
      change of claim or scope on 10 August 2026.

## Administrative actions requiring the authors

- [ ] Confirm author list/order, affiliations, corresponding author and ORCIDs.
- [ ] Confirm CRediT roles and competing-interest wording.
- [ ] Select a software/artifact license approved by all rights holders.
- [ ] Confirm the executed-award co-funding formula, if any.
- [ ] Decide when the private GitHub repository may become public.
- [ ] Populate `CITATION.cff.in` and `.zenodo.json.in` with confirmed metadata.
- [ ] Upload/publish the archive in Zenodo and insert the reserved DOI.
- [ ] Remove author-identifying funding/AI metadata if the journal requires it
      outside the anonymous manuscript file; retain it on the title page.
- [ ] Confirm originality/not-under-review statement in the cover letter.
- [ ] Disclose and attach closely related papers/preprints with a concise
      difference statement if the IEEE Author Portal requests them.
- [ ] Replace `Anonymous Author(s)` in both LaTeX sources; TDSC is normally
      single-anonymous.
- [ ] Recheck the TDSC portal on submission day for article type, page limit,
      biographies, template, supplement designation, and current special issues.
- [ ] Obtain all-author approval of the generative-AI disclosure.

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
