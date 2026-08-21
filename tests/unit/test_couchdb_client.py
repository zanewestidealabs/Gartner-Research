from __future__ import annotations

import pytest

from gartner_app.couchdb.client import CouchDBClient


@pytest.mark.parametrize(
    "database",
    [
        "gartner_core",
        "gartner_research",
        "gartner_ops",
        "gartner_archive",
        "_users",
        "_replicator",
        "_global_changes",
    ],
)
def test_database_names_are_accepted(database: str) -> None:
    assert CouchDBClient.validate_database_name(database) == database


@pytest.mark.parametrize(
    "database",
    ["Gartner", "../secrets", "_other", "has space", "http://example"],
)
def test_unsafe_database_names_are_rejected(database: str) -> None:
    with pytest.raises(ValueError, match="unsafe"):
        CouchDBClient.validate_database_name(database)


def test_document_ids_are_url_encoded() -> None:
    path = CouchDBClient.document_path(
        "gartner_core",
        "schema:mdr/2.1",
    )
    assert path == "/gartner_core/schema%3Amdr%2F2.1"
