"""Validate, plan, and idempotently import approved canonical JSON sources."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient, CouchDBError
from gartner_app.migration.transforms import build_canonical_documents


def batches(documents: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [
        documents[offset : offset + size]
        for offset in range(0, len(documents), size)
    ]


def _without_revision(document: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in document.items() if key != "_rev"}


def upsert_canonical_batch(
    client: CouchDBClient,
    database: str,
    documents: list[dict[str, Any]],
) -> tuple[int, int, int, int]:
    existing = client.get_documents(
        database,
        [document["_id"] for document in documents],
    )
    changed: list[dict[str, Any]] = []
    created = 0
    updated = 0
    skipped = 0
    protected = 0
    for document in documents:
        prior = existing.get(document["_id"])
        if prior is None:
            created += 1
            changed.append(document)
        elif _without_revision(prior) == document:
            skipped += 1
        elif prior.get("updated_by") != "migration:canonical:v1":
            protected += 1
        else:
            document["_rev"] = prior["_rev"]
            updated += 1
            changed.append(document)

    if not changed:
        return created, updated, skipped, protected
    results = client.bulk_docs(database, changed)
    failures = [result for result in results if result.get("error")]
    if failures:
        sample = json.dumps(failures[:5], ensure_ascii=False)
        raise CouchDBError(
            f"_bulk_docs returned {len(failures)} failures; sample: {sample}"
        )
    return created, updated, skipped, protected


def import_canonical(
    root: Path,
    manifest_path: Path,
    *,
    batch_size: int = 200,
    dry_run: bool = False,
) -> dict[str, Any]:
    if not 1 <= batch_size <= 500:
        raise ValueError("batch size must be between 1 and 500")
    grouped = build_canonical_documents(root.resolve(), manifest_path.resolve())
    summary: dict[str, Any] = {"dry_run": dry_run, "databases": {}}

    client = None
    settings = None
    if not dry_run:
        settings = Settings.from_env()
        username, password = settings.require_gateway_credentials()
        client = CouchDBClient(
            settings.couchdb_url,
            username=username,
            password=password,
            connect_timeout=settings.connect_timeout_seconds,
            read_timeout=settings.read_timeout_seconds,
        )
    database_names = {
        "core": settings.couchdb_core_db if settings else "gartner_core",
        "research": (
            settings.couchdb_research_db if settings else "gartner_research"
        ),
        "archive": (
            settings.couchdb_archive_db if settings else "gartner_archive"
        ),
    }

    for database_role, documents in sorted(grouped.items()):
        created = 0
        updated = 0
        skipped = 0
        protected = 0
        for batch in batches(documents, batch_size):
            if client is not None:
                batch_created, batch_updated, batch_skipped, batch_protected = (
                    upsert_canonical_batch(
                    client,
                    database_names[database_role],
                    batch,
                    )
                )
                created += batch_created
                updated += batch_updated
                skipped += batch_skipped
                protected += batch_protected
        summary["databases"][database_role] = {
            "database": database_names[database_role],
            "documents": len(documents),
            "batches": len(batches(documents, batch_size)),
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "protected": protected,
            "document_types": dict(
                sorted(Counter(doc["doc_type"] for doc in documents).items())
            ),
        }
    summary["documents"] = sum(
        item["documents"] for item in summary["databases"].values()
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("migration/canonical_sources.json"),
    )
    parser.add_argument("--batch-size", type=int, default=200)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = (
        args.manifest.resolve()
        if args.manifest.is_absolute()
        else (root / args.manifest).resolve()
    )
    result = import_canonical(
        root,
        manifest,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
