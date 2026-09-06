from __future__ import annotations

from pathlib import Path

import pytest

from src.experiments.verify_publication_artifact import verify


def test_local_evidence_manifests_and_primary_claims() -> None:
    root = Path("results/paper_digest")
    if not root.exists():
        pytest.skip("full derived evidence is not present in this checkout")

    summary = verify(root)
    assert summary["manifests"] == 5
    assert summary["manifested_outputs"] == 44
    assert summary["gate1_label_rows"] == 1440
    assert summary["gate1_positive_impact"] == 1276
    assert summary["expansion_label_rows"] == 3600
    assert summary["expansion_positive_impact"] == 2184
    assert summary["reinforcement_label_rows"] == 3600


def test_compact_publication_artifact_when_present() -> None:
    root = Path("publication/artifact")
    if not root.exists():
        pytest.skip("publication artifact has not been assembled")
    summary = verify(root)
    assert summary["release_files"] > 0
