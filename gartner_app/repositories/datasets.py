"""JSON, CouchDB, and comparison repositories for migration-sensitive reads."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from gartner_app.config import Settings
from gartner_app.couchdb.client import (
    CouchDBClient,
    CouchDBConflict,
    CouchDBError,
)
from gartner_app.repositories.json_backend import LegacyJsonRepository

LOGGER = logging.getLogger(__name__)


class MigrationWriteBlocked(RuntimeError):
    """A persistent write was attempted while compare mode is read-only."""


class RevisionPreconditionRequired(RuntimeError):
    """A CouchDB write omitted the required If-Match revision token."""


class DatasetRepository(Protocol):
    def read_document(self, source_path: str) -> Any: ...

    def read_schema(self, source_path: str) -> Any: ...

    def read_vendors(self, source_path: str) -> list[dict[str, Any]]: ...

    def revision(self, source_path: str) -> str: ...

    def write_document(
        self,
        source_path: str,
        value: Any,
        *,
        expected_revision: str | None = None,
    ) -> dict[str, Any]: ...


class JsonDatasetRepository:
    def __init__(self, repository: LegacyJsonRepository) -> None:
        self.repository = repository

    def read_document(self, source_path: str) -> Any:
        return self.repository.read(source_path)

    def read_schema(self, source_path: str) -> Any:
        return self.read_document(source_path)

    def read_vendors(self, source_path: str) -> list[dict[str, Any]]:
        data = self.repository.read(source_path)
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            vendors = data.get("vendors")
            if isinstance(vendors, list):
                return [item for item in vendors if isinstance(item, dict)]
            for value in data.values():
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []

    def revision(self, source_path: str) -> str:
        return f"json-{_semantic_hash(self.read_document(source_path))}"

    def write_document(
        self,
        source_path: str,
        value: Any,
        *,
        expected_revision: str | None = None,
    ) -> dict[str, Any]:
        self.repository.write_atomic(source_path, value)
        return {
            "backend": "json",
            "path": source_path,
            "revision": f"json-{_semantic_hash(value)}",
        }


class CouchDatasetRepository:
    def __init__(
        self,
        client: CouchDBClient,
        database: str,
        source_manifest: Path,
        ops_database: str = "gartner_ops",
        json_repository: JsonDatasetRepository | None = None,
    ) -> None:
        self.client = client
        self.database = client.validate_database_name(database)
        self.ops_database = client.validate_database_name(ops_database)
        self.json_repository = json_repository
        raw = json.loads(source_manifest.read_text(encoding="utf-8"))
        self.source_kinds = {
            item["path"]: item["kind"] for item in raw["sources"]
        }

    def _find_source(
        self,
        source_path: str,
        doc_type: str,
        *,
        many: bool,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {
            "selector": {
                "doc_type": {"$eq": doc_type},
                "source.path": {"$eq": source_path},
            },
            "limit": 500,
        }
        if many:
            query["sort"] = [
                {"doc_type": "asc"},
                {"source.path": "asc"},
                {"source_index": "asc"},
            ]
            query["use_index"] = [
                f"idx-{doc_type.replace('_', '-')}-source-path-index",
                f"idx_{doc_type.replace('vendor_', '')}_source_path_index",
            ]
            # Explicit names differ for vendor_score and vendor_pricing.
            names = {
                "vendor_score": [
                    "idx-score-source-path-index",
                    "idx_score_source_path_index",
                ],
                "vendor_pricing": [
                    "idx-pricing-source-path-index",
                    "idx_pricing_source_path_index",
                ],
                "mq_score": [
                    "idx-mq-source-path-index",
                    "idx_mq_source_path_index",
                ],
                "market_insight": [
                    "idx-insight-source-path-index",
                    "idx_insight_source_path_index",
                ],
                "analyst_take": [
                    "idx-analyst-take-source-path-index",
                    "idx_analyst_take_source_path_index",
                ],
                "innovation_profile": [
                    "idx-innovation-source-path-index",
                    "idx_innovation_source_path_index",
                ],
            }
            query["use_index"] = names[doc_type]
        else:
            names = {
                "schema": [
                    "idx-schema-source-path",
                    "idx_schema_source_path",
                ],
                "framework": [
                    "idx-framework-source-path",
                    "idx_framework_source_path",
                ],
                "report_definition": [
                    "idx-report-definition-source-path",
                    "idx_report_definition_source_path",
                ],
            }
            query["use_index"] = names[doc_type]
        return self.client.find(self.database, query).get("docs", [])

    def _json_fallback(self, source_path: str) -> Any:
        if not self.json_repository:
            raise FileNotFoundError(
                f"canonical source is not imported: {source_path}"
            )
        LOGGER.warning(
            "couchdb source missing, falling back to JSON repository for %s",
            source_path,
        )
        return self.json_repository.read_document(source_path)

    def _revision_from_json(self, source_path: str) -> str:
        if not self.json_repository:
            raise FileNotFoundError(source_path)
        return self.json_repository.revision(source_path)

    def read_document(self, source_path: str) -> Any:
        doc_type = self.source_kinds.get(source_path)
        if doc_type is None:
            raise FileNotFoundError(
                f"canonical source is not selected: {source_path}"
            )
        if doc_type in {"schema", "framework", "report_definition"}:
            documents = self._find_source(source_path, doc_type, many=False)
            if not documents:
                return self._json_fallback(source_path)
            return documents[0]["source_payload"]
        if doc_type not in {
            "vendor_score",
            "vendor_pricing",
            "mq_score",
            "market_insight",
            "analyst_take",
            "innovation_profile",
        }:
            raise FileNotFoundError(
                f"canonical source cannot be reconstructed: {source_path}"
            )
        documents = self._find_source(source_path, doc_type, many=True)
        if not documents:
            return self._json_fallback(source_path)
        first = documents[0]
        records = [document["record"] for document in documents]
        collection_key = first.get("collection_key")
        if not collection_key:
            return records
        return {**first.get("dataset_metadata", {}), collection_key: records}

    def read_schema(self, source_path: str) -> Any:
        return self.read_document(source_path)

    def read_vendors(self, source_path: str) -> list[dict[str, Any]]:
        data = self.read_document(source_path)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("vendors"), list):
            return data["vendors"]
        return []

    @staticmethod
    def _revision_token(documents: list[dict[str, Any]]) -> str:
        if len(documents) == 1:
            return str(documents[0]["_rev"])
        revisions = [
            f"{document['_id']}:{document['_rev']}" for document in documents
        ]
        digest = hashlib.sha256(
            "\n".join(sorted(revisions)).encode("utf-8")
        ).hexdigest()
        return f"collection-{digest}"

    def _source_documents(self, source_path: str) -> list[dict[str, Any]]:
        doc_type = self.source_kinds.get(source_path)
        if doc_type in {"schema", "framework", "report_definition"}:
            return self._find_source(source_path, doc_type, many=False)
        if doc_type in {
            "vendor_score",
            "vendor_pricing",
            "mq_score",
            "market_insight",
            "analyst_take",
            "innovation_profile",
        }:
            return self._find_source(source_path, doc_type, many=True)
        raise ValueError(f"dataset has no revision token: {source_path}")

    def revision(self, source_path: str) -> str:
        doc_type = self.source_kinds.get(source_path)
        documents = self._source_documents(source_path)
        if not documents:
            if self.json_repository and doc_type in {
                "schema",
                "framework",
                "report_definition",
                "vendor_score",
                "vendor_pricing",
                "mq_score",
                "market_insight",
                "analyst_take",
                "innovation_profile",
            }:
                return self._revision_from_json(source_path)
            raise FileNotFoundError(source_path)
        return self._revision_token(documents)

    @staticmethod
    def _normalize_revision(value: str) -> str:
        normalized = value.strip()
        if normalized.startswith("W/"):
            normalized = normalized[2:]
        return normalized.strip('"')

    def _check_precondition(
        self,
        documents: list[dict[str, Any]],
        expected_revision: str | None,
    ) -> str:
        if expected_revision is None:
            raise RevisionPreconditionRequired(
                "CouchDB writes require an If-Match header"
            )
        current = self._revision_token(documents)
        expected = self._normalize_revision(expected_revision)
        if expected != "*" and expected != current:
            raise CouchDBConflict(
                409,
                "PUT",
                f"/{self.database}",
                "If-Match revision does not match current data",
            )
        return current

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _start_audit(
        self,
        source_path: str,
        target_ids: list[str],
    ) -> dict[str, Any]:
        timestamp = self._timestamp()
        audit = {
            "_id": f"audit:{uuid.uuid4()}",
            "doc_type": "audit_event",
            "schema_version": 1,
            "status": "pending",
            "created_at": timestamp,
            "created_by": "gateway",
            "updated_at": timestamp,
            "updated_by": "gateway",
            "action": "dataset_write",
            "target_path": source_path,
            "target_ids": target_ids,
        }
        result = self.client.put_document(
            self.ops_database,
            audit["_id"],
            audit,
        )
        audit["_rev"] = result["rev"]
        return audit

    def _finish_audit(
        self,
        audit: dict[str, Any],
        *,
        status: str,
        revisions: list[str] | None = None,
        error: str | None = None,
    ) -> None:
        audit["status"] = status
        audit["updated_at"] = self._timestamp()
        if revisions is not None:
            audit["target_revisions"] = revisions
        if error is not None:
            audit["error"] = error
        self.client.put_document(
            self.ops_database,
            audit["_id"],
            audit,
        )

    def _write_single(
        self,
        source_path: str,
        document: dict[str, Any],
        value: Any,
    ) -> dict[str, Any]:
        audit = self._start_audit(source_path, [document["_id"]])
        updated = dict(document)
        updated["source_payload"] = value
        updated["updated_at"] = self._timestamp()
        updated["updated_by"] = "gateway"
        try:
            result = self.client.put_document(
                self.database,
                updated["_id"],
                updated,
            )
        except Exception as exc:
            self._finish_audit(
                audit,
                status="failed",
                error=type(exc).__name__,
            )
            raise
        self._finish_audit(
            audit,
            status="completed",
            revisions=[result["rev"]],
        )
        return {
            "backend": "couchdb",
            "path": source_path,
            "updated": 1,
            "revision": result["rev"],
            "audit_id": audit["_id"],
        }

    def _write_collection(
        self,
        source_path: str,
        documents: list[dict[str, Any]],
        value: Any,
        current_revision: str,
    ) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("collection-backed datasets require an object")
        collection_key = documents[0].get("collection_key")
        records = value.get(collection_key) if collection_key else None
        if not isinstance(records, list):
            raise ValueError(
                f"dataset requires a {collection_key!r} record collection"
            )
        by_id = {
            str(record.get("id")): record
            for record in records
            if isinstance(record, dict) and record.get("id") is not None
        }
        existing_ids = {str(document.get("record_id")) for document in documents}
        if set(by_id) != existing_ids:
            raise ValueError(
                "collection membership changes require a dedicated create/delete API"
            )
        metadata = {
            key: item for key, item in value.items() if key != collection_key
        }
        changed: list[dict[str, Any]] = []
        timestamp = self._timestamp()
        for document in documents:
            updated = dict(document)
            updated["record"] = by_id[str(document["record_id"])]
            updated["dataset_metadata"] = metadata
            if updated["record"] == document.get("record") and metadata == document.get(
                "dataset_metadata", {}
            ):
                continue
            updated["updated_at"] = timestamp
            updated["updated_by"] = "gateway"
            changed.append(updated)
        if not changed:
            return {
                "backend": "couchdb",
                "path": source_path,
                "updated": 0,
                "revision": current_revision,
            }

        audit = self._start_audit(
            source_path,
            [document["_id"] for document in changed],
        )
        results = self.client.bulk_docs(self.database, changed)
        failures = [result for result in results if result.get("error")]
        if failures:
            self._finish_audit(
                audit,
                status="failed",
                error=str(failures[0].get("error")),
            )
            if any(result.get("error") == "conflict" for result in failures):
                raise CouchDBConflict(
                    409,
                    "POST",
                    f"/{self.database}/_bulk_docs",
                    "revision conflict",
                )
            raise CouchDBError(f"dataset bulk write failed: {failures[:3]}")
        revisions = [result["rev"] for result in results]
        revision_by_id = {
            document["_id"]: document["_rev"] for document in documents
        }
        revision_by_id.update(
            {result["id"]: result["rev"] for result in results}
        )
        new_revision = self._revision_token(
            [
                {"_id": document_id, "_rev": revision}
                for document_id, revision in revision_by_id.items()
            ]
        )
        self._finish_audit(
            audit,
            status="completed",
            revisions=revisions,
        )
        return {
            "backend": "couchdb",
            "path": source_path,
            "updated": len(changed),
            "revisions": revisions,
            "revision": new_revision,
            "audit_id": audit["_id"],
        }

    def write_document(
        self,
        source_path: str,
        value: Any,
        *,
        expected_revision: str | None = None,
    ) -> dict[str, Any]:
        doc_type = self.source_kinds.get(source_path)
        if doc_type in {"schema", "framework", "report_definition"}:
            documents = self._find_source(source_path, doc_type, many=False)
            if not documents:
                raise FileNotFoundError(source_path)
            self._check_precondition(documents, expected_revision)
            return self._write_single(source_path, documents[0], value)
        if doc_type in {
            "market_insight",
            "analyst_take",
            "innovation_profile",
        }:
            documents = self._find_source(source_path, doc_type, many=True)
            if not documents:
                raise FileNotFoundError(source_path)
            current_revision = self._check_precondition(
                documents,
                expected_revision,
            )
            return self._write_collection(
                source_path,
                documents,
                value,
                current_revision,
            )
        raise ValueError(f"dataset is not writable through this API: {source_path}")


def _semantic_hash(value: Any) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class CompareDatasetRepository:
    """Serve JSON while checking CouchDB and logging only difference metadata."""

    def __init__(
        self,
        json_repository: JsonDatasetRepository,
        couch_repository: CouchDatasetRepository,
    ) -> None:
        self.json_repository = json_repository
        self.couch_repository = couch_repository

    def _compare(self, family: str, source_path: str, primary: Any, other: Any) -> None:
        primary_hash = _semantic_hash(primary)
        other_hash = _semantic_hash(other)
        if primary_hash != other_hash:
            LOGGER.warning(
                "data parity mismatch family=%s source=%s json_sha256=%s "
                "couchdb_sha256=%s",
                family,
                source_path,
                primary_hash,
                other_hash,
            )

    def read_document(self, source_path: str) -> Any:
        primary = self.json_repository.read_document(source_path)
        try:
            other = self.couch_repository.read_document(source_path)
            self._compare("document", source_path, primary, other)
        except Exception as exc:
            LOGGER.warning(
                "data parity query failed family=document source=%s error=%s",
                source_path,
                type(exc).__name__,
            )
        return primary

    def read_schema(self, source_path: str) -> Any:
        primary = self.json_repository.read_schema(source_path)
        try:
            other = self.couch_repository.read_schema(source_path)
            self._compare("schema", source_path, primary, other)
        except Exception as exc:
            LOGGER.warning(
                "data parity query failed family=schema source=%s error=%s",
                source_path,
                type(exc).__name__,
            )
        return primary

    def read_vendors(self, source_path: str) -> list[dict[str, Any]]:
        primary = self.json_repository.read_vendors(source_path)
        try:
            other = self.couch_repository.read_vendors(source_path)
            self._compare("vendors", source_path, primary, other)
        except Exception as exc:
            LOGGER.warning(
                "data parity query failed family=vendors source=%s error=%s",
                source_path,
                type(exc).__name__,
            )
        return primary

    def revision(self, source_path: str) -> str:
        return self.couch_repository.revision(source_path)

    def write_document(
        self,
        source_path: str,
        value: Any,
        *,
        expected_revision: str | None = None,
    ) -> dict[str, Any]:
        raise MigrationWriteBlocked(
            "persistent writes are disabled in compare mode; switch explicitly "
            "to json or couchdb after reconciliation"
        )


def build_dataset_repository(
    root: Path,
    legacy_repository: LegacyJsonRepository,
    settings: Settings | None = None,
) -> DatasetRepository:
    settings = settings or Settings.from_env()
    json_repository = JsonDatasetRepository(legacy_repository)
    if settings.data_backend == "json":
        return json_repository

    username, password = settings.require_gateway_credentials()
    couch_repository = CouchDatasetRepository(
        CouchDBClient(
            settings.couchdb_url,
            username=username,
            password=password,
            connect_timeout=settings.connect_timeout_seconds,
            read_timeout=settings.read_timeout_seconds,
        ),
        settings.couchdb_core_db,
        root / "migration" / "canonical_sources.json",
        settings.couchdb_ops_db,
        json_repository=json_repository,
    )
    if settings.data_backend == "compare":
        return CompareDatasetRepository(json_repository, couch_repository)
    return couch_repository
