from __future__ import annotations

import pytest

from gartner_app.couchdb.queries import (
    evidence_for_criterion,
    evidence_for_snapshot,
    manifests_by_disposition,
    research_targets,
    score_proposals,
    snapshots_by_outcome,
    source_snapshots,
    vendor_scores,
)


def test_manifest_query_declares_full_index_order() -> None:
    query = manifests_by_disposition("core_candidate", limit=50)
    assert query["sort"] == [
        {"doc_type": "asc"},
        {"proposed_disposition": "asc"},
        {"relative_path": "asc"},
    ]
    assert query["use_index"][1] == "idx_manifest_disposition_path"
    assert query["limit"] == 50


def test_vendor_score_query_is_bounded() -> None:
    query = vendor_scores("mdr", "2026", bookmark="next")
    assert query["selector"]["market"] == {"$eq": "mdr"}
    assert query["bookmark"] == "next"
    assert query["limit"] == 200


def test_evidence_query_uses_all_identity_fields() -> None:
    query = evidence_for_criterion(
        "vendor:crowdstrike",
        "schema:mdr:2.1",
        "detection.alert_fidelity",
    )
    assert query["selector"]["criterion_id"] == {
        "$eq": "detection.alert_fidelity"
    }


def test_query_limit_is_rejected_when_unbounded() -> None:
    with pytest.raises(ValueError, match="limit"):
        manifests_by_disposition("core_candidate", limit=501)


def test_research_target_query_uses_resume_index() -> None:
    query = research_targets("run:1", "pending")
    assert query["selector"]["run_id"] == {"$eq": "run:1"}
    assert query["use_index"][1] == "idx_target_run_status_vendor"


def test_score_proposal_query_is_scoped_to_one_criterion() -> None:
    query = score_proposals("run:1", "vendor:1", "EXM-04")
    assert query["selector"]["criterion_id"] == {"$eq": "EXM-04"}
    assert query["limit"] == 100


def test_source_snapshot_query_preserves_retrieval_order() -> None:
    query = source_snapshots("source:1")
    assert query["sort"][-1] == {"retrieved_at": "asc"}
    assert query["use_index"][1] == "idx_snapshot_source_retrieved"


def test_snapshot_outcome_query_is_run_and_vendor_scoped() -> None:
    query = snapshots_by_outcome("run:1", "vendor:1", "blocked")
    assert query["selector"]["outcome"] == {"$eq": "blocked"}
    assert query["use_index"][1] == "idx_snapshot_run_vendor_outcome"


def test_evidence_snapshot_query_uses_lineage_index() -> None:
    query = evidence_for_snapshot("snapshot:1")
    assert query["selector"]["snapshot_id"] == {"$eq": "snapshot:1"}
    assert query["use_index"][1] == "idx_evidence_snapshot"
