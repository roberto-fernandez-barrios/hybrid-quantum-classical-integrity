# IEEE TDSC submission checklist — Paper 1.5 v1.3.4

Scientific evidence is frozen at artifact 1.3.0 and the methodology is
unchanged from 1.3.2. Version 1.3.4 is a corrective bibliographic/editorial
release. Derived metadata/coverage artifacts were regenerated from frozen
code/evidence to correct an inconsistency; scientific observations and
decisions are unchanged.

## Bibliography and companion work

- [x] The 58 entries inherited from v1.3.3 were verified individually against
      primary sources with a 2026-09-08 inclusive cutoff.
- [x] The final bibliography/audit set contains 60 entries: all 58 inherited
      entries plus Barber et al. and Engelen et al.
- [x] Koebler, Ginart, Kundu, Shi, SLSA, Alsaedi and Volya metadata corrected.
- [x] No duplicate DOI, arXiv identifier or normalized title; no unaudited,
      missing, uncited or dangling key.
- [x] Conditional Validity and VBC cite their public arXiv records.
- [x] Certificates is a submitted manuscript; its Zenodo identifier is
      identified only as a software/reproducibility artifact, not a paper DOI.
- [x] PDFs of all three companion manuscripts are in
      `related_manuscripts/` for portal upload.
- [x] Machine-readable record: `publication/tdsc/reference_audit_v1.3.4.csv`.

## Objective corrections and framing

- [x] Gate A per-regime and headline ranges are generated from frozen evidence
      into `policy_macros.tex`; no active TeX headline range is hand typed.
- [x] Gate A is framed as a stress test of a fragile cluster-dependent
      fingerprint, not defeat of a generally powerful detector.
- [x] CICIDS2017 cluster/duplicate limitations are acknowledged using primary
      literature.
- [x] Trusted containment is attributed constructively to Corollary 3; the
      experiment measures gross, overlapping and net interruption cost.
- [x] Aggregate served fractions are summaries of the prespecified
      equal-weight intervention grid, not deployment prevalence.
- [x] The abstract says “feature-bearing batch policies,” so `I_Ym` is not
      silently included in the 4,365--4,496 range.
- [x] `I_XFY_trusted` feature coverage is calibrated; prediction and label
      coverage are exact. The CSV, policy manifest and global manifest bind
      this correction, and offline guards prevent regression.
- [x] “Commitment” is not used to imply a cryptographic primitive; protected
      aggregate/item-aligned references are named directly.
- [x] Index Terms use “workflow integrity,” not “runtime assurance.”
- [x] P3 is “coverage-complete abstaining,” with no universal power claim.
- [x] The main text gives the reduced-calibration/coarser-resolution reason for
      not adopting the split construction and briefly discloses the A2 timing.

## Editorial and portal package

- [x] Title unchanged.
- [x] Cover letter is a stable first-submission letter, not a version history,
      and is limited to approximately 1--1.5 pages.
- [x] Main/supplement PDF metadata includes title, authors, subject and keywords.
- [x] Supplement is standalone with title, authors, affiliation, relation,
      funding context, version and artifact DOI.
- [x] Reproduction guide distinguishes compact derived-evidence artifact from
      the full tagged source and explicitly excludes raw jobs/datasets.
- [x] AI disclosure records OpenAI Codex and Anthropic Claude Code accurately;
      human authors verified and accept responsibility.
- [x] HSaaS is connected once, conservatively, to the ATHENA-AEGIS prototype;
      no deployment, Fleet Management, confidentiality, QPU-protection or
      provider-attestation claim is made.
- [x] Separate CRediT, competing-interest, funding, AI-use, related-work and
      reproducibility statements are present.

## Automated final preflight

- [x] Complete `pytest` passes with at least 330 tests.
- [x] Artifact verifier passes: eight evidence manifests and the generated
      counts recorded in `publication/RELEASE_STATUS.md`.
- [x] Dataset hash verifier passes without downloading or executing jobs.
- [x] Scientific evidence files changed relative to v1.3.3: zero.
- [x] Only the declared frozen-derived coverage CSV and binding manifests differ
      within artifact evidence/metadata.
- [x] Main is at most 12 US-Letter pages and abstract is at most 200 words.
- [x] Supplement page/floats, every main/supplement page, figures, dense tables,
      reference-column balance and font embedding are visually inspected.
- [x] No undefined citation/reference, duplicate label or material overfull box.
- [x] Two consecutive builds are byte-identical, or any toolchain limitation is
      documented without layout/hash hacks.
- [x] DOI fields in BibTeX, rendered BBL and visible PDF have been counted; the
      official IEEEtran behavior is documented without modifying the BST.
- [ ] Final artifact/source ZIPs and `SHA256SUMS.txt` verify locally and on Zenodo.

## Release and stop rule

- [ ] Fresh version DOI reserved through `ZENODO_TOKEN` without logging it.
- [ ] DOI inserted; full checks rerun; release commit and annotated immutable tag
      `paper15-q1-v1.3.4` created and pushed.
- [ ] GitHub Release and Zenodo version published; version/concept DOI relation,
      assets, sizes and hashes verified.
- [ ] Documentary post-release commit pushed; `main` and
      `paper15-q1-expansion` synchronized; final tree clean.
- [ ] Portal-facing files reviewed, but nothing submitted automatically.

After v1.3.4 the article is reopened only for a portal requirement, editor,
real reviewer, or a later objectively demonstrated error. There is no
preventive v1.3.5 or additional hostile review.
