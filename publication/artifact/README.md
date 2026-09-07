# Paper 1.5 compact review artifact — version 1.3.0

This directory is the self-contained, derived-evidence artifact for
*Observational Indistinguishability and Integrity Blind Regions Across the
Evidence Boundaries of Hybrid Quantum-Classical Kernel Workflows*.

It contains no raw benchmark dataset. The 57 MB package includes the
TDSC manuscript and supplement PDFs, the frozen Markdown source, figures, figure
source tables, environment lock, source/tests snapshot, 7
evidence manifests and all 83 outputs referenced by
those manifests.

Version 1.1.0 added the preregistered reinforcement gates (null calibration of
non-invariant sensors with disjoint clean pools, symmetric preprocessing
ablation, cross-validated tuning of both learners); version 1.1.1 changed only
the funding acknowledgement wording; version 1.2.0 adds the preregistered
policy-level gates (family-wise regime calibration and the offline end-to-end
`allow/hold/block` evaluation), computed from the frozen 1.1.1 outputs without
re-executing any kernel or draw; version 1.3.0 replaces the family-calibration
rule of 1.2.0 (whose stated guarantee was false; amendment A2) by the full
conformal max-rank p-value, regenerates the policy gates from the same frozen
outputs, and adds the preregistered adversarial Gate A (adaptive
cluster-preserving perturbation, 240 exact-statevector jobs). The 1.0.0
evidence tables are byte-identical except for the two gate-completeness
tables, whose machine-specific raw-result paths were replaced by
repository-relative paths.

## Verify without recomputation

From the unpacked artifact directory:

```powershell
python -m pip install pandas==2.3.3
python software\src\experiments\verify_publication_artifact.py --root .
```

The verifier checks every embedded manifest, all manifested outputs, their
SHA-256 hashes and row counts, the primary label-boundary counts (3,600 / 2,184
expansion and 1,440 / 1,276 Gate 1, plus the signed decreased / unchanged /
increased counts), the calibrated label-path consistency checks of the
reinforcement gate, the policy-level claims of the regenerated policy gates
(including the exact level of the conformal rule under exchangeable
re-splits), the replay and trust checks of the adversarial gate, and every file
listed in `ARTIFACT_MANIFEST.sha256`. Any changed byte, row count, acceptance check or
primary count causes a non-zero exit.

## Layout

- `evidence/` — derived CSV/JSON evidence and embedded SHA-256 contracts
  (`gate1`, `expansion`, `quantum_integrity`, `hsaas`, `reinforcement`,
  `policy`, `adversarial`);
- `manuscript/` — TDSC PDFs, frozen source, novelty audit, adversary model and
  threat-model card, formal core, preregistrations, result summaries, figures
  and tables;
- `environment/` — Python 3.10 dependency lock and packaging metadata;
- `software/` — exact Python source and tests snapshot used for version 1.3.0.

See `manuscript/Q1_REPRODUCTION.md` for dataset staging and experiment replay.
Exact-statevector evaluation and binomial-shot emulation are not QPU evidence.

## Licensing and citation

Software is released under Apache-2.0 (`LICENSE`); derived evidence, figures
and documentation under CC BY 4.0 (`LICENSE-DATA`); the manuscript PDFs are
author preprints excluded from both (`LICENSING.md`). Cite the version DOI in
`CITATION.cff`.
