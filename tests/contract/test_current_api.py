"""Read-only characterization tests for the existing JSON-backed Flask app."""

from __future__ import annotations

import pytest

from app import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


@pytest.mark.parametrize(
    ("path", "content_type"),
    [
        ("/", "text/html"),
        ("/api/vendors", "application/json"),
        ("/api/metadata", "application/json"),
        ("/api/filter-options?fields=region,specialization,ir_focus_type", "application/json"),
        ("/api/schema-files", "application/json"),
        ("/api/reports", "application/json"),
        ("/api/asmf-framework", "application/json"),
        ("/api/health/live", "application/json"),
        ("/api/health/ready", "application/json"),
    ],
)
def test_read_route_baseline(client, path: str, content_type: str) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert response.content_type.startswith(content_type)
    assert response.data


def test_route_map_contains_migration_sensitive_writes() -> None:
    routes = {
        (rule.rule, tuple(sorted(rule.methods - {"HEAD", "OPTIONS"})))
        for rule in app.url_map.iter_rules()
    }

    assert ("/api/update-definition", ("POST",)) in routes
    assert ("/api/update-adoption-plan", ("POST",)) in routes
    assert ("/api/mdr-market-insight", ("GET",)) in routes
    assert ("/api/mdr-market-insight", ("POST",)) in routes
    assert ("/api/innovation-profiles", ("GET",)) in routes
    assert ("/api/innovation-profiles", ("POST",)) in routes


def test_filter_options_returns_each_requested_field() -> None:
    response = app.test_client().get(
        "/api/filter-options?fields=region,specialization,ir_focus_type"
    )

    assert response.status_code == 200
    assert set(response.get_json()) == {"region", "specialization", "ir_focus_type"}
