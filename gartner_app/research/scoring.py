"""Bridge legacy strict scoring into snapshot-backed score proposals."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from gartner_app.config import Settings
from gartner_app.couchdb.client import (
    CouchDBClient,
    CouchDBConflict,
    CouchDBNotFound,
)
from gartner_app.couchdb.queries import source_snapshots
from gartner_app.domain.research import (
    EvidenceExcerpt,
    ResearchTarget,
    ScoreProposal,
)
from gartner_app.repositories.research import ResearchRepository
from gartner_app.research.lineage import (
    canonicalize_url,
    source_document_id,
)
from gartner_app.services.research_workflow import ResearchWorkflowService


def _vendor_id(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"vendor:{slug or 'unknown'}"


class LegacyScoreProposalSink:
    def __init__(
        self,
        workflow: ResearchWorkflowService,
        *,
        project_id: str,
        run_id: str,
        actor: str,
    ) -> None:
        self.workflow = workflow
        self.project_id = project_id
        self.run_id = run_id
        self.actor = actor

    @classmethod
    def from_settings(
        cls,
        *,
        project_id: str,
        run_id: str,
        actor: str,
    ) -> "LegacyScoreProposalSink":
        settings = Settings.from_env()
        username, password = settings.require_gateway_credentials()
        client = CouchDBClient(
            settings.couchdb_url,
            username=username,
            password=password,
            connect_timeout=settings.connect_timeout_seconds,
            read_timeout=settings.read_timeout_seconds,
        )
        return cls(
            ResearchWorkflowService(
                ResearchRepository(client, settings.couchdb_research_db)
            ),
            project_id=project_id,
            run_id=run_id,
            actor=actor,
        )

    def _target(
        self,
        *,
        vendor_id: str,
        criterion_id: str,
        canonical_url: str,
    ) -> ResearchTarget:
        digest = hashlib.sha256(
            f"{self.run_id}|{vendor_id}|{criterion_id}".encode("utf-8")
        ).hexdigest()
        document_id = f"research_target:score:{digest}"
        try:
            return ResearchTarget.model_validate(
                self.workflow.research.get(document_id)
            )
        except CouchDBNotFound:
            target = ResearchTarget(
                _id=document_id,
                project_id=self.project_id,
                run_id=self.run_id,
                vendor_id=vendor_id,
                canonical_url=canonical_url,
                criterion_ids=[criterion_id],
                status="complete",
                created_by=self.actor,
                updated_by=self.actor,
            )
            try:
                self.workflow.research.create(target)
            except CouchDBConflict:
                return ResearchTarget.model_validate(
                    self.workflow.research.get(document_id)
                )
            return target

    def capture(
        self,
        *,
        vendor_name: str,
        schema_id: str,
        criterion_id: str,
        score_record: dict[str, Any],
        evidence_block: dict[str, Any] | None,
        algorithm_version: str,
    ) -> ScoreProposal | None:
        vendor_id = _vendor_id(vendor_name)
        excerpts = (evidence_block or {}).get("excerpts", []) or []
        first_url = next(
            (
                str(item.get("url"))
                for item in excerpts
                if isinstance(item, dict) and item.get("url")
            ),
            "urn:no-public-evidence",
        )
        target = self._target(
            vendor_id=vendor_id,
            criterion_id=criterion_id,
            canonical_url=first_url,
        )
        evidence_ids: list[str] = []
        for item in excerpts:
            if not isinstance(item, dict):
                continue
            url = str(item.get("url") or "")
            excerpt = str(item.get("excerpt") or "").strip()
            if not url or not excerpt:
                continue
            source_id = source_document_id(canonicalize_url(url))
            snapshots = self.workflow.research.find(
                source_snapshots(source_id, limit=500)
            ).get("docs", [])
            snapshot = next(
                (
                    document
                    for document in reversed(snapshots)
                    if document.get("outcome") == "success"
                ),
                None,
            )
            if snapshot is None:
                continue
            evidence_digest = hashlib.sha256(
                (
                    f"{self.run_id}|{vendor_id}|{criterion_id}|"
                    f"{snapshot['_id']}|{excerpt}"
                ).encode("utf-8")
            ).hexdigest()
            evidence_id = f"evidence:{evidence_digest}"
            try:
                evidence = self.workflow.record_evidence(
                    project_id=self.project_id,
                    run_id=self.run_id,
                    target_id=target.id,
                    vendor_id=vendor_id,
                    schema_id=schema_id,
                    criterion_id=criterion_id,
                    source_url=url,
                    source_id=source_id,
                    snapshot_id=snapshot["_id"],
                    excerpt=excerpt,
                    source_text=str(snapshot.get("text") or ""),
                    document_id=evidence_id,
                    actor=self.actor,
                )
            except CouchDBConflict:
                evidence = EvidenceExcerpt.model_validate(
                    self.workflow.research.get(evidence_id)
                )
            evidence_ids.append(evidence.id)

        score = float(score_record["new_score"])
        if score > 0 and not evidence_ids:
            return None
        proposal_digest = hashlib.sha256(
            (
                f"{self.run_id}|{vendor_id}|{criterion_id}|"
                f"{algorithm_version}"
            ).encode("utf-8")
        ).hexdigest()
        proposal_id = f"score_proposal:{proposal_digest}"
        try:
            return self.workflow.propose_score(
                project_id=self.project_id,
                run_id=self.run_id,
                vendor_id=vendor_id,
                schema_id=schema_id,
                criterion_id=criterion_id,
                score=score,
                confidence=score_record["confidence"],
                evidence_ids=evidence_ids,
                rationale=score_record["rationale"],
                algorithm_version=algorithm_version,
                document_id=proposal_id,
                actor=self.actor,
            )
        except CouchDBConflict:
            return ScoreProposal.model_validate(
                self.workflow.research.get(proposal_id)
            )
