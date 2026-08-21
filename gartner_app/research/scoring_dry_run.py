"""Verify snapshot-backed strict scoring without writing canonical JSON files."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from _revalidate_precyber_scoring import rescore_subpillar

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient
from gartner_app.domain.research import ResearchPolicy
from gartner_app.repositories.research import ResearchRepository
from gartner_app.research.checkpoints import ResearchCheckpointStore
from gartner_app.research.lineage import LegacyCacheLineageSink
from gartner_app.research.scoring import LegacyScoreProposalSink
from gartner_app.services.research_workflow import ResearchWorkflowService

ROOT = Path(__file__).resolve().parents[2]
VENDOR_FILE = ROOT / "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"
SCHEMA_FILE = ROOT / "Preemptive_Cybersecurity_Schema_v2.json"
CACHE_DIR = ROOT / "research" / "cache" / "pages_precyber"


def _cache_path(url: str) -> Path:
    digest = hashlib.sha1(
        url.encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def _select_vendor(vendors: list[dict]) -> dict:
    def cached_excerpt_count(vendor: dict) -> int:
        urls = {
            str(item.get("url"))
            for block in (vendor.get("sub_pillar_evidence") or {}).values()
            if isinstance(block, dict)
            for item in block.get("excerpts", [])
            if isinstance(item, dict) and item.get("url")
        }
        return sum(_cache_path(url).exists() for url in urls)

    return max(vendors, key=cached_excerpt_count)


def _complete(
    repository: ResearchRepository,
    document_id: str,
    *,
    actor: str,
) -> None:
    document = repository.get(document_id)
    repository.replace(
        document_id,
        {
            "status": "completed",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": actor,
        },
        expected_revision=document["_rev"],
    )


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
    workflow = ResearchWorkflowService(repository)
    actor = "verification:strict-scoring-dry-run"
    policy = ResearchPolicy.model_validate(
        repository.get("research_policy:precyber-public-web:1.0")
    )
    cycle = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    project = workflow.create_project(
        market="verification_precyber_scoring",
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
        model_metadata={"mode": "proposal-only-verification"},
        actor=actor,
    )

    raw = json.loads(VENDOR_FILE.read_text(encoding="utf-8"))
    vendors = raw if isinstance(raw, list) else raw["vendors"]
    vendor = _select_vendor(vendors)
    vendor_name = str(vendor.get("vendor") or "Unknown")
    evidence_map = vendor.get("sub_pillar_evidence") or {}
    original_scores = (
        vendor.get("sub_pillar_scores_v2_researched")
        or vendor.get("sub_pillar_scores_current")
        or {}
    )
    expected = set(vendor.get("expected_coverage") or [])
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    definitions = schema["preemptive_cybersecurity_taxonomy_v2.0"][
        "sub_pillars"
    ]

    lineage = LegacyCacheLineageSink(
        workflow,
        project_id=project.id,
        run_id=research_run.id,
        actor=actor,
    )
    imported_urls: set[str] = set()
    for block in evidence_map.values():
        if not isinstance(block, dict):
            continue
        for item in block.get("excerpts", []):
            if not isinstance(item, dict) or not item.get("url"):
                continue
            url = str(item["url"])
            path = _cache_path(url)
            if path.exists() and url not in imported_urls:
                lineage.capture_cache_file(
                    path,
                    vendor_id=f"vendor:verification-{vendor_name.lower()}",
                )
                imported_urls.add(url)

    scoring = LegacyScoreProposalSink(
        workflow,
        project_id=project.id,
        run_id=research_run.id,
        actor=actor,
    )
    created = 0
    skipped = 0
    zero_evidence = 0
    idempotent_replays = 0
    for criterion_id, definition in definitions.items():
        record = rescore_subpillar(
            sid=criterion_id,
            sp_def=definition,
            evidence_block=evidence_map.get(criterion_id),
            in_expected_coverage=criterion_id in expected,
            original_score=float(
                original_scores.get(criterion_id, 0.0) or 0.0
            ),
        )
        proposal = scoring.capture(
            vendor_name=vendor_name,
            schema_id=project.schema_id,
            criterion_id=criterion_id,
            score_record=record,
            evidence_block=evidence_map.get(criterion_id),
            algorithm_version="strict-v2.3",
        )
        if proposal is None:
            skipped += 1
        else:
            created += 1
            if not proposal.evidence_ids:
                zero_evidence += 1
            replay = scoring.capture(
                vendor_name=vendor_name,
                schema_id=project.schema_id,
                criterion_id=criterion_id,
                score_record=record,
                evidence_block=evidence_map.get(criterion_id),
                algorithm_version="strict-v2.3",
            )
            if replay is not None and replay.id == proposal.id:
                idempotent_replays += 1

    checkpoints = ResearchCheckpointStore(
        workflow,
        project_id=project.id,
        run_id=research_run.id,
        stage="scoring",
        actor=actor,
    )
    progress = {
        "completed_batches": [1],
        "completed_vendors": [vendor_name],
    }
    checkpoints.save(progress)
    resumed = checkpoints.load()
    _complete(repository, research_run.id, actor=actor)
    _complete(repository, project.id, actor=actor)
    return {
        "project_id": project.id,
        "run_id": research_run.id,
        "vendor": vendor_name,
        "cache_sources_imported": len(imported_urls),
        "proposals_created": created,
        "proposals_skipped_missing_snapshot": skipped,
        "zero_evidence_proposals": zero_evidence,
        "idempotent_proposal_replays": idempotent_replays,
        "checkpoint_resumed": resumed == progress,
        "canonical_json_written": False,
        "final_run_status": repository.get(research_run.id)["status"],
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
            f"Scoring run {result['run_id']} created "
            f"{result['proposals_created']} proposals"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
