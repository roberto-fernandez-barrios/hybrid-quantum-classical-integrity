# Reproducibility details

## Seeds
- split_seeds: 42, 43, 44
- model_seeds: 42, 43
- paired_seed_units: 6

## Experimental sizes
- max_train: 128
- max_test: 128
- q_reps: 1
- q_backend_method: statevector
- q_shots: 1024
- q_max_iter: 1000

## Classical model
- model: SVC-RBF
- C: 1.0
- gamma: scale
- kernel: rbf

## Quantum models
- model: QSVC
- kernel: FidelityQuantumKernel
- feature maps: ZZ, Z, PauliXZ, PauliXYZ
- interpreted unique empirical profiles: ZZ, PauliXYZ, Z/PauliXZ-equivalent
- reps: 1
- backend traceability setting: statevector

## Software versions
- python: 3.10.16 | packaged by Anaconda, Inc. | (main, Dec 11 2024, 16:19:12) [MSC v.1929 64 bit (AMD64)]
- numpy: 2.2.6
- pandas: 2.3.3
- sklearn: 1.7.2
- qiskit: 2.3.0
- qiskit_aer: 0.17.2
- qiskit_machine_learning: 0.9.0

Note: the q_max_iter value above is the run configuration used for the paper-core experiments. Other code defaults may differ and should not be interpreted as the reported run configuration.
