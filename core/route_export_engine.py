"""Route export engine for cURL and Postman collection generation."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

from core.postman_test_script_engine import (
    PostmanTestScriptEngine,
    enrich_operation_spec_for_tests,
)
from utilities.system import SystemUtility


class RouteExportEngine:
    """Collect route metadata and export cURL/Postman artifacts."""

    def __init__(
        self,
        app: FastAPI,
        output_file: Optional[str] = None,
        environment_file: Optional[str] = None,
    ) -> None:
        self.app = app
        postman_dir = Path(os.getenv("POSTMAN_OUTPUT_DIR", "postman"))
        if output_file is None:
            output_file = os.getenv(
                "POSTMAN_COLLECTION_FILE",
                str(postman_dir / "postman_collection.json"),
            )
        self.output_file = output_file
        if environment_file is None:
            raw = os.getenv("POSTMAN_ENV_FILE", "postman_environment.json")
            ep = Path(raw)
            if ep.is_absolute() or ep.parent != Path("."):
                environment_file = raw
            else:
                environment_file = str(postman_dir / ep.name)
        else:
            environment_file = environment_file
        self.environment_file = environment_file
        self.base_url = os.getenv("POSTMAN_BASE_URL") or (
            f"http://{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8000')}"
        )
        self._route_memory: list[dict[str, str]] = []
        self._seen_keys: set[tuple[str, str]] = set()

    def _also_export_postman_environment_file(self) -> bool:
        """When true, also write ``postman_environment.json`` (see ``POSTMAN_EXPORT_ENVIRONMENT``)."""
        v = os.getenv("POSTMAN_EXPORT_ENVIRONMENT", "").strip().lower()
        return v in ("1", "true", "yes", "on")

    def _postman_project_display_name(self) -> str:
        """Label for Postman collection/environment: git repo folder, or override, or app title."""
        override = os.getenv("POSTMAN_COLLECTION_NAME", "").strip()
        if override:
            return override
        git_name = SystemUtility.git_repository_folder_name()
        if git_name:
            return git_name
        return str(self.app.title)

    def install(self) -> None:
        """Install monkey patches that observe route registration."""
        if getattr(self.app.state, "_route_export_engine_installed", False):
            return

        self._patch_app_add_api_route()
        self._patch_router_add_api_route()
        self._patch_app_include_router()
        self._patch_router_include_api_router_alias()

        self.app.state._route_export_engine_installed = True

    def _patch_app_add_api_route(self) -> None:
        original = self.app.add_api_route
        engine = self

        def wrapped_add_api_route(
            path: str, endpoint: Any, *args: Any, **kwargs: Any
        ) -> Any:
            result = original(path, endpoint, *args, **kwargs)
            methods = kwargs.get("methods") or ["GET"]
            engine._record_route(path=path, methods=methods)
            return result

        self.app.add_api_route = wrapped_add_api_route  # type: ignore[assignment]

    def _patch_router_add_api_route(self) -> None:
        original = APIRouter.add_api_route
        engine = self

        def wrapped_router_add_api_route(
            router_self: APIRouter,
            path: str,
            endpoint: Any,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            result = original(router_self, path, endpoint, *args, **kwargs)
            methods = kwargs.get("methods") or ["GET"]
            full_path = f"{router_self.prefix}{path}" if router_self.prefix else path
            engine._record_route(path=full_path, methods=methods)
            return result

        APIRouter.add_api_route = wrapped_router_add_api_route  # type: ignore[assignment]

    def _patch_app_include_router(self) -> None:
        original = self.app.include_router
        engine = self

        def wrapped_include_router(router: APIRouter, *args: Any, **kwargs: Any) -> Any:
            result = original(router, *args, **kwargs)
            include_prefix = kwargs.get("prefix", "")
            for route in router.routes:
                if not isinstance(route, APIRoute):
                    continue
                path = f"{include_prefix}{route.path}" if include_prefix else route.path
                methods = route.methods or {"GET"}
                engine._record_route(path=path, methods=methods)
            return result

        self.app.include_router = wrapped_include_router  # type: ignore[assignment]

    def _patch_router_include_api_router_alias(self) -> None:
        """Provide include_api_router alias when projects use that naming."""
        if not hasattr(APIRouter, "include_api_router"):
            APIRouter.include_api_router = APIRouter.include_router  # type: ignore[attr-defined]

    def _record_route(self, path: str, methods: set[str] | list[str]) -> None:
        normalized_path = path if path.startswith("/") else f"/{path}"
        for method in methods:
            upper_method = method.upper()
            if upper_method in {"HEAD", "OPTIONS"}:
                continue
            key = (upper_method, normalized_path)
            if key in self._seen_keys:
                continue
            self._seen_keys.add(key)
            self._route_memory.append({"method": upper_method, "path": normalized_path})

    def build_curl_examples(self) -> list[str]:
        """Build cURL examples from OpenAPI operations."""
        examples: list[str] = []
        for operation in self._collect_operation_specs():
            method = operation["method"]
            path_with_values = operation["path_with_values"]
            query_string = operation["query_string"]
            display_name = operation["display_name"]
            # Only the URL line is an f-string; static lines use literal ``{{var}}`` for Postman.
            parts = [
                f"# {display_name}",
                f"curl -X {method} '{{{{base_url}}}}{path_with_values}{query_string}'",
                "-H 'accept: application/json'",
                "-H 'x-reference-urn: {{reference_urn}}'",
            ]
            if operation.get("needs_bearer"):
                parts.append("-H 'Authorization: Bearer {{token}}'")
            json_body = operation["json_body"]
            if json_body is not None:
                parts.append("-H 'Content-Type: application/json'")
                parts.append(f"-d '{json.dumps(json_body)}'")
            examples.append("\n".join(parts))
        return examples

    def export_postman_collection(self) -> tuple[Path, Optional[Path]]:
        """Write Postman collection JSON; optionally a separate environment file.

        Postman cannot attach an Environment from inside a Collection JSON. For **one import**,
        defaults are stored on the collection as ``variable`` (no environment needed). Set
        ``POSTMAN_EXPORT_ENVIRONMENT=1`` to also write ``POSTMAN_ENV_FILE`` (under
        ``POSTMAN_OUTPUT_DIR``, default ``postman/``) for workspace-style environments;
        you can then **Import** and multi-select both files in one dialog.
        """
        path_tree: dict[str, Any] = {}
        for operation in self._collect_operation_specs():
            method = operation["method"]
            raw_url = f"{{{{base_url}}}}{operation['path_template']}{operation['query_string']}"
            item: dict[str, Any] = {
                "name": operation["display_name"],
                "request": {
                    "method": method,
                    "header": [
                        {"key": "Accept", "value": "application/json"},
                        {
                            "key": "x-reference-urn",
                            "value": "{{reference_urn}}",
                            "type": "text",
                        },
                    ],
                    "url": {
                        "raw": raw_url,
                        "host": ["{{base_url}}"],
                        "path": operation["postman_path_segments"],
                    },
                },
            }
            desc_parts: list[str] = []
            if operation.get("summary"):
                desc_parts.append(operation["summary"])
            if operation.get("operation_id"):
                desc_parts.append(f"operationId: `{operation['operation_id']}`")
            if desc_parts:
                item["request"]["description"] = "\n\n".join(desc_parts)
            if operation["query_items"]:
                item["request"]["url"]["query"] = operation["query_items"]
            if operation["path_variables"]:
                item["request"]["url"]["variable"] = operation["path_variables"]
            if operation.get("needs_bearer"):
                item["request"]["header"].append(
                    {
                        "key": "Authorization",
                        "value": "Bearer {{token}}",
                        "type": "text",
                    }
                )
            json_body = operation["json_body"]
            if json_body is not None:
                item["request"]["header"].append(
                    {"key": "Content-Type", "value": "application/json"}
                )
                item["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(json_body, indent=2),
                    "options": {"raw": {"language": "json"}},
                }
            item["event"] = PostmanTestScriptEngine.build_events(operation)
            segments = self._postman_folder_segments_from_openapi_path(
                operation["openapi_path"]
            )
            self._postman_path_tree_insert(path_tree, segments, item)

        collection_items = self._postman_path_tree_to_items(path_tree)

        also_env = self._also_export_postman_environment_file()
        project = self._postman_project_display_name()
        payload = {
            "info": {
                "name": f"{project} - Auto Generated",
                "description": self._postman_collection_description(also_env),
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": collection_items,
            "event": PostmanTestScriptEngine.build_collection_events(project),
            "variable": self._default_collection_variables(),
        }

        output_path = Path(self.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if not also_env:
            return output_path, None
        env_path = Path(self.environment_file)
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text(
            json.dumps(self._build_postman_environment(), indent=2),
            encoding="utf-8",
        )
        return output_path, env_path

    def _postman_collection_description(
        self, also_writes_environment_file: bool
    ) -> str:
        base = (
            "**One-click import:** this file includes **collection variables** "
            "(`base_url`, `reference_urn`, `reference_number`, `token`, `refresh_token`). "
            "Folders mirror the **URL path** (e.g. `health/live`, `items/{id}`). "
            "Import only this collection — no environment required. "
            "Edit values under the collection → **Variables** (or use the collection menu → Edit). "
            "Run **Collection Runner** for auto-generated tests per request."
        )
        if also_writes_environment_file:
            return (
                base
                + " A matching environment file was also generated; you can **Import** and "
                "multi-select **both** JSON files in one Postman Import dialog if you prefer "
                "environment-scoped variables."
            )
        return (
            base + " To also emit a separate environment JSON under `postman/`, set env var "
            "`POSTMAN_EXPORT_ENVIRONMENT=1` before boot."
        )

    @staticmethod
    def _postman_folder_segments_from_openapi_path(openapi_path: str) -> list[str]:
        """Path segments for Postman folders (OpenAPI path, e.g. ``/api/v1/items/{id}``)."""
        p = (openapi_path or "").strip()
        if not p or p == "/":
            return []
        return [seg for seg in p.strip("/").split("/") if seg]

    @staticmethod
    def _postman_path_tree_insert(
        root: dict[str, Any], segments: list[str], request_item: dict[str, Any]
    ) -> None:
        node = root
        for seg in segments:
            node = node.setdefault(seg, {})
        node.setdefault("__leaves__", []).append(request_item)

    @staticmethod
    def _postman_path_tree_to_items(node: dict[str, Any]) -> list[dict[str, Any]]:
        """Turn nested path dict into Postman ``item`` list (folders + requests)."""
        items: list[dict[str, Any]] = []
        leaves: list[dict[str, Any]] = list(node.get("__leaves__", []))
        leaves.sort(
            key=lambda x: (
                x.get("request", {}).get("method", ""),
                x.get("name", ""),
            )
        )
        folder_keys = sorted(k for k in node.keys() if k != "__leaves__")
        for name in folder_keys:
            child = node[name]
            nested = RouteExportEngine._postman_path_tree_to_items(child)
            items.append({"name": name, "item": nested})
        items.extend(leaves)
        return items

    def _default_collection_variables(self) -> list[dict[str, str]]:
        """Collection-level defaults (mirror env file for offline use)."""
        return [
            {"key": "base_url", "value": self.base_url},
            {"key": "reference_urn", "value": "{{$randomUUID}}"},
            {"key": "reference_number", "value": "1"},
            {"key": "token", "value": ""},
            {"key": "refresh_token", "value": ""},
        ]

    def _build_postman_environment(self) -> dict[str, Any]:
        """Postman v2.1 environment export with shared variables."""
        return {
            "id": str(uuid.uuid4()),
            "name": f"{self._postman_project_display_name()} - Environment",
            "values": [
                {"key": "base_url", "value": self.base_url, "enabled": True},
                {
                    "key": "reference_urn",
                    "value": "{{$randomUUID}}",
                    "enabled": True,
                },
                {
                    "key": "reference_number",
                    "value": "1",
                    "enabled": True,
                },
                {"key": "token", "value": "", "enabled": True},
                {"key": "refresh_token", "value": "", "enabled": True},
            ],
            "_postman_variable_scope": "environment",
        }

    def _collect_operation_specs(self) -> list[dict[str, Any]]:
        """Collect operation data from OpenAPI for cURL and Postman generation."""
        schema = self.app.openapi()
        paths = schema.get("paths", {})
        components: dict[str, Any] = (
            schema["components"] if isinstance(schema.get("components"), dict) else {}
        )
        operations: list[dict[str, Any]] = []
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            path_parameters = path_item.get("parameters", [])
            for method, operation in path_item.items():
                method_upper = str(method).upper()
                if method_upper in {"HEAD", "OPTIONS"}:
                    continue
                if method_upper not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                    continue
                if not isinstance(operation, dict):
                    continue

                all_parameters = [*path_parameters, *operation.get("parameters", [])]
                path_variables, path_value_map = self._extract_path_parameters(
                    all_parameters
                )
                query_items = self._extract_query_parameters(all_parameters)

                path_template = path
                path_with_values = path
                for key, value in path_value_map.items():
                    path_with_values = path_with_values.replace(
                        f"{{{key}}}", str(value)
                    )
                    path_template = path_template.replace(f"{{{key}}}", f":{key}")

                query_string = self._query_string(query_items)
                json_body = self._extract_json_request_body(
                    operation=operation,
                    components=schema.get("components", {}),
                )
                postman_path_segments = [
                    segment[1:] if segment.startswith(":") else segment
                    for segment in path_template.strip("/").split("/")
                    if segment
                ]
                display_name = self._operation_display_name(
                    operation, method_upper, path_template
                )
                op_id = operation.get("operationId")
                operation_id = (
                    op_id.strip() if isinstance(op_id, str) and op_id.strip() else None
                )
                summary_raw = operation.get("summary")
                summary_str = (
                    summary_raw.strip()
                    if isinstance(summary_raw, str) and summary_raw.strip()
                    else None
                )
                needs_bearer = self._operation_requires_bearer(schema, operation)
                row: dict[str, Any] = {
                    "method": method_upper,
                    "openapi_path": path,
                    "path_template": path_template,
                    "path_with_values": path_with_values,
                    "postman_path_segments": postman_path_segments,
                    "query_items": query_items,
                    "query_string": query_string,
                    "path_variables": path_variables,
                    "json_body": json_body,
                    "display_name": display_name,
                    "operation_id": operation_id,
                    "summary": summary_str,
                    "needs_bearer": needs_bearer,
                }
                enrich_operation_spec_for_tests(
                    row, operation, components, path_parameters
                )
                operations.append(row)
        return operations

    def _operation_display_name(
        self, operation: dict[str, Any], method: str, path_template: str
    ) -> str:
        summary = operation.get("summary")
        if isinstance(summary, str) and summary.strip():
            return summary.strip()
        op_id = operation.get("operationId")
        if isinstance(op_id, str) and op_id.strip():
            return op_id.strip()
        return f"{method} {path_template}"

    def _resolve_effective_security(
        self, schema: dict[str, Any], operation: dict[str, Any]
    ) -> list[dict[str, list[str]]]:
        op_sec = operation.get("security")
        if op_sec is not None:
            if not isinstance(op_sec, list):
                return []
            return [s for s in op_sec if isinstance(s, dict)]
        global_sec = schema.get("security")
        if isinstance(global_sec, list):
            return [s for s in global_sec if isinstance(s, dict)]
        return []

    def _operation_requires_bearer(
        self, schema: dict[str, Any], operation: dict[str, Any]
    ) -> bool:
        """True if OpenAPI security implies sending ``Authorization: Bearer …``.

        Covers **HTTP Bearer** (``type: http``, ``scheme: bearer``) and **OAuth2 /
        OpenID Connect** schemes (access tokens are normally sent as Bearer).
        """
        requirements = self._resolve_effective_security(schema, operation)
        if not requirements:
            return False
        schemes = (
            schema.get("components", {}).get("securitySchemes", {})
            if isinstance(schema.get("components"), dict)
            else {}
        )
        for req in requirements:
            for name in req:
                scheme = schemes.get(name)
                if self._security_scheme_uses_bearer_token(scheme):
                    return True
        return False

    def _security_scheme_uses_bearer_token(self, scheme: Any) -> bool:
        """Whether this security scheme typically uses a Bearer token in ``Authorization``."""
        if not isinstance(scheme, dict):
            return False
        stype = scheme.get("type")
        if stype == "oauth2":
            return True
        if stype == "openIdConnect":
            return True
        if stype == "http":
            return str(scheme.get("scheme", "")).lower() == "bearer"
        return False

    def _extract_path_parameters(
        self, parameters: list[dict[str, Any]]
    ) -> tuple[list[dict[str, str]], dict[str, Any]]:
        variables: list[dict[str, str]] = []
        value_map: dict[str, Any] = {}
        for parameter in parameters:
            if not isinstance(parameter, dict):
                continue
            if parameter.get("in") != "path":
                continue
            name = parameter.get("name")
            if not isinstance(name, str):
                continue
            sample = self._sample_from_parameter(parameter)
            value_map[name] = sample
            variables.append({"key": name, "value": str(sample)})
        return variables, value_map

    def _extract_query_parameters(
        self, parameters: list[dict[str, Any]]
    ) -> list[dict[str, str]]:
        query_items: list[dict[str, str]] = []
        for parameter in parameters:
            if not isinstance(parameter, dict):
                continue
            if parameter.get("in") != "query":
                continue
            name = parameter.get("name")
            if not isinstance(name, str):
                continue
            sample = self._sample_from_parameter(parameter)
            query_items.append({"key": name, "value": str(sample)})
        return query_items

    def _query_string(self, query_items: list[dict[str, str]]) -> str:
        if not query_items:
            return ""
        parts = [f"{item['key']}={item['value']}" for item in query_items]
        return f"?{'&'.join(parts)}"

    def _extract_json_request_body(
        self, operation: dict[str, Any], components: dict[str, Any]
    ) -> dict[str, Any] | list[Any] | str | int | float | bool | None:
        request_body = operation.get("requestBody")
        if not isinstance(request_body, dict):
            return None
        content = request_body.get("content", {})
        if not isinstance(content, dict):
            return None
        media = content.get("application/json")
        if not isinstance(media, dict):
            # Explicitly skip form-data and non-JSON media types for now.
            return None
        schema = media.get("schema", {})
        if not isinstance(schema, dict):
            return None
        return self._sample_from_schema(schema, components)

    def _sample_from_parameter(self, parameter: dict[str, Any]) -> Any:
        if "example" in parameter:
            return parameter["example"]
        schema = parameter.get("schema", {})
        if isinstance(schema, dict):
            return self._sample_from_schema(schema, {})
        return "value"

    def _sample_from_schema(
        self, schema: dict[str, Any], components: dict[str, Any]
    ) -> Any:
        if "example" in schema:
            return schema["example"]
        if "default" in schema:
            return schema["default"]

        ref = schema.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            name = ref.split("/")[-1]
            target = components.get("schemas", {}).get(name, {})
            if isinstance(target, dict):
                return self._sample_from_schema(target, components)

        schema_type = schema.get("type")
        if schema_type == "object":
            properties = schema.get("properties", {})
            if not isinstance(properties, dict):
                return {}
            required = schema.get("required", [])
            if not isinstance(required, list):
                required = []
            result: dict[str, Any] = {}
            picked = set(required)
            if not picked:
                picked = set(list(properties.keys())[:3])
            for key in picked:
                value_schema = properties.get(key, {})
                if isinstance(value_schema, dict):
                    result[key] = self._sample_from_schema(value_schema, components)
            return result
        if schema_type == "array":
            items = schema.get("items", {})
            if isinstance(items, dict):
                return [self._sample_from_schema(items, components)]
            return []
        if schema_type == "integer":
            return 1
        if schema_type == "number":
            return 1.0
        if schema_type == "boolean":
            return True
        if schema_type == "string":
            enum_values = schema.get("enum")
            if isinstance(enum_values, list) and enum_values:
                return enum_values[0]
            if schema.get("format") == "date-time":
                return "2026-01-01T00:00:00Z"
            return "string"
        return "value"

    def clear_memory(self) -> None:
        """Clear in-memory route and cURL registry."""
        self._route_memory.clear()
        self._seen_keys.clear()
