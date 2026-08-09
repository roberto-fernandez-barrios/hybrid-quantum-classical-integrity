# Exact-statevector kernel validation record

Date: 2026-08-09  
Status: passed; suitable for ideal-simulation expansion gates, not for shot-noise or hardware claims.

## Purpose

The archived Gate 1 runs use Qiskit Machine Learning's reference
`FidelityQuantumKernel(fidelity=None)`. That evaluator constructs a
compute-uncompute workload for each sample pair and caused the 256/256 and OOD
expansion queues to stall. The replacement evaluator computes the same ideal
fidelity definition,

\[
K(x,y)=|\langle\phi(x)\mid\phi(y)\rangle|^2,
\]

by preparing every unique statevector once and forming kernel blocks by matrix
multiplication. Symmetric blocks use the same eigenvalue-clipping PSD repair as
the installed Qiskit Machine Learning reference implementation.

The engine is selected explicitly with
`--q-backend-method exact_statevector`. Output filenames, run configuration,
and fingerprints therefore distinguish it from the archived `statevector`
reference runs. The option is forbidden as evidence of finite-shot sampling,
noise, or QPU execution.

## Validation layers

1. Unit matrices: symmetric and cross-kernel blocks match
   `FidelityQuantumKernel` at `rtol=atol=1e-10`.
2. Algebraic invariants: symmetry, unit diagonal, numerical range, bounded
   caches, and cache reuse are tested.
3. End-to-end replay: CICIDS ID, split 42, model seed 42, dimension 8,
   ZZ map, 128/128 samples, `paper_core` suite.
4. Scale pilot: the same configuration at 256/256 completes successfully.

The repository test result is `6 passed`. The environment was Qiskit 2.3.0,
Qiskit Machine Learning 0.9.0, NumPy 2.2.6, SciPy 1.15.3, and scikit-learn
1.7.2.

## End-to-end comparison

Both replays contain 38 rows and the same 126 columns. After excluding run IDs,
configuration fingerprints, and timing fields:

- every categorical field is identical;
- every discrete performance, impact, and integrity-signal field is identical;
- only `roc_auc`, `roc_auc_drop`, and `impact_roc_auc` differ;
- their maximum absolute difference is `0.0001221896383187`;
- this is one half-tie increment for a balanced 64-positive/64-negative test
  set, `1 / (2 * 64 * 64) = 0.0001220703125`, consistent with an ordering change
  at numerical precision in continuous decision scores.

The archived quantum training time is 162.8337 s and the replacement training
time is 0.3040 s, a 535.6x speed-up for this replay. The complete 256/256 pilot
finishes successfully; its quantum fit takes 0.60 s.

This establishes operational equivalence for the benchmark endpoints under an
explicit `2e-4` ROC-AUC tolerance. It does not assert bitwise identity of
continuous scores or equivalence to sampling/hardware execution.

## Artifact hashes (SHA-256)

- archived reference CSV: `81A3FFB40BFA0B651ADB7A72ADF119A2ABEC9AAAB41F91D45C5F8925F1CF8160`
- exact-statevector replay CSV: `49B36C3656FABFFE0F5AD2FBC565046798DC0C1C332C651CC857BFDA23B31201`
- evaluator source at validation: `22A8A4FE44DD295BFB7A4C5E896FC07B2E359A2BDC8A9445CA07EABD8034B5D7`

The hashes are validation anchors, not final-release identifiers. They must be
regenerated if the evaluator or pilot artifacts change.
