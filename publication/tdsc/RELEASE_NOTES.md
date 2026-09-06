# TDSC submission build `1.1.0-tdsc-rc2`

Date: 2026-09-06

`rc2` supersedes `rc1` (2026-08-10). The frozen 1.0.0 evidence, its counts and
the central claim are unchanged. `rc2` adds preregistered sensitivity evidence
and closes the author-side gates that could be closed without external
accounts.

## Added

- Three preregistered reinforcement gates (`manuscript/paper15_v11_reinforcement_prereg.md`,
  frozen before execution): null calibration of the non-invariant sensors with
  disjoint clean calibration/evaluation pools (alpha = 0.05 per sensor, 200 +
  200 draws per cell, eight environments); symmetric preprocessing ablation of
  the secondary ZZ-minus-SVC profile; cross-validated tuning of both learners
  on training rows only (CICIDS ID and UNSW temporal OOD, the latter selected
  by a rule recorded before execution).
- Fifth evidence manifest, 22 additional derived tables, one additional figure
  (`fig_q1_calibrated_coverage.pdf`), and verifier checks that the calibrated
  feature and feature-plus-prediction regimes never fire on evaluation-label
  interventions.
- Related work: QML-PipeGuard (arXiv:2605.25066) and evaluation blindness
  (arXiv:2608.02786); positioning table rows.
- Section II-C "Relation to Companion Work" disclosing the three companion
  manuscripts with an explicit non-overlap statement.
- Confirmed author block, affiliation and funding footnote (single-anonymous
  TDSC default); updated generative-AI disclosure (OpenAI Codex and Anthropic
  Claude Code).

## Deliberately unchanged

- No QPU, calibrated-noise, scheduling, provider, multi-tenancy or Fleet
  Management experiment was added.
- Abstract counts, Propositions 1--2, the 3,600/1,800/2,184 label-path counts,
  the 165-cell quantum gate and the six-scenario contract are untouched.
- No DOI, license, competing-interest statement or CRediT confirmation was
  guessed.

## Release

All-author approval of the manuscript, CRediT roles, competing interests,
funding statement and AI disclosure was received on 2026-09-06. Licenses were
added (Apache-2.0 code, CC BY 4.0 evidence/documentation, manuscript excluded),
the version DOI `10.5281/zenodo.22550853` was reserved and inserted, the PDFs were rebuilt
(11 + 6 pages, clean preflight), checksums regenerated and the artifact
reassembled and verified. `rc2` is the submission release, tagged
`paper15-q1-v1.1.0`.
