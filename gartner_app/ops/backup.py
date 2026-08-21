"""Create a portable, checksummed CouchDB JSONL backup."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BACKUP_ROOT = ROOT / "backups" / "couchdb"


def _encoded(document: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            document,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def _semantic(document: dict[str, Any]) -> bytes:
    value = {key: item for key, item in document.items() if key != "_rev"}
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def backup(
    settings: Settings,
    *,
    output_root: Path = DEFAULT_BACKUP_ROOT,
) -> dict[str, Any]:
    admin_username, admin_password = settings.require_admin_credentials()
    client = CouchDBClient(
        settings.couchdb_url,
        username=admin_username,
        password=admin_password,
        connect_timeout=settings.connect_timeout_seconds,
        read_timeout=settings.read_timeout_seconds,
    )
    created_at = datetime.now(timezone.utc)
    backup_id = created_at.strftime("%Y%m%dT%H%M%SZ")
    destination = output_root / backup_id
    destination.mkdir(parents=True, exist_ok=False)
    databases: list[dict[str, Any]] = []
    for database in settings.database_names:
        documents = client.all_documents(database)
        path = destination / f"{database}.jsonl"
        file_hash = hashlib.sha256()
        semantic_hash = hashlib.sha256()
        with path.open("wb") as output:
            for document in documents:
                encoded = _encoded(document)
                output.write(encoded)
                file_hash.update(encoded)
                semantic_hash.update(_semantic(document))
        databases.append(
            {
                "name": database,
                "file": path.name,
                "documents": len(documents),
                "bytes": path.stat().st_size,
                "sha256": file_hash.hexdigest(),
                "semantic_sha256": semantic_hash.hexdigest(),
            }
        )

    manifest = {
        "backup_version": 1,
        "backup_id": backup_id,
        "created_at": created_at.isoformat(),
        "couchdb": {
            "version": client.ping().get("version"),
            "url": settings.couchdb_url,
        },
        "configuration": {
            "database_names": list(settings.database_names),
            "bind_expectation": "127.0.0.1",
            "source_controlled_indexes": "gartner_app/couchdb/indexes.py",
            "source_controlled_security": "gartner_app/couchdb/bootstrap.py",
            "secrets_included": False,
        },
        "databases": databases,
    }
    manifest_path = destination / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return {
        "backup_id": backup_id,
        "path": str(destination),
        "manifest": str(manifest_path),
        "databases": databases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_BACKUP_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = backup(Settings.from_env(), output_root=args.output_root)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Backup {result['backup_id']} written to {result['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
