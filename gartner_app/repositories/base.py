"""Generic repository contract and CouchDB implementation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from gartner_app.couchdb.client import CouchDBClient


class DocumentRepository(Protocol):
    def get(self, document_id: str) -> dict[str, Any]: ...

    def save(self, document: Mapping[str, Any]) -> dict[str, Any]: ...

    def find(
        self,
        selector: Mapping[str, Any],
        *,
        fields: list[str] | None = None,
        limit: int = 100,
        bookmark: str | None = None,
    ) -> dict[str, Any]: ...


class CouchRepository:
    def __init__(
        self,
        client: CouchDBClient,
        database: str,
        *,
        doc_type: str,
    ) -> None:
        self.client = client
        self.database = client.validate_database_name(database)
        self.doc_type = doc_type

    def get(self, document_id: str) -> dict[str, Any]:
        document = self.client.get_document(self.database, document_id)
        if document.get("doc_type") != self.doc_type:
            raise ValueError(
                f"document {document_id!r} is not type {self.doc_type!r}"
            )
        return document

    def save(self, document: Mapping[str, Any]) -> dict[str, Any]:
        document_id = document.get("_id")
        if not isinstance(document_id, str) or not document_id:
            raise ValueError("document requires a non-empty _id")
        if document.get("doc_type") != self.doc_type:
            raise ValueError(f"document requires doc_type={self.doc_type!r}")
        return self.client.put_document(
            self.database,
            document_id,
            document,
        )

    def find(
        self,
        selector: Mapping[str, Any],
        *,
        fields: list[str] | None = None,
        limit: int = 100,
        bookmark: str | None = None,
    ) -> dict[str, Any]:
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        query: dict[str, Any] = {
            "selector": {"doc_type": self.doc_type, **selector},
            "limit": limit,
        }
        if fields is not None:
            query["fields"] = fields
        if bookmark is not None:
            query["bookmark"] = bookmark
        return self.client.find(self.database, query)
