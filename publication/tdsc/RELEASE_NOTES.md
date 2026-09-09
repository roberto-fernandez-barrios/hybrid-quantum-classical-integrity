# TDSC submission build `1.3.4-tdsc`

Date: 2026-09-09.

v1.3.4 is a corrective bibliographic/editorial release. No experiment,
kernel, model, dataset, seed, attack, draw, intervention, policy decision,
scientific result or formal theorem was re-executed or changed. The methodology
is unchanged from 1.3.2. Derived
metadata/coverage artifacts were regenerated from the frozen code/evidence to
correct an inconsistency; scientific observations and decisions are unchanged.

## Corrective closure

- Audited all 58 inherited references manually against primary records and
  froze the result in `reference_audit_v1.3.4.csv`; added Barber et al. on
  beyond-exchangeability conformal inference and Engelen et al. on CICIDS2017
  data quality.
- Corrected Koebler, Ginart, Kundu, Shi, SLSA, Alsaedi and Volya metadata;
  replaced the VBC manuscript/software citation with arXiv:2609.04388; retained
  Certificates as a submitted manuscript and labelled its Zenodo DOI as a
  software artifact.
- Corrected `policy_regime_coverage.csv`: the trusted regime has calibrated
  feature coverage and exact prediction/label coverage. Updated only that
  derived CSV and its manifests/hashes, with an offline regression guard.
- Derived all Gate A headline extrema from manifested frozen CSVs. The article
  now reports the feature regime separately from feature-plus-prediction and
  frames Gate A as a stress test of a fragile cluster-dependent fingerprint.
- Separated theory-predicted trusted containment from the empirical cost;
  labelled aggregate served fractions as summaries of the prespecified
  equal-weight intervention grid; made the label-marginal exclusion explicit.
- Replaced cryptographically ambiguous “commitment” wording with aggregate
  anchor/reference, changed the index term to “workflow integrity,” and
  clarified P3, the split construction, A2 disclosure and ATHENA-AEGIS HSaaS
  scope.
- Rewrote the cover letter as a stable first-submission letter; refreshed the
  title page, related-work disclosure, AI-use disclosure, reproduction guide,
  PDF metadata and portal-facing companion files.
- Kept the title, threat model, formal core, experiments and scientific results
  unchanged. Main and supplement validation results are recorded in
  `publication/RELEASE_STATUS.md`.

## Immutable predecessors

Tags and Zenodo records through `paper15-q1-v1.3.3` remain immutable.
