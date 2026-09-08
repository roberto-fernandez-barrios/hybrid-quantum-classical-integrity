# TDSC submission build `1.3.2-tdsc`

Date: 2026-09-08. Controlled methodological/editorial correction of 1.3.1;
the experimental evidence is frozen at artifact 1.3.0 and no experiment,
kernel, job, attack, seed, model, dataset or draw was rerun. All co-authors
approved the changes.

## Closing changes in 1.3.2

- Repair B after a source-to-policy audit: Class A now accurately denotes the
  statistically thresholded aggregate comparisons against a
  benchmark-protected clean same-item-set oracle that were executed, without
  item pairing or demonstrated deployed authentication. B/C remain trusted
  aggregate/item-aligned exact invariants.
- Reference provenance, granularity and statistical/exact decision semantics
  are distinct; the headline is minimum evidence granularity relative to the
  protected integrity claim.
- Corollaries 1–3 are contiguous. `I_Ym` is reported as zero containment with
  5,450 residual-blind material cases at the structural endpoint.
- Trusted cost distinguishes 85 gross exact blocks, 46 overlaps and 39 net
  additional near-null interruptions / 1,200 (3.25 percentage points).
- Adaptive results retain aggregate material served rates and add the complete
  per-strength materiality/detection/served profile (matched I_XFY range
  0.22–0.90).
- `unsafe_allow` remains an internal CSV identifier; manuscript terminology is
  materially altered audit result served, never an allowed malicious network
  event. The 24,000 rows, materiality endpoint, conformal premise and
  batch/trusted denominators are explicitly bounded.
- Abstract is 188 words. Quantum validation remains ideal-statevector and
  finite-shot emulation only. Eight evidence manifests and permanent closing
  guards are included.

## Inherited 1.3.1 corrections


- Abstract shortened to at most 250 words (CI test) with the conformal claim
  stated as a property under exchangeability and the executed rates
  (0.048–0.058) reported separately; the trusted-regime cost printed as
  629 of 1,200 near-null synthetic controls, mostly statistical holds.
- Introduction: concrete threat scenario (label join or store stale,
  corrupted or rewritten; a signature authenticates the object, not the
  item-level correspondence; aggregate reference for conclusion integrity,
  item alignment for identity, Proposition 6 when the attacker controls both).
- Related work: VAMP (Stokes, England, Kane, MILCOM 2021) positioned; Table 1
  rebuilt on nine axes including real QPU evidence, provider/authentication
  evidence, drift handling and deployed/runtime evaluation, where QCIVET,
  QML-PipeGuard and VAMP exceed this work.
- Section III-A: primitive/derived workflow state and intervention semantics;
  III-B: reference levels A (statistical or historical), B (trusted aggregate
  same-batch), C (trusted item-aligned same-batch); III-F: Proposition 7 with
  K_sem / K̂ / K_obs and class-indexed inclusions; (iii) corrected for
  finite-shot estimation.
- Table 3 (adversary): the last hand-typed retention range replaced by the
  generated 83–91 % macros; quantum rows annotated with the intervention
  class and the observed-kernel anchor.
- Section V-D and VI-C: P3 renamed coverage-complete abstaining with its
  definition (fail-closed on missing coverage; no minimum-power guarantee);
  the trusted-regime interruption decomposed (544 holds + 85 blocks = 629).
- Section VI-A/VI-B: zero-response cells reframed as validation checks; the
  witness table and the coverage-count table moved to the supplement or into
  the text (all counts kept); Fig. 3 (quantum heatmap) moved to the
  supplement next to its table.
- Figures: policy figure with non-colliding titles, legends off the data and
  the interruption decomposition annotated; adversarial figure with legends
  below the axes; heatmap re-sized for legibility.
- Discussion, limitations and conclusion aligned (near-null synthetic
  controls are not operational traffic; P3 limitation; exact-provenance cost
  is 85 of 1,200 on top of the statistical cost).

## Deliberately unchanged

- Every number, decision, manifest hash of the gate1, expansion, quantum
  integrity, hsaas and reinforcement evidence; the policy and adversarial
  tables differ only in the textual `policy_class` label of P3.
- Tags `paper15-q1-v1.1.0`, `paper15-q1-v1.1.1`, `paper15-q1-v1.2.0` and
  `paper15-q1-v1.3.0` and their Zenodo versions are immutable.

## Release

Page counts, PDF hashes, test and file counts are in
`publication/RELEASE_STATUS.md`. The version DOI is inserted by the release
pipeline before the annotated tag `paper15-q1-v1.3.1`
(`publication/DOI_STATUS.md`).

# Earlier builds

## `1.3.0-tdsc`

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
  abstaining, then labelled `strict`); offline end-to-end evaluation with
  cost endpoints; Gate A design.
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

Released as tag `paper15-q1-v1.3.0`, version DOI 10.5281/zenodo.22648573.

## Older builds

`1.2.0-tdsc` (2026-09-07): scientific closure (formal core, adversary model,
policy gates, retitling); superseded in one point by 1.3.0.
`1.1.1-tdsc` (2026-09-06): funding acknowledgement wording only.
`1.1.0-tdsc-rc2` (2026-09-06): three preregistered reinforcement gates, fifth
evidence manifest, QML-PipeGuard and evaluation-blindness positioning,
companion-work disclosure, confirmed author block, generative-AI disclosure;
submission release tagged `paper15-q1-v1.1.0`. `1.1.0-tdsc-rc1` (2026-08-10):
first TDSC conversion of the frozen 1.0.0 evidence.
