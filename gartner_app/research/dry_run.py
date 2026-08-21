"""Exercise stop, resume, review, and publish with three verification vendors."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient
from gartner_app.repositories.research import ResearchRepository
from gartner_app.services.research_workflow import ResearchWorkflowService

VENDORS = (
    ("alpha", 2.25, "accept", None),
    ("bravo", 3.0, "edit", 2.75),
    ("charlie", 1.5, "accept", None),
)


def _git_revision() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return "uncommitted"
    return result.stdout.strip() or "uncommitted"


def run(settings: Settings) -> dict[str, object]:
    username, password = settings.require_gateway_credentials()
    client = CouchDBClient(
        settings.couchdb_url,
        username=username,
        password=password,
        connect_timeout=settings.connect_timeout_seconds,
        read_timeout=settings.read_timeout_seconds,
    )
    repository = ResearchRepository(client, settings.couchdb_research_db)
    workflow = ResearchWorkflowService(
        repository,
        core_client=client,
        core_database=settings.couchdb_core_db,
    )
    actor = "verification:research-dry-run"
    recovered_shells = 0
    shells = repository.find(
        {
            "selector": {
                "doc_type": {"$eq": "research_project"},
                "market": {"$eq": "verification_precyber"},
                "methodology_id": {"$eq": "precyber-research-standard"},
                "status": {"$eq": "active"},
            },
            "limit": 100,
        }
    ).get("docs", [])
    for shell in shells:
        runs = repository.find(
            {
                "selector": {
                    "doc_type": {"$eq": "research_run"},
                    "project_id": {"$eq": shell["_id"]},
                },
                "limit": 1,
            }
        ).get("docs", [])
        if not runs:
            repository.replace(
                shell["_id"],
                {
                    "status": "failed",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "updated_by": actor,
                    "failure_reason": "verification stopped before run creation",
                },
                expected_revision=shell["_rev"],
            )
            recovered_shells += 1
            continue
        for previous_run in runs:
            if previous_run.get("status") != "running":
                continue
            decisions = repository.find(
                {
                    "selector": {
                        "doc_type": {"$eq": "review_decision"},
                        "run_id": {"$eq": previous_run["_id"]},
                    },
                    "limit": 100,
                }
            ).get("docs", [])
            final_status = "completed" if len(decisions) >= 3 else "failed"
            repository.replace(
                previous_run["_id"],
                {
                    "status": final_status,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "updated_by": actor,
                    "recovered_by": "verification lifecycle repair",
                },
                expected_revision=previous_run["_rev"],
            )
            repository.replace(
                shell["_id"],
                {
                    "status": final_status,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "updated_by": actor,
                },
                expected_revision=shell["_rev"],
            )
            recovered_shells += 1
    cycle = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    project = workflow.create_project(
        market="verification_precyber",
        cycle=cycle,
        methodology_id="precyber-research-standard",
        schema_id="schema:precyber:2",
        actor=actor,
    )
    run_document = workflow.start_run(
        project,
        methodology_version="1.0",
        code_revision=_git_revision(),
        model_metadata={"mode": "deterministic-verification"},
        actor=actor,
    )
    targets = workflow.add_targets(
        project,
        run_document,
        [
            {
                "vendor_id": f"vendor:verification-{name}",
                "canonical_url": f"https://example.test/{name}/capability",
                "criterion_ids": ["EXM-04"],
            }
            for name, *_ in VENDORS
        ],
        actor=actor,
    )

    initial_checkpoint = workflow.save_checkpoint(
        project_id=project.id,
        run_id=run_document.id,
        stage="rendering",
        cursor=targets[0].id,
        completed_target_ids=[targets[0].id],
        state={"reason": "intentional stop/resume boundary"},
        actor=actor,
    )
    resumed = workflow.resume(run_document.id, "rendering")
    stored_checkpoint = repository.get(initial_checkpoint.id)
    workflow.save_checkpoint(
        project_id=project.id,
        run_id=run_document.id,
        stage="rendering",
        cursor=None,
        completed_target_ids=[target.id for target in targets],
        state={"resumed": True},
        expected_revision=stored_checkpoint["_rev"],
        actor=actor,
    )

    publications: list[str] = []
    decisions: list[str] = []
    for target, (name, score, action, adjusted_score) in zip(
        targets, VENDORS, strict=True
    ):
        evidence = workflow.record_evidence(
            project_id=project.id,
            run_id=run_document.id,
            target_id=target.id,
            vendor_id=target.vendor_id,
            schema_id=project.schema_id,
            criterion_id="EXM-04",
            source_url=target.canonical_url,
            excerpt=(
                f"Verification vendor {name} documents a concrete, "
                "auditable capability for the selected criterion."
            ),
            source_text=(
                f"Rendered verification source for {name}; deterministic "
                f"cycle {cycle}."
            ),
            actor=actor,
        )
        proposal = workflow.propose_score(
            project_id=project.id,
            run_id=run_document.id,
            vendor_id=target.vendor_id,
            schema_id=project.schema_id,
            criterion_id="EXM-04",
            score=score,
            confidence="medium",
            evidence_ids=[evidence.id],
            rationale=(
                "Verification proposal derived from one immutable public "
                "evidence excerpt."
            ),
            algorithm_version="strict-v2.3-verification",
            actor=actor,
        )
        decision = workflow.review(
            proposal,
            reviewer=actor,
            action=action,
            accepted_score=adjusted_score,
            comment="Reviewed during CouchDB workflow verification.",
        )
        result = workflow.publish(
            project,
            proposal,
            decision,
            actor=actor,
        )
        publications.append(result["id"])
        decisions.append(decision.id)

    for target in targets:
        stored_target = repository.get(target.id)
        repository.replace(
            target.id,
            {
                "status": "complete",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": actor,
            },
            expected_revision=stored_target["_rev"],
        )
    stored_run = repository.get(run_document.id)
    repository.replace(
        run_document.id,
        {
            "status": "completed",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": actor,
        },
        expected_revision=stored_run["_rev"],
    )
    stored_project = repository.get(project.id)
    repository.replace(
        project.id,
        {
            "status": "completed",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": actor,
        },
        expected_revision=stored_project["_rev"],
    )

    return {
        "project_id": project.id,
        "run_id": run_document.id,
        "target_count": len(targets),
        "resume_checkpoint_found": resumed["checkpoint"] is not None,
        "pending_at_resume": len(resumed["pending_targets"]),
        "recovered_incomplete_project_shells": recovered_shells,
        "decision_ids": decisions,
        "publication_ids": publications,
        "final_run_status": repository.get(run_document.id)["status"],
        "final_target_statuses": sorted(
            {repository.get(target.id)["status"] for target in targets}
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run(Settings.from_env())
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"Research dry run {result['run_id']} published "
            f"{len(result['publication_ids'])} reviewed scores"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
