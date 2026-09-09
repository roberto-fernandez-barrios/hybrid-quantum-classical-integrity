# Paper 1.5 quantum-specific integrity gate

Date: 2026-08-09  
Status: complete simulator gate; hardware/backend validation remains open.

## Design

The gate crosses five CICIDS split seeds, projected dimensions 4/6/8, and 11
clean/control/perturbation conditions, giving 165 independent split-dimension
cells. Training and evaluation use 64/64 rows to isolate the quantum workflow
boundary rather than repeat the scale study.

Conditions:

- clean negative control;
- optimization-level-1 transpilation control;
- a common post-feature-map X gate, which changes circuit structure but must
  preserve all fidelities;
- data-dependent RZ mutations at 0.02 and 0.10;
- feature-map repetition change from 1 to 2;
- asymmetric kernel edit;
- diagonal erosion;
- symmetric PSD-preserving kernel mixture;
- binomial fidelity-estimation emulators at 256 and 1024 shots.

The shot conditions sample from exact fidelities. They are finite-shot
estimation emulators, not sampler-backend or QPU runs.

## Acceptance audit

All nine prespecified checks pass:

1. 165/165 cells present;
2. clean hashes, kernels, and predictions remain unchanged;
3. transpilation changes the canonical OpenQASM 3 hash while preserving kernel
   semantics and output;
4. the common-unitary rewrite changes the circuit hash while preserving the
   fidelity kernel and output;
5. all data-dependent circuit mutations change the kernel;
6. the symmetry sensor detects every asymmetric edit;
7. the diagonal sensor detects every diagonal erosion;
8. the PSD-preserving mixture is algebraically valid in every cell but is
   caught by trusted kernel provenance/semantic comparison;
9. both shot estimators produce non-zero repeated-estimation discrepancy in
   every cell.

## Sensor-conditional coverage

| Condition | Circuit provenance | Kernel provenance | Semantic kernel | Algebraic kernel | Repeated estimate | Output changes |
|---|---:|---:|---:|---:|---:|---:|
| Clean | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Benign transpilation | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Common-unitary rewrite | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Parameterized RZ 0.02 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| Parameterized RZ 0.10 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.13 |
| Feature-map reps 1→2 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.73 |
| Asymmetric kernel edit | 0.00 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| Kernel diagonal erosion | 0.00 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| PSD-preserving kernel mix | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.07 |
| Shot estimator 256 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.47 |
| Shot estimator 1024 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.20 |

The result rejects a one-sensor security story:

- raw circuit or matrix hashes are sensitive to benign semantic equivalence and
  therefore require adjudication rather than automatic rejection;
- kernel algebra detects malformed matrices but cannot detect a symmetric,
  unit-diagonal, PSD-preserving substitution;
- output monitoring misses many circuit/kernel changes, including every mild
  parameter mutation and every algebraically malformed edit at the tested
  severity;
- repeated estimation separates stochastic fidelity estimation from a fixed
  exact reference and reacts in all shot-emulator cells.

The intended countermeasure is a layered contract: authenticated circuit and
parameter provenance, approved-transpilation policy, semantic probe kernels,
algebraic validation, repeated estimation with uncertainty bounds, PSD repair
as containment rather than proof of integrity, and output-level monitoring.

## Quantitative effects

Changing feature-map repetitions changes predictions in 11/15 cells, with mean
balanced-accuracy drop 0.00521 and maximum drop 0.04688. The PSD-preserving
mixture changes predictions in 1/15 cells. The 256- and 1024-shot emulators
change predictions in 7/15 and 3/15 cells; mean drops are 0.00521 and 0.00313.
These effect sizes are secondary: an integrity violation can be material even
before the chosen 64-row output metric changes.

## Claim boundary and ATHENA mapping

This gate supplies quantum-specific simulator evidence for circuit construction,
transpilation equivalence, kernel estimation, integrity metrics, sensor blind
regions, and countermeasure composition. It strengthens ATHENA-AEGIS G3.1,
G3.2, and G3.3, but it does not close scheduling, calibrated noise, provider
metadata, multi-tenant interference, or QPU execution. Those remain the final
operational validation tier.

## Artifacts

- runner: `src/experiments/run_quantum_integrity_gate.py`
- strict manifest: `results/paper_digest/paper15_q1_quantum_integrity_gate/quantum_integrity_gate_manifest.json`
- observations and summaries: `results/paper_digest/paper15_q1_quantum_integrity_gate/`
- publication figure: `manuscript/figures/fig_q1_quantum_integrity_contract.{png,pdf}`
- publication tables: `manuscript/tables/quantum_integrity_gate_*.csv`
