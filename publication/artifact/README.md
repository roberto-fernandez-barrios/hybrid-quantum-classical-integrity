# Compact verification artifact — version 1.3.6

This directory is the self-contained, derived-evidence artifact for
*Observational Indistinguishability and Integrity Blind Regions in Hybrid
Quantum-Classical Workflows*.

It contains no raw benchmark dataset. The 74 MB package includes the
article and supplement PDFs, scientific provenance, figures, figure source
tables, environment lock, source/tests snapshot, 9
evidence manifests and all 93 outputs referenced by
those manifests.

## Verify without recomputation

From the unpacked artifact directory:

```powershell
python -m pip install pandas==2.3.3
python software\src\experiments\verify_publication_artifact.py --root .
```

The verifier checks every embedded manifest, all manifested outputs, their
SHA-256 hashes and row counts, the primary label-boundary counts, calibrated
policy checks, adversarial replay and trust checks, and every file listed in
`ARTIFACT_MANIFEST.sha256`. Any changed byte, row count, acceptance check, or
primary count causes a non-zero exit.

## Layout

- `evidence/` — derived CSV/JSON evidence and embedded SHA-256 contracts
  (`gate1`, `expansion`, `quantum_integrity`, `hsaas`, `reinforcement`,
  `policy`, `adversarial`, `amendment_v132`, `geometry_sensitivity`);
- `manuscript/` — article PDFs, formal and adversary models,
  preregistrations, result summaries, figures, and tables;
- `environment/` — Python 3.10 dependency lock and packaging metadata;
- `software/` — exact Python source and tests snapshot used for version 1.3.6.

See `manuscript/REPRODUCIBILITY.md` for dataset staging and experiment replay.
Exact-statevector evaluation and binomial-shot emulation are not QPU evidence.

## Licensing and citation

Software is released under Apache-2.0 (`LICENSE`); derived evidence, figures
and documentation under CC BY 4.0 (`LICENSE-DATA`); the manuscript PDFs are
author preprints excluded from both (`LICENSING.md`). Cite the version DOI in
`CITATION.cff`.
