from __future__ import annotations

from copy import deepcopy

import pytest

from gartner_app.couchdb.client import CouchDBConflict, CouchDBNotFound
from gartner_app.domain.research import ResearchProject, ScoreProposal
from gartner_app.research.lineage import (
    LegacyCacheLineageSink,
    canonicalize_url,
)
from gartner_app.research.scoring import LegacyScoreProposalSink
from gartner_app.research.checkpoints import ResearchCheckpointStore
from gartner_app.repositories.research import ResearchRepository
from gartner_app.services.research_workflow import ResearchWorkflowService


class MemoryClient:
    def __init__(self) -> None:
        self.databases: dict[str, dict[str, dict]] = {
            "research": {},
            "core": {},
        }

    @staticmethod
    def validate_database_name(database: str) -> str:
        return database

    @staticmethod
    def document_path(database: str, document_id: str) -> str:
        return f"/{database}/{document_id}"

    def get_document(self, database: str, document_id: str) -> dict:
        try:
            return deepcopy(self.databases[database][document_id])
        except KeyError as exc:
            raise CouchDBNotFound(404, "GET", document_id, "missing") from exc

    def put_document(
        self, database: str, document_id: str, document: dict
    ) -> dict:
        existing = self.databases[database].get(document_id)
        if existing and document.get("_rev") != existing["_rev"]:
            raise CouchDBConflict(409, "PUT", document_id, "conflict")
        generation = int(existing["_rev"].split("-", 1)[0]) + 1 if existing else 1
        stored = deepcopy(document)
        stored["_rev"] = f"{generation}-test"
        self.databases[database][document_id] = stored
        return {"ok": True, "id": document_id, "rev": stored["_rev"]}

    def find(self, database: str, query: dict) -> dict:
        selector = query["selector"]

        def matches(document: dict) -> bool:
            for key, expected in selector.items():
                actual = document.get(key)
                if isinstance(expected, dict) and "$eq" in expected:
                    expected = expected["$eq"]
                if actual != expected:
                    return False
            return True

        return {
            "docs": [
                deepcopy(value)
                for value in self.databases[database].values()
                if matches(value)
            ][: query.get("limit", 100)]
        }


@pytest.fixture
def workflow() -> tuple[ResearchWorkflowService, MemoryClient]:
    client = MemoryClient()
    repository = ResearchRepository(client, "research")  # type: ignore[arg-type]
    return (
        ResearchWorkflowService(
            repository,
            core_client=client,  # type: ignore[arg-type]
            core_database="core",
        ),
        client,
    )


def test_three_vendor_run_can_checkpoint_and_resume(workflow) -> None:
    service, _ = workflow
    project = service.create_project(
        market="precyber",
        cycle="2026",
        methodology_id="precyber-standard",
        schema_id="schema:precyber:2",
        actor="analyst",
    )
    run = service.start_run(
        project,
        methodology_version="1.0",
        code_revision="abc123",
        actor="analyst",
    )
    targets = service.add_targets(
        project,
        run,
        [
            {
                "vendor_id": f"vendor:{name}",
                "canonical_url": f"https://{name}.example/research",
                "criterion_ids": ["EXM-04"],
            }
            for name in ("alpha", "bravo", "charlie")
        ],
        actor="analyst",
    )
    checkpoint = service.save_checkpoint(
        project_id=project.id,
        run_id=run.id,
        stage="rendering",
        cursor=targets[0].id,
        completed_target_ids=[targets[0].id],
        actor="worker",
    )

    state = service.resume(run.id, "rendering")

    assert checkpoint.cursor == targets[0].id
    assert len(state["pending_targets"]) == 3
    assert state["checkpoint"]["completed_target_ids"] == [targets[0].id]


def test_evidence_and_proposals_are_immutable(workflow) -> None:
    service, client = workflow
    evidence = service.record_evidence(
        project_id="project:1",
        run_id="run:1",
        target_id="target:1",
        vendor_id="vendor:alpha",
        schema_id="schema:1",
        criterion_id="EXM-04",
        source_url="https://example.test",
        excerpt="A sufficiently concrete public capability statement.",
        source_text="full rendered source",
        actor="collector",
    )
    stored = client.get_document("research", evidence.id)

    with pytest.raises(ValueError, match="immutable"):
        service.research.replace(
            evidence.id,
            {"excerpt": "changed"},
            expected_revision=stored["_rev"],
        )


def test_reviewed_proposal_publishes_separate_accepted_score(workflow) -> None:
    service, client = workflow
    project = ResearchProject(
        _id="research_project:test",
        market="precyber",
        cycle="2026",
        methodology_id="standard",
        schema_id="schema:1",
        created_by="analyst",
        updated_by="analyst",
    )
    proposal = ScoreProposal(
        _id="score_proposal:test",
        project_id=project.id,
        run_id="run:test",
        vendor_id="vendor:alpha",
        schema_id=project.schema_id,
        criterion_id="EXM-04",
        proposed_score=2.25,
        confidence="medium",
        evidence_ids=["evidence:1"],
        rationale="Public evidence supports partial capability only.",
        algorithm_version="strict-v2.3",
        created_by="scorer",
        updated_by="scorer",
    )
    service.research.create(project)
    service.research.create(proposal)
    decision = service.review(
        proposal,
        reviewer="reviewer",
        action="edit",
        accepted_score=2.0,
        comment="Adjusted after evidence review.",
    )

    result = service.publish(
        project,
        proposal,
        decision,
        actor="reviewer",
    )
    published = client.get_document("core", result["id"])

    assert published["score"] == 2.0
    assert published["proposal_id"] == proposal.id
    assert client.get_document("research", proposal.id)["proposed_score"] == 2.25


def test_url_canonicalization_removes_tracking_without_losing_query() -> None:
    value = canonicalize_url(
        "HTTPS://Example.COM:443/path/?b=2&utm_source=test&a=1#section"
    )
    assert value == "https://example.com/path?a=1&b=2"


def test_legacy_cache_retry_creates_immutable_snapshot_history(workflow) -> None:
    service, client = workflow
    sink = LegacyCacheLineageSink(
        service,
        project_id="project:lineage",
        run_id="run:lineage",
        actor="worker:test",
    )
    blocked = sink.capture(
        vendor_id="vendor:alpha",
        record={
            "url": "https://example.test/capability",
            "fetched_at": "2026-07-23T00:00:00+00:00",
            "ok": False,
            "text": "",
            "error": "bot_blocked",
            "render_engine": "playwright",
        },
        attempt=1,
    )
    success = sink.capture(
        vendor_id="vendor:alpha",
        record={
            "url": "https://example.test/capability",
            "fetched_at": "2026-07-23T00:01:00+00:00",
            "ok": True,
            "content_type": "text/html",
            "text": "Concrete capability evidence. " * 30,
            "error": None,
            "render_engine": "playwright",
        },
        headed=True,
        attempt=2,
        previous_snapshot_id=blocked.id,
    )

    assert blocked.outcome == "blocked"
    assert success.outcome == "success"
    assert success.previous_snapshot_id == blocked.id
    assert len(
        [
            document
            for document in client.databases["research"].values()
            if document["doc_type"] == "source_reference"
        ]
    ) == 1
    stored = client.get_document("research", blocked.id)
    with pytest.raises(ValueError, match="immutable"):
        service.research.replace(
            blocked.id,
            {"outcome": "success"},
            expected_revision=stored["_rev"],
        )


def test_legacy_progress_round_trips_through_research_checkpoint(
    workflow,
) -> None:
    service, _ = workflow
    store = ResearchCheckpointStore(
        service,
        project_id="project:1",
        run_id="run:1",
        stage="svc_pricing",
        actor="worker:test",
    )
    progress = {
        "completed_batches": [1, 2],
        "completed_vendors": ["Alpha", "Bravo"],
    }

    store.save(progress)
    assert store.load() == progress
    progress["completed_batches"].append(3)
    progress["completed_vendors"].append("Charlie")
    store.save(progress)
    assert store.load() == progress


def test_score_bridge_requires_snapshot_for_positive_proposal(workflow) -> None:
    service, _ = workflow
    sink = LegacyScoreProposalSink(
        service,
        project_id="project:score",
        run_id="run:score",
        actor="worker:test",
    )

    proposal = sink.capture(
        vendor_name="Alpha",
        schema_id="schema:1",
        criterion_id="EXM-04",
        score_record={
            "new_score": 2.0,
            "confidence": "medium",
            "rationale": "Partial public evidence.",
        },
        evidence_block={
            "excerpts": [
                {
                    "url": "https://missing.example/evidence",
                    "excerpt": "A claim without a captured snapshot.",
                }
            ]
        },
        algorithm_version="strict-v2.3",
    )

    assert proposal is None


def test_score_bridge_links_proposal_evidence_to_snapshot(workflow) -> None:
    service, client = workflow
    lineage = LegacyCacheLineageSink(
        service,
        project_id="project:score",
        run_id="run:score",
        actor="worker:test",
    )
    url = "https://example.test/scoring-evidence"
    snapshot = lineage.capture(
        vendor_id="vendor:alpha",
        record={
            "url": url,
            "fetched_at": "2026-07-23T00:00:00+00:00",
            "ok": True,
            "text": "Concrete public capability evidence. " * 30,
            "error": None,
            "render_engine": "playwright",
        },
    )
    scoring = LegacyScoreProposalSink(
        service,
        project_id="project:score",
        run_id="run:score",
        actor="worker:test",
    )

    proposal = scoring.capture(
        vendor_name="Alpha",
        schema_id="schema:1",
        criterion_id="EXM-04",
        score_record={
            "new_score": 2.25,
            "confidence": "medium",
            "rationale": "One criterion is partially supported.",
        },
        evidence_block={
            "excerpts": [
                {
                    "url": url,
                    "excerpt": "Concrete public capability evidence.",
                }
            ]
        },
        algorithm_version="strict-v2.3",
    )

    assert proposal is not None
    evidence = client.get_document(
        "research",
        proposal.evidence_ids[0],
    )
    assert evidence["snapshot_id"] == snapshot.id

    repeated = scoring.capture(
        vendor_name="Alpha",
        schema_id="schema:1",
        criterion_id="EXM-04",
        score_record={
            "new_score": 2.25,
            "confidence": "medium",
            "rationale": "One criterion is partially supported.",
        },
        evidence_block={
            "excerpts": [
                {
                    "url": url,
                    "excerpt": "Concrete public capability evidence.",
                }
            ]
        },
        algorithm_version="strict-v2.3",
    )
    assert repeated is not None
    assert repeated.id == proposal.id
    assert len(
        [
            document
            for document in client.databases["research"].values()
            if document["doc_type"] == "score_proposal"
        ]
    ) == 1
