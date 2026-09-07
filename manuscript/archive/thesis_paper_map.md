# Thesis paper map

## Paper 1 - Generalization

Focus:
Quantum and classical kernels under equivalent conditions.

Main question:
Do quantum kernels exhibit different generalization behaviour than classical kernels under distribution shift and morphing?

Role in thesis:
Establishes the empirical basis that kernel choice matters under distributional change.

## Paper 1.5 - Robustness and auditability

Focus:
Structured perturbations, impact, detectability, and stealth.

Main question:
Once quantum and classical kernels are deployed under controlled settings, do they expose different vulnerability and auditability profiles?

Role in thesis:
Bridges generalization analysis with operational monitoring. It shows that quantum kernels may require kernel-specific robustness auditing.

Current experiment:
paper_core_full_zz_128

Main evidence so far:
- Under ID evaluation, QSVC-ZZ shows higher perturbation impact than SVC-RBF.
- The effect increases with projected dimension.
- Top stealth attacks are dominated by structured corruption and covariate perturbations in ID.
- OOD effects are weaker in absolute value.

## Paper 2 - Drift monitoring and adaptation

Focus:
QK-MMD, early drift detection, streaming monitoring, and adaptation.

Main question:
Can quantum-kernel-based monitoring detect distributional changes early enough to support robust adaptation?

Role in thesis:
Turns the vulnerability/auditability findings into an operational monitoring framework.
