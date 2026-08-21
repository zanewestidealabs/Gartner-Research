"""Non-secret application and CouchDB health endpoints."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient

health_blueprint = Blueprint("health", __name__)


def _couchdb_status(settings: Settings) -> dict[str, Any]:
    client = CouchDBClient(
        settings.couchdb_url,
        connect_timeout=settings.connect_timeout_seconds,
        read_timeout=min(settings.read_timeout_seconds, 5),
    )
    server = client.ping()
    return {
        "reachable": True,
        "version": server.get("version"),
    }


@health_blueprint.get("/api/health/live")
def live():
    return jsonify({"status": "ok"})


@health_blueprint.get("/api/health/ready")
def ready():
    settings = Settings.from_env()
    couchdb: dict[str, Any]
    try:
        couchdb = _couchdb_status(settings)
    except Exception as exc:
        couchdb = {
            "reachable": False,
            "error": type(exc).__name__,
        }

    couchdb_required = settings.data_backend in {"couchdb", "compare"}
    is_ready = not couchdb_required or couchdb["reachable"]
    status_code = 200 if is_ready else 503
    return (
        jsonify(
            {
                "status": "ready" if is_ready else "not_ready",
                "data_backend": settings.data_backend,
                "couchdb_required": couchdb_required,
                "couchdb": couchdb,
            }
        ),
        status_code,
    )
