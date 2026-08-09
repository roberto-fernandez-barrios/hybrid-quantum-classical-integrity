# Gate 1 result - ID seed expansion

Experiment:

- Branch: paper15-q1-expansion
- Protocol: ID
- Dataset: CICIDS-derived binary benchmark
- max_train/max_test: 128/128
- dims: 8,10,12
- split_seeds: 42,43,44,45,46
- model_seeds: 42,43,44,45
- seed units: 20
- models: SVC-RBF, QSVC-ZZ, QSVC-Z, QSVC-PauliXYZ

Raw completion:

- expected CSV: 240
- expected JSON: 240
- completed successfully: yes

Main result:

QSVC-ZZ remains consistently more impacted than SVC-RBF under ID perturbations.

Impact ratios ZZ/SVC:

- dim 8: 2.524113
- dim 10: 3.093780
- dim 12: 3.323361

Shared-normalized stealth ratios ZZ/SVC:

- dim 8: 1.734340
- dim 10: 2.045335
- dim 12: 2.121251

Paired differences QSVC-ZZ minus SVC-RBF:

Impact:

- dim 8: mean diff 0.024267, CI95 [0.017738, 0.030797]
- dim 10: mean diff 0.032888, CI95 [0.025731, 0.040045]
- dim 12: mean diff 0.038550, CI95 [0.032887, 0.044214]

Shared-normalized stealth:

- dim 8: mean diff 0.011299, CI95 [0.008121, 0.014477]
- dim 10: mean diff 0.015877, CI95 [0.012354, 0.019401]
- dim 12: mean diff 0.017975, CI95 [0.015102, 0.020849]

Decision:

Gate 1 passes. The main ID claim survives expansion from 6 to 20 seed-units.

Interpretation update:

The prior-preserving target-shift perturbation remains the clearest high-impact/low-detectability auditability-gap case. This is not exclusive to QSVC-ZZ; it appears across both classical and quantum kernels. Therefore, the strongest framing is:

1. auditability gaps are a benchmark-level failure mode;
2. QSVC-ZZ has the strongest aggregate ID vulnerability profile among the evaluated kernels.
