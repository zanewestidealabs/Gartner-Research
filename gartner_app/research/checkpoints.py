"""CouchDB-backed compatibility store for legacy worker progress."""

from __future__ import annotations

from typing import Any

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient
from gartner_app.repositories.research import ResearchRepository
from gartner_app.services.research_workflow import ResearchWorkflowService


class ResearchCheckpointStore:
    def __init__(
        self,
        workflow: ResearchWorkflowService,
        *,
        project_id: str,
        run_id: str,
        stage: str,
        actor: str,
    ) -> None:
        self.workflow = workflow
        self.project_id = project_id
        self.run_id = run_id
        self.stage = stage
        self.actor = actor

    @classmethod
    def from_settings(
        cls,
        *,
        project_id: str,
        run_id: str,
        stage: str,
        actor: str,
    ) -> "ResearchCheckpointStore":
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
            stage=stage,
            actor=actor,
        )

    def load(self) -> dict[str, Any]:
        checkpoint = self.workflow.research.checkpoint(
            self.run_id,
            self.stage,
        )
        if checkpoint is None:
            return {"completed_batches": [], "completed_vendors": []}
        progress = checkpoint.get("state", {}).get("legacy_progress", {})
        return {
            "completed_batches": list(
                progress.get("completed_batches", [])
            ),
            "completed_vendors": list(
                progress.get("completed_vendors", [])
            ),
        }

    def save(self, progress: dict[str, Any]) -> None:
        existing = self.workflow.research.checkpoint(
            self.run_id,
            self.stage,
        )
        batches = list(progress.get("completed_batches", []))
        vendors = list(progress.get("completed_vendors", []))
        self.workflow.save_checkpoint(
            project_id=self.project_id,
            run_id=self.run_id,
            stage=self.stage,
            cursor=str(batches[-1]) if batches else None,
            completed_target_ids=[],
            state={
                "legacy_progress": {
                    "completed_batches": batches,
                    "completed_vendors": vendors,
                }
            },
            expected_revision=(
                existing.get("_rev") if existing is not None else None
            ),
            actor=self.actor,
        )
