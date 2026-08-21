from __future__ import annotations

import json

import _render_precyber_zero_vendors as renderer


class CapturingSink:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def capture(self, **values):
        self.calls.append(values)


def test_playwright_cache_writer_appends_success_lineage(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(renderer, "CACHE_DIR", tmp_path)
    sink = CapturingSink()
    url = "https://example.test/capability"
    html = (
        "<html><body><main>"
        + ("Concrete capability architecture and metrics. " * 180)
        + "</main></body></html>"
    )

    text_length = renderer._write_cache(
        url,
        html,
        lineage_sink=sink,
        vendor="Example Vendor",
        headed=True,
    )

    assert text_length >= renderer.MIN_USEFUL_TEXT
    assert sink.calls[0]["vendor_id"] == "vendor:example-vendor"
    assert sink.calls[0]["retrieval_method"] == "playwright"
    assert sink.calls[0]["headed"] is True
    cache_record = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert cache_record["ok"] is True


def test_playwright_cache_writer_retains_failed_attempt_lineage(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(renderer, "CACHE_DIR", tmp_path)
    sink = CapturingSink()

    text_length = renderer._write_cache(
        "https://example.test/blocked",
        None,
        error="fetch_failed",
        lineage_sink=sink,
        vendor="Example Vendor",
    )

    assert text_length == 0
    assert sink.calls[0]["record"]["ok"] is False
    assert sink.calls[0]["record"]["error"] == "fetch_failed"
