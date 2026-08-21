"""Shared CouchDB document contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DocType(StrEnum):
    VENDOR = "vendor"
    SCHEMA = "schema"
    VENDOR_SCORE = "vendor_score"
    VENDOR_PRICING = "vendor_pricing"
    MARKET_INSIGHT = "market_insight"
    ANALYST_TAKE = "analyst_take"
    MQ_SCORE = "mq_score"
    INNOVATION_PROFILE = "innovation_profile"
    FRAMEWORK = "framework"
    ADOPTION_PLAN = "adoption_plan"
    REPORT_DEFINITION = "report_definition"
    APP_CONFIG = "app_config"
    RESEARCH_PROJECT = "research_project"
    RESEARCH_RUN = "research_run"
    RESEARCH_TARGET = "research_target"
    SOURCE_REFERENCE = "source_reference"
    SOURCE_SNAPSHOT = "source_snapshot"
    EVIDENCE_EXCERPT = "evidence_excerpt"
    SCORE_PROPOSAL = "score_proposal"
    REVIEW_DECISION = "review_decision"
    RESEARCH_CHECKPOINT = "research_checkpoint"
    RESEARCH_JOB = "research_job"
    ANNOTATION = "annotation"
    RESEARCH_POLICY = "research_policy"
    MIGRATION_MANIFEST = "migration_manifest"
    IMPORT_BATCH = "import_batch"
    DEAD_LETTER = "dead_letter"
    AUDIT_EVENT = "audit_event"
    IDEMPOTENCY_RECORD = "idempotency_record"
    GENERATED_ARTIFACT = "generated_artifact"
    LEGACY_DATASET = "legacy_dataset"
    LEGACY_RECORD = "legacy_record"
    LEGACY_ASSET_MANIFEST = "legacy_asset_manifest"


class SourceProvenance(BaseModel):
    model_config = ConfigDict(extra="allow")

    kind: str
    path: str | None = None
    sha256: str | None = None
    import_batch_id: str | None = None


class DocumentEnvelope(BaseModel):
    """Common fields required on application-owned CouchDB documents."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        use_enum_values=True,
    )

    id: str = Field(alias="_id", min_length=3, max_length=512)
    rev: str | None = Field(default=None, alias="_rev")
    doc_type: DocType
    schema_version: int = Field(default=1, ge=1)
    status: str = "active"
    created_at: datetime = Field(default_factory=utc_now)
    created_by: str
    updated_at: datetime = Field(default_factory=utc_now)
    updated_by: str
    source: SourceProvenance | None = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if value.startswith("_"):
            raise ValueError("application document IDs cannot start with '_'")
        if any(character.isspace() for character in value):
            raise ValueError("application document IDs cannot contain whitespace")
        return value

    def to_couchdb(self) -> dict[str, Any]:
        return self.model_dump(
            by_alias=True,
            mode="json",
            exclude_none=True,
        )


class MigrationManifest(DocumentEnvelope):
    doc_type: DocType = DocType.MIGRATION_MANIFEST
    relative_path: str
    size_bytes: int = Field(ge=0)
    modified_at: datetime
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    parse_status: str
    top_level_type: str | None = None
    top_level_keys: list[str] = Field(default_factory=list)
    record_count: int | None = Field(default=None, ge=0)
    inferred_family: str
    proposed_disposition: str
