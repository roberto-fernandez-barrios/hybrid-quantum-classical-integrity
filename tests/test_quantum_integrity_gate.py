from __future__ import annotations

import unittest

import numpy as np

from src.experiments.run_quantum_integrity_gate import (
    _algebraic_signals,
    _circuit_hash,
    _kernel_blocks,
    _make_common_unitary,
    _make_parameterized_rz,
    _sample_symmetric_fidelity,
)
from src.qml.quantum_qsvc import QuantumCfg, _make_feature_map


class QuantumIntegrityGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.feature_map = _make_feature_map(
            3,
            QuantumCfg(feature_map="zz", reps=1, backend_method="exact_statevector"),
        )
        self.x_train = np.array(
            [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
            dtype=float,
        )
        self.x_test = np.array([[0.15, 0.25, 0.35], [0.65, 0.75, 0.85]], dtype=float)

    def test_canonical_circuit_hash_is_repeatable_and_sensitive(self) -> None:
        first = _circuit_hash(self.feature_map)
        second = _circuit_hash(self.feature_map)
        changed = _circuit_hash(_make_common_unitary(self.feature_map))

        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)

    def test_semantically_common_unitary_preserves_kernel_but_parameter_gate_changes_it(self) -> None:
        base_train, base_test = _kernel_blocks(self.feature_map, self.x_train, self.x_test)
        common_train, common_test = _kernel_blocks(
            _make_common_unitary(self.feature_map), self.x_train, self.x_test
        )
        changed_train, changed_test = _kernel_blocks(
            _make_parameterized_rz(self.feature_map, 0.1), self.x_train, self.x_test
        )

        np.testing.assert_allclose(base_train, common_train, rtol=1e-10, atol=1e-10)
        np.testing.assert_allclose(base_test, common_test, rtol=1e-10, atol=1e-10)
        self.assertGreater(float(np.max(np.abs(base_train - changed_train))), 1e-6)
        self.assertGreater(float(np.max(np.abs(base_test - changed_test))), 1e-6)

    def test_algebraic_checks_have_declared_blind_region(self) -> None:
        base, _ = _kernel_blocks(self.feature_map, self.x_train, self.x_test)
        asymmetric = base.copy()
        asymmetric[0, 1] += 0.02
        diagonal = base.copy()
        diagonal[0, 0] -= 0.02
        psd_mix = 0.95 * base + 0.05 * np.eye(len(base))

        asym_signals = _algebraic_signals(asymmetric)
        diag_signals = _algebraic_signals(diagonal)
        mix_signals = _algebraic_signals(psd_mix)

        self.assertGreater(asym_signals["kernel_symmetry_residual"], 1e-8)
        self.assertGreater(diag_signals["kernel_diagonal_residual"], 1e-8)
        self.assertLessEqual(abs(mix_signals["kernel_symmetry_residual"]), 1e-12)
        self.assertLessEqual(abs(mix_signals["kernel_diagonal_residual"]), 1e-12)
        self.assertGreaterEqual(mix_signals["kernel_min_eigenvalue"], -1e-10)

        first = _sample_symmetric_fidelity(base, 256, np.random.default_rng(1))
        second = _sample_symmetric_fidelity(base, 256, np.random.default_rng(2))
        self.assertGreater(float(np.max(np.abs(first - second))), 0.0)


if __name__ == "__main__":
    unittest.main()
