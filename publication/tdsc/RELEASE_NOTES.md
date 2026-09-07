# TDSC submission build `1.3.0-tdsc`

Date: 2026-09-07. Final scientific closure release. Gates F and D were
regenerated from the frozen 1.1.1 outputs without re-executing any kernel,
model or draw; Gate A (240 exact-statevector jobs) is the only new
computation. Protocol: `manuscript/paper15_v13_prereg.md`, frozen at commit
`cad9136` before any regenerated table or new job existed (amendment A3 at
`678c5d7`, before the first builder run).

## Changed in the manuscript

- Section III-D: Proposition 5(b) replaced by the full conformal max-rank
  p-value with its exact finite-sample level and proof; Proposition 5(c)
  records the falsity of the 1.2.0 rule with the five-vector counterexample.
- Section III-F (new): Proposition 7, the quantum branch as an instance of
  the view lattice; remark after Proposition 3 on metrics other than balanced
  accuracy.
- Section II-C (new): calibration of multi-sensor decisions (conformal
  p-values, exchangeability, Tippett, Westfall–Young, ties, dependence among
  conformal p-values).
- Section IV: adversary table with the executed cluster-preserving attacker
  (F5) and conformal identifying rates.
- Section V: dataset weights explicit (five CICIDS2017, two UNSW-NB15, one
  ToN-IoT environments; six of nine with Gate 1); policy taxonomy (P0
  baseline, P1 uncalibrated risk-tolerant, P2 calibrated risk-tolerant, P3
  strict fail-closed); offline end-to-end evaluation with cost endpoints;
  Gate A design.
- Section VI: decision-level calibration with the decomposition of the 1.2.0
  excess into rule bias and design effect and E1 reported separately;
  offline end-to-end decisions with the benign-interruption cost of the
  trusted regime; new subsection on the adaptive cluster-preserving attacker;
  ZZ-versus-SVC reduced to one sentence (details in the supplement).
- Figures: single-panel coverage heatmap (Fig. 1); three-panel policy figure
  with the benign cost (Fig. 2); adversarial figure (Fig. 3); quantum heatmap
  (Fig. 4). Tables: main policy table with clean FPR and benign interruption;
  main adversarial table.
- Sections VII–IX: contract wording made precise (contracts fail closed on
  invariants; P2 serves under declared residual uncertainty; P3 abstains);
  discussion and limitations extended to the adaptive attacker, the marginal
  nature of the conformal level and the benign cost of provenance.
- Acknowledgment: generative-AI disclosure extended to the 1.3.0 work.
- All numbers of the regenerated and new gates enter through generated macros
  (`tables/policy_macros.tex`).

## Deliberately unchanged

- No QPU, calibrated-noise, scheduling, provider, multi-tenancy, deployed
  service or Fleet Management experiment was added.
- Abstract counts of the exact blind regions (3,600 / 1,800; 1,440 / 720), the
  signed label counts, the 165-cell quantum gate and the six-scenario
  contract are untouched.
- Tags `paper15-q1-v1.1.0`, `paper15-q1-v1.1.1` and `paper15-q1-v1.2.0` and
  their Zenodo versions are immutable.

## Release

Page counts, PDF hashes, test and file counts are in
`publication/RELEASE_STATUS.md`. The version DOI is inserted by the release
pipeline before the annotated tag `paper15-q1-v1.3.0`
(`publication/DOI_STATUS.md`).

# Earlier builds

`1.2.0-tdsc` (2026-09-07): scientific closure (formal core, adversary model,
policy gates, retitling); superseded in one point by 1.3.0.
`1.1.1-tdsc` (2026-09-06): funding acknowledgement wording only.
`1.1.0-tdsc-rc2` (2026-09-06): three preregistered reinforcement gates, fifth
evidence manifest, QML-PipeGuard and evaluation-blindness positioning,
companion-work disclosure, confirmed author block, generative-AI disclosure;
submission release tagged `paper15-q1-v1.1.0`. `1.1.0-tdsc-rc1` (2026-08-10):
first TDSC conversion of the frozen 1.0.0 evidence.
