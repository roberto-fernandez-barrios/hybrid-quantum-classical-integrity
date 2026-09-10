from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.experiments.build_q1_reinforcement_evidence import CALIBRATED_SENSORS
from src.experiments.build_v137_correction_evidence import _score_frame_legacy
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
