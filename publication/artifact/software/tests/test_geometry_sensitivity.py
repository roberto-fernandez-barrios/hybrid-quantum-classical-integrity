from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from src.experiments.run_v135_geometry_sensitivity import (
    ALL_BATCH_SENSOR_COLUMNS,
    ATTACK_CURRENT_GEOMETRY,
    CALIBRATION_DRAW_TAG,
    CLEAN_CURRENT_GEOMETRY,
    GEOMETRY_ID,
    REFERENCE_GEOMETRY,
    _batch_stats,
    geometry_attack_specs,
    validate_geometry_record,
)
from src.experiments.verify_geometry_sensitivity import verify
from src.integrity.signals import MMDConfig


REPO = Path(__file__).resolve().parents[1]


def _declared_geometry() -> dict[str, str]:
    return {
        "geometry_id": GEOMETRY_ID,
        "reference_geometry": REFERENCE_GEOMETRY,
        "clean_current_geometry": CLEAN_CURRENT_GEOMETRY,
        "attack_current_geometry": ATTACK_CURRENT_GEOMETRY,
        "clean_draw_tag": CALIBRATION_DRAW_TAG,
    }


def test_geometry_contract_rejects_silent_reference_mismatch() -> None:
    record = _declared_geometry()
    validate_geometry_record(record)
    record["attack_current_geometry"] = "same_item_frozen_E"
    with pytest.raises(ValueError, match="Declared/implemented geometry mismatch"):
        validate_geometry_record(record)


def test_geometry_suite_is_exactly_the_frozen_feature_side_set() -> None:
    tags = [s.tag for s in geometry_attack_specs()]
    assert len(tags) == 22
    assert len(tags) == len(set(tags))
    assert {t for t in tags if t.startswith("sham_")} == {
        "sham_identity",
        "sham_tiny_gaussian_sigma_0.001",
        "sham_tiny_scaling_alpha_0.001",
    }
    assert sum(t.startswith("feature_dropout_p_") for t in tags) == 3
    assert sum(t.startswith("mean_shift_pf_delta_") for t in tags) == 3
    assert sum(t.startswith("scaling_drift_alpha_") for t in tags) == 3
    assert sum(t.startswith("cluster_preserving_mean_shift_delta_") for t in tags) == 5
    assert sum(t.startswith("cluster_preserving_scaling_alpha_") for t in tags) == 5


def test_exact_same_item_identity_is_zero_and_not_a_clean_resample() -> None:
    X = np.array([[0.0, 1.0], [1.0, 0.0], [2.0, 1.0], [3.0, 0.0]])
    y = np.array([0, 1, 1, 0])
    pred = np.array([0, 1, 0, 0])
    scores = np.array([-1.0, 0.8, -0.2, -0.5])
    stats = _batch_stats(
        X_ref=X,
        y_ref=y,
        pred_ref=pred,
        scores_ref=scores,
        X_cur=X.copy(),
        y_cur=y.copy(),
        pred_cur=pred.copy(),
        scores_cur=scores.copy(),
        mmd_cfg=MMDConfig(max_samples=512, gamma="median", rng_seed=42, max_pairs=4096),
    )
    assert set(ALL_BATCH_SENSOR_COLUMNS) == set(stats)
    assert max(abs(v) for v in stats.values()) == 0.0
    assert CLEAN_CURRENT_GEOMETRY == "fresh_eval_draw_01"
    assert CLEAN_CURRENT_GEOMETRY != "paired_identity"


def test_manifested_geometry_evidence_verifies_when_present() -> None:
    manifest = REPO / "publication/artifact/evidence/geometry_sensitivity/geometry_sensitivity_manifest.json"
    if not manifest.is_file():
        pytest.skip("Geometry sensitivity has not been executed yet")
    checks = verify(REPO, Path("publication/artifact/evidence/geometry_sensitivity"))
    assert checks and all(checks.values())
