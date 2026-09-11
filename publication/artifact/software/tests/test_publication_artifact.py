from __future__ import annotations

from pathlib import Path

import pytest

from src.experiments.verify_publication_artifact import verify


def test_local_evidence_manifests_and_primary_claims() -> None:
    root = Path("results/paper_digest")
    if not root.exists():
        pytest.skip("full derived evidence is not present in this checkout")

    summary = verify(root)
    assert summary["manifests"] == 11
    assert summary["manifested_outputs"] == 115
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
    assert (
        summary["historical_v132_v136_trusted_statistical_holds"],
        summary["historical_v132_v136_gross_exact_blocks"],
        summary["historical_v132_v136_trusted_total_interruptions"],
    ) == (544, 85, 629)
    assert summary["adversarial_conditions"] == 16
    assert summary["v132_sensor_audit_rows"] == 14
    assert summary["v132_adaptive_strength_cells"] == 10
    assert summary["historical_v132_v136_batch_interruptions"] == 590
    assert summary["historical_v132_v136_exact_overlap"] == 46
    assert summary["historical_v132_v136_net_additional"] == 39
    assert summary["historical_v132_v136_net_additional_basis_points"] == 325
    assert summary["geometry_observations"] == 13200
    assert summary["geometry_environments"] == 8
    assert summary["geometry_interventions"] == 22
    assert summary["geometry_gateA_matched_rows"] == 24
    assert summary["v137_corrected_observations"] == 64560
    assert summary["v137_jsd_changed_observation_rows"] == 58074
    assert summary["v137_label_geometry_rows"] == 3600
    assert summary["v137_label_aligned_family_material_fires"] == 343
    assert summary["v137_label_aligned_union_material_fires"] == 1183
    assert (
        summary["current_v137_v138_gross_exact_blocks"],
        summary["current_v137_v138_corrected_batch_interruptions"],
        summary["current_v137_v138_trusted_total_interruptions"],
        summary["current_v137_v138_exact_overlap"],
        summary["current_v137_v138_net_additional"],
        summary["current_v137_v138_net_additional_basis_points"],
    ) == (85, 576, 617, 44, 41, 342)


def test_compact_publication_artifact_when_present() -> None:
    root = Path("publication/artifact")
    if not root.exists():
        pytest.skip("publication artifact has not been assembled")
    summary = verify(root)
    assert summary["release_files"] > 0
