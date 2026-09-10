from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.experiments.build_q1_reinforcement_evidence import CALIBRATED_SENSORS
from src.experiments.build_v137_correction_evidence import (
    ALL_DECOMPOSITION_SENSORS,
    _decomposition,
    _score_frame_legacy,
)
from src.experiments.build_q1_policy_evidence import score_frame


def _values(n: int) -> dict[str, np.ndarray]:
    return {sensor: np.linspace(0.0, 1.0, n) for sensor in CALIBRATED_SENSORS}


def test_legacy_scoring_reproduces_finite_current_decisions() -> None:
    calibration = _values(200)
    rows = pd.DataFrame({sensor: [0.25, 0.75] for sensor in CALIBRATED_SENSORS})
    thresholds = {sensor: 0.5 for sensor in CALIBRATED_SENSORS}
    old = _score_frame_legacy(rows, calibration, thresholds)
    new = score_frame(rows, calibration, thresholds)
    for regime in ("I_X", "I_XF", "I_Ym", "I_XFY"):
        assert old[f"fire_union__{regime}"].equals(new[f"fire_union__{regime}"])
        assert old[f"fire_family__{regime}"].equals(new[f"fire_family__{regime}"])
        assert np.array_equal(old[f"pvalue_family__{regime}"], new[f"pvalue_family__{regime}"])


def test_legacy_nan_isolated_from_current_fail_closed_path() -> None:
    calibration = _values(200)
    rows = pd.DataFrame({sensor: [0.25] for sensor in CALIBRATED_SENSORS})
    rows.loc[0, "integrity_jsd_vs_clean_eval"] = np.nan
    thresholds = {sensor: 0.5 for sensor in CALIBRATED_SENSORS}
    legacy = _score_frame_legacy(rows, calibration, thresholds)
    assert not bool(legacy.loc[0, "fire_sensor__integrity_jsd_vs_clean_eval"])
    with pytest.raises(ValueError, match="must all be finite"):
        score_frame(rows, calibration, thresholds)


def test_response_only_decomposition_does_not_require_family_columns() -> None:
    row: dict[str, object] = {
        "attack": "feature_dropout_p_0.020",
        "attack_class": "pipeline",
        "mechanism": "dropout",
        "strength": 0.02,
    }
    row.update({sensor: 0.1 for sensor in ALL_DECOMPOSITION_SENSORS})
    result = _decomposition({"gate1_frozen_design": pd.DataFrame([row])})
    assert len(result) > 0
    assert result["n_sensor_fire"].isna().all()
    assert result["n_family_fire"].isna().all()
