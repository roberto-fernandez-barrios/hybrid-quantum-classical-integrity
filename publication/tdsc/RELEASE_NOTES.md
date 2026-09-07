# TDSC submission build `1.2.0-tdsc`

Date: 2026-09-07. Scientific closure release. No kernel, model or draw was
re-executed with respect to 1.1.1; the two new gates are computed from the
frozen 1.1.1 outputs under a preregistered protocol
(`manuscript/paper15_v12_policy_prereg.md`, frozen at commit `2c2e54a` before
analysis, amendment A1 recorded on the first builder run).

## Changed in the manuscript

- Title and framing: observational indistinguishability and integrity blind
  regions across evidence boundaries, with the evaluation-label path as a
  protected boundary, explicit trusted references, multi-environment
  validation and executable calibrated fail-closed policy composition.
- Section III rebuilt as an observation model (states, interventions, views,
  refinement, trusted item-aligned references, structural versus sensor blind
  regions, Lemma 1, Propositions 1–6, Corollaries 1–2, eight counterexamples
  with witness counts). The earlier Propositions 1–2 are Corollary 1.
- Section IV: adversary and failure model (Table 3) with four classes and the
  roots each class cannot write.
- Related work extended to stealthy-attack detectability in cyber-physical
  systems, runtime assurance, integrity monitoring, evaluation integrity and
  quantum provenance; positioning table rewritten as a positive delimitation.
- Results: signed conclusion change reported (2,184 lowered / 983 unchanged /
  433 raised label rows; all 2,617 changed conclusions carry item-aligned
  confusion evidence); decision-level calibration (Gate F); end-to-end
  decisions (Gate D, Table 5, Fig. 2); ZZ-versus-SVC demoted to a short
  secondary subsection.
- Statistics: inference unit for false-alarm rates is the (environment,
  split) cluster; pooled rates and the 1.1.0 binomial intervals are
  descriptive; the residual excess of the family rule over nominal is
  reported as executed.
- All numbers of the new gates enter through generated macros
  (`tables/policy_macros.tex`).

## Deliberately unchanged

- No QPU, calibrated-noise, scheduling, provider, multi-tenancy or Fleet
  Management experiment was added.
- Abstract counts of the exact blind regions (3,600 / 1,800; 1,440 / 720),
  the 165-cell quantum gate and the six-scenario contract are untouched.
- Tags `paper15-q1-v1.1.0` and `paper15-q1-v1.1.1` and their Zenodo versions
  are immutable.

## Release

Page counts, PDF hashes, test and file counts are in
`publication/RELEASE_STATUS.md`. The version DOI is inserted by the release
pipeline before the annotated tag `paper15-q1-v1.2.0`
(`publication/DOI_STATUS.md`).

# Earlier builds

`1.1.1-tdsc` (2026-09-06): funding acknowledgement wording only.
`1.1.0-tdsc-rc2` (2026-09-06): three preregistered reinforcement gates, fifth
evidence manifest, QML-PipeGuard and evaluation-blindness positioning,
companion-work disclosure, confirmed author block, generative-AI disclosure;
submission release tagged `paper15-q1-v1.1.0`. `1.1.0-tdsc-rc1` (2026-08-10):
first TDSC conversion of the frozen 1.0.0 evidence.
