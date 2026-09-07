# Paper 1.5 Q1 Expansion - Gate 1

Branch:

paper15-q1-expansion

Fallback frozen version:

tag paper15-v10-workshop-ready

Goal:

Test whether the main ID findings survive a larger seed design.

Current workshop version used:

- split_seeds: 42,43,44
- model_seeds: 42,43
- seed units: 6

Gate 1 expansion:

- split_seeds: 42,43,44,45,46
- model_seeds: 42,43,44,45
- seed units: 20
- protocol: ID only
- dims: 8,10,12
- feature maps: zz,z,pauli_xyz
- max_train: 128
- max_test: 128

Success criteria:

1. QSVC-ZZ minus SVC-RBF impact CI95 remains positive at dims 8,10,12.
2. QSVC-ZZ minus SVC-RBF shared-normalized stealth CI95 remains positive at dims 8,10,12.
3. Prior-preserving target-shift remains among the clearest high-impact/low-detectability auditability-gap cases.
4. No old model-local stealth ratios are used for the final claim.

Decision after Gate 1:

- If results hold: launch larger sample-size experiment.
- If results weaken but remain partially positive: reformulate claim as seed-sensitive but still methodologically useful.
- If results fail: keep V10 as workshop/preliminary fallback.
