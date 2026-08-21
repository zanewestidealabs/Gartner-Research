"""Typed documents for the resumable research and review workflow."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from gartner_app.domain.models import DocType, DocumentEnvelope


class ResearchProject(DocumentEnvelope):
    doc_type: DocType = DocType.RESEARCH_PROJECT
    market: str
    cycle: str
    methodology_id: str
    schema_id: str


class ResearchRun(DocumentEnvelope):
    doc_type: DocType = DocType.RESEARCH_RUN
    project_id: str
    methodology_version: str
    schema_id: str
    code_revision: str
    policy_id: str | None = None
    model_metadata: dict[str, Any] = Field(default_factory=dict)
    status: Literal["running", "paused", "review", "completed", "failed"] = (
        "running"
    )


class ResearchTarget(DocumentEnvelope):
    doc_type: DocType = DocType.RESEARCH_TARGET
    project_id: str
    run_id: str
    vendor_id: str
    canonical_url: str
    criterion_ids: list[str] = Field(min_length=1)
    status: Literal["pending", "collecting", "blocked", "complete"] = "pending"
    retry_mode: Literal["headless", "headed"] = "headless"


class EvidenceExcerpt(DocumentEnvelope):
    doc_type: DocType = DocType.EVIDENCE_EXCERPT
    project_id: str
    run_id: str
    target_id: str
    vendor_id: str
    schema_id: str
    criterion_id: str
    source_url: str
    source_id: str | None = None
    snapshot_id: str | None = None
    excerpt: str = Field(min_length=1, max_length=4000)
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    collection_status: Literal["collected", "short", "blocked"] = "collected"


class SourceReference(DocumentEnvelope):
    doc_type: DocType = DocType.SOURCE_REFERENCE
    canonical_url: str
    original_urls: list[str] = Field(min_length=1)
    domain: str
    project_ids: list[str] = Field(default_factory=list)
    vendor_ids: list[str] = Field(default_factory=list)
    first_seen_at: datetime
    last_seen_at: datetime


class SourceSnapshot(DocumentEnvelope):
    doc_type: DocType = DocType.SOURCE_SNAPSHOT
    source_id: str
    project_id: str
    run_id: str
    target_id: str | None = None
    vendor_id: str
    retrieved_at: datetime
    retrieval_method: Literal[
        "urllib",
        "playwright",
        "cache_import",
        "unknown",
    ]
    outcome: Literal["success", "short", "blocked", "failed"]
    http_status: int | None = Field(default=None, ge=100, le=599)
    content_type: str | None = None
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    text_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    text_length: int = Field(ge=0)
    text: str = Field(max_length=200_000)
    error: str | None = None
    bot_wall_signals: list[str] = Field(default_factory=list)
    headed: bool = False
    attempt: int = Field(default=1, ge=1)
    previous_snapshot_id: str | None = None
    legacy_cache_path: str | None = None
    legacy_cache_sha256: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )


class ResearchPolicy(DocumentEnvelope):
    doc_type: DocType = DocType.RESEARCH_POLICY
    name: str
    version: str
    min_useful_text: int = Field(default=500, ge=1)
    min_support_excerpt_length: int = Field(default=80, ge=1)
    max_concurrency: int = Field(default=2, ge=1)
    max_excerpts_per_criterion: int = Field(default=5, ge=1)
    bot_wall_patterns: list[str] = Field(default_factory=list)
    retry_modes: list[Literal["headless", "headed"]] = Field(
        default_factory=lambda: ["headless", "headed"]
    )


class ScoreProposal(DocumentEnvelope):
    doc_type: DocType = DocType.SCORE_PROPOSAL
    project_id: str
    run_id: str
    vendor_id: str
    schema_id: str
    criterion_id: str
    proposed_score: float = Field(ge=0, le=5)
    confidence: Literal["low", "medium", "high"]
    evidence_ids: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)
    algorithm_version: str
    review_status: Literal["pending", "accepted", "rejected", "edited"] = (
        "pending"
    )

    @model_validator(mode="after")
    def require_evidence_for_positive_score(self) -> "ScoreProposal":
        if self.proposed_score > 0 and not self.evidence_ids:
            raise ValueError("positive score proposals require evidence_ids")
        return self


class ReviewDecision(DocumentEnvelope):
    doc_type: DocType = DocType.REVIEW_DECISION
    project_id: str
    run_id: str
    proposal_id: str
    reviewer: str
    action: Literal["accept", "reject", "edit"]
    accepted_score: float | None = Field(default=None, ge=0, le=5)
    comment: str = Field(min_length=1)
    status: Literal["decided", "published"] = "decided"
    publication_id: str | None = None

    @model_validator(mode="after")
    def require_score_for_edit(self) -> "ReviewDecision":
        if self.action == "edit" and self.accepted_score is None:
            raise ValueError("edit decisions require accepted_score")
        if self.action == "reject" and self.accepted_score is not None:
            raise ValueError("reject decisions cannot contain accepted_score")
        return self


class ResearchCheckpoint(DocumentEnvelope):
    doc_type: DocType = DocType.RESEARCH_CHECKPOINT
    project_id: str
    run_id: str
    stage: Literal[
        "targeting",
        "rendering",
        "harvesting",
        "evidence_harvesting",
        "svc_pricing",
        "scoring",
        "review",
        "publishing",
    ]
    cursor: str | None = None
    completed_target_ids: list[str] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)

    @field_validator("completed_target_ids")
    @classmethod
    def unique_completed_targets(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("completed_target_ids must be unique")
        return value
