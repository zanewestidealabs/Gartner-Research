"""Bounded Mango query builders paired with source-controlled indexes."""

from __future__ import annotations

from typing import Any


def _pagination(
    query: dict[str, Any],
    *,
    limit: int,
    bookmark: str | None,
) -> dict[str, Any]:
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")
    query["limit"] = limit
    if bookmark:
        query["bookmark"] = bookmark
    return query


def manifests_by_disposition(
    disposition: str,
    *,
    limit: int = 200,
    bookmark: str | None = None,
) -> dict[str, Any]:
    return _pagination(
        {
            "selector": {
                "doc_type": {"$eq": "migration_manifest"},
                "proposed_disposition": {"$eq": disposition},
            },
            # CouchDB 3.3 requires the full compound order, including equality
            # fields, to select this index for a sorted query.
            "sort": [
                {"doc_type": "asc"},
                {"proposed_disposition": "asc"},
                {"relative_path": "asc"},
            ],
            "fields": [
                "_id",
                "_rev",
                "relative_path",
                "sha256",
                "size_bytes",
                "parse_status",
                "inferred_family",
                "proposed_disposition",
            ],
            "use_index": [
                "idx-manifest-disposition-path",
                "idx_manifest_disposition_path",
            ],
        },
        limit=limit,
        bookmark=bookmark,
    )


def vendor_scores(
    market: str,
    cycle: str,
    *,
    limit: int = 200,
    bookmark: str | None = None,
) -> dict[str, Any]:
    return _pagination(
        {
            "selector": {
                "doc_type": {"$eq": "vendor_score"},
                "market": {"$eq": market},
                "cycle": {"$eq": cycle},
            },
            "sort": [
                {"doc_type": "asc"},
                {"market": "asc"},
                {"cycle": "asc"},
                {"vendor_id": "asc"},
            ],
            "use_index": [
                "idx-score-market-cycle-vendor",
                "idx_score_market_cycle_vendor",
            ],
        },
        limit=limit,
        bookmark=bookmark,
    )


def evidence_for_criterion(
    vendor_id: str,
    schema_id: str,
    criterion_id: str,
    *,
    limit: int = 100,
    bookmark: str | None = None,
) -> dict[str, Any]:
    return _pagination(
        {
            "selector": {
                "doc_type": {"$eq": "evidence_excerpt"},
                "vendor_id": {"$eq": vendor_id},
                "schema_id": {"$eq": schema_id},
                "criterion_id": {"$eq": criterion_id},
            },
            "sort": [
                {"doc_type": "asc"},
                {"vendor_id": "asc"},
                {"schema_id": "asc"},
                {"criterion_id": "asc"},
            ],
            "use_index": [
                "idx-evidence-vendor-schema-criterion",
                "idx_evidence_vendor_schema_criterion",
            ],
        },
        limit=limit,
        bookmark=bookmark,
    )


def research_targets(
    run_id: str,
    status: str,
    *,
    limit: int = 100,
    bookmark: str | None = None,
) -> dict[str, Any]:
    return _pagination(
        {
            "selector": {
                "doc_type": {"$eq": "research_target"},
                "run_id": {"$eq": run_id},
                "status": {"$eq": status},
            },
            "sort": [
                {"doc_type": "asc"},
                {"run_id": "asc"},
                {"status": "asc"},
                {"vendor_id": "asc"},
            ],
            "use_index": [
                "idx-target-run-status-vendor",
                "idx_target_run_status_vendor",
            ],
        },
        limit=limit,
        bookmark=bookmark,
    )


def score_proposals(
    run_id: str,
    vendor_id: str,
    criterion_id: str,
    *,
    limit: int = 100,
    bookmark: str | None = None,
) -> dict[str, Any]:
    return _pagination(
        {
            "selector": {
                "doc_type": {"$eq": "score_proposal"},
                "run_id": {"$eq": run_id},
                "vendor_id": {"$eq": vendor_id},
                "criterion_id": {"$eq": criterion_id},
            },
            "sort": [
                {"doc_type": "asc"},
                {"run_id": "asc"},
                {"vendor_id": "asc"},
                {"criterion_id": "asc"},
            ],
            "use_index": [
                "idx-proposal-run-vendor-criterion",
                "idx_proposal_run_vendor_criterion",
            ],
        },
        limit=limit,
        bookmark=bookmark,
    )


def source_snapshots(
    source_id: str,
    *,
    limit: int = 100,
    bookmark: str | None = None,
) -> dict[str, Any]:
    return _pagination(
        {
            "selector": {
                "doc_type": {"$eq": "source_snapshot"},
                "source_id": {"$eq": source_id},
            },
            "sort": [
                {"doc_type": "asc"},
                {"source_id": "asc"},
                {"retrieved_at": "asc"},
            ],
            "use_index": [
                "idx-snapshot-source-retrieved",
                "idx_snapshot_source_retrieved",
            ],
        },
        limit=limit,
        bookmark=bookmark,
    )


def snapshots_by_outcome(
    run_id: str,
    vendor_id: str,
    outcome: str,
    *,
    limit: int = 100,
    bookmark: str | None = None,
) -> dict[str, Any]:
    return _pagination(
        {
            "selector": {
                "doc_type": {"$eq": "source_snapshot"},
                "run_id": {"$eq": run_id},
                "vendor_id": {"$eq": vendor_id},
                "outcome": {"$eq": outcome},
            },
            "sort": [
                {"doc_type": "asc"},
                {"run_id": "asc"},
                {"vendor_id": "asc"},
                {"outcome": "asc"},
            ],
            "use_index": [
                "idx-snapshot-run-vendor-outcome",
                "idx_snapshot_run_vendor_outcome",
            ],
        },
        limit=limit,
        bookmark=bookmark,
    )


def evidence_for_snapshot(
    snapshot_id: str,
    *,
    limit: int = 100,
    bookmark: str | None = None,
) -> dict[str, Any]:
    return _pagination(
        {
            "selector": {
                "doc_type": {"$eq": "evidence_excerpt"},
                "snapshot_id": {"$eq": snapshot_id},
            },
            "use_index": [
                "idx-evidence-snapshot",
                "idx_evidence_snapshot",
            ],
        },
        limit=limit,
        bookmark=bookmark,
    )
