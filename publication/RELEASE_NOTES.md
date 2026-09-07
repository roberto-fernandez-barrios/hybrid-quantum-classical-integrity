# Paper 1.5 release notes

The authoritative counts of every release (manifests, outputs, files, tests,
pages, hashes, DOIs) are generated into `publication/RELEASE_STATUS.md`;
the notes below describe scope only.

## 1.2.0 — 2026-09-07 (scientific closure for IEEE TDSC)

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
  (environment, split) cluster.
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
