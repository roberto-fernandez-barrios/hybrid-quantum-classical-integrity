from __future__ import annotations

from pathlib import Path

import pytest

from src.experiments.verify_publication_artifact import verify


def test_local_evidence_manifests_and_primary_claims() -> None:
    root = Path("results/paper_digest")
    if not root.exists():
        pytest.skip("full derived evidence is not present in this checkout")

    summary = verify(root)
    assert summary["manifests"] == 8
    assert summary["manifested_outputs"] == 86
    assert summary["gate1_label_rows"] == 1440
    assert summary["gate1_positive_impact"] == 1276
    assert summary["expansion_label_rows"] == 3600
    assert summary["expansion_positive_impact"] == 2184
    assert summary["reinforcement_label_rows"] == 3600
    assert summary["expansion_label_increased"] == 433
    assert summary["expansion_label_material"] == 2617
    assert summary["policy_material_observations"] == 7008
    assert summary["policy_regimes"] == 5
    assert summary["policy_conformal_level_x10000"] == 498
    assert (summary["policy_trusted_benign_holds"], summary["policy_trusted_benign_blocks"]) == (544, 85)
    assert summary["policy_trusted_benign_interruptions"] == 629
    assert summary["adversarial_conditions"] == 16
    assert summary["v132_sensor_audit_rows"] == 14
    assert summary["v132_adaptive_strength_cells"] == 10
    assert summary["v132_trusted_gross_exact_blocks"] == 85
    assert summary["v132_trusted_exact_overlap"] == 46
    assert summary["v132_trusted_net_additional"] == 39


def test_compact_publication_artifact_when_present() -> None:
    root = Path("publication/artifact")
    if not root.exists():
        pytest.skip("publication artifact has not been assembled")
    summary = verify(root)
    assert summary["release_files"] > 0
