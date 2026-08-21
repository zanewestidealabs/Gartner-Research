"""Report non-secret CouchDB capacity and maintenance status."""

from __future__ import annotations

import json

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient


def main() -> int:
    settings = Settings.from_env()
    username, password = settings.require_admin_credentials()
    client = CouchDBClient(
        settings.couchdb_url,
        username=username,
        password=password,
        connect_timeout=settings.connect_timeout_seconds,
        read_timeout=settings.read_timeout_seconds,
    )
    databases = []
    for name in settings.database_names:
        info = client.database_info(name)
        sizes = info.get("sizes", {})
        databases.append(
            {
                "name": name,
                "documents": info.get("doc_count", 0),
                "deleted_documents": info.get("doc_del_count", 0),
                "disk_bytes": sizes.get("file", info.get("disk_size", 0)),
                "active_bytes": sizes.get("active", info.get("data_size", 0)),
                "external_bytes": sizes.get("external", 0),
                "compact_running": info.get("compact_running", False),
            }
        )
    print(
        json.dumps(
            {
                "version": client.ping().get("version"),
                "databases": databases,
                "active_tasks": client.active_tasks(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
