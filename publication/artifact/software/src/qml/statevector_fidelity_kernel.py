"""Exact, cached statevector evaluator for fidelity quantum kernels.

Qiskit Machine Learning's reference ``FidelityQuantumKernel`` evaluates one
compute-uncompute circuit per sample pair.  That is faithful to sampler-backed
execution, but unnecessarily expensive for the explicitly ideal-statevector
experiments in this repository.  In the ideal case,

    K(x, y) = |<phi(x) | phi(y)>|^2,

so each state needs to be prepared once and every pair can be obtained by one
matrix multiplication.  This class implements the same kernel definition and
keeps bounded LRU caches for prepared states and completed kernel blocks.

It is intentionally not a shot-noise or hardware estimator.  Those require a
separate primitive-backed experiment and must not use this class.
"""

from __future__ import annotations

from collections import OrderedDict
import hashlib
from typing import Any

import numpy as np
from qiskit.quantum_info import Statevector


class ExactStatevectorFidelityKernel:
    """Qiskit-QSVC-compatible exact fidelity-kernel evaluator."""

    def __init__(
        self,
        feature_map: Any,
        *,
        enforce_psd: bool = True,
        max_state_cache_entries: int = 4,
        max_kernel_cache_entries: int = 24,
    ) -> None:
        if max_state_cache_entries < 1:
            raise ValueError("max_state_cache_entries must be >= 1")
        if max_kernel_cache_entries < 1:
            raise ValueError("max_kernel_cache_entries must be >= 1")

        self.feature_map = feature_map
        self.enforce_psd = bool(enforce_psd)
        self._parameters = tuple(feature_map.parameters)
        if not self._parameters:
            raise ValueError("feature_map must expose at least one input parameter")

        self.max_state_cache_entries = int(max_state_cache_entries)
        self.max_kernel_cache_entries = int(max_kernel_cache_entries)
        self._state_cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self._kernel_cache: OrderedDict[tuple[str, str], np.ndarray] = OrderedDict()
        self.state_preparations = 0
        self.state_cache_hits = 0
        self.kernel_cache_hits = 0

    @staticmethod
    def _as_2d(values: np.ndarray) -> np.ndarray:
        array = np.ascontiguousarray(values, dtype=np.float64)
        if array.ndim == 1:
            array = array.reshape(1, -1)
        if array.ndim != 2:
            raise ValueError(f"Expected a 2D array, got shape={array.shape}")
        if not np.isfinite(array).all():
            raise ValueError("Kernel input contains NaN or infinity")
        return array

    @staticmethod
    def _array_key(array: np.ndarray) -> str:
        digest = hashlib.sha256()
        digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
        digest.update(array.tobytes(order="C"))
        return digest.hexdigest()

    @staticmethod
    def _put_lru(cache: OrderedDict, key: object, value: np.ndarray, limit: int) -> None:
        cache[key] = value
        cache.move_to_end(key)
        while len(cache) > limit:
            cache.popitem(last=False)

    def _states(self, values: np.ndarray, key: str) -> np.ndarray:
        cached = self._state_cache.get(key)
        if cached is not None:
            self._state_cache.move_to_end(key)
            self.state_cache_hits += 1
            return cached

        if values.shape[1] != len(self._parameters):
            raise ValueError(
                "Input dimension does not match feature-map parameters: "
                f"{values.shape[1]} != {len(self._parameters)}"
            )

        states = np.empty(
            (values.shape[0], 2 ** int(self.feature_map.num_qubits)),
            dtype=np.complex128,
        )
        for index, row in enumerate(values):
            assignment = dict(zip(self._parameters, row, strict=True))
            bound = self.feature_map.assign_parameters(assignment, inplace=False)
            states[index] = np.asarray(Statevector.from_instruction(bound).data)

        self.state_preparations += int(values.shape[0])
        self._put_lru(
            self._state_cache,
            key,
            states,
            self.max_state_cache_entries,
        )
        return states

    def evaluate(
        self,
        x_vec: np.ndarray,
        y_vec: np.ndarray | None = None,
    ) -> np.ndarray:
        """Return the exact ideal-statevector fidelity block."""

        x = self._as_2d(x_vec)
        symmetric = y_vec is None
        y = x if symmetric else self._as_2d(y_vec)
        if x.shape[1] != y.shape[1]:
            raise ValueError(f"Feature dimensions differ: {x.shape[1]} != {y.shape[1]}")

        x_key = self._array_key(x)
        y_key = x_key if symmetric else self._array_key(y)
        kernel_key = (x_key, y_key)
        cached = self._kernel_cache.get(kernel_key)
        if cached is not None:
            self._kernel_cache.move_to_end(kernel_key)
            self.kernel_cache_hits += 1
            return cached.copy()

        x_states = self._states(x, x_key)
        y_states = x_states if y_key == x_key else self._states(y, y_key)
        overlaps = x_states.conj() @ y_states.T
        kernel = np.square(np.abs(overlaps), dtype=np.float64)
        kernel = np.clip(kernel.real, 0.0, 1.0)

        if y_key == x_key:
            kernel = 0.5 * (kernel + kernel.T)
            np.fill_diagonal(kernel, 1.0)
            if self.enforce_psd:
                eigenvalues, eigenvectors = np.linalg.eig(kernel)
                kernel = eigenvectors @ np.diag(np.maximum(0.0, eigenvalues)) @ eigenvectors.T
                kernel = kernel.real

        self._put_lru(
            self._kernel_cache,
            kernel_key,
            kernel,
            self.max_kernel_cache_entries,
        )
        return kernel.copy()

    def cache_info(self) -> dict[str, int]:
        """Return counters suitable for run metadata and performance audits."""

        return {
            "state_cache_entries": len(self._state_cache),
            "kernel_cache_entries": len(self._kernel_cache),
            "state_preparations": self.state_preparations,
            "state_cache_hits": self.state_cache_hits,
            "kernel_cache_hits": self.kernel_cache_hits,
        }
