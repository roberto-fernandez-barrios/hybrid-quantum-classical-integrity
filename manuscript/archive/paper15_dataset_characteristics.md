# Dataset characteristics

## data\cicids_subset.csv
- rows: 3000
- columns: 78
- label_col: label
- feature_columns_before_projection: 77
- label_counts:
  - 0: 1500
  - 1: 1500
- positive_class_rate_assuming_1_is_positive: 0.500000

## data\processed\cicids_ood_tuesday_train.csv
- rows: 3000
- columns: 79
- label_col: label
- feature_columns_before_projection: 78
- label_counts:
  - 1: 1500
  - 0: 1500
- positive_class_rate_assuming_1_is_positive: 0.500000

## data\processed\cicids_ood_wednesday_test.csv
- rows: 3000
- columns: 79
- label_col: label
- feature_columns_before_projection: 78
- label_counts:
  - 0: 1500
  - 1: 1500
- positive_class_rate_assuming_1_is_positive: 0.500000

## Experimental subsampling
- max_train: 128
- max_test: 128
- projected_dimensions_main_feature_map_comparison: 8, 10, 12
- projected_dimensions_original_ZZ_analysis: 4, 6, 8, 10, 12
- split_seeds: 42, 43, 44
- model_seeds: 42, 43
- paired_seed_units: 6