"""Interactively store local credentials and bootstrap CouchDB.

Secrets are entered in the local terminal, never echoed, and written only to
the repository's ignored ``.env`` file.
"""

from __future__ import annotations

import argparse
import getpass
import os
import secrets
from pathlib import Path

from dotenv import dotenv_values, set_key

from gartner_app.config import Settings
from gartner_app.couchdb.bootstrap import bootstrap


def _required_secret(prompt: str) -> str:
    value = getpass.getpass(prompt)
    if not value:
        raise ValueError("a non-empty password is required")
    return value


def configure_and_bootstrap(env_file: Path) -> dict[str, object]:
    values = dotenv_values(env_file)
    admin_username = values.get("COUCHDB_ADMIN_USERNAME") or "admin"
    gateway_username = values.get("COUCHDB_USERNAME") or "gartner_gateway"
    admin_password = _required_secret(
        f"CouchDB password for {admin_username}: "
    )
    gateway_password = (
        values.get("COUCHDB_PASSWORD") or secrets.token_urlsafe(32)
    )

    updates = {
        "COUCHDB_ADMIN_USERNAME": admin_username,
        "COUCHDB_ADMIN_PASSWORD": admin_password,
        "COUCHDB_USERNAME": gateway_username,
        "COUCHDB_PASSWORD": gateway_password,
    }
    for key, value in updates.items():
        set_key(str(env_file), key, value, quote_mode="always")
        os.environ[key] = value

    return bootstrap(Settings.from_env(dotenv=False))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(".env"),
    )
    args = parser.parse_args()
    env_file = args.env_file.resolve()
    if not env_file.exists():
        raise FileNotFoundError(
            f"{env_file} does not exist; copy .env.example first"
        )

    result = configure_and_bootstrap(env_file)
    print()
    print(f"CouchDB {result['couchdb_version']} bootstrap complete.")
    print(f"Created databases: {result['created_databases']}")
    print(f"Gateway user: {result['gateway_user']}")
    print(f"Indexes checked: {len(result['indexes'])}")
    print("Secrets were stored only in the ignored .env file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
