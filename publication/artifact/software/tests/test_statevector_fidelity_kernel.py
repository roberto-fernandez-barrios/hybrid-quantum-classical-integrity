from __future__ import annotations

import unittest

import numpy as np
from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel

from src.qml.statevector_fidelity_kernel import ExactStatevectorFidelityKernel


class ExactStatevectorFidelityKernelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.feature_map = ZZFeatureMap(feature_dimension=3, reps=1)
        self.x = np.array(
            [
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6],
                [0.7, 0.8, 0.9],
                [1.0, 1.1, 1.2],
            ],
            dtype=float,
        )
        self.y = np.array(
            [
                [0.15, 0.25, 0.35],
                [0.45, 0.55, 0.65],
            ],
            dtype=float,
        )

    def test_matches_qiskit_reference_kernel(self) -> None:
        reference = FidelityQuantumKernel(feature_map=self.feature_map, fidelity=None)
        exact = ExactStatevectorFidelityKernel(self.feature_map)

        np.testing.assert_allclose(
            exact.evaluate(self.x),
            reference.evaluate(self.x),
            rtol=1e-10,
            atol=1e-10,
        )
        np.testing.assert_allclose(
            exact.evaluate(self.x, self.y),
            reference.evaluate(self.x, self.y),
            rtol=1e-10,
            atol=1e-10,
        )

    def test_is_symmetric_with_unit_diagonal(self) -> None:
        exact = ExactStatevectorFidelityKernel(self.feature_map)
        kernel = exact.evaluate(self.x)

        np.testing.assert_allclose(kernel, kernel.T, atol=1e-12)
        np.testing.assert_allclose(np.diag(kernel), np.ones(len(self.x)), atol=1e-12)
        self.assertGreaterEqual(float(kernel.min()), -1e-12)
        self.assertLessEqual(float(kernel.max()), 1.0 + 1e-12)

    def test_reuses_state_and_kernel_blocks(self) -> None:
        exact = ExactStatevectorFidelityKernel(self.feature_map)
        first = exact.evaluate(self.x, self.y)
        info_after_first = exact.cache_info()
        second = exact.evaluate(self.x, self.y)
        info_after_second = exact.cache_info()

        np.testing.assert_array_equal(first, second)
        self.assertEqual(info_after_first["state_preparations"], 6)
        self.assertEqual(info_after_second["state_preparations"], 6)
        self.assertEqual(info_after_second["kernel_cache_hits"], 1)


if __name__ == "__main__":
    unittest.main()
