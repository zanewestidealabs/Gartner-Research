from __future__ import annotations

from typing import Any

from gartner_app.migration.import_manifests import upsert_batch


class FakeClient:
    def get_documents(
        self,
        database: str,
        document_ids: list[str],
    ) -> dict[str, dict[str, Any]]:
        assert database == "gartner_ops"
        assert document_ids == ["manifest:new", "manifest:existing"]
        return {
            "manifest:existing": {
                "_id": "manifest:existing",
                "_rev": "2-existing",
            }
        }

    def bulk_docs(
        self,
        database: str,
        documents: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        assert database == "gartner_ops"
        assert "_rev" not in documents[0]
        assert documents[1]["_rev"] == "2-existing"
        return [
            {"id": "manifest:new", "ok": True, "rev": "1-new"},
            {"id": "manifest:existing", "ok": True, "rev": "3-updated"},
        ]


def test_upsert_batch_applies_existing_revisions() -> None:
    documents = [
        {"_id": "manifest:new"},
        {"_id": "manifest:existing"},
    ]
    created, updated = upsert_batch(
        FakeClient(),  # type: ignore[arg-type]
        "gartner_ops",
        documents,
    )
    assert created == 1
    assert updated == 1
