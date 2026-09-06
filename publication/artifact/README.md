# Paper 1.5 compact review artifact — version 1.1.0

This directory is the self-contained, derived-evidence artifact for
*Information-Set Conditional Integrity Auditing for Hybrid Quantum-Classical
Kernel Workflows*.

It contains no raw benchmark dataset. The 40 MB package includes the
TDSC manuscript and supplement PDFs, the frozen Markdown source, figures, figure
source tables, environment lock, source/tests snapshot, 5
evidence manifests and all 44 outputs referenced by
those manifests.

Version 1.1.0 adds the preregistered reinforcement gates (null calibration of
non-invariant sensors with disjoint clean pools, symmetric preprocessing
ablation, cross-validated tuning of both learners). The 1.0.0 evidence, counts
and claims are unchanged.

## Verify without recomputation

From the unpacked artifact directory:

```powershell
python -m pip install pandas==2.3.3
python software\src\experiments\verify_publication_artifact.py --root .
```

The verifier checks every embedded manifest, all manifested outputs, their
SHA-256 hashes and row counts, the primary label-boundary counts (3,600 / 2,184
expansion and 1,440 / 1,276 Gate 1), the calibrated label-path consistency
checks of the reinforcement gate, and every file listed in
`ARTIFACT_MANIFEST.sha256`. Any changed byte, row count, acceptance check or
primary count causes a non-zero exit.

## Layout

- `evidence/` — derived CSV/JSON evidence and embedded SHA-256 contracts
  (`gate1`, `expansion`, `quantum_integrity`, `hsaas`, `reinforcement`);
- `manuscript/` — TDSC PDFs, frozen source, novelty audit, threat model,
  preregistration, reinforcement summary, figures and tables;
- `environment/` — Python 3.10 dependency lock and packaging metadata;
- `software/` — exact Python source and tests snapshot used for version 1.1.0.

See `manuscript/Q1_REPRODUCTION.md` for dataset staging and experiment replay.
Exact-statevector evaluation and binomial-shot emulation are not QPU evidence.

## Licensing and citation

Software is released under Apache-2.0 (`LICENSE`); derived evidence, figures
and documentation under CC BY 4.0 (`LICENSE-DATA`); the manuscript PDFs are
author preprints excluded from both (`LICENSING.md`). Cite the version DOI in
`CITATION.cff`.
