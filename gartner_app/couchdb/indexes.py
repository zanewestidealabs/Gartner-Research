"""Source-controlled Mango index definitions."""

from __future__ import annotations

from typing import Any

IndexDefinition = dict[str, Any]


def _index(
    name: str,
    fields: list[str],
    *,
    doc_type: str,
) -> IndexDefinition:
    ddoc = name.replace("_", "-")
    return {
        "ddoc": ddoc,
        "name": name,
        "type": "json",
        "index": {
            "fields": fields,
            "partial_filter_selector": {"doc_type": doc_type},
        },
    }


CORE_INDEXES: tuple[IndexDefinition, ...] = (
    _index(
        "idx_vendor_status_name",
        ["doc_type", "status", "name_normalized"],
        doc_type="vendor",
    ),
    _index(
        "idx_schema_market_status_version",
        ["doc_type", "market", "status", "version_sort"],
        doc_type="schema",
    ),
    _index(
        "idx_schema_source_path",
        ["doc_type", "source.path"],
        doc_type="schema",
    ),
    _index(
        "idx_score_market_cycle_vendor",
        ["doc_type", "market", "cycle", "vendor_id"],
        doc_type="vendor_score",
    ),
    _index(
        "idx_score_vendor_schema_cycle",
        ["doc_type", "vendor_id", "schema_id", "cycle"],
        doc_type="vendor_score",
    ),
    _index(
        "idx_score_source_path_index",
        ["doc_type", "source.path", "source_index"],
        doc_type="vendor_score",
    ),
    _index(
        "idx_pricing_market_cycle_vendor",
        ["doc_type", "market", "cycle", "vendor_id"],
        doc_type="vendor_pricing",
    ),
    _index(
        "idx_pricing_source_path_index",
        ["doc_type", "source.path", "source_index"],
        doc_type="vendor_pricing",
    ),
    _index(
        "idx_mq_source_path_index",
        ["doc_type", "source.path", "source_index"],
        doc_type="mq_score",
    ),
    _index(
        "idx_insight_source_path_index",
        ["doc_type", "source.path", "source_index"],
        doc_type="market_insight",
    ),
    _index(
        "idx_analyst_take_source_path_index",
        ["doc_type", "source.path", "source_index"],
        doc_type="analyst_take",
    ),
    _index(
        "idx_innovation_source_path_index",
        ["doc_type", "source.path", "source_index"],
        doc_type="innovation_profile",
    ),
    _index(
        "idx_framework_source_path",
        ["doc_type", "source.path"],
        doc_type="framework",
    ),
    _index(
        "idx_report_definition_source_path",
        ["doc_type", "source.path"],
        doc_type="report_definition",
    ),
    _index(
        "idx_insight_market_type_perspective",
        ["doc_type", "market", "report_type", "perspective", "status"],
        doc_type="market_insight",
    ),
)

RESEARCH_INDEXES: tuple[IndexDefinition, ...] = (
    _index(
        "idx_project_market_cycle_status",
        ["doc_type", "market", "cycle", "status"],
        doc_type="research_project",
    ),
    _index(
        "idx_run_project_status_created",
        ["doc_type", "project_id", "status", "created_at"],
        doc_type="research_run",
    ),
    _index(
        "idx_target_project_vendor_status",
        ["doc_type", "project_id", "vendor_id", "status"],
        doc_type="research_target",
    ),
    _index(
        "idx_target_run_status_vendor",
        ["doc_type", "run_id", "status", "vendor_id"],
        doc_type="research_target",
    ),
    _index(
        "idx_source_canonical_url",
        ["doc_type", "canonical_url"],
        doc_type="source_reference",
    ),
    _index(
        "idx_snapshot_source_retrieved",
        ["doc_type", "source_id", "retrieved_at"],
        doc_type="source_snapshot",
    ),
    _index(
        "idx_snapshot_run_vendor_outcome",
        ["doc_type", "run_id", "vendor_id", "outcome"],
        doc_type="source_snapshot",
    ),
    _index(
        "idx_evidence_snapshot",
        ["doc_type", "snapshot_id"],
        doc_type="evidence_excerpt",
    ),
    _index(
        "idx_evidence_vendor_schema_criterion",
        ["doc_type", "vendor_id", "schema_id", "criterion_id"],
        doc_type="evidence_excerpt",
    ),
    _index(
        "idx_proposal_review_status",
        ["doc_type", "review_status", "created_at"],
        doc_type="score_proposal",
    ),
    _index(
        "idx_proposal_run_vendor_criterion",
        ["doc_type", "run_id", "vendor_id", "criterion_id"],
        doc_type="score_proposal",
    ),
    _index(
        "idx_decision_run_status_created",
        ["doc_type", "run_id", "status", "created_at"],
        doc_type="review_decision",
    ),
    _index(
        "idx_checkpoint_run_stage",
        ["doc_type", "run_id", "stage"],
        doc_type="research_checkpoint",
    ),
    _index(
        "idx_job_status_updated",
        ["doc_type", "status", "updated_at"],
        doc_type="research_job",
    ),
)

OPS_INDEXES: tuple[IndexDefinition, ...] = (
    _index(
        "idx_manifest_disposition_path",
        ["doc_type", "proposed_disposition", "relative_path"],
        doc_type="migration_manifest",
    ),
    _index(
        "idx_import_batch_status_created",
        ["doc_type", "status", "created_at"],
        doc_type="import_batch",
    ),
    _index(
        "idx_dead_letter_batch_path",
        ["doc_type", "import_batch_id", "relative_path"],
        doc_type="dead_letter",
    ),
    _index(
        "idx_audit_target_created",
        ["doc_type", "target_path", "created_at"],
        doc_type="audit_event",
    ),
)
