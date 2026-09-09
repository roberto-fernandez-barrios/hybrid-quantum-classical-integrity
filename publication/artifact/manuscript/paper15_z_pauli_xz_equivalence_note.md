# Z vs PauliXZ equivalence note

## Finding

A sanity check was performed to determine whether QSVC-Z and QSVC-PauliXZ should be treated as distinct quantum feature maps in the current experimental configuration.

The result shows exact kernel equivalence:

- max_abs_diff = 0.0
- mean_abs_diff = 0.0
- allclose at 1e-12 = True
- allclose at 1e-8 = True

This was observed on synthetic random data using FidelityQuantumKernel.

## Circuit-level interpretation

Under the current Qiskit configuration with reps=1, the PauliXZ feature map decomposes into a sequence that is state-equivalent to the ZFeatureMap for the fidelity kernel used in this benchmark.

The relevant single-qubit structure is:

H H P(2x) H P(2x)

The initial H H pair cancels, and the intermediate phase operation on the computational basis state does not change the induced fidelity kernel. As a result, PauliXZ and Z induce identical kernel matrices under this configuration.

## Manuscript consequence

QSVC-Z and QSVC-PauliXZ should not be presented as independent feature-map behaviours.

The paper should instead state that the evaluated quantum kernels collapse into three unique empirical kernel profiles:

- QSVC-ZZ
- QSVC-PauliXYZ
- QSVC-Z/PauliXZ-equivalent

## Claim correction

Do not write:

"We evaluate four distinct quantum feature maps."

Write:

"We evaluate four feature-map configurations, of which Z and PauliXZ are found to induce identical fidelity kernels under the current reps=1 configuration. Therefore, the main feature-map comparison is interpreted over three unique empirical kernel profiles: ZZ, PauliXYZ, and Z/PauliXZ-equivalent."

## Impact on results

This does not invalidate the main conclusion. The key feature-map heterogeneity result remains:

- QSVC-ZZ exhibits the strongest aggregate ID vulnerability profile.
- QSVC-PauliXYZ shows an intermediate profile.
- QSVC-Z/PauliXZ-equivalent shows a milder profile.

The equivalence should be reported transparently as a methodological finding and limitation.
