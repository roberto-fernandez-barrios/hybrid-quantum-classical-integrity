# Changelog

## 1.2.0 — 2026-09-07

Scientific closure of Paper 1.5 for IEEE TDSC. No kernel, model or draw was
re-executed; every new table is computed from the frozen 1.1.1 outputs. The
1.0.0 evidence tables are byte-identical except for the two gate-completeness
tables, whose machine-specific raw-result paths were replaced by
repository-relative paths.

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
