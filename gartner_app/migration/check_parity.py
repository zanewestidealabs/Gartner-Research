"""Compare canonical JSON source content with reconstructed CouchDB content."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient
from gartner_app.repositories.datasets import (
    CouchDatasetRepository,
    JsonDatasetRepository,
)
from gartner_app.repositories.json_backend import LegacyJsonRepository

SUPPORTED_KINDS = {
    "schema",
    "framework",
    "report_definition",
    "vendor_score",
    "vendor_pricing",
    "mq_score",
    "market_insight",
    "analyst_take",
    "innovation_profile",
}


def semantic_hash(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def check_parity(
    root: Path,
    manifest_path: Path,
    settings: Settings | None = None,
) -> dict[str, Any]:
    settings = settings or Settings.from_env()
    username, password = settings.require_gateway_credentials()
    json_repository = JsonDatasetRepository(LegacyJsonRepository(root))
    couch_repository = CouchDatasetRepository(
        CouchDBClient(
            settings.couchdb_url,
            username=username,
            password=password,
            connect_timeout=settings.connect_timeout_seconds,
            read_timeout=settings.read_timeout_seconds,
        ),
        settings.couchdb_core_db,
        manifest_path,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []
    for source in manifest["sources"]:
        if source["kind"] not in SUPPORTED_KINDS:
            continue
        path = source["path"]
        json_value = json_repository.read_document(path)
        couch_value = couch_repository.read_document(path)
        json_hash = semantic_hash(json_value)
        couch_hash = semantic_hash(couch_value)
        results.append(
            {
                "path": path,
                "kind": source["kind"],
                "match": json_hash == couch_hash,
                "json_sha256": json_hash,
                "couchdb_sha256": couch_hash,
            }
        )
    mismatches = [result for result in results if not result["match"]]
    return {
        "checked": len(results),
        "matched": len(results) - len(mismatches),
        "mismatched": len(mismatches),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("migration/canonical_sources.json"),
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="include per-source hashes in output",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = (
        args.manifest.resolve()
        if args.manifest.is_absolute()
        else (root / args.manifest).resolve()
    )
    result = check_parity(root, manifest_path)
    if not args.details:
        result.pop("results")
    print(json.dumps(result, indent=2))
    return 1 if result["mismatched"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
