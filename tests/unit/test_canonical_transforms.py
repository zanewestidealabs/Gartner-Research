from __future__ import annotations

import json
from pathlib import Path

import pytest

from gartner_app.migration.import_canonical import (
    import_canonical,
    upsert_canonical_batch,
)
from gartner_app.migration.transforms import (
    build_canonical_documents,
    content_id,
    slug,
)


def test_slug_is_stable_and_couch_safe() -> None:
    assert slug("CrowdStrike, Inc.") == "crowdstrike-inc"
    assert slug("  AI TRiSM  ") == "ai-trism"
    assert slug("***")


def test_content_id_is_order_independent() -> None:
    assert content_id("evidence", {"a": 1, "b": 2}) == content_id(
        "evidence", {"b": 2, "a": 1}
    )


def test_build_documents_splits_records_and_deduplicates_vendors(
    tmp_path: Path,
) -> None:
    (tmp_path / "scores.json").write_text(
        json.dumps(
            {
                "vendors": [
                    {"vendor": "Acme", "score": 4},
                    {"vendor": "Example", "score": 3},
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "pricing.json").write_text(
        json.dumps({"vendors": [{"vendor": "Acme", "price": "$10"}]}),
        encoding="utf-8",
    )
    manifest = {
        "sources": [
            {
                "path": "scores.json",
                "kind": "vendor_score",
                "market": "test",
                "cycle": "2026",
                "version": "1",
                "status": "active",
            },
            {
                "path": "pricing.json",
                "kind": "vendor_pricing",
                "market": "test",
                "cycle": "2026",
                "version": "1",
                "status": "active",
            },
        ]
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = build_canonical_documents(tmp_path, manifest_path)

    types = [document["doc_type"] for document in result["core"]]
    assert types.count("vendor") == 2
    assert types.count("vendor_score") == 2
    assert types.count("vendor_pricing") == 1
    assert len({document["_id"] for document in result["core"]}) == 5


def test_source_must_stay_below_root(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "path": "../outside.json",
                        "kind": "schema",
                        "market": "test",
                        "cycle": "2026",
                        "version": "1",
                        "status": "active",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="escapes repository root"):
        build_canonical_documents(tmp_path, manifest_path)


def test_real_manifest_dry_run_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[2]
    manifest = root / "migration" / "canonical_sources.json"

    first = import_canonical(root, manifest, dry_run=True)
    second = import_canonical(root, manifest, dry_run=True)

    assert first == second
    assert first["documents"] > 1000
    assert first["databases"]["research"]["document_types"] == {
        "evidence_excerpt": 261,
        "research_target": 264,
    }


def test_canonical_upsert_skips_identical_documents() -> None:
    class FakeClient:
        def get_documents(
            self, database: str, document_ids: list[str]
        ) -> dict[str, dict]:
            assert database == "example"
            assert document_ids == ["vendor:acme"]
            return {
                "vendor:acme": {
                    "_id": "vendor:acme",
                    "_rev": "1-example",
                    "doc_type": "vendor",
                    "name": "Acme",
                }
            }

        def bulk_docs(self, database: str, documents: list[dict]) -> list[dict]:
            raise AssertionError("identical documents must not be rewritten")

    created, updated, skipped, protected = upsert_canonical_batch(
        FakeClient(),  # type: ignore[arg-type]
        "example",
        [{"_id": "vendor:acme", "doc_type": "vendor", "name": "Acme"}],
    )
    assert (created, updated, skipped, protected) == (0, 0, 1, 0)


def test_canonical_upsert_protects_gateway_changes() -> None:
    class FakeClient:
        def get_documents(
            self, database: str, document_ids: list[str]
        ) -> dict[str, dict]:
            return {
                "vendor:acme": {
                    "_id": "vendor:acme",
                    "_rev": "2-live",
                    "doc_type": "vendor",
                    "name": "Changed",
                    "updated_by": "gateway",
                }
            }

        def bulk_docs(self, database: str, documents: list[dict]) -> list[dict]:
            raise AssertionError("gateway-modified documents must be protected")

    created, updated, skipped, protected = upsert_canonical_batch(
        FakeClient(),  # type: ignore[arg-type]
        "example",
        [
            {
                "_id": "vendor:acme",
                "doc_type": "vendor",
                "name": "Original",
                "updated_by": "migration:canonical:v1",
            }
        ],
    )
    assert (created, updated, skipped, protected) == (0, 0, 0, 1)
