"""Local-only API gateway for the CouchDB research workflow."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from gartner_app.config import Settings
from gartner_app.couchdb.client import (
    CouchDBClient,
    CouchDBConflict,
    CouchDBNotFound,
)
from gartner_app.domain.research import (
    ResearchProject,
    ResearchRun,
    ReviewDecision,
    ScoreProposal,
)
from gartner_app.repositories.research import ResearchRepository
from gartner_app.services.research_workflow import ResearchWorkflowService

research_blueprint = Blueprint("research", __name__, url_prefix="/api/research")
_LOCAL_ADDRESSES = {"127.0.0.1", "::1", "localhost"}


def _service() -> ResearchWorkflowService:
    settings = Settings.from_env()
    username, password = settings.require_gateway_credentials()
    client = CouchDBClient(
        settings.couchdb_url,
        username=username,
        password=password,
        connect_timeout=settings.connect_timeout_seconds,
        read_timeout=settings.read_timeout_seconds,
    )
    return ResearchWorkflowService(
        ResearchRepository(client, settings.couchdb_research_db),
        core_client=client,
        core_database=settings.couchdb_core_db,
    )


def _payload() -> dict[str, Any]:
    value = request.get_json(silent=False)
    if not isinstance(value, dict):
        raise ValueError("request body must be a JSON object")
    return value


def _actor() -> str:
    value = request.headers.get("X-Research-Actor", "").strip()
    if not value:
        raise ValueError("X-Research-Actor header is required")
    return value


@research_blueprint.before_request
def guard_research_gateway():
    settings = Settings.from_env()
    if settings.data_backend != "couchdb":
        return (
            jsonify(
                {
                    "error": "Research writes require DATA_BACKEND=couchdb",
                    "code": "couchdb_backend_required",
                }
            ),
            503,
        )
    if request.remote_addr not in _LOCAL_ADDRESSES:
        return (
            jsonify(
                {
                    "error": "Research workflow API is restricted to localhost",
                    "code": "localhost_required",
                }
            ),
            403,
        )
    return None


@research_blueprint.errorhandler(ValueError)
@research_blueprint.errorhandler(ValidationError)
def invalid_request(error: Exception):
    return jsonify({"error": str(error), "code": "invalid_request"}), 400


@research_blueprint.errorhandler(CouchDBNotFound)
def not_found(error: CouchDBNotFound):
    return jsonify({"error": str(error), "code": "not_found"}), 404


@research_blueprint.errorhandler(CouchDBConflict)
def conflict(error: CouchDBConflict):
    return jsonify({"error": str(error), "code": "revision_conflict"}), 409


@research_blueprint.post("/projects")
def create_project():
    value = _payload()
    project = _service().create_project(
        market=value["market"],
        cycle=value["cycle"],
        methodology_id=value["methodology_id"],
        schema_id=value["schema_id"],
        actor=_actor(),
    )
    return jsonify(project.to_couchdb()), 201


@research_blueprint.post("/projects/<path:project_id>/runs")
def start_run(project_id: str):
    service = _service()
    project = ResearchProject.model_validate(service.research.get(project_id))
    value = _payload()
    run = service.start_run(
        project,
        methodology_version=value["methodology_version"],
        code_revision=value["code_revision"],
        model_metadata=value.get("model_metadata"),
        policy_id=value.get("policy_id"),
        actor=_actor(),
    )
    return jsonify(run.to_couchdb()), 201


@research_blueprint.post("/runs/<path:run_id>/targets")
def add_targets(run_id: str):
    service = _service()
    run = ResearchRun.model_validate(service.research.get(run_id))
    project = ResearchProject.model_validate(
        service.research.get(run.project_id)
    )
    value = _payload()
    targets = service.add_targets(
        project,
        run,
        value["targets"],
        actor=_actor(),
    )
    return jsonify({"targets": [item.to_couchdb() for item in targets]}), 201


@research_blueprint.post("/runs/<path:run_id>/evidence")
def record_evidence(run_id: str):
    value = _payload()
    evidence = _service().record_evidence(
        project_id=value["project_id"],
        run_id=run_id,
        target_id=value["target_id"],
        vendor_id=value["vendor_id"],
        schema_id=value["schema_id"],
        criterion_id=value["criterion_id"],
        source_url=value["source_url"],
        excerpt=value["excerpt"],
        source_text=value["source_text"],
        collection_status=value.get("collection_status", "collected"),
        source_id=value.get("source_id"),
        snapshot_id=value.get("snapshot_id"),
        actor=_actor(),
    )
    return jsonify(evidence.to_couchdb()), 201


@research_blueprint.post("/runs/<path:run_id>/proposals")
def propose_score(run_id: str):
    value = _payload()
    proposal = _service().propose_score(
        project_id=value["project_id"],
        run_id=run_id,
        vendor_id=value["vendor_id"],
        schema_id=value["schema_id"],
        criterion_id=value["criterion_id"],
        score=value["score"],
        confidence=value["confidence"],
        evidence_ids=value["evidence_ids"],
        rationale=value["rationale"],
        algorithm_version=value["algorithm_version"],
        actor=_actor(),
    )
    return jsonify(proposal.to_couchdb()), 201


@research_blueprint.post("/proposals/<path:proposal_id>/decisions")
def review_proposal(proposal_id: str):
    service = _service()
    proposal = ScoreProposal.model_validate(service.research.get(proposal_id))
    value = _payload()
    decision = service.review(
        proposal,
        reviewer=_actor(),
        action=value["action"],
        comment=value["comment"],
        accepted_score=value.get("accepted_score"),
    )
    return jsonify(decision.to_couchdb()), 201


@research_blueprint.put("/runs/<path:run_id>/checkpoints/<stage>")
def save_checkpoint(run_id: str, stage: str):
    value = _payload()
    checkpoint = _service().save_checkpoint(
        project_id=value["project_id"],
        run_id=run_id,
        stage=stage,
        cursor=value.get("cursor"),
        completed_target_ids=value.get("completed_target_ids", []),
        state=value.get("state"),
        expected_revision=request.headers.get("If-Match"),
        actor=_actor(),
    )
    return jsonify(checkpoint.to_couchdb()), 200


@research_blueprint.get("/runs/<path:run_id>/resume")
def resume_run(run_id: str):
    stage = request.args.get("stage", "targeting")
    return jsonify(_service().resume(run_id, stage))


@research_blueprint.post("/decisions/<path:decision_id>/publish")
def publish_decision(decision_id: str):
    service = _service()
    decision = ReviewDecision.model_validate(
        service.research.get(decision_id)
    )
    proposal = ScoreProposal.model_validate(
        service.research.get(decision.proposal_id)
    )
    project = ResearchProject.model_validate(
        service.research.get(decision.project_id)
    )
    result = service.publish(
        project,
        proposal,
        decision,
        actor=_actor(),
    )
    return jsonify(result), 201
