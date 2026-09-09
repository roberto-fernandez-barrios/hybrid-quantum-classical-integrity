# Paper 1.5 release notes

The authoritative counts of every release (manifests, outputs, files, tests,
pages, hashes, DOIs) are generated into `publication/RELEASE_STATUS.md`;
the notes below describe scope only.

## 1.3.4 — 2026-09-09 (final corrective bibliographic/editorial release)

- No experiment, kernel, model, dataset, seed, attack, draw, intervention,
  policy decision, scientific result or formal theorem was re-executed or
  changed. Scientific evidence remains frozen at artifact 1.3.0.
- Audited the 58 inherited references one by one against primary sources;
  corrected Koebler, Ginart, Kundu, Shi, SLSA, Alsaedi and Volya metadata;
  added Barber et al. and Engelen et al.; corrected companion identifiers.
- Corrected the trusted-regime feature coverage in one derived CSV from
  `exact` to `calibrated`; updated its embedded/global manifest hashes only.
- Generated Gate A range extrema from the frozen evidence and reframed the
  gate as a fragile cluster-fingerprint stress test. Trusted containment is
  theory-predicted; the experiment measures its cost. Aggregate served
  fractions describe the equal-weight stress grid, not deployment prevalence.
- Closed cover letter, PDF metadata/layout, standalone supplement metadata,
  reproduction documentation, AI disclosure, companion PDFs and release
  packaging. Full validation is recorded in `publication/RELEASE_STATUS.md`.

## 1.3.3 — 2026-09-08 (bibliographic/editorial closure; evidence frozen)

- Bibliographic/editorial correction only; no experiment, kernel, draw,
  model, seed, intervention, policy decision or scientific evidence was rerun
  or changed. Methodology is unchanged from 1.3.2.
- Verified and added Hinder et al. on adaptive drift evasion, Max-Rank on
  dependence-aware conformal multiple testing and QProv on quantum provenance.
- Added the original Simplex paper, TESSERACT and RFC 9334/RATS under a strict
  text-neutral space budget; did not add the optional Acharya--Zhang or
  reproducible-quantum-build preprints.
- Upgraded the quantum-security primer, QEMI and quantum Design by Contract to
  verified publications; corrected Quantum Leak and Qiskit metadata.
- Corrected positioning against VAMP, adaptive-drift prior art, QCIVET and
  QML-PipeGuard. The central claim remains claim-relative minimum evidence
  granularity, not novelty for any constituent technique.
- Completed one readability pass without changing science, claims, results,
  structure or page count; main remains 12 pages and abstract at most 200 words.
- Added permanent bibliographic guards. Bibliographic cutoff: 2026-09-08.

## 1.3.2 — 2026-09-08 (methodological alignment; evidence frozen at 1.3.0)

- Audited every selected sensor through runner, builders, frozen CSVs and
  policy API; repair B corrects Class A to the executed statistical
  same-item-set aggregate comparisons against a benchmark-protected oracle.
- No experiment/job/model/kernel/attack/seed/dataset/draw rerun. New evidence
  consists only of derived reference, trusted-cost and strength-profile tables.
- Trusted cost: 85 gross exact blocks, 46 overlapping batch interruptions,
  39 net additional / 1,200 (3.25 percentage points).
- Adaptive P2 served rates: aggregate 0.39/0.28/0.29 for I_X/I_XF/I_XFY;
  complete profile by strength, materiality and detection, including matched
  I_XFY range 0.22–0.90.
- Corollaries contiguous; `I_Ym` zero containment / 5,450 residual-blind
  material cases; audit-corruption endpoint, structural tau→0+, clustered
  units and unequal denominators explicitly framed.
- Abstract 188 words; bounded simulator-only quantum branch; eight evidence
  manifests; submission package and ATHENA/2.5 traceability updated.

## 1.3.1 — 2026-09-07 (formal and editorial correction; evidence frozen at 1.3.0)

- No new science: no kernel, job, dataset, seed, model, QPU, noise or attacker
  run; every number of the article is that of 1.3.0.
- Proposition 7(iii) restated for finite-shot estimation: exact equality has
  false-alarm probability 1 − Pr[K̂ = K₀ | honest], not universally one
  (1/2 at fidelity 1/2 with two shots); the discrepancy needs a calibrated
  null, otherwise no statistical integrity claim. Semantic, estimated and
  observed kernels separated with class-indexed inclusions.
- Workflow state split into primitive and derived artifacts with explicit
  intervention semantics (`src/integrity/workflow_state.py`).
- Reference taxonomy: Level A statistical/historical reference; Level B
  trusted aggregate same-batch reference; Level C trusted item-aligned
  same-batch reference.
- Conformal claim: finite-sample level under exchangeability stated
  separately from the observed rates of the executed design (0.048–0.058).
- P3 renamed coverage-complete abstaining (fail-closed on missing coverage;
  no minimum-power guarantee); decisions unchanged; `policy_class` label
  regenerated.
- Headline numbers from macros only (83–91 % retention); trusted-regime
  interruption decomposed: 544 statistical holds + 85 exact-reference blocks
  = 629 of 1,200 near-null synthetic controls.
- Abstract ≤ 250 words (CI test); threat scenario; VAMP and a nine-axis
  positioning table; figures made legible; 12 + 17 pages.
- New tests (`tests/test_workflow_state.py`,
  `tests/test_manuscript_consistency.py`); verifier records the interruption
  decomposition; tags 1.1.0–1.3.0 immutable.

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
  material observations but interrupts 52 % of the near-null controls;
  policy taxonomy corrected (P2 calibrated risk-tolerant; P3 abstaining,
  renamed coverage-complete abstaining in 1.3.1); "offline end-to-end"
  wording throughout.
- Gate A (new, preregistered): adaptive cluster-preserving perturbation,
  240 exact-statevector jobs; detection of feature drift under the conformal
  rule falls from 0.96–1.00 to 0.01–0.66 at matched strengths while 83–91 %
  of the conclusion changes are kept; P2 serves 959–1,328 of 3,418 material
  adaptive rows; the trusted regime blocks all of them.
- Formal core 1.2 (Proposition 5 replaced, Proposition 7 quantum lattice,
  metric remark, C9), statement-by-statement formal review with brute-force
  tests; seventh evidence manifest; verifier and CI extended; 76 tests.
- Final hostile review (Audit 5) fixed one headline number (material
  retention of the adaptive attacker: 83–91 %, correcting the higher range of
  the first draft; one hand-typed row survived and was removed in 1.3.1), the abstract
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
