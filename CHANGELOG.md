# Changelog

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
