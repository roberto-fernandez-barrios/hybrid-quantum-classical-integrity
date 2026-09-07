# Changelog

## 1.3.0 — 2026-09-07

Final scientific iteration of Paper 1.5 for IEEE TDSC. After this version the
article is reopened only for an objective error that invalidates a claim, an
editorial requirement of the journal, or a reviewer request. Protocol:
`manuscript/paper15_v13_prereg.md` (frozen at `cad9136`, amendment A3 at
`678c5d7`, both before any regenerated table or new job existed).

- **Amendment A2 — the family rule of 1.2.0 is replaced.** Two independent
  reviews found that Proposition 5(b) of 1.2.0 was false: the executed rule
  scored calibration draws against the calibration set only and the audited
  batch against all calibration draws, and with several sensors and tied
  max-rank scores the claimed level `alpha + 1/(n+1)` fails (five-vector
  counterexample: 0.60 against a claimed 0.40). Artifact 1.3.0 adopts the
  full conformal max-rank p-value, whose level under exchangeability is
  exactly `floor(alpha (n+1))/(n+1) = 10/201` with ties counted against
  firing; the deterministic counting bound behind it is tested exhaustively
  over every weak ordering (all tie patterns) for small `n` and one to three
  sensors, over random tied configurations with up to ten sensors, and
  against the counterexample (`tests/test_family_calibration_exhaustive.py`).
  The 1.2.0 rule is kept only as a comparison column.
- **Gate F regenerated** from the frozen 1.1.1 outputs (no kernel, model or
  draw re-executed): decision false-alarm rates 0.056 / 0.058 / 0.048 /
  0.053 (I_X / I_XF / I_Ym / I_XFY) against 0.061 / 0.073 / 0.048 / 0.079 for
  the 1.2.0 rule and 0.125 / 0.203 / 0.048 / 0.259 for the union. The 1.2.0
  excess decomposes into rule bias (+0.005 / +0.015 / 0 / +0.025) and design
  effect (+0.006 / +0.008 / −0.003 / +0.003); under 30 exchangeable
  re-splits of the pooled draws the 1.2.0 rule fires at 0.052 / 0.058 /
  0.040 / 0.059 and the conformal rule at 0.044 / 0.042 / 0.040 / 0.036. E1
  is kept in the primary aggregate and also reported alone (0.125 / 0.115 /
  0.045 / 0.123) and excluded (0.048 / 0.052 / 0.048 / 0.045). The split
  construction is reported once as sensitivity S1.
- **Gate D regenerated** with the conformal rule and new cost metrics
  (benign interruption on the 1,200 near-null shams, clean false action with
  its denominator flagged, non-material interruption): P2 serves 4,496 /
  4,365 / 7,008 / 4,390 / 0 of 7,008 material observations (1.2.0 rule:
  4,494 / 4,327 / 7,008 / 4,322 / 0); the trusted item-aligned regime serves
  none and has zero clean false actions on its 1,200 exact-zero rows but
  interrupts 52 % of benign near-null variation (544 held, 85 blocked). The
  evaluation is described everywhere as offline, on frozen outputs.
- **Policy taxonomy corrected**: P0 baseline; P1 uncalibrated, risk-tolerant;
  P2 calibrated, risk-tolerant (serves under a declared residual blind
  region; never called fail-closed); P3 strict fail-closed / abstaining. The
  contracts of the prototype fail closed on their invariants. "Missing
  evidence is never converted into assurance" replaced by the precise
  statement (P2 converts it into a declared, accepted risk; P3 abstains).
- **Gate A (preregistered, new)**: adaptive cluster-preserving perturbation
  (adversary class F5, previously "discussed, not executed"): the executed
  drift mechanisms applied only to the entries outside the tight feature
  clusters that the batch-level fingerprint relies on; 240 exact-statevector
  jobs, eight environments, strengths 0.02–0.50, matched controls that
  reproduce the frozen expansion exactly. At matched strengths detection
  under the conformal rule falls from 0.96–1.00 to 0.01–0.34 (I_X) and
  0.06–0.66 (I_XF) while 83–91 % of the material fraction is kept; P2 serves
  1,328 / 959 / 1,006 of 3,418 material adaptive rows in I_X / I_XF / I_XFY
  against 0 / 6 / 10 for the executed mechanisms; the trusted regime blocks
  every material adaptive row. L3 (confusion-preserving relabeling) is not
  executed, with the reason recorded (808 realised witnesses; no conclusion
  could change).
- **Formal core 1.2**: Proposition 5 replaced; Proposition 7 (the quantum
  branch as an instance of the view lattice: provenance refines semantics,
  algebra and outputs coarsen the kernel, shot noise turns the exact anchor
  into a calibrated test); remark on metrics other than balanced accuracy
  (any function of the confusion matrix; AUC needs the score-label
  multiset); counterexample C9. Statement-by-statement review with
  hypotheses, proof, counterexample search and brute-force tests
  (`manuscript/FORMAL_REVIEW_1.3.0.md`, `tests/test_formal_core.py`).
- **Manuscript**: abstract, introduction and conclusion rewritten around the
  corrected calibration, the benign cost of the trusted regime and the
  adaptive attacker; new related-work subsection on conformal p-values,
  exchangeability, rank tests and Tippett / Westfall–Young; ZZ-versus-SVC
  moved to the supplement except one sentence; the dataset weight made
  explicit (five CICIDS2017, two UNSW-NB15, one ToN-IoT environments; six of
  nine with Gate 1); adversary table with the executed F5 row; new
  three-panel policy figure with the benign cost; new adversarial figure;
  the adversarial table and the coverage heatmap in the supplement
  (12-page ceiling).
- **Code**: `src/integrity/family_calibration.py` (conformal rule, split
  construction, superseded rule for comparison), `src/attacks/cluster_preserving.py`,
  `paper_f5` suite, `run_v13_f5_queue`, `build_q1_adversarial_evidence`,
  `make_q1_adversarial_figures`, extended policy builder, tables and
  figures; seventh evidence manifest (12 tables); verifier extended to the
  conformal level under re-splits and to the adversarial replay and trust
  checks; 35 new tests (76 in total).
- **Documentation**: preregistration with amendments A2 and A3, result
  summary, formal review, ATHENA traceability, threat-model card and
  adversary model (F5 executed), Paper 2.5 roadmap (§23), hostile review
  audit 5, generative-AI disclosure extended to the 1.3.0 work.
- **Final hostile review (Audit 5)** before the release build: the
  materiality-retention headline of the adaptive attacker was mis-stated as
  88–95 % in the first draft of this version; the generated ratios are
  0.831–0.907, so every document now says 83–91 % and the article uses
  generated macros; the abstract range of the conformal rule is stated for
  the regimes with feature evidence (0.053–0.058); one rounding
  inconsistency (0.565 printed as 0.57 in prose, 0.56 in tables) aligned;
  machine-specific paths removed from the queue status file and from the
  manuscript copy of the expansion gate-completeness table.
- Tags `paper15-q1-v1.1.0`, `paper15-q1-v1.1.1` and `paper15-q1-v1.2.0` and
  their Zenodo versions are immutable.

## 1.2.0 — 2026-09-07

Scientific closure of Paper 1.5 for IEEE TDSC. No kernel, model or draw was
re-executed; every new table is computed from the frozen 1.1.1 outputs. The
1.0.0 evidence tables are byte-identical except for the two gate-completeness
tables, whose machine-specific raw-result paths were replaced by
repository-relative paths. **Superseded by 1.3.0 in one point: the
family-calibration rule of Gate F had a false guarantee (amendment A2); its
numbers are correct for the rule as executed and are kept as comparison
columns.**

- **Formal core reconstructed** around observational indistinguishability:
  states, interventions, views, refinement order, trusted item-aligned
  references, structural versus sensor blind regions, monotonicity under
  refinement, exact closure conditions, materiality-forces-separability,
  three auditor classes (reference-anchored, anchor-free, post-hoc),
  union-versus-family calibration and the no-local-guarantee proposition.
  Propositions 1--2 of 1.1.x are now corollaries. Eight minimal
  counterexamples with witness counts from the frozen evidence
  (`manuscript/FORMAL_CORE.md`).
- **Finding of the audit (prereg amendment A1):** `impact_bal_acc` in the
  1.0.0/1.1.x tables is the positive part of the signed conclusion change.
  The 1.1.1 sentence "no negative impact occurs" referred to the clipped
  column: 433 expansion and 59 Gate-1 label-path rows *raise* the reported
  balanced accuracy. The material label-path count under the signed
  definition is 2,617 (2,184 lowered + 433 raised); all 2,617 carry non-zero
  item-aligned confusion evidence. The verifier now recomputes the signed
  counts (2,184 / 983 / 433 and 1,276 / 105 / 59).
- **Gate F (preregistered):** family-wise (decision-level) calibration of
  every batch-level regime from the existing calibration draws; decision
  false-alarm rate falls from 0.125 / 0.203 / 0.048 / 0.259 (union of
  per-sensor rules) to 0.061 / 0.073 / 0.048 / 0.079 on the disjoint
  evaluation draws; inference unit corrected to the (environment, split)
  cluster; earlier binomial intervals declared descriptive.
- **Gate D (preregistered):** end-to-end `allow/hold/block` evaluation of four
  policies over five information regimes on 24,000 frozen observations;
  primary endpoint unsafe allows: batch-level regimes with feature evidence
  serve 4,322--4,494 of 7,008 materially changed results, the label-marginal
  regime serves all of them, the trusted item-aligned regime serves none with
  zero false holds; composition with the six frozen contract
  envelopes reproduces their actions.
- **New code:** `src/integrity/family_calibration.py`, `src/hsaas/policy.py`,
  `src/experiments/build_q1_policy_evidence.py`, `make_q1_policy_tables.py`
  (LaTeX tables and number macros), `make_q1_policy_figures.py`,
  `make_release_status.py` (single source of truth for counts),
  `scripts/verify_datasets.py`; sixth evidence manifest (21 tables);
  verifier extended to the signed label counts and the policy claims;
  12 new tests.
- **Adversary model** (`manuscript/ADVERSARY_MODEL.md`, threat-model card
  2.0): every executed intervention assigned to fault robustness, integrity
  corruption, adversarial attack or adaptive attacker, with actor,
  capability, access point, knowledge, objective, budget, alterable assets,
  uncontrolled roots, observable set and supported claim.
- **Manuscript** retitled and reorganized around observability /
  indistinguishability, blind regions, trusted evidence, calibrated policy and
  end-to-end response; related work extended to stealthy-attack
  detectability in cyber-physical systems, runtime assurance, integrity
  monitoring and evaluation integrity; positive delimitation instead of
  "no previous study"; ZZ-versus-SVC demoted to a short secondary subsection
  with details in the supplement; signed conclusion counts reported.
- **Documentation and reproduction:** portable reproduction guide with
  official dataset sources, expected hashes, staging commands and PowerShell /
  POSIX forms; machine-specific paths removed from scripts and evidence;
  historical drafts moved to `manuscript/archive/` (non-authoritative);
  stale counts replaced by references to the generated
  `publication/RELEASE_STATUS.md`; ATHENA traceability and Paper 2.5
  roadmap updated so that calibration, contracts and hash chaining are
  attributed to Paper 1.5 and the 2.5 core is longitudinal, context-conditioned
  operational assurance on real execution.

## 1.1.1 — 2026-09-06

- funding acknowledgement compliance update: the statement now follows the
  formula prescribed by the Spanish State Research Agency for the 2024
  Knowledge Generation projects (grant PID2024-155693NB-C43, ATHENA-AEGIS,
  funded by MICIU/AEI/10.13039/501100011033 and by ERDF/EU);
- no scientific content, results, figures, data or claims changed; the derived
  evidence and its manifests are byte-identical to 1.1.0. New Zenodo version
  10.5281/zenodo.22552643 (concept DOI 10.5281/zenodo.22550852).

## 1.1.0 — 2026-09-06

- added three preregistered reinforcement gates without changing the frozen
  1.0.0 evidence or claims: null calibration of the non-invariant sensors with
  disjoint clean calibration/evaluation pools (`paper_null` suite,
  `clean_resample` control, alpha = 0.05 per sensor), a symmetric
  preprocessing ablation of the secondary ZZ-minus-SVC profile, and
  cross-validated tuning of both learners on training rows only;
- added `run_v11_reinforcement_queue`, `build_q1_reinforcement_evidence`,
  `make_q1_reinforcement_figures` and `assemble_publication_artifact`;
  extended the verifier to five manifests and the calibrated label-path checks;
- kept historical run identifiers stable: new runner options are excluded from
  the configuration fingerprint when at their defaults, and a frozen job
  regenerates bit-identically under single-threaded BLAS;
- retargeted the submission package to IEEE TDSC (rc2): confirmed author block,
  funding footnote, updated related work (QML-PipeGuard, evaluation blindness),
  companion-work disclosure, and generative-AI disclosure;
- updated the novelty review with the 6 September 2026 recheck.

## 1.0.0 — 2026-08-09

- froze the central claim as information-set conditional integrity auditing;
- completed the full manuscript with a 224-word abstract, Methods, Results,
  Discussion, Limitations and declarations;
- repositioned the propositions, contracts/hash chain and ZZ-SVC result as
  supporting rather than standalone novelty;
- added an updated nearest-work audit including QCIVET and concurrent 2026 work;
- corrected label-intervention terminology, evidence-set partial ordering,
  pseudo-replication, interval interpretation and headroom/preprocessing limits;
- added the 165-cell quantum integrity gate and six-scenario fail-closed contract
  demonstrator as bounded simulator evidence;
- corrected ATHENA-AEGIS traceability and limited WP5 attribution to Task 5.2;
- added an independent evidence/hash verifier, 17-test suite, CI and exact
  Python 3.10 environment lock;
- assembled a self-contained derived-evidence artifact and submission files.
