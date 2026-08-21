"""Idempotently import JSON inventory manifests into ``gartner_ops``."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient, CouchDBError
from gartner_app.domain.models import MigrationManifest


def iter_batches(
    source: Path,
    batch_size: int,
) -> Iterator[list[dict[str, Any]]]:
    batch: list[dict[str, Any]] = []
    with source.open("r", encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                document = MigrationManifest.model_validate(raw).to_couchdb()
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(
                    f"invalid manifest at line {line_number}: {exc}"
                ) from exc
            batch.append(document)
            if len(batch) == batch_size:
                yield batch
                batch = []
    if batch:
        yield batch


def upsert_batch(
    client: CouchDBClient,
    database: str,
    documents: list[dict[str, Any]],
) -> tuple[int, int]:
    existing = client.get_documents(
        database,
        [document["_id"] for document in documents],
    )
    for document in documents:
        prior = existing.get(document["_id"])
        if prior is not None:
            document["_rev"] = prior["_rev"]

    results = client.bulk_docs(database, documents)
    failures = [result for result in results if result.get("error")]
    if failures:
        sample = json.dumps(failures[:5], ensure_ascii=False)
        raise CouchDBError(
            f"_bulk_docs returned {len(failures)} failures; sample: {sample}"
        )
    return len(documents) - len(existing), len(existing)


def import_manifests(
    source: Path,
    *,
    batch_size: int = 200,
    dry_run: bool = False,
) -> dict[str, int | str | bool]:
    if not 1 <= batch_size <= 500:
        raise ValueError("batch size must be between 1 and 500")
    settings = Settings.from_env()
    username, password = settings.require_gateway_credentials()
    client = CouchDBClient(
        settings.couchdb_url,
        username=username,
        password=password,
        connect_timeout=settings.connect_timeout_seconds,
        read_timeout=settings.read_timeout_seconds,
    )

    created = 0
    updated = 0
    batches = 0
    validated = 0
    for batch in iter_batches(source, batch_size):
        batches += 1
        validated += len(batch)
        if dry_run:
            continue
        batch_created, batch_updated = upsert_batch(
            client,
            settings.couchdb_ops_db,
            batch,
        )
        created += batch_created
        updated += batch_updated

    return {
        "source": str(source),
        "dry_run": dry_run,
        "validated": validated,
        "batches": batches,
        "created": created,
        "updated": updated,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("migration/manifests/json_inventory.jsonl"),
    )
    parser.add_argument("--batch-size", type=int, default=200)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = import_manifests(
        args.source.resolve(),
        batch_size=args.batch_size,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
