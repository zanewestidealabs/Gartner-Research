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


@pytest.mark.parametrize(
    ("schema_file", "dimension_count", "relationship_count"),
    [
        ("agentic_soc_framework_v1.json", 11, 31),
        ("agentic_enterprise_operations_framework_v1.json", 11, 28),
    ],
)
def test_framework_maps_are_schema_scoped_and_preserve_connectors(
    client, schema_file: str, dimension_count: int, relationship_count: int
) -> None:
    framework_response = client.get("/api/asmf-framework", query_string={"schema": schema_file})
    orbital_response = client.get("/api/asmf-orbital-map", query_string={"schema": schema_file})

    assert framework_response.status_code == 200
    assert orbital_response.status_code == 200

    framework = framework_response.get_json()
    orbital_map = orbital_response.get_json()
    dimensions = framework["dimensions"]

    assert len(dimensions) == dimension_count
    assert len(orbital_map["relationships"]) == relationship_count
    assert all(
        relationship["from"] in dimensions
        and relationship["to"] in dimensions
        and relationship["type"] in orbital_map["relationship_types"]
        for relationship in orbital_map["relationships"]
    )


def test_schema_catalog_includes_all_frameworks() -> None:
    response = app.test_client().get("/api/schema-files")

    assert response.status_code == 200
    framework_files = {
        schema["filename"]
        for schema in response.get_json()["schemas"]
        if schema["kind"] == "framework"
    }
    assert {
        "agentic_soc_framework_v1.json",
        "agentic_enterprise_operations_framework_v1.json",
    } <= framework_files


def test_apef_remains_a_dedicated_ecosystem_report(client) -> None:
    schema_response = client.get("/api/schema-files")
    graph_response = client.get("/api/apef-graph")
    framework_response = client.get(
        "/api/asmf-framework",
        query_string={"schema": "AI_platform_ecosystem_framework_v1.json"},
    )
    orbital_response = client.get(
        "/api/asmf-orbital-map",
        query_string={"schema": "AI_platform_ecosystem_framework_v1.json"},
    )

    assert schema_response.status_code == 200
    assert graph_response.status_code == 200
    assert framework_response.status_code == 400
    assert orbital_response.status_code == 400
    apec = next(
        schema
        for schema in schema_response.get_json()["schemas"]
        if schema["filename"] == "AI_platform_ecosystem_framework_v1.json"
    )
    graph = graph_response.get_json()

    assert apec["kind"] == "apef"
    assert apec["structure"] == "apef"
    assert len(graph["vendors"]) == 7
    assert graph["edges"]
