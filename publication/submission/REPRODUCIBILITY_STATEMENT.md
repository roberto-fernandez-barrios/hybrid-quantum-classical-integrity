# Reproducibility statement

The review artifact for Paper 1.5 v1.3.4 contains the source code, locked
dependencies, tests, compact derived evidence, generated tables and figures,
eight evidence manifests, the artifact-wide SHA-256 manifest, preregistrations,
the reference audit, and a fail-closed verifier. A reviewer can follow
`README.md` → `Q1_REPRODUCTION.md` → `publication/artifact/README.md` →
`python -m src.experiments.verify_publication_artifact --root publication/artifact`.

The compact artifact starts from frozen derived evidence. It does not include
raw benchmark jobs or redistribute CICIDS2017, UNSW-NB15, or ToN-IoT datasets.
The full tagged source snapshot contains the replay code; official dataset
sources, expected hashes, staging, and the distinction between compact
verification and full replay are documented in `Q1_REPRODUCTION.md`.

Version 1.3.4 is a corrective bibliographic/editorial release. No experiment,
kernel, model, dataset, seed, attack, draw, intervention, policy decision,
scientific result, or formal theorem was re-executed or changed. Derived
metadata/coverage artifacts were regenerated from frozen code/evidence to
correct an inconsistency; scientific observations and decisions are unchanged.

Zenodo concept DOI: 10.5281/zenodo.22550852. The immutable v1.3.4 version DOI
is recorded in `CITATION.cff` and `publication/DOI_STATUS.md` after release.
