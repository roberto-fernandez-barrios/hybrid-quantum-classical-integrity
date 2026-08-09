# Paper 1.5 compact review artifact — version 1.0.0

This directory is the self-contained, derived-evidence artifact for
*Information-Set Conditional Integrity Auditing for Hybrid Quantum-Classical
Kernel Workflows*.

It contains no raw benchmark dataset. The 21 MB package includes the manuscript,
figures, source tables, environment lock, source/tests snapshot, four evidence
manifests and all 22 outputs referenced by those manifests.

## Verify without recomputation

From the unpacked artifact directory:

```powershell
python -m pip install pandas==2.3.3
python software\src\experiments\verify_publication_artifact.py --root .
```

Expected report:

```json
{
  "expansion_label_rows": 3600,
  "expansion_positive_impact": 2184,
  "gate1_label_rows": 1440,
  "gate1_positive_impact": 1276,
  "manifested_outputs": 22,
  "manifests": 4
}
```

The report also includes the number of files checked against
`ARTIFACT_MANIFEST.sha256`. Any changed byte, row count, acceptance check or
primary count causes a non-zero exit.

## Layout

- `evidence/` — derived CSV/JSON evidence and embedded SHA-256 contracts;
- `manuscript/` — final source, novelty audit, threat model, figures and tables;
- `environment/` — Python 3.10.16 dependency lock and packaging metadata;
- `software/` — exact Python source and tests snapshot used for version 1.0.0.

See `manuscript/Q1_REPRODUCTION.md` for full dataset staging and experiment
replay. Exact-statevector and binomial-shot emulation are not QPU evidence.
