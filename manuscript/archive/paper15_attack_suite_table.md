## Appendix A. Perturbation suite

**Table A1. Paper-core perturbation suite.** The main experiments evaluate the following attack identifiers. Clean rows are excluded from this list; the 18 rows correspond to the perturbation cases used in the ID attack summaries.

| ID | Family | Attack identifier | Nominal strength |
|---:|---|---|---:|
| 1 | corruption | `feature_sign_flip_p_0.020` | 0.02 |
| 2 | corruption | `feature_sign_flip_p_0.050` | 0.05 |
| 3 | corruption | `feature_sign_flip_p_0.100` | 0.1 |
| 4 | covariate_shift | `mean_shift_pf_delta_0.020` | 0.02 |
| 5 | covariate_shift | `scaling_drift_alpha_0.020` | 0.02 |
| 6 | covariate_shift | `mean_shift_pf_delta_0.050` | 0.05 |
| 7 | covariate_shift | `scaling_drift_alpha_0.050` | 0.05 |
| 8 | covariate_shift | `mean_shift_pf_delta_0.100` | 0.1 |
| 9 | covariate_shift | `scaling_drift_alpha_0.100` | 0.1 |
| 10 | pipeline | `feature_dropout_p_0.020` | 0.02 |
| 11 | pipeline | `feature_dropout_p_0.050` | 0.05 |
| 12 | pipeline | `feature_dropout_p_0.100` | 0.1 |
| 13 | target_shift | `label_flip_prior_preserving_r_0.020` | 0.02 |
| 14 | target_shift | `label_flip_r_0.020` | 0.02 |
| 15 | target_shift | `label_flip_prior_preserving_r_0.050` | 0.05 |
| 16 | target_shift | `label_flip_r_0.050` | 0.05 |
| 17 | target_shift | `label_flip_prior_preserving_r_0.100` | 0.1 |
| 18 | target_shift | `label_flip_r_0.100` | 0.1 |
