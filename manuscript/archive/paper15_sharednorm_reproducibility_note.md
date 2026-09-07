# Shared-normalization reproducibility note

The aggregate CSV contains model-local detectability columns:

`detectability_norm_group_cols = protocol,dataset_tag,model,svd_dim`

Therefore, these columns should not be used as the source for cross-model shared-normalized stealth ratios.

The manuscript uses the corrected archived derived artefacts in:

`results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm/`

The official verification command is:

```powershell
python -m src.experiments.verify_sharednorm_artifacts `
  --shared-dir results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm `
  --agg results/aggregated/agg_paper_core_all_fmaps_plus_baseline.csv

Expected QSVC-ZZ vs SVC-RBF ID shared-normalized stealth ratios:

dim=8: 1.588016
dim=10: 1.805480
dim=12: 1.666626
```
