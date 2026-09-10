# Release notes — v1.3.7

Version DOI: 10.5281/zenodo.22698329. Concept DOI:
10.5281/zenodo.22550852.

Version 1.3.7 is the sensor-correction and label-geometry closure release. It
corrects a histogram-support defect in the Jensen--Shannon drift sensors and
completes the preregistered geometry-aligned sensitivity for label-side
statistical response. All datasets, environments, rows, splits, model seeds,
model configurations, kernels, maps, attacks, strengths, calibration draws,
policies and structural theorems remain unchanged.

The historical audit found 744 direct defective coordinates (527
lineage-deduplicated scientific evaluations), all in applicable feature JSD
under mean shift or scaling drift; every family-scored NaN row already had
another sensor and both primary decisions firing. The correction nevertheless
changes already-finite JSD coordinates and thresholds, so the release contains
the complete dependency-limited replay and an auditable old/new ledger.

The original label result is reproduced at 11/2,617 conformal and 43/2,617
union. Under the aligned `s(E,T_y(B))` geometry it becomes 343/2,700 and
1,183/2,700. All 764 aggregate-blind aligned rows remain exactly equal to
their paired clean sensor response, and exact trusted-reference results are
unchanged.

Headline policy deltas, sensor decomposition, the frozen-only descriptive
without-KS ablation, L1 threshold lattice description, preregistration,
manifests and complete validation results are included in the artifact.
Previous releases remain immutable.
