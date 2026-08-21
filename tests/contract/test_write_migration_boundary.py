from __future__ import annotations

import json
from pathlib import Path

import app as app_module
from gartner_app.couchdb.client import CouchDBConflict
from gartner_app.repositories.datasets import MigrationWriteBlocked
from gartner_app.repositories.datasets import RevisionPreconditionRequired


class BlockingRepository:
    def __init__(self, value: dict) -> None:
        self.value = value

    def read_document(self, source_path: str) -> dict:
        return json.loads(json.dumps(self.value))

    def write_document(
        self,
        source_path: str,
        value: dict,
        *,
        expected_revision: str | None = None,
    ) -> dict:
        raise MigrationWriteBlocked("compare mode is read-only")


class ConflictRepository(BlockingRepository):
    def write_document(
        self,
        source_path: str,
        value: dict,
        *,
        expected_revision: str | None = None,
    ) -> dict:
        raise CouchDBConflict(409, "PUT", "/core/doc", "conflict")


class PreconditionRepository(BlockingRepository):
    def write_document(
        self,
        source_path: str,
        value: dict,
        *,
        expected_revision: str | None = None,
    ) -> dict:
        raise RevisionPreconditionRequired("If-Match required")


def _profile_payload() -> dict:
    root = Path(app_module.__file__).resolve().parent
    data = json.loads((root / "innovation_profiles.json").read_text(encoding="utf-8"))
    return data["profiles"][0]


def test_compare_mode_write_is_rejected(monkeypatch) -> None:
    profile = _profile_payload()
    monkeypatch.setattr(
        app_module,
        "dataset_repository",
        BlockingRepository({"profiles": [profile]}),
    )
    app_module.app.config.update(TESTING=True)

    response = app_module.app.test_client().post(
        "/api/innovation-profiles",
        json=profile,
    )

    assert response.status_code == 503
    assert response.get_json()["code"] == "compare_mode_read_only"


def test_revision_conflict_maps_to_http_409(monkeypatch) -> None:
    profile = _profile_payload()
    monkeypatch.setattr(
        app_module,
        "dataset_repository",
        ConflictRepository({"profiles": [profile]}),
    )
    app_module.app.config.update(TESTING=True)

    response = app_module.app.test_client().post(
        "/api/innovation-profiles",
        json=profile,
    )

    assert response.status_code == 409
    assert response.get_json()["code"] == "revision_conflict"


def test_missing_if_match_maps_to_http_428(monkeypatch) -> None:
    profile = _profile_payload()
    monkeypatch.setattr(
        app_module,
        "dataset_repository",
        PreconditionRepository({"profiles": [profile]}),
    )
    app_module.app.config.update(TESTING=True)

    response = app_module.app.test_client().post(
        "/api/innovation-profiles",
        json=profile,
    )

    assert response.status_code == 428
    assert response.get_json()["code"] == "if_match_required"


def test_editable_get_returns_etag() -> None:
    app_module.app.config.update(TESTING=True)
    response = app_module.app.test_client().get(
        "/api/innovation-profiles?id=ai-product-attribution-transparency"
    )

    assert response.status_code == 200
    assert response.headers["ETag"].startswith('"')
