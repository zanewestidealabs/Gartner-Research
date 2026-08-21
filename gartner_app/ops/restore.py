"""Restore and verify a portable backup into isolated CouchDB databases."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient, CouchDBError

_SAFE_PREFIX = re.compile(r"^[a-z][a-z0-9_]{2,30}$")


def _semantic(document: dict[str, Any]) -> bytes:
    value = {key: item for key, item in document.items() if key != "_rev"}
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _load_documents(path: Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict) or not value.get("_id"):
                raise ValueError(
                    f"{path.name}:{line_number} is not a CouchDB document"
                )
            value.pop("_rev", None)
            documents.append(value)
    return documents


def restore_drill(
    settings: Settings,
    *,
    manifest_path: Path,
    prefix: str,
    keep: bool = False,
) -> dict[str, Any]:
    if not _SAFE_PREFIX.fullmatch(prefix):
        raise ValueError("prefix must match ^[a-z][a-z0-9_]{2,30}$")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    admin_username, admin_password = settings.require_admin_credentials()
    gateway_username, _ = settings.require_gateway_credentials()
    client = CouchDBClient(
        settings.couchdb_url,
        username=admin_username,
        password=admin_password,
        connect_timeout=settings.connect_timeout_seconds,
        read_timeout=settings.read_timeout_seconds,
    )
    restored: list[dict[str, Any]] = []
    created_databases: list[str] = []
    try:
        for entry in manifest["databases"]:
            target = f"{prefix}_{entry['name']}"
            client.validate_database_name(target)
            if not client.ensure_database(target):
                raise CouchDBError(f"restore target already exists: {target}")
            created_databases.append(target)
            client.set_security(
                target,
                {
                    "admins": {"names": [], "roles": ["gartner_admin"]},
                    "members": {
                        "names": [gateway_username],
                        "roles": [
                            "gartner_reader",
                            "gartner_writer",
                            "gartner_researcher",
                        ],
                    },
                },
            )
            documents = _load_documents(
                manifest_path.parent / entry["file"]
            )
            for start in range(0, len(documents), 200):
                results = client.bulk_docs(
                    target,
                    documents[start : start + 200],
                )
                failures = [
                    item for item in results if item.get("error")
                ]
                if failures:
                    raise CouchDBError(
                        f"restore failures in {target}: {failures[:3]}"
                    )
            restored_documents = client.all_documents(target)
            semantic_hash = hashlib.sha256()
            for document in restored_documents:
                semantic_hash.update(_semantic(document))
            actual_hash = semantic_hash.hexdigest()
            expected_hash = entry["semantic_sha256"]
            if actual_hash != expected_hash:
                raise CouchDBError(
                    f"semantic hash mismatch for {target}: "
                    f"{actual_hash} != {expected_hash}"
                )
            restored.append(
                {
                    "source": entry["name"],
                    "target": target,
                    "documents": len(restored_documents),
                    "semantic_sha256": actual_hash,
                    "matched": True,
                }
            )
    finally:
        if not keep:
            for database in reversed(created_databases):
                client.delete_database(database)
    return {
        "backup_id": manifest["backup_id"],
        "kept": keep,
        "databases": restored,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--prefix", default="restore_drill")
    parser.add_argument("--keep", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = restore_drill(
        Settings.from_env(),
        manifest_path=args.manifest,
        prefix=args.prefix,
        keep=args.keep,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"Restore drill for {result['backup_id']} verified "
            f"{len(result['databases'])} databases"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
