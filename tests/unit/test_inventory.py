from __future__ import annotations

import pytest

from gartner_app.migration.inventory import classify


@pytest.mark.parametrize(
    ("path", "family", "disposition"),
    [
        (
            "schema4-0_enhanced.json",
            "schema_framework",
            "core_candidate",
        ),
        (
            "MDR Services Vendor 2-1 Consolidated.json",
            "vendor_score_pricing",
            "core_candidate",
        ),
        (
            "research/cache/pages/example.json",
            "research_cache",
            "manifest_only_candidate",
        ),
        (
            "research/backups/vendor_backup.json",
            "backup",
            "archive_candidate",
        ),
        (
            "research/precyber_svc_checkpoints/progress.json",
            "research_checkpoint",
            "research_candidate",
        ),
        (
            "analyst_take_reports.json",
            "report_insight_profile",
            "core_candidate",
        ),
    ],
)
def test_classification(
    path: str,
    family: str,
    disposition: str,
) -> None:
    assert classify(path) == (family, disposition)
