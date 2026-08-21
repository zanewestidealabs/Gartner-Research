"""Deterministic transforms from approved legacy JSON sources to CouchDB docs."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from gartner_app.domain.models import DocumentEnvelope

MIGRATION_TIMESTAMP = "2026-07-22T00:00:00Z"
CORE_KINDS = {
    "schema",
    "vendor_score",
    "vendor_pricing",
    "mq_score",
    "market_insight",
    "analyst_take",
    "innovation_profile",
    "framework",
    "report_definition",
}
RESEARCH_KINDS = {"research_target", "evidence_excerpt"}


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    if normalized:
        return normalized
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def content_id(prefix: str, value: Any) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _envelope(
    document_id: str,
    doc_type: str,
    *,
    status: str,
    source_path: str,
    source_hash: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    raw = {
        "_id": document_id,
        "doc_type": doc_type,
        "schema_version": 1,
        "status": status,
        "created_at": MIGRATION_TIMESTAMP,
        "created_by": "migration:canonical:v1",
        "updated_at": MIGRATION_TIMESTAMP,
        "updated_by": "migration:canonical:v1",
        "source": {
            "kind": "legacy_json",
            "path": source_path,
            "sha256": source_hash,
        },
        **payload,
    }
    return DocumentEnvelope.model_validate(raw).to_couchdb()


def _records(data: Any, keys: tuple[str, ...]) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in keys:
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _collection_shape(
    data: Any,
    keys: tuple[str, ...],
) -> tuple[str | None, dict[str, Any]]:
    if not isinstance(data, dict):
        return None, {}
    for key in keys:
        if isinstance(data.get(key), list):
            return key, {
                name: value for name, value in data.items() if name != key
            }
    return None, dict(data)


def _vendor_name(record: dict[str, Any]) -> str:
    for field in ("vendor", "name", "vendor_name", "company"):
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _single_document(
    selection: dict[str, Any],
    data: Any,
    source_hash: str,
) -> list[dict[str, Any]]:
    kind = selection["kind"]
    market = selection["market"]
    version = selection["version"]
    path = selection["path"]
    doc_id = f"{kind}:{slug(market)}:{slug(version)}"
    return [
        _envelope(
            doc_id,
            kind,
            status=selection["status"],
            source_path=path,
            source_hash=source_hash,
            payload={
                "market": market,
                "cycle": selection["cycle"],
                "version": version,
                "source_payload": data,
            },
        )
    ]


def _record_documents(
    selection: dict[str, Any],
    data: Any,
    source_hash: str,
) -> list[dict[str, Any]]:
    kind = selection["kind"]
    path = selection["path"]
    market = selection["market"]
    cycle = selection["cycle"]
    version = selection["version"]
    record_keys = ("vendors", "records", "targets")
    records = _records(data, record_keys)
    collection_key, dataset_metadata = _collection_shape(data, record_keys)
    documents: list[dict[str, Any]] = []
    for source_index, record in enumerate(records):
        name = _vendor_name(record)
        record_key = slug(name) if name else content_id("record", record).split(":")[1]
        variant = selection.get("variant")
        suffix = f":{slug(str(variant))}" if variant else ""
        if kind in {"vendor_score", "vendor_pricing", "mq_score"}:
            document_id = (
                f"{kind.replace('_', '-')}:{slug(market)}:{slug(cycle)}:"
                f"{record_key}:{slug(version)}{suffix}"
            )
            payload = {
                "market": market,
                "cycle": cycle,
                "version": version,
                "source_index": source_index,
                "collection_key": collection_key,
                "dataset_metadata": dataset_metadata,
                "vendor_id": f"vendor:{record_key}",
                "vendor_name": name,
                "record": record,
            }
            if variant:
                payload["variant"] = variant
            documents.append(
                _envelope(
                    document_id,
                    kind,
                    status=selection["status"],
                    source_path=path,
                    source_hash=source_hash,
                    payload=payload,
                )
            )
        else:
            prefix = "evidence" if kind == "evidence_excerpt" else "target"
            document_id = content_id(
                f"{prefix}:{slug(market)}:{slug(version)}",
                record,
            )
            documents.append(
                _envelope(
                    document_id,
                    kind,
                    status=selection["status"],
                    source_path=path,
                    source_hash=source_hash,
                    payload={
                        "market": market,
                        "cycle": cycle,
                        "version": version,
                        "source_index": source_index,
                        "collection_key": collection_key,
                        "dataset_metadata": dataset_metadata,
                        "record": record,
                    },
                )
            )
    return documents


def _collection_documents(
    selection: dict[str, Any],
    data: Any,
    source_hash: str,
) -> list[dict[str, Any]]:
    kind = selection["kind"]
    collection_key = "profiles" if kind == "innovation_profile" else "reports"
    records = _records(data, (collection_key,))
    _, dataset_metadata = _collection_shape(data, (collection_key,))
    documents: list[dict[str, Any]] = []
    for source_index, record in enumerate(records):
        record_id = str(record.get("id") or content_id("item", record).split(":")[1])
        documents.append(
            _envelope(
                f"{kind.replace('_', '-')}:{slug(selection['market'])}:"
                f"{slug(record_id)}:{slug(selection['version'])}",
                kind,
                status=selection["status"],
                source_path=selection["path"],
                source_hash=source_hash,
                payload={
                    "market": selection["market"],
                    "cycle": selection["cycle"],
                    "version": selection["version"],
                    "source_index": source_index,
                    "collection_key": collection_key,
                    "dataset_metadata": dataset_metadata,
                    "record_id": record_id,
                    "record": record,
                },
            )
        )
    return documents


def transform_source(
    root: Path,
    selection: dict[str, Any],
) -> tuple[str, list[dict[str, Any]]]:
    relative_path = selection["path"]
    source_path = (root / relative_path).resolve()
    if not source_path.is_relative_to(root.resolve()):
        raise ValueError(f"source escapes repository root: {relative_path}")
    with source_path.open("r", encoding="utf-8-sig") as source:
        data = json.load(source)
    source_hash = file_sha256(source_path)
    kind = selection["kind"]

    if kind in {"schema", "framework", "report_definition", "legacy_dataset"}:
        documents = _single_document(selection, data, source_hash)
    elif kind in {
        "vendor_score",
        "vendor_pricing",
        "mq_score",
        "research_target",
        "evidence_excerpt",
    }:
        documents = _record_documents(selection, data, source_hash)
    elif kind in {"market_insight", "analyst_take", "innovation_profile"}:
        documents = _collection_documents(selection, data, source_hash)
    else:
        raise ValueError(f"unsupported canonical source kind: {kind}")

    database = selection.get("database")
    if database is None:
        if kind in CORE_KINDS:
            database = "core"
        elif kind in RESEARCH_KINDS:
            database = "research"
        else:
            database = "archive"
    return database, documents


def build_canonical_documents(
    root: Path,
    manifest_path: Path,
) -> dict[str, list[dict[str, Any]]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    vendor_sources: dict[str, list[dict[str, str]]] = defaultdict(list)
    vendor_names: dict[str, str] = {}
    vendor_markets: dict[str, set[str]] = defaultdict(set)

    for selection in manifest["sources"]:
        database, documents = transform_source(root, selection)
        grouped[database].extend(documents)
        for document in documents:
            vendor_id = document.get("vendor_id")
            vendor_name = document.get("vendor_name")
            if isinstance(vendor_id, str) and isinstance(vendor_name, str) and vendor_name:
                vendor_names[vendor_id] = vendor_name
                vendor_markets[vendor_id].add(selection["market"])
                vendor_sources[vendor_id].append(
                    {
                        "path": selection["path"],
                        "sha256": document["source"]["sha256"],
                    }
                )

    for vendor_id in sorted(vendor_names):
        grouped["core"].append(
            _envelope(
                vendor_id,
                "vendor",
                status="active",
                source_path=vendor_sources[vendor_id][0]["path"],
                source_hash=vendor_sources[vendor_id][0]["sha256"],
                payload={
                    "name": vendor_names[vendor_id],
                    "name_normalized": slug(vendor_names[vendor_id]),
                    "markets": sorted(vendor_markets[vendor_id]),
                    "source_files": sorted(
                        vendor_sources[vendor_id],
                        key=lambda item: item["path"],
                    ),
                },
            )
        )

    for database, documents in grouped.items():
        ids = [document["_id"] for document in documents]
        duplicates = sorted(
            document_id for document_id in set(ids) if ids.count(document_id) > 1
        )
        if duplicates:
            raise ValueError(
                f"duplicate deterministic IDs in {database}: {duplicates[:5]}"
            )
        documents.sort(key=lambda document: document["_id"])
    return dict(grouped)
