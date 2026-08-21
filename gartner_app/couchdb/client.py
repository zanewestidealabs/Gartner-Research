"""Small owned CouchDB HTTP client with bounded retries and redacted errors."""

from __future__ import annotations

import re
import json
from collections.abc import Iterable, Mapping
from typing import Any
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_DATABASE_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_SYSTEM_DATABASES = {"_users", "_replicator", "_global_changes"}


class CouchDBError(RuntimeError):
    """Base CouchDB integration error."""


class CouchDBResponseError(CouchDBError):
    def __init__(self, status_code: int, method: str, path: str, detail: str):
        super().__init__(
            f"CouchDB {method} {path} failed with HTTP {status_code}: {detail}"
        )
        self.status_code = status_code
        self.method = method
        self.path = path


class CouchDBConflict(CouchDBResponseError):
    """Optimistic concurrency conflict."""


class CouchDBNotFound(CouchDBResponseError):
    """Requested database or document was not found."""


class CouchDBClient:
    def __init__(
        self,
        base_url: str,
        *,
        username: str | None = None,
        password: str | None = None,
        connect_timeout: float = 3,
        read_timeout: float = 30,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = (connect_timeout, read_timeout)
        self.session = session or requests.Session()
        if username is not None or password is not None:
            if not username or password is None:
                raise ValueError("both CouchDB username and password are required")
            self.session.auth = (username, password)
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "gartner-research-gateway/0.1",
            }
        )
        retry = Retry(
            total=3,
            connect=3,
            read=2,
            status=2,
            backoff_factor=0.25,
            status_forcelist=(429, 502, 503, 504),
            allowed_methods=frozenset({"GET", "HEAD", "OPTIONS", "PUT"}),
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    @staticmethod
    def validate_database_name(database: str) -> str:
        if (
            database not in _SYSTEM_DATABASES
            and not _DATABASE_NAME.fullmatch(database)
        ):
            raise ValueError(f"unsafe CouchDB database name: {database!r}")
        return database

    @staticmethod
    def document_path(database: str, document_id: str) -> str:
        CouchDBClient.validate_database_name(database)
        return f"/{database}/{quote(document_id, safe='')}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        expected: Iterable[int] = (200,),
        payload: Mapping[str, Any] | list[Any] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> requests.Response:
        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            json=payload,
            params=params,
            timeout=self.timeout,
        )
        expected_statuses = set(expected)
        if response.status_code not in expected_statuses:
            detail = response.text[:500].replace("\r", " ").replace("\n", " ")
            error_type: type[CouchDBResponseError]
            if response.status_code == 404:
                error_type = CouchDBNotFound
            elif response.status_code == 409:
                error_type = CouchDBConflict
            else:
                error_type = CouchDBResponseError
            raise error_type(response.status_code, method, path, detail)
        return response

    def ping(self) -> dict[str, Any]:
        return self._request("GET", "/").json()

    def database_info(self, database: str) -> dict[str, Any]:
        self.validate_database_name(database)
        return self._request("GET", f"/{database}").json()

    def active_tasks(self) -> list[dict[str, Any]]:
        value = self._request("GET", "/_active_tasks").json()
        return value if isinstance(value, list) else []

    def ensure_database(self, database: str) -> bool:
        self.validate_database_name(database)
        response = self._request(
            "PUT",
            f"/{database}",
            expected=(201, 202, 412),
        )
        return response.status_code != 412

    def delete_database(self, database: str) -> bool:
        self.validate_database_name(database)
        response = self._request(
            "DELETE",
            f"/{database}",
            expected=(200, 202, 404),
        )
        return response.status_code != 404

    def set_security(
        self, database: str, security: Mapping[str, Any]
    ) -> dict[str, Any]:
        self.validate_database_name(database)
        return self._request(
            "PUT",
            f"/{database}/_security",
            expected=(200,),
            payload=security,
        ).json()

    def create_index(
        self, database: str, definition: Mapping[str, Any]
    ) -> dict[str, Any]:
        self.validate_database_name(database)
        return self._request(
            "POST",
            f"/{database}/_index",
            expected=(200,),
            payload=definition,
        ).json()

    def get_document(self, database: str, document_id: str) -> dict[str, Any]:
        return self._request(
            "GET", self.document_path(database, document_id)
        ).json()

    def put_document(
        self,
        database: str,
        document_id: str,
        document: Mapping[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            self.document_path(database, document_id),
            expected=(201, 202),
            payload=document,
        ).json()

    def find(
        self, database: str, query: Mapping[str, Any]
    ) -> dict[str, Any]:
        self.validate_database_name(database)
        return self._request(
            "POST",
            f"/{database}/_find",
            expected=(200,),
            payload=query,
        ).json()

    def get_documents(
        self,
        database: str,
        document_ids: list[str],
    ) -> dict[str, dict[str, Any]]:
        """Return existing documents for IDs without failing on missing IDs."""
        self.validate_database_name(database)
        result = self._request(
            "POST",
            f"/{database}/_all_docs",
            expected=(200,),
            payload={"keys": document_ids},
            params={"include_docs": "true"},
        ).json()
        documents: dict[str, dict[str, Any]] = {}
        for row in result.get("rows", []):
            document = row.get("doc")
            if isinstance(document, dict) and isinstance(
                document.get("_id"), str
            ):
                documents[document["_id"]] = document
        return documents

    def all_documents(
        self,
        database: str,
        *,
        page_size: int = 500,
    ) -> list[dict[str, Any]]:
        """Return every document, including design docs, in bounded pages."""
        self.validate_database_name(database)
        if not 1 <= page_size <= 1000:
            raise ValueError("page_size must be between 1 and 1000")
        documents: list[dict[str, Any]] = []
        start_key: str | None = None
        while True:
            params: dict[str, Any] = {
                "include_docs": "true",
                "limit": page_size,
            }
            if start_key is not None:
                params["startkey"] = json.dumps(start_key)
                params["skip"] = 1
            result = self._request(
                "GET",
                f"/{database}/_all_docs",
                expected=(200,),
                params=params,
            ).json()
            rows = result.get("rows", [])
            for row in rows:
                document = row.get("doc")
                if isinstance(document, dict):
                    documents.append(document)
            if len(rows) < page_size:
                break
            start_key = rows[-1]["key"]
        return documents

    def explain(
        self, database: str, query: Mapping[str, Any]
    ) -> dict[str, Any]:
        self.validate_database_name(database)
        return self._request(
            "POST",
            f"/{database}/_explain",
            expected=(200,),
            payload=query,
        ).json()

    def bulk_docs(
        self,
        database: str,
        documents: list[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        self.validate_database_name(database)
        result = self._request(
            "POST",
            f"/{database}/_bulk_docs",
            expected=(201, 202),
            payload={"docs": documents},
        ).json()
        if not isinstance(result, list):
            raise CouchDBError("CouchDB returned an invalid _bulk_docs response")
        return result
