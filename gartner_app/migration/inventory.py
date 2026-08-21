"""Inventory repository JSON files and propose a migration disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gartner_app.domain.models import MigrationManifest, SourceProvenance

EXCLUDED_DIRECTORIES = {".git", ".venv", ".vscode", "__pycache__"}
INVENTORY_VERSION = "inventory:v1"


def iter_json_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*.json")):
        if any(part in EXCLUDED_DIRECTORIES for part in path.parts):
            continue
        if path.is_file():
            yield path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(relative_path: str) -> tuple[str, str]:
    normalized = relative_path.replace("\\", "/").lower()
    filename = normalized.rsplit("/", 1)[-1]

    if "/cache/" in f"/{normalized}" or normalized.startswith(
        ".harvest_cache/"
    ):
        return "research_cache", "manifest_only_candidate"
    if "/backups/" in f"/{normalized}" or "backup" in filename:
        return "backup", "archive_candidate"
    if "checkpoint" in normalized or filename in {"progress.json"}:
        return "research_checkpoint", "research_candidate"
    if re.search(r"(^|/)(batch|lot)[-_]?", normalized) or "/batches/" in normalized:
        return "research_batch", "research_candidate"
    if "schema" in filename or "framework" in filename:
        return "schema_framework", "core_candidate"
    if any(
        marker in filename
        for marker in (
            "vendor",
            "score",
            "pricing",
            "mq_gap",
            "mq-gap",
        )
    ):
        return "vendor_score_pricing", "core_candidate"
    if any(
        marker in filename
        for marker in (
            "report",
            "insight",
            "analyst",
            "profile",
            "adoption",
        )
    ):
        return "report_insight_profile", "core_candidate"
    if normalized.startswith("research/"):
        return "research_other", "research_candidate"
    if normalized.startswith("static/"):
        return "static_application_data", "core_candidate"
    return "unclassified", "review_required"


def inspect_json(path: Path) -> tuple[str, str | None, list[str], int | None]:
    try:
        with path.open("r", encoding="utf-8-sig") as source:
            value: Any = json.load(source)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "invalid", None, [], None

    if isinstance(value, list):
        return "parsed", "array", [], len(value)
    if isinstance(value, dict):
        keys = sorted(str(key) for key in value)[:100]
        count: int | None = None
        for candidate in (
            "vendors",
            "reports",
            "profiles",
            "items",
            "records",
            "results",
        ):
            nested = value.get(candidate)
            if isinstance(nested, list):
                count = len(nested)
                break
        return "parsed", "object", keys, count
    return "parsed", type(value).__name__, [], None


def build_manifest(root: Path, path: Path) -> MigrationManifest:
    relative_path = path.relative_to(root).as_posix()
    stat = path.stat()
    modified_at = datetime.fromtimestamp(stat.st_mtime, timezone.utc)
    digest = sha256_file(path)
    parse_status, top_type, top_keys, record_count = inspect_json(path)
    family, disposition = classify(relative_path)
    path_key = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()

    return MigrationManifest(
        _id=f"manifest:{path_key}",
        created_at=modified_at,
        created_by=INVENTORY_VERSION,
        updated_at=modified_at,
        updated_by=INVENTORY_VERSION,
        source=SourceProvenance(
            kind="repository_file",
            path=relative_path,
            sha256=digest,
        ),
        relative_path=relative_path,
        size_bytes=stat.st_size,
        modified_at=modified_at,
        sha256=digest,
        parse_status=parse_status,
        top_level_type=top_type,
        top_level_keys=top_keys,
        record_count=record_count,
        inferred_family=family,
        proposed_disposition=disposition,
    )


def write_inventory(root: Path, output: Path) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    counts: Counter[str] = Counter()
    parse_counts: Counter[str] = Counter()
    total_bytes = 0

    with output.open("w", encoding="utf-8", newline="\n") as destination:
        for path in iter_json_files(root):
            manifest = build_manifest(root, path)
            destination.write(
                json.dumps(
                    manifest.to_couchdb(),
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
            destination.write("\n")
            counts[manifest.proposed_disposition] += 1
            parse_counts[manifest.parse_status] += 1
            total_bytes += manifest.size_bytes

    return {
        "root": str(root),
        "output": str(output),
        "file_count": sum(counts.values()),
        "total_bytes": total_bytes,
        "dispositions": dict(sorted(counts.items())),
        "parse_statuses": dict(sorted(parse_counts.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("migration/manifests/json_inventory.jsonl"),
    )
    args = parser.parse_args()

    root = args.root.resolve()
    output = (
        args.output
        if args.output.is_absolute()
        else (root / args.output).resolve()
    )
    summary = write_inventory(root, output)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
