"""Validated local configuration for JSON/CouchDB data access."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv

DataBackend = Literal["json", "couchdb", "compare"]


def _positive_float(name: str, default: float) -> float:
    raw = os.getenv(name, str(default))
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    data_backend: DataBackend
    couchdb_url: str
    couchdb_username: str | None
    couchdb_password: str | None
    couchdb_admin_username: str | None
    couchdb_admin_password: str | None
    couchdb_core_db: str
    couchdb_research_db: str
    couchdb_ops_db: str
    couchdb_archive_db: str
    connect_timeout_seconds: float
    read_timeout_seconds: float

    @classmethod
    def from_env(cls, *, dotenv: bool = True) -> "Settings":
        if dotenv:
            load_dotenv()

        backend = os.getenv("DATA_BACKEND", "json").strip().lower()
        if backend not in {"json", "couchdb", "compare"}:
            raise ValueError("DATA_BACKEND must be json, couchdb, or compare")

        url = os.getenv("COUCHDB_URL", "http://127.0.0.1:5984").rstrip("/")
        if not url.startswith(("http://", "https://")):
            raise ValueError("COUCHDB_URL must be an HTTP(S) URL")

        return cls(
            data_backend=backend,  # type: ignore[arg-type]
            couchdb_url=url,
            couchdb_username=os.getenv("COUCHDB_USERNAME") or None,
            couchdb_password=os.getenv("COUCHDB_PASSWORD") or None,
            couchdb_admin_username=os.getenv("COUCHDB_ADMIN_USERNAME") or None,
            couchdb_admin_password=os.getenv("COUCHDB_ADMIN_PASSWORD") or None,
            couchdb_core_db=os.getenv("COUCHDB_CORE_DB", "gartner_core"),
            couchdb_research_db=os.getenv(
                "COUCHDB_RESEARCH_DB", "gartner_research"
            ),
            couchdb_ops_db=os.getenv("COUCHDB_OPS_DB", "gartner_ops"),
            couchdb_archive_db=os.getenv(
                "COUCHDB_ARCHIVE_DB", "gartner_archive"
            ),
            connect_timeout_seconds=_positive_float(
                "COUCHDB_CONNECT_TIMEOUT_SECONDS", 3
            ),
            read_timeout_seconds=_positive_float(
                "COUCHDB_READ_TIMEOUT_SECONDS", 30
            ),
        )

    @property
    def database_names(self) -> tuple[str, str, str, str]:
        return (
            self.couchdb_core_db,
            self.couchdb_research_db,
            self.couchdb_ops_db,
            self.couchdb_archive_db,
        )

    def require_gateway_credentials(self) -> tuple[str, str]:
        if not self.couchdb_username or not self.couchdb_password:
            raise ValueError(
                "COUCHDB_USERNAME and COUCHDB_PASSWORD are required"
            )
        return self.couchdb_username, self.couchdb_password

    def require_admin_credentials(self) -> tuple[str, str]:
        if not self.couchdb_admin_username or not self.couchdb_admin_password:
            raise ValueError(
                "COUCHDB_ADMIN_USERNAME and COUCHDB_ADMIN_PASSWORD are required"
            )
        return self.couchdb_admin_username, self.couchdb_admin_password
