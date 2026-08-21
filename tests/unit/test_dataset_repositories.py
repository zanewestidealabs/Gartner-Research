from __future__ import annotations

import json
from pathlib import Path

import pytest

from gartner_app.couchdb.client import CouchDBConflict
from gartner_app.repositories.datasets import (
    CompareDatasetRepository,
    CouchDatasetRepository,
    JsonDatasetRepository,
    RevisionPreconditionRequired,
)
from gartner_app.repositories.json_backend import LegacyJsonRepository


def test_json_dataset_repository_unwraps_vendors(tmp_path: Path) -> None:
    (tmp_path / "vendors.json").write_text(
        json.dumps({"vendors": [{"vendor": "Acme"}]}),
        encoding="utf-8",
    )
    repository = JsonDatasetRepository(LegacyJsonRepository(tmp_path))

    assert repository.read_vendors("vendors.json") == [{"vendor": "Acme"}]


def test_couch_dataset_repository_preserves_source_order(tmp_path: Path) -> None:
    manifest = tmp_path / "canonical.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "path": "vendors.json",
                        "kind": "vendor_score",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    class FakeClient:
        @staticmethod
        def validate_database_name(database: str) -> str:
            return database

        def find(self, database: str, query: dict) -> dict:
            assert database == "core"
            assert query["sort"][-1] == {"source_index": "asc"}
            return {"docs": [{"record": {"vendor": "A"}}, {"record": {"vendor": "B"}}]}

    repository = CouchDatasetRepository(
        FakeClient(),  # type: ignore[arg-type]
        "core",
        manifest,
    )
    assert repository.read_vendors("vendors.json") == [
        {"vendor": "A"},
        {"vendor": "B"},
    ]


def test_couch_dataset_repository_reconstructs_aggregate(tmp_path: Path) -> None:
    manifest = tmp_path / "canonical.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "path": "reports.json",
                        "kind": "market_insight",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    class FakeClient:
        @staticmethod
        def validate_database_name(database: str) -> str:
            return database

        def find(self, database: str, query: dict) -> dict:
            return {
                "docs": [
                    {
                        "collection_key": "reports",
                        "dataset_metadata": {"version": "1"},
                        "record": {"id": "first"},
                    },
                    {
                        "collection_key": "reports",
                        "dataset_metadata": {"version": "1"},
                        "record": {"id": "second"},
                    },
                ]
            }

    repository = CouchDatasetRepository(
        FakeClient(),  # type: ignore[arg-type]
        "core",
        manifest,
    )
    assert repository.read_document("reports.json") == {
        "version": "1",
        "reports": [{"id": "first"}, {"id": "second"}],
    }


def test_couch_dataset_repository_falls_back_to_json_when_unimported(tmp_path: Path) -> None:
    manifest = tmp_path / "canonical.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {"path": "agentic_enterprise_operations_framework_v1.json", "kind": "framework"}
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "agentic_enterprise_operations_framework_v1.json").write_text(
        json.dumps({"framework_name": "AEOF", "schema_version": "1.0"}),
        encoding="utf-8",
    )

    class FakeClient:
        @staticmethod
        def validate_database_name(database: str) -> str:
            return database

        def find(self, database: str, query: dict) -> dict:
            return {"docs": []}

    json_repo = JsonDatasetRepository(LegacyJsonRepository(tmp_path))
    repository = CouchDatasetRepository(
        FakeClient(),  # type: ignore[arg-type]
        "core",
        manifest,
        "ops",
        json_repository=json_repo,
    )

    assert repository.read_document("agentic_enterprise_operations_framework_v1.json") == {
        "framework_name": "AEOF",
        "schema_version": "1.0",
    }
    assert repository.revision("agentic_enterprise_operations_framework_v1.json").startswith(
        "json-"
    )


def test_compare_repository_serves_json_on_couch_failure(tmp_path: Path) -> None:
    (tmp_path / "vendors.json").write_text(
        json.dumps([{"vendor": "Acme"}]),
        encoding="utf-8",
    )
    primary = JsonDatasetRepository(LegacyJsonRepository(tmp_path))

    class BrokenCouch:
        def read_vendors(self, source_path: str) -> list[dict]:
            raise RuntimeError("unavailable")

    repository = CompareDatasetRepository(
        primary,
        BrokenCouch(),  # type: ignore[arg-type]
    )
    assert repository.read_vendors("vendors.json") == [{"vendor": "Acme"}]


def test_compare_repository_blocks_persistent_writes(tmp_path: Path) -> None:
    from gartner_app.repositories.datasets import MigrationWriteBlocked

    (tmp_path / "reports.json").write_text(
        json.dumps({"reports": [{"id": "one"}]}),
        encoding="utf-8",
    )
    primary = JsonDatasetRepository(LegacyJsonRepository(tmp_path))
    repository = CompareDatasetRepository(
        primary,
        object(),  # type: ignore[arg-type]
    )

    with pytest.raises(MigrationWriteBlocked):
        repository.write_document(
            "reports.json",
            {"reports": [{"id": "one", "title": "Changed"}]},
        )
    assert primary.read_document("reports.json") == {
        "reports": [{"id": "one"}]
    }


def test_couch_single_write_is_audited(tmp_path: Path) -> None:
    manifest = tmp_path / "canonical.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {"path": "schema.json", "kind": "schema"}
                ]
            }
        ),
        encoding="utf-8",
    )

    class FakeClient:
        def __init__(self) -> None:
            self.puts: list[tuple[str, str, dict]] = []

        @staticmethod
        def validate_database_name(database: str) -> str:
            return database

        def find(self, database: str, query: dict) -> dict:
            return {
                "docs": [
                    {
                        "_id": "schema:test:1",
                        "_rev": "1-old",
                        "doc_type": "schema",
                        "source_payload": {"version": 1},
                    }
                ]
            }

        def put_document(
            self, database: str, document_id: str, document: dict
        ) -> dict:
            self.puts.append((database, document_id, dict(document)))
            return {"ok": True, "id": document_id, "rev": f"{len(self.puts)}-new"}

    client = FakeClient()
    repository = CouchDatasetRepository(
        client,  # type: ignore[arg-type]
        "core",
        manifest,
        "ops",
    )

    result = repository.write_document(
        "schema.json",
        {"version": 2},
        expected_revision="1-old",
    )

    assert result["updated"] == 1
    assert [item[0] for item in client.puts] == ["ops", "core", "ops"]
    assert client.puts[0][2]["status"] == "pending"
    assert client.puts[2][2]["status"] == "completed"
    assert client.puts[1][2]["_rev"] == "1-old"
    assert client.puts[1][2]["source_payload"] == {"version": 2}


def test_couch_write_requires_revision_precondition(tmp_path: Path) -> None:
    manifest = tmp_path / "canonical.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {"path": "schema.json", "kind": "schema"}
                ]
            }
        ),
        encoding="utf-8",
    )

    class FakeClient:
        @staticmethod
        def validate_database_name(database: str) -> str:
            return database

        def find(self, database: str, query: dict) -> dict:
            return {
                "docs": [
                    {
                        "_id": "schema:test:1",
                        "_rev": "1-old",
                        "doc_type": "schema",
                        "source_payload": {"version": 1},
                    }
                ]
            }

    repository = CouchDatasetRepository(
        FakeClient(),  # type: ignore[arg-type]
        "core",
        manifest,
        "ops",
    )
    with pytest.raises(RevisionPreconditionRequired):
        repository.write_document("schema.json", {"version": 2})


def test_couch_conflict_is_preserved_and_audited(tmp_path: Path) -> None:
    manifest = tmp_path / "canonical.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {"path": "schema.json", "kind": "schema"}
                ]
            }
        ),
        encoding="utf-8",
    )

    class ConflictClient:
        def __init__(self) -> None:
            self.audit_states: list[str] = []

        @staticmethod
        def validate_database_name(database: str) -> str:
            return database

        def find(self, database: str, query: dict) -> dict:
            return {
                "docs": [
                    {
                        "_id": "schema:test:1",
                        "_rev": "1-old",
                        "doc_type": "schema",
                        "source_payload": {"version": 1},
                    }
                ]
            }

        def put_document(
            self, database: str, document_id: str, document: dict
        ) -> dict:
            if database == "core":
                raise CouchDBConflict(409, "PUT", "/core/doc", "conflict")
            self.audit_states.append(document["status"])
            return {"ok": True, "id": document_id, "rev": "1-audit"}

    client = ConflictClient()
    repository = CouchDatasetRepository(
        client,  # type: ignore[arg-type]
        "core",
        manifest,
        "ops",
    )

    with pytest.raises(CouchDBConflict):
        repository.write_document(
            "schema.json",
            {"version": 2},
            expected_revision="1-old",
        )
    assert client.audit_states == ["pending", "failed"]
