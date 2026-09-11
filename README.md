# Observational Indistinguishability and Integrity Blind Regions in Hybrid Quantum-Classical Workflows

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22706167.svg)](https://doi.org/10.5281/zenodo.22706167)
[![CI](https://github.com/roberto-fernandez-barrios/hybrid-quantum-classical-integrity/actions/workflows/tests.yml/badge.svg)](https://github.com/roberto-fernandez-barrios/hybrid-quantum-classical-integrity/actions/workflows/tests.yml)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-31016/)
[![License: Apache-2.0](https://img.shields.io/badge/code-Apache--2.0-blue.svg)](LICENSE)

Official source code and reproducibility artifact for *Observational
Indistinguishability and Integrity Blind Regions in Hybrid Quantum-Classical
Workflows*.

## Overview

Hybrid quantum-classical workflows combine datasets, preprocessing,
parameterized circuits, kernel estimation, classical learning, evaluation
labels, and reported conclusions. Integrity checks at one stage can therefore
miss interventions at another stage even when every observed value available
to the auditor remains internally consistent.

This work formalizes auditability relative to an intervention class, an
information set, and explicitly trusted references. It characterizes
structural blind regions, establishes claim-relative evidence sufficiency and
necessity within the declared reference lattice, and evaluates those
boundaries across simulated
quantum-kernel workflows, multiple network-security datasets, calibrated
decision rules, and an adaptive stress test.

The repository contains the article and supplement, frozen derived evidence,
cryptographic manifests, the implementation and tests, and the instructions
needed for quick verification or full replay from public benchmark datasets.

## Main result

- Auditability is information-relative: indistinguishable interventions cannot
  be separated from the baseline using the declared view alone.
- Structural blind regions shrink monotonically as trusted evidence refines the
  observable view.
- Reference granularity is claim-relative: a trusted same-batch scalar
  reference suffices for a conclusion-only claim; an aggregate reference also
  certifies aggregate integrity; item-identity integrity needs item alignment.
- An adaptive, cluster-preserving fingerprint attack stress-tests the limits of
  aggregate statistical monitoring under the frozen design.
- A preregistered geometry-aligned sensitivity separates the clean-resample
  calibration geometry from same-item editing and preserves the matched
  control/adaptive ordering while retaining materiality.
- The v1.3.8 editorial and traceability release promotes the published aligned
  label response to the primary statistical interpretation, exposes the
  existing without-KS ablation and recomputes presentation values from
  manifested evidence without changing the structural theory or frozen design.
- The quantum path is a bounded simulator-based instantiation that separates
  semantic, estimated, and observed kernels without making a hardware claim.

## Artifact

| Resource | Location |
|---|---|
| Paper | [PDF](output/pdf/paper15_tdsc_submission.pdf) |
| Supplement | [PDF](output/pdf/paper15_tdsc_supplement.pdf) |
| Current release | [Version 1.3.8](https://doi.org/10.5281/zenodo.22706167) |
| Immutable predecessor | [Zenodo version 1.3.7](https://doi.org/10.5281/zenodo.22698329) |
| Version history | [Zenodo concept record](https://doi.org/10.5281/zenodo.22550852) |
| Immutable release tag | `paper15-q1-v1.3.8` |
| Manuscript source | [`publication/tdsc/`](publication/tdsc/) |
| Reproducibility guide | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |

Version `1.3.8` is a final editorial and traceability release. It promotes the
already published geometry-aligned label response to the primary statistical
interpretation, clarifies claim-relative evidence sufficiency, exposes the
existing without-KS ablation, corrects release-status and draw-independence
wording, and removes hard-coded presentation values in favor of manifested
recomputation. No scientific observation, dataset, model, split, attack,
calibration draw, theorem or prior evidence file is changed. Version `1.3.7`,
its tag, DOI and every earlier release remain immutable.

## Quick verification

Python 3.10 is the reference interpreter. From the repository root:

```bash
python -m venv .venv
python -m pip --python .venv install -r requirements-lock.txt
python -m pip --python .venv install -e . --no-deps
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider
.venv/Scripts/python.exe -m src.experiments.verify_publication_artifact --root publication/artifact
pwsh -NoProfile -File publication/tdsc/build.ps1
```

On Linux or macOS, replace `.venv/Scripts/python.exe` with
`.venv/bin/python`. The authoritative expected counts, page totals, DOI, and
PDF hashes are in [`publication/RELEASE_STATUS.md`](publication/RELEASE_STATUS.md).

## Repository layout

| Path | Purpose |
|---|---|
| `.github/` | Continuous-integration workflow for tests and artifact verification |
| `src/` | Workflow, attack, integrity, dataset, and experiment implementations |
| `tests/` | Unit, formal, consistency, and evidence-contract tests |
| `scripts/` | Dataset verification and supporting reproducibility utilities |
| `manuscript/` | Formal model, adversary model, preregistrations, amendments, and result provenance |
| `publication/artifact/` | Self-contained compact verification artifact and manifested evidence |
| `publication/tdsc/` | Article and supplement sources, generated tables, figures, and clean build |
| `output/pdf/` | Published article and supplement PDFs |

Generated data, raw benchmark files, experiment workspaces, caches, and local
submission administration are intentionally excluded from Git.

## Reproduction

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for:

1. quick artifact verification without raw datasets;
2. full replay from the public CICIDS2017, UNSW-NB15, and ToN-IoT sources;
3. environment and dataset hash requirements;
4. expected verifier, test, and build outputs;
5. compute requirements and external-data limitations.

The compact verifier fails closed on missing files, manifest mismatches,
unexpected row counts, incomplete acceptance checks, or changed primary
counts.

## Scientific scope

The artifact establishes integrity conclusions only relative to the declared
views, trusted references, intervention classes, and frozen finite design. It
does not establish physical-QPU security, calibrated device-noise coverage,
provider attestation, scheduling or multi-tenancy protection, side-channel
resistance, production authentication, or deployed incident operations.

Exact-statevector execution is an ideal-simulation acceleration, and the
finite-shot conditions are binomial fidelity-estimation emulators rather than
measurements from a QPU or calibrated backend.

## Citation

Citation metadata is provided in [CITATION.cff](CITATION.cff).

- Version: `1.3.8`
- Version DOI: [10.5281/zenodo.22706167](https://doi.org/10.5281/zenodo.22706167)
- Immutable predecessor DOI: [10.5281/zenodo.22698329](https://doi.org/10.5281/zenodo.22698329)
- Concept DOI: [10.5281/zenodo.22550852](https://doi.org/10.5281/zenodo.22550852)

Use the version DOI when citing the exact published artifact. The concept DOI
resolves to the latest archived version in the Zenodo record family.

## Funding

This work is part of grant PID2024-155693NB-C43, ATHENA-AEGIS (Advanced Secure
Technologies for Hybrid Quantum-Classical Environments and Applications),
funded by MICIU/AEI/10.13039/501100011033 and by ERDF/EU.

## License

Software is licensed under [Apache License 2.0](LICENSE). Derived evidence,
figures, tables, and documentation are licensed under
[CC BY 4.0](LICENSE-DATA). Manuscript sources and PDFs are author preprints;
see [LICENSING.md](LICENSING.md) for the precise file-level scope.
