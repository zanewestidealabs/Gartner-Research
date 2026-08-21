"""Idempotently create local databases, security objects, and Mango indexes."""

from __future__ import annotations

import argparse
import json

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient, CouchDBNotFound
from gartner_app.couchdb.indexes import (
    CORE_INDEXES,
    OPS_INDEXES,
    RESEARCH_INDEXES,
)

SYSTEM_DATABASES = ("_users", "_replicator", "_global_changes")


def _security(gateway_username: str) -> dict[str, object]:
    return {
        "admins": {"names": [], "roles": ["gartner_admin"]},
        "members": {
            "names": [gateway_username],
            "roles": [
                "gartner_reader",
                "gartner_writer",
                "gartner_researcher",
            ],
        },
    }


def _ensure_gateway_user(
    client: CouchDBClient,
    username: str,
    password: str,
) -> str:
    user_id = f"org.couchdb.user:{username}"
    document = {
        "_id": user_id,
        "name": username,
        "password": password,
        "roles": [
            "gartner_reader",
            "gartner_writer",
            "gartner_researcher",
        ],
        "type": "user",
    }
    try:
        existing = client.get_document("_users", user_id)
    except CouchDBNotFound:
        pass
    else:
        document["_rev"] = existing["_rev"]
    client.put_document("_users", user_id, document)
    return user_id


def bootstrap(settings: Settings) -> dict[str, object]:
    admin_username, admin_password = settings.require_admin_credentials()
    gateway_username, gateway_password = settings.require_gateway_credentials()
    client = CouchDBClient(
        settings.couchdb_url,
        username=admin_username,
        password=admin_password,
        connect_timeout=settings.connect_timeout_seconds,
        read_timeout=settings.read_timeout_seconds,
    )

    server = client.ping()
    created_databases: list[str] = []
    for database in (*SYSTEM_DATABASES, *settings.database_names):
        if client.ensure_database(database):
            created_databases.append(database)

    _ensure_gateway_user(client, gateway_username, gateway_password)
    security = _security(gateway_username)
    for database in settings.database_names:
        client.set_security(database, security)

    index_results: list[dict[str, object]] = []
    index_sets = {
        settings.couchdb_core_db: CORE_INDEXES,
        settings.couchdb_research_db: RESEARCH_INDEXES,
        settings.couchdb_ops_db: OPS_INDEXES,
        settings.couchdb_archive_db: (),
    }
    for database, indexes in index_sets.items():
        for definition in indexes:
            result = client.create_index(database, definition)
            index_results.append(
                {
                    "database": database,
                    "name": definition["name"],
                    "result": result.get("result"),
                }
            )

    return {
        "couchdb_version": server.get("version"),
        "created_databases": created_databases,
        "gateway_user": gateway_username,
        "indexes": index_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="print the bootstrap summary as JSON",
    )
    args = parser.parse_args()
    result = bootstrap(Settings.from_env())
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"CouchDB {result['couchdb_version']} bootstrapped")
        print(f"Created databases: {result['created_databases']}")
        print(f"Indexes checked: {len(result['indexes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
