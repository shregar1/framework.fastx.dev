"""Tests for Postman export and generated script engines."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI

from core.postman_test_script_engine import (
    PostmanTestScriptEngine,
    enrich_operation_spec_for_tests,
)
from core.route_export_engine import RouteExportEngine


def _count_requests(items: list[dict]) -> int:
    total = 0
    for node in items:
        if "request" in node:
            total += 1
        if "item" in node:
            total += _count_requests(node["item"])
    return total


def _first_request(items: list[dict]) -> dict | None:
    for node in items:
        if "request" in node:
            return node
        if "item" in node:
            found = _first_request(node["item"])
            if found is not None:
                return found
    return None


def test_export_groups_requests_by_endpoint_path(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    app = FastAPI(title="Sample API")
    engine = RouteExportEngine(app)
    engine.install()

    @app.get("/health/live")
    async def live():
        return {"status": "alive"}

    @app.post("/api/v1/catalog/products")
    async def create_product():
        return {"ok": True}

    @app.get("/api/v1/catalog/products/{id}")
    async def fetch_product(id: int):
        return {"id": id}

    collection_path, env_path = engine.export_postman_collection()
    assert collection_path.exists()
    assert env_path is None

    payload = json.loads(collection_path.read_text(encoding="utf-8"))
    assert payload["info"]["name"].endswith(" - Auto Generated")
    assert _count_requests(payload["item"]) == 3

    root_names = {n["name"] for n in payload["item"]}
    assert "api" in root_names
    assert "health" in root_names


def test_export_request_contains_generated_tests_and_headers(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    app = FastAPI(title="Scripted API")
    engine = RouteExportEngine(app)
    engine.install()

    @app.post("/api/v1/orders")
    async def create_order(payload: dict):
        return payload

    collection_path, _ = engine.export_postman_collection()
    payload = json.loads(collection_path.read_text(encoding="utf-8"))
    req = _first_request(payload["item"])
    assert req is not None
    headers = req["request"]["header"]
    header_keys = {h["key"].lower() for h in headers}
    assert "accept" in header_keys
    assert "x-reference-urn" in header_keys

    assert "event" in req and len(req["event"]) == 2
    test_exec = req["event"][1]["script"]["exec"]
    joined = "\n".join(test_exec)
    assert "exhaustive auto-generated tests" in joined
    assert "[NEG]" in joined
    assert "JSON: malformed (truncated)" in joined
    # Wrong-type query probe is emitted only when OpenAPI lists query parameters.


def test_export_writes_environment_file_when_enabled(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("POSTMAN_EXPORT_ENVIRONMENT", "1")
    app = FastAPI(title="Env API")
    engine = RouteExportEngine(app)
    engine.install()

    @app.get("/status")
    async def status():
        return {"ok": True}

    collection_path, env_path = engine.export_postman_collection()
    assert collection_path.exists()
    assert env_path is not None and env_path.exists()

    env_payload = json.loads(env_path.read_text(encoding="utf-8"))
    keys = {v["key"] for v in env_payload["values"]}
    assert {
        "base_url",
        "reference_urn",
        "reference_number",
        "token",
        "refresh_token",
    } <= keys


def test_bearer_security_adds_authorization_header(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    app = FastAPI(title="Secure API")
    app.openapi_schema = {
        "openapi": "3.0.2",
        "info": {"title": "Secure API", "version": "1.0.0"},
        "paths": {
            "/secure/data": {
                "get": {
                    "summary": "SecureData",
                    "responses": {"200": {"description": "ok"}},
                    "security": [{"BearerAuth": []}],
                }
            }
        },
        "components": {
            "securitySchemes": {"BearerAuth": {"type": "http", "scheme": "bearer"}}
        },
    }
    engine = RouteExportEngine(app)
    engine.install()

    collection_path, _ = engine.export_postman_collection()
    payload = json.loads(collection_path.read_text(encoding="utf-8"))
    req = _first_request(payload["item"])
    assert req is not None
    headers = req["request"]["header"]
    auth_values = [h["value"] for h in headers if h["key"] == "Authorization"]
    assert "Bearer {{token}}" in auth_values


def test_enrich_operation_extracts_request_body_and_query_metadata() -> None:
    spec = {
        "query_items": [
            {"key": "page", "value": "1"},
            {"key": "search", "value": "text"},
        ],
        "json_body": {"name": "A"},
    }
    operation = {
        "parameters": [
            {
                "name": "page",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            },
            {
                "name": "search",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
            },
        ],
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {"name": {"type": "string"}},
                    }
                }
            }
        },
        "responses": {
            "201": {
                "description": "created",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["id", "name"],
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                            },
                        }
                    }
                },
            },
            "422": {"description": "validation error"},
        },
    }

    enrich_operation_spec_for_tests(
        spec, operation, components={}, path_level_parameters=[]
    )

    assert spec["negative_has_json_body"] is True
    assert spec["request_body_root_kind"] == "object"
    assert "name" in spec["request_body_required_keys"]
    assert "page" in spec["required_query_names"]
    assert spec["response_json_root_kind"] == "object"
    assert "id" in spec["response_required_keys"]
    assert spec["response_property_types"]["id"] == "integer"


def test_collection_test_hook_sets_token_from_envelope_data_tokens() -> None:
    """Login-style IResponseDTO with nested data.tokens syncs Postman collection vars."""
    events = PostmanTestScriptEngine.build_collection_events("API")
    test_event = next(e for e in events if e.get("listen") == "test")
    joined = "\n".join(test_event["script"]["exec"])
    assert "data.tokens" in joined
    assert "accessToken" in joined
    assert "refresh_token" in joined
