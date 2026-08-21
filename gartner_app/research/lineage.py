"""Bridge legacy research cache records into CouchDB source lineage."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from gartner_app.config import Settings
from gartner_app.couchdb.client import CouchDBClient
from gartner_app.couchdb.queries import source_snapshots
from gartner_app.domain.research import SourceSnapshot
from gartner_app.repositories.research import ResearchRepository
from gartner_app.services.research_workflow import ResearchWorkflowService

_TRACKING_PARAMETERS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
}
_BOT_PATTERNS = (
    "access denied",
    "verify you are a human",
    "perimeterx",
    "captcha",
    "cloudflare",
)


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    scheme = parts.scheme.lower()
    hostname = (parts.hostname or "").lower()
    port = parts.port
    if port and not (
        (scheme == "http" and port == 80)
        or (scheme == "https" and port == 443)
    ):
        hostname = f"{hostname}:{port}"
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/")
    query = urlencode(
        sorted(
            (key, value)
            for key, value in parse_qsl(
                parts.query,
                keep_blank_values=True,
            )
            if not key.lower().startswith("utm_")
            and key.lower() not in _TRACKING_PARAMETERS
        )
    )
    return urlunsplit((scheme, hostname, path, query, ""))


def source_document_id(canonical_url: str) -> str:
    digest = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()
    return f"source:{digest}"


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class LegacyCacheLineageSink:
    def __init__(
        self,
        workflow: ResearchWorkflowService,
        *,
        project_id: str,
        run_id: str,
        actor: str,
    ) -> None:
        self.workflow = workflow
        self.project_id = project_id
        self.run_id = run_id
        self.actor = actor

    @classmethod
    def from_settings(
        cls,
        *,
        project_id: str,
        run_id: str,
        actor: str,
    ) -> "LegacyCacheLineageSink":
        settings = Settings.from_env()
        username, password = settings.require_gateway_credentials()
        client = CouchDBClient(
            settings.couchdb_url,
            username=username,
            password=password,
            connect_timeout=settings.connect_timeout_seconds,
            read_timeout=settings.read_timeout_seconds,
        )
        return cls(
            ResearchWorkflowService(
                ResearchRepository(client, settings.couchdb_research_db)
            ),
            project_id=project_id,
            run_id=run_id,
            actor=actor,
        )

    def capture(
        self,
        *,
        vendor_id: str,
        record: dict[str, Any],
        target_id: str | None = None,
        cache_path: Path | None = None,
        retrieval_method: str | None = None,
        headed: bool = False,
        attempt: int | None = None,
        previous_snapshot_id: str | None = None,
    ) -> SourceSnapshot:
        original_url = str(record["url"])
        canonical_url = canonicalize_url(original_url)
        domain = urlsplit(canonical_url).hostname or ""
        source_id = source_document_id(canonical_url)
        self.workflow.register_source(
            canonical_url=canonical_url,
            original_url=original_url,
            domain=domain,
            project_id=self.project_id,
            vendor_id=vendor_id,
            actor=self.actor,
            document_id=source_id,
        )
        history = self.workflow.research.find(
            source_snapshots(source_id, limit=500)
        ).get("docs", [])
        if history:
            latest = history[-1]
            if previous_snapshot_id is None:
                previous_snapshot_id = latest["_id"]
            if attempt is None:
                attempt = int(latest.get("attempt", len(history))) + 1
        elif attempt is None:
            attempt = 1

        text = str(record.get("text") or "")[:200_000]
        error = record.get("error")
        signals = [
            pattern
            for pattern in _BOT_PATTERNS
            if pattern in f"{text} {error or ''}".lower()
        ]
        if error == "bot_blocked" or signals:
            outcome = "blocked"
        elif record.get("ok") is True and len(text) >= 500:
            outcome = "success"
        elif record.get("ok") is True or error == "too_short":
            outcome = "short"
        else:
            outcome = "failed"

        cache_sha256 = None
        relative_cache_path = None
        if cache_path is not None and cache_path.exists():
            cache_sha256 = hashlib.sha256(cache_path.read_bytes()).hexdigest()
            try:
                relative_cache_path = (
                    cache_path.resolve()
                    .relative_to(Path.cwd().resolve())
                    .as_posix()
                )
            except ValueError:
                relative_cache_path = cache_path.as_posix()
        fetched_at = record.get("fetched_at")
        retrieved_at = (
            datetime.fromisoformat(fetched_at)
            if isinstance(fetched_at, str)
            else datetime.now(timezone.utc)
        )
        method = (
            retrieval_method
            or record.get("render_engine")
            or ("cache_import" if cache_path else "unknown")
        )
        snapshot = SourceSnapshot(
            _id=f"snapshot:{uuid.uuid4()}",
            source_id=source_id,
            project_id=self.project_id,
            run_id=self.run_id,
            target_id=target_id,
            vendor_id=vendor_id,
            retrieved_at=retrieved_at,
            retrieval_method=method,
            outcome=outcome,
            http_status=record.get("http_status"),
            content_type=record.get("content_type"),
            content_sha256=_sha256(text),
            text_sha256=_sha256(text),
            text_length=len(text),
            text=text,
            error=error,
            bot_wall_signals=signals,
            headed=headed,
            attempt=attempt,
            previous_snapshot_id=previous_snapshot_id,
            legacy_cache_path=relative_cache_path,
            legacy_cache_sha256=cache_sha256,
            created_by=self.actor,
            updated_by=self.actor,
        )
        return self.workflow.record_snapshot(snapshot)

    def capture_cache_file(
        self,
        cache_path: Path,
        *,
        vendor_id: str,
        target_id: str | None = None,
    ) -> SourceSnapshot:
        record = json.loads(cache_path.read_text(encoding="utf-8"))
        return self.capture(
            vendor_id=vendor_id,
            record=record,
            target_id=target_id,
            cache_path=cache_path,
        )
