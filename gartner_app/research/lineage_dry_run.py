"""Verify append-only source lineage with real PreCyber cache records."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient, CouchDBNotFound
from gartner_app.domain.research import ResearchPolicy
from gartner_app.repositories.research import ResearchRepository
from gartner_app.research.lineage import LegacyCacheLineageSink
from gartner_app.services.research_workflow import ResearchWorkflowService

ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / "research" / "cache" / "pages_precyber"
SUCCESS_CACHE = CACHE_DIR / "00be3eafb796709d472de65ea90e2b2b8d68bf8f.json"
SECOND_CACHE = CACHE_DIR / "0151f4280dbf4b6c60db919d457fb367eb664f17.json"
FAILED_CACHE = CACHE_DIR / "0171b5cd56e3609618e8a16d517a8b55a48fc151.json"


def _complete(
    repository: ResearchRepository,
    document_id: str,
    *,
    status: str,
    actor: str,
) -> None:
    document = repository.get(document_id)
    repository.replace(
        document_id,
        {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": actor,
        },
        expected_revision=document["_rev"],
    )


def run(settings: Settings) -> dict[str, object]:
    for path in (SUCCESS_CACHE, SECOND_CACHE, FAILED_CACHE):
        if not path.exists():
            raise FileNotFoundError(path)
    username, password = settings.require_gateway_credentials()
    client = CouchDBClient(
        settings.couchdb_url,
        username=username,
        password=password,
        connect_timeout=settings.connect_timeout_seconds,
        read_timeout=settings.read_timeout_seconds,
    )
    repository = ResearchRepository(client, settings.couchdb_research_db)
    workflow = ResearchWorkflowService(repository)
    actor = "verification:lineage-dry-run"
    policy_id = "research_policy:precyber-public-web:1.0"
    try:
        policy = ResearchPolicy.model_validate(repository.get(policy_id))
    except CouchDBNotFound:
        policy = workflow.create_policy(
            name="precyber-public-web",
            version="1.0",
            actor=actor,
            min_useful_text=500,
            min_support_excerpt_length=80,
            max_concurrency=2,
            max_excerpts_per_criterion=5,
            bot_wall_patterns=[
                "access denied",
                "verify you are a human",
                "perimeterx",
            ],
        )

    cycle = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    project = workflow.create_project(
        market="verification_precyber_lineage",
        cycle=cycle,
        methodology_id="precyber-research-standard",
        schema_id="schema:precyber:2",
        actor=actor,
    )
    research_run = workflow.start_run(
        project,
        methodology_version="1.0",
        code_revision="uncommitted",
        policy_id=policy.id,
        model_metadata={"mode": "legacy-cache-lineage-verification"},
        actor=actor,
    )
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (SUCCESS_CACHE, SECOND_CACHE, FAILED_CACHE)
    ]
    targets = workflow.add_targets(
        project,
        research_run,
        [
            {
                "vendor_id": f"vendor:lineage-{index}",
                "canonical_url": record["url"],
                "criterion_ids": ["EXM-04"],
            }
            for index, record in enumerate(records, start=1)
        ],
        actor=actor,
    )
    sink = LegacyCacheLineageSink(
        workflow,
        project_id=project.id,
        run_id=research_run.id,
        actor=actor,
    )

    blocked_record = {
        **records[0],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ok": False,
        "text": "",
        "error": "bot_blocked",
        "render_engine": "playwright",
    }
    blocked = sink.capture(
        vendor_id=targets[0].vendor_id,
        target_id=targets[0].id,
        record=blocked_record,
        retrieval_method="playwright",
        attempt=1,
    )
    recovered = sink.capture(
        vendor_id=targets[0].vendor_id,
        target_id=targets[0].id,
        record=records[0],
        cache_path=SUCCESS_CACHE,
        retrieval_method="playwright",
        headed=True,
        attempt=2,
        previous_snapshot_id=blocked.id,
    )
    second = sink.capture_cache_file(
        SECOND_CACHE,
        vendor_id=targets[1].vendor_id,
        target_id=targets[1].id,
    )
    failed = sink.capture_cache_file(
        FAILED_CACHE,
        vendor_id=targets[2].vendor_id,
        target_id=targets[2].id,
    )
    evidence = workflow.record_evidence(
        project_id=project.id,
        run_id=research_run.id,
        target_id=targets[0].id,
        vendor_id=targets[0].vendor_id,
        schema_id=project.schema_id,
        criterion_id="EXM-04",
        source_url=records[0]["url"],
        source_id=recovered.source_id,
        snapshot_id=recovered.id,
        excerpt=records[0]["text"][:500],
        source_text=records[0]["text"],
        actor=actor,
    )

    _complete(repository, targets[0].id, status="complete", actor=actor)
    _complete(repository, targets[1].id, status="complete", actor=actor)
    _complete(repository, targets[2].id, status="blocked", actor=actor)
    _complete(repository, research_run.id, status="completed", actor=actor)
    _complete(repository, project.id, status="completed", actor=actor)
    return {
        "project_id": project.id,
        "run_id": research_run.id,
        "policy_id": policy.id,
        "snapshot_ids": [
            blocked.id,
            recovered.id,
            second.id,
            failed.id,
        ],
        "outcomes": [
            blocked.outcome,
            recovered.outcome,
            second.outcome,
            failed.outcome,
        ],
        "retry_previous_snapshot_id": recovered.previous_snapshot_id,
        "evidence_id": evidence.id,
        "evidence_snapshot_id": evidence.snapshot_id,
        "final_run_status": repository.get(research_run.id)["status"],
        "target_statuses": [
            repository.get(target.id)["status"] for target in targets
        ],
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
            f"Lineage run {result['run_id']} recorded "
            f"{len(result['snapshot_ids'])} snapshots"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
