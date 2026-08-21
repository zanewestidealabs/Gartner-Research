"""CouchDB repositories for first-class research workflow documents."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from gartner_app.couchdb.client import (
    CouchDBClient,
    CouchDBConflict,
    CouchDBNotFound,
)
from gartner_app.couchdb.queries import research_targets, score_proposals
from gartner_app.domain.models import DocumentEnvelope

IMMUTABLE_TYPES = {
    "source_snapshot",
    "evidence_excerpt",
    "score_proposal",
    "review_decision",
    "research_policy",
}


class ResearchRepository:
    def __init__(self, client: CouchDBClient, database: str) -> None:
        self.client = client
        self.database = client.validate_database_name(database)

    def get(self, document_id: str) -> dict[str, Any]:
        return self.client.get_document(self.database, document_id)

    def create(self, document: DocumentEnvelope) -> dict[str, Any]:
        payload = document.to_couchdb()
        if document.rev is not None:
            raise ValueError("new research documents cannot include _rev")
        try:
            self.get(document.id)
        except CouchDBNotFound:
            return self.client.put_document(self.database, document.id, payload)
        raise CouchDBConflict(
            409,
            "PUT",
            self.client.document_path(self.database, document.id),
            "document already exists",
        )

    def replace(
        self,
        document_id: str,
        changes: Mapping[str, Any],
        *,
        expected_revision: str,
    ) -> dict[str, Any]:
        current = self.get(document_id)
        if current.get("doc_type") in IMMUTABLE_TYPES:
            raise ValueError(f"{current['doc_type']} documents are immutable")
        if current.get("_rev") != expected_revision:
            raise CouchDBConflict(
                409,
                "PUT",
                self.client.document_path(self.database, document_id),
                "revision does not match",
            )
        protected = {"_id", "_rev", "doc_type", "created_at", "created_by"}
        if protected.intersection(changes):
            raise ValueError("changes include protected document fields")
        payload = {**current, **changes, "_rev": expected_revision}
        return self.client.put_document(self.database, document_id, payload)

    def find(self, query: Mapping[str, Any]) -> dict[str, Any]:
        return self.client.find(self.database, query)

    def targets(
        self,
        run_id: str,
        status: str,
        *,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return self.find(research_targets(run_id, status, limit=limit))["docs"]

    def proposals(
        self,
        run_id: str,
        vendor_id: str,
        criterion_id: str,
        *,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        query = score_proposals(
            run_id,
            vendor_id,
            criterion_id,
            limit=limit,
        )
        return self.find(query)["docs"]

    def checkpoint(self, run_id: str, stage: str) -> dict[str, Any] | None:
        result = self.find(
            {
                "selector": {
                    "doc_type": {"$eq": "research_checkpoint"},
                    "run_id": {"$eq": run_id},
                    "stage": {"$eq": stage},
                },
                "limit": 2,
                "use_index": [
                    "idx-checkpoint-run-stage",
                    "idx_checkpoint_run_stage",
                ],
            }
        )
        documents = result.get("docs", [])
        if len(documents) > 1:
            raise RuntimeError("multiple checkpoints exist for run and stage")
        return documents[0] if documents else None
