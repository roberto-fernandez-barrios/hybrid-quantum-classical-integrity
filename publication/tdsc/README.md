# IEEE TDSC manuscript package (release 1.3.4; experimental evidence frozen at 1.3.0)

This directory contains the submission sources for the regular-paper candidate
"Observational Indistinguishability and Integrity Blind Regions in Hybrid
Quantum-Classical Workflows". The
manuscript is formatted with `IEEEtran` in Computer Society journal mode.

## Source inventory

- `main.tex` — complete article: abstract (170–200 words, CI-checked),
  introduction with a concrete threat scenario and compact related-work
  positioning (including VAMP, Hinder et al., Max-Rank, QProv, QCIVET,
  QML-PipeGuard, authenticated provenance, Simplex, TESSERACT and RATS), observation model with primitive
  and derived artifacts, audited three-axis reference profile with A/B/C
  shorthand and the quantum branch as an
  instance of the view lattice (semantic, estimated and observed kernels;
  Proposition 7 corrected for finite-shot estimation), adversary and failure
  model with the executed adaptive attacker, methodology (policy P3 as
  coverage-complete abstaining), results (validation checks of the
  structural prediction, conformal decision-level calibration with the
  executed rates reported separately from the exchangeability property,
  offline end-to-end decisions with the interruption cost decomposed into
  statistical holds and exact-reference blocks, the adaptive
  cluster-preserving attacker, quantum-workflow coverage), integrity-audit
  contract, discussion and limitations, conclusion, declarations;
- `supplement.tex` — formal core with proofs (Lemma 1, Propositions 1–7,
  Corollaries 1–3, including the finite-shot counterexample), experimental
  design, coverage contract, statistical units and dependence structure,
  exact-statevector validation, quantum gate (table and heatmap), contract
  and policy composition, the 1.1.0 reinforcement gates, the regenerated
  1.2.0/1.3.0 policy gates with the 1.2.0 rule as comparison, the 1.3.0
  adversarial gate in full, the secondary model-impact profile, and the
  reproduction mapping;
- `references.bib` — bibliography cited by the main article;
- `reference_audit_v1.3.4.csv` — frozen reference-by-reference primary-source
  audit (58 inherited entries plus two bounded additions);
- `figures/` — vector figures used in the article and supplement
  (`fig_q1_policy_decisions.pdf`, `fig_q1_adversarial_cluster_preserving.pdf`,
  `fig_q1_quantum_integrity_contract.pdf`, `fig_q1_calibrated_coverage.pdf`,
  `fig_q1_external_forest.pdf`,
  `fig_q1_sensor_coverage.pdf`);
- `tables/` — LaTeX tables and the number-macro file `policy_macros.tex`,
  all generated from the manifested CSV evidence by
  `src/experiments/make_q1_reinforcement_tables.py` and
  `src/experiments/make_q1_policy_tables.py` (never edited by hand);
- `SUPPLEMENT_README.md` — IEEE-oriented description and execution guide;
- `CLAIMS_TRACEABILITY.md` — claim-to-evidence map;
- `build.ps1` — clean, checked LaTeX build;
- `make_submission_package.ps1` — creates the self-contained, versioned TDSC
  source ZIP under `publication/`;
- `RELEASE_NOTES.md` — submission-build scope;
- `CHECKSUMS.sha256` — hashes of the rendered submission PDFs;
- `VERSION` — submission build identifier.

The cover letter, title-page metadata, AI disclosure and portal checklist are
in `publication/submission/`. Journal rules and the template audit are in
`journal/`.

## Build

Prerequisites are PowerShell 7 (`pwsh`, cross-platform), a LaTeX distribution
providing `pdflatex`, `bibtex` and `IEEEtran`, and Poppler's `pdfinfo`. From
the repository root:

```powershell
pwsh -NoProfile -File publication/tdsc/build.ps1
```

The script copies the sources into a fresh directory below `tmp/`, compiles
the main article and supplement from that clean staging directory, rejects
broken references and overfull boxes, checks the 12-page article ceiling, and
writes `output/pdf/paper15_tdsc_submission.pdf` and
`output/pdf/paper15_tdsc_supplement.pdf`. The page counts and PDF hashes of
the released build are recorded in `publication/RELEASE_STATUS.md`
(generated); any required biographies can change pagination.

### Bibliography rendering audit

The final `references.bib` contains 43 DOI fields. The official
`IEEEtran.bst` used by this build emits none of those fields in `main.bbl`;
the visible DOI strings in the article are documentary/funding identifiers in
the prose, not bibliography-field output. This is the unmodified official
style behavior. The source retains every verified DOI in `references.bib` and
the primary URL in `reference_audit_v1.3.4.csv`; no BST substitution, explicit
DOI duplication, URL duplication, or layout workaround is applied merely to
force DOI display.

## Scientific verification

Python 3.10 is the frozen reference interpreter. From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m src.experiments.verify_publication_artifact `
  --root publication\artifact
```

The verifier checks the artifact-wide SHA-256 manifest, eight evidence
manifests, the manifested outputs, table shapes, the primary count claims
including the signed label-path counts, the calibrated label-path checks, the
policy-level claims (including the level of the conformal rule under
exchangeable re-splits and the decomposition of the trusted-regime
interruption into 544 holds and 85 blocks) and the replay and trust checks of
the adversarial gate used by the paper. The test suite adds the
intervention-semantics and finite-shot tests (`tests/test_workflow_state.py`)
and the manuscript consistency gates (`tests/test_manuscript_consistency.py`:
abstract length, superseded headline strings, conformal and P3 wording,
interruption decomposition). Full replay instructions are in
`Q1_REPRODUCTION.md`; raw public benchmark datasets are staged by the
documented procedures and are not redistributed.

## Claim boundary

The paper establishes integrity auditability only relative to a declared view,
declared trusted references and a declared intervention class. It combines
the observation model, exact and calibrated blind regions, an explicit
adversary model with an executed adaptive attacker, multi-dataset/fixed-OOD
validation, conformal decision-level calibration, an offline end-to-end
policy evaluation on frozen outputs with its benign cost, bounded
simulator-only quantum controls and a local contract prototype. It does not
establish QPU security, calibrated device-noise coverage, scheduling
security, provider integrity or attestation, multi-tenancy protection,
deployed runtime services, context-conditioned runtime calibration under
non-stationarity, recovery, or operational Fleet Management. The ZZ-versus-SVC
profile is secondary evidence reported in the supplement.

## Author actions

All authors confirmed authorship, ORCIDs, CRediT roles, competing interests,
funding wording, the AI-use disclosure and the licensing scheme on
2026-09-06; the corrective bibliographic/editorial 1.3.4 release is covered by the
AI-use disclosure and remains subject to author responsibility. The version DOI of 1.3.4 is inserted by the release
pipeline (`publication/DOI_STATUS.md`). IEEE Computer Society author
guidance verified on 2026-09-08: regular Transactions papers are limited to
12 formatted pages including references and biographies (USD 220 per
overlength page); author biographies are not required for journal
submissions; the article is at 12 pages without biographies.

Version 1.3.4 is a corrective bibliographic/editorial release. No experiment,
kernel, model, dataset, seed, attack, draw, intervention, policy decision,
scientific result or formal theorem was re-executed or changed. Derived
metadata/coverage artifacts were regenerated from the frozen code/evidence to
correct an inconsistency; scientific observations and decisions are unchanged.
