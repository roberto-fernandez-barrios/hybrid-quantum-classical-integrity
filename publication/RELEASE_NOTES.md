# Paper 1.5 release notes

The authoritative counts of every release (manifests, outputs, files, tests,
pages, hashes, DOIs) are generated into `publication/RELEASE_STATUS.md`;
the notes below describe scope only.

## 1.3.0 — 2026-09-07 (final scientific closure for IEEE TDSC)

- Amendment A2: the family-calibration rule of 1.2.0 had a false guarantee
  (five-vector counterexample); replaced by the full conformal max-rank
  p-value with exact level 10/201 under exchangeability, ties included, and
  tested exhaustively; the 1.2.0 rule kept only for comparison.
- Gate F regenerated: 0.056 / 0.058 / 0.048 / 0.053 against 0.061 / 0.073 /
  0.048 / 0.079 (1.2.0) and 0.125 / 0.203 / 0.048 / 0.259 (union);
  decomposition of the 1.2.0 excess into rule bias and design effect;
  exchangeable re-splits; E1 reported in the primary aggregate, alone and
  excluded; split construction as sensitivity.
- Gate D regenerated with the conformal rule and the benign-interruption cost
  made explicit: the trusted item-aligned regime serves none of the 7,008
  material observations but interrupts 52 % of benign near-null variation;
  policy taxonomy corrected (P2 calibrated risk-tolerant, P3 strict
  fail-closed); "offline end-to-end" wording throughout.
- Gate A (new, preregistered): adaptive cluster-preserving perturbation,
  240 exact-statevector jobs; detection of feature drift under the conformal
  rule falls from 0.96–1.00 to 0.01–0.66 at matched strengths while 83–91 %
  of the conclusion changes are kept; P2 serves 959–1,328 of 3,418 material
  adaptive rows; the trusted regime blocks all of them.
- Formal core 1.2 (Proposition 5 replaced, Proposition 7 quantum lattice,
  metric remark, C9), statement-by-statement formal review with brute-force
  tests; seventh evidence manifest; verifier and CI extended; 76 tests.
- Final hostile review (Audit 5) fixed one headline number (material
  retention of the adaptive attacker: 83–91 %, not 88–95 %), the abstract
  range of the conformal rule (0.053–0.058 for the regimes with feature
  evidence) and one rounding inconsistency before the release build.
- Manuscript: calibration, benign cost, adaptive attacker and quantum lattice
  in the main text; ZZ-versus-SVC in the supplement; dataset weights explicit;
  conformal / multiple-testing related work.
- No QPU, calibrated noise, scheduling, provider, multi-tenancy, deployed
  service or Fleet Management experiment was added; tags 1.1.0, 1.1.1 and
  1.2.0 immutable.

## 1.2.0 — 2026-09-07 (scientific closure for IEEE TDSC; superseded in one point by 1.3.0)

- Formal core rebuilt around observational indistinguishability with explicit
  trusted references; monotonicity, closure, materiality and no-local-guarantee
  results; eight counterexamples with witnesses; earlier Propositions 1–2
  become corollaries.
- Audit finding (prereg amendment A1): the clipped "harm" endpoint hid 433
  expansion and 59 Gate-1 label-path rows whose balanced accuracy *rose*; the
  signed counts are now reported and verified (2,184 / 983 / 433 and
  1,276 / 105 / 59); all 2,617 changed conclusions carry item-aligned
  confusion evidence.
- Gate F: decision-level (family-wise) calibration; false-alarm rate of the
  batch-level regimes 0.061 / 0.073 / 0.048 / 0.079 against 0.125 / 0.203 /
  0.048 / 0.259 for the 1.1.0 union rule; inference unit corrected to the
  (environment, split) cluster. The rule's stated guarantee was later found
  false (1.3.0, amendment A2).
- Gate D: end-to-end `allow/hold/block` evaluation of four policies over five
  regimes on 24,000 frozen observations; batch-level regimes with feature
  evidence serve 4,322–4,494 of 7,008 materially changed results, the
  label-marginal regime serves all of them, the trusted item-aligned regime
  serves none with zero false holds; composition with the frozen
  contracts reproduces their actions.
- Adversary model with four classes and uncontrolled roots; threat-model card
  2.0; related work extended to classical stealth/detectability, runtime
  assurance, integrity monitoring and evaluation integrity.
- Sixth evidence manifest (21 tables), verifier extended, 12 new tests,
  generated number macros, single source of truth for counts, portable
  reproduction guide with dataset hashes, machine-specific paths removed,
  historical drafts archived.
- No kernel, model or draw re-executed; tags 1.1.0 and 1.1.1 immutable.

## 1.1.1 — 2026-09-06 (editorial)

Funding acknowledgement wording only; evidence byte-identical to 1.1.0.

## 1.1.0 — 2026-09-06 (TDSC submission release)

Three preregistered reinforcement gates (null calibration with disjoint clean
pools, symmetric preprocessing ablation, cross-validated tuning), fifth
evidence manifest, confirmed author block, licenses, first Zenodo version.

## 1.0.0 — 2026-08-09 (first submission candidate; historical)

First submission-candidate release of the manuscript and artifact. It froze
the scientific scope at information-set conditional integrity auditing and
excluded QPU execution, scheduling, multi-tenancy, provider security and
operational Fleet Management. Contents: anonymous Markdown source and a
visually verified 16-page PDF; three figures and their source tables;
claim-specific novelty review through 9 August 2026; compact Gate 1,
expansion, quantum-integrity and HSaaS evidence with four embedded manifests
and 22 manifested outputs; exact dependency lock, 17-test suite and
independent verifier; cover letter, highlights, title-page template and
checklist. The tag `paper15-q1-v1.0.0` was never archived with a DOI.
