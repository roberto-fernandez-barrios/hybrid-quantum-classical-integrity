from __future__ import annotations

import unittest

import numpy as np

from src.qml.quantum_qsvc import QuantumCfg, predict_qsvc, scores_qsvc, train_qsvc
from src.qml.statevector_fidelity_kernel import ExactStatevectorFidelityKernel


class ExactQsvcIntegrationTests(unittest.TestCase):
    def test_train_predict_and_score_with_explicit_exact_backend(self) -> None:
        x = np.array(
            [
                [0.05, 0.10],
                [0.10, 0.20],
                [0.20, 0.15],
                [0.25, 0.30],
                [1.10, 1.00],
                [1.20, 1.10],
                [1.30, 1.15],
                [1.40, 1.25],
            ],
            dtype=float,
        )
        y = np.array([0, 0, 0, 0, 1, 1, 1, 1], dtype=int)
        cfg = QuantumCfg(
            feature_map="zz",
            reps=1,
            backend_method="exact_statevector",
            seed=42,
            max_iter=100,
        )

        model, feature_map, kernel = train_qsvc(x, y, cfg)
        predictions = predict_qsvc(model, x)
        scores = scores_qsvc(model, x)

        self.assertIsInstance(kernel, ExactStatevectorFidelityKernel)
        self.assertEqual(feature_map.num_qubits, 2)
        self.assertEqual(predictions.shape, (8,))
        self.assertIsNotNone(scores)
        self.assertTrue(np.isfinite(scores).all())
        self.assertEqual(set(np.unique(predictions).tolist()), {0, 1})


if __name__ == "__main__":
    unittest.main()
