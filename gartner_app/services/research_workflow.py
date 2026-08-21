"""Resumable research workflow with explicit proposal and review boundaries."""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

from gartner_app.couchdb.client import CouchDBClient, CouchDBNotFound
from gartner_app.domain.research import (
    EvidenceExcerpt,
    ResearchCheckpoint,
    ResearchProject,
    ResearchRun,
    ResearchTarget,
    ResearchPolicy,
    ReviewDecision,
    ScoreProposal,
    SourceReference,
    SourceSnapshot,
)
from gartner_app.repositories.research import ResearchRepository


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _id(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4()}"


class ResearchWorkflowService:
    def __init__(
        self,
        research: ResearchRepository,
        *,
        core_client: CouchDBClient | None = None,
        core_database: str | None = None,
    ) -> None:
        self.research = research
        self.core_client = core_client
        self.core_database = (
            core_client.validate_database_name(core_database)
            if core_client is not None and core_database is not None
            else None
        )

    def create_project(
        self,
        *,
        market: str,
        cycle: str,
        methodology_id: str,
        schema_id: str,
        actor: str,
    ) -> ResearchProject:
        project = ResearchProject(
            _id=_id("research_project"),
            market=market,
            cycle=cycle,
            methodology_id=methodology_id,
            schema_id=schema_id,
            created_by=actor,
            updated_by=actor,
        )
        self.research.create(project)
        return project

    def start_run(
        self,
        project: ResearchProject,
        *,
        methodology_version: str,
        code_revision: str,
        actor: str,
        model_metadata: dict[str, Any] | None = None,
        policy_id: str | None = None,
    ) -> ResearchRun:
        run = ResearchRun(
            _id=_id("research_run"),
            project_id=project.id,
            methodology_version=methodology_version,
            schema_id=project.schema_id,
            code_revision=code_revision,
            policy_id=policy_id,
            model_metadata=model_metadata or {},
            created_by=actor,
            updated_by=actor,
        )
        self.research.create(run)
        return run

    def add_targets(
        self,
        project: ResearchProject,
        run: ResearchRun,
        targets: Iterable[dict[str, Any]],
        *,
        actor: str,
    ) -> list[ResearchTarget]:
        created: list[ResearchTarget] = []
        for value in targets:
            target = ResearchTarget(
                _id=_id("research_target"),
                project_id=project.id,
                run_id=run.id,
                vendor_id=value["vendor_id"],
                canonical_url=value["canonical_url"],
                criterion_ids=value["criterion_ids"],
                retry_mode=value.get("retry_mode", "headless"),
                created_by=actor,
                updated_by=actor,
            )
            self.research.create(target)
            created.append(target)
        return created

    def record_evidence(
        self,
        *,
        project_id: str,
        run_id: str,
        target_id: str,
        vendor_id: str,
        schema_id: str,
        criterion_id: str,
        source_url: str,
        excerpt: str,
        source_text: str,
        actor: str,
        collection_status: str = "collected",
        source_id: str | None = None,
        snapshot_id: str | None = None,
        document_id: str | None = None,
    ) -> EvidenceExcerpt:
        evidence = EvidenceExcerpt(
            _id=document_id or _id("evidence"),
            project_id=project_id,
            run_id=run_id,
            target_id=target_id,
            vendor_id=vendor_id,
            schema_id=schema_id,
            criterion_id=criterion_id,
            source_url=source_url,
            source_id=source_id,
            snapshot_id=snapshot_id,
            excerpt=excerpt,
            source_sha256=hashlib.sha256(
                source_text.encode("utf-8")
            ).hexdigest(),
            collection_status=collection_status,
            created_by=actor,
            updated_by=actor,
        )
        self.research.create(evidence)
        return evidence

    def create_policy(
        self,
        *,
        name: str,
        version: str,
        actor: str,
        min_useful_text: int = 500,
        min_support_excerpt_length: int = 80,
        max_concurrency: int = 2,
        max_excerpts_per_criterion: int = 5,
        bot_wall_patterns: list[str] | None = None,
    ) -> ResearchPolicy:
        policy = ResearchPolicy(
            _id=f"research_policy:{name}:{version}",
            name=name,
            version=version,
            min_useful_text=min_useful_text,
            min_support_excerpt_length=min_support_excerpt_length,
            max_concurrency=max_concurrency,
            max_excerpts_per_criterion=max_excerpts_per_criterion,
            bot_wall_patterns=bot_wall_patterns or [],
            created_by=actor,
            updated_by=actor,
        )
        self.research.create(policy)
        return policy

    def register_source(
        self,
        *,
        canonical_url: str,
        original_url: str,
        domain: str,
        project_id: str,
        vendor_id: str,
        actor: str,
        document_id: str,
    ) -> SourceReference:
        now = _now()
        try:
            existing = self.research.get(document_id)
        except CouchDBNotFound:
            source = SourceReference(
                _id=document_id,
                canonical_url=canonical_url,
                original_urls=[original_url],
                domain=domain,
                project_ids=[project_id],
                vendor_ids=[vendor_id],
                first_seen_at=now,
                last_seen_at=now,
                created_by=actor,
                updated_by=actor,
            )
            self.research.create(source)
            return source
        original_urls = sorted(
            {*existing.get("original_urls", []), original_url}
        )
        project_ids = sorted(
            {*existing.get("project_ids", []), project_id}
        )
        vendor_ids = sorted({*existing.get("vendor_ids", []), vendor_id})
        self.research.replace(
            document_id,
            {
                "original_urls": original_urls,
                "project_ids": project_ids,
                "vendor_ids": vendor_ids,
                "last_seen_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "updated_by": actor,
            },
            expected_revision=existing["_rev"],
        )
        return SourceReference.model_validate(
            {
                **existing,
                "original_urls": original_urls,
                "project_ids": project_ids,
                "vendor_ids": vendor_ids,
                "last_seen_at": now,
                "updated_at": now,
                "updated_by": actor,
            }
        )

    def record_snapshot(self, snapshot: SourceSnapshot) -> SourceSnapshot:
        self.research.create(snapshot)
        return snapshot

    def propose_score(
        self,
        *,
        project_id: str,
        run_id: str,
        vendor_id: str,
        schema_id: str,
        criterion_id: str,
        score: float,
        confidence: str,
        evidence_ids: list[str],
        rationale: str,
        algorithm_version: str,
        actor: str,
        document_id: str | None = None,
    ) -> ScoreProposal:
        proposal = ScoreProposal(
            _id=document_id or _id("score_proposal"),
            project_id=project_id,
            run_id=run_id,
            vendor_id=vendor_id,
            schema_id=schema_id,
            criterion_id=criterion_id,
            proposed_score=score,
            confidence=confidence,
            evidence_ids=evidence_ids,
            rationale=rationale,
            algorithm_version=algorithm_version,
            created_by=actor,
            updated_by=actor,
        )
        self.research.create(proposal)
        return proposal

    def review(
        self,
        proposal: ScoreProposal,
        *,
        reviewer: str,
        action: str,
        comment: str,
        accepted_score: float | None = None,
    ) -> ReviewDecision:
        decision = ReviewDecision(
            _id=_id("review_decision"),
            project_id=proposal.project_id,
            run_id=proposal.run_id,
            proposal_id=proposal.id,
            reviewer=reviewer,
            action=action,
            accepted_score=(
                proposal.proposed_score if action == "accept" else accepted_score
            ),
            comment=comment,
            created_by=reviewer,
            updated_by=reviewer,
        )
        self.research.create(decision)
        return decision

    def save_checkpoint(
        self,
        *,
        project_id: str,
        run_id: str,
        stage: str,
        actor: str,
        cursor: str | None,
        completed_target_ids: list[str],
        state: dict[str, Any] | None = None,
        expected_revision: str | None = None,
    ) -> ResearchCheckpoint:
        existing = self.research.checkpoint(run_id, stage)
        if existing is None:
            checkpoint = ResearchCheckpoint(
                _id=f"research_checkpoint:{run_id}:{stage}",
                project_id=project_id,
                run_id=run_id,
                stage=stage,
                cursor=cursor,
                completed_target_ids=completed_target_ids,
                state=state or {},
                created_by=actor,
                updated_by=actor,
            )
            self.research.create(checkpoint)
            return checkpoint
        if not expected_revision:
            raise ValueError("updating a checkpoint requires expected_revision")
        now = _now()
        self.research.replace(
            existing["_id"],
            {
                "cursor": cursor,
                "completed_target_ids": completed_target_ids,
                "state": state or {},
                "updated_at": now.isoformat(),
                "updated_by": actor,
            },
            expected_revision=expected_revision,
        )
        return ResearchCheckpoint.model_validate(
            {
                **existing,
                "cursor": cursor,
                "completed_target_ids": completed_target_ids,
                "state": state or {},
                "updated_at": now,
                "updated_by": actor,
            }
        )

    def resume(self, run_id: str, stage: str) -> dict[str, Any]:
        checkpoint = self.research.checkpoint(run_id, stage)
        pending = self.research.targets(run_id, "pending")
        blocked = self.research.targets(run_id, "blocked")
        return {
            "run_id": run_id,
            "stage": stage,
            "checkpoint": checkpoint,
            "pending_targets": pending,
            "blocked_targets": blocked,
        }

    def publish(
        self,
        project: ResearchProject,
        proposal: ScoreProposal,
        decision: ReviewDecision,
        *,
        actor: str,
    ) -> dict[str, Any]:
        if self.core_client is None or self.core_database is None:
            raise RuntimeError("core database is not configured for publishing")
        if decision.proposal_id != proposal.id:
            raise ValueError("decision does not belong to proposal")
        if decision.action == "reject":
            raise ValueError("rejected proposals cannot be published")
        score = decision.accepted_score
        if score is None:
            raise ValueError("review decision has no accepted score")
        document_id = (
            f"vendor_score:research:{proposal.run_id}:"
            f"{proposal.vendor_id}:{proposal.criterion_id}"
        )
        document = {
            "_id": document_id,
            "doc_type": "vendor_score",
            "schema_version": 1,
            "status": "accepted",
            "market": project.market,
            "cycle": project.cycle,
            "vendor_id": proposal.vendor_id,
            "schema_id": proposal.schema_id,
            "criterion_id": proposal.criterion_id,
            "score": score,
            "proposal_id": proposal.id,
            "decision_id": decision.id,
            "evidence_ids": proposal.evidence_ids,
            "created_at": _now().isoformat(),
            "created_by": actor,
            "updated_at": _now().isoformat(),
            "updated_by": actor,
        }
        return self.core_client.put_document(
            self.core_database,
            document_id,
            document,
        )
