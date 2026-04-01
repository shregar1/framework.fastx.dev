"""Generates Postman Collection v2.1 ``event`` scripts for API regression tests."""

from __future__ import annotations

import json
import os
import re
import uuid
from typing import Any


class PostmanTestScriptEngine:
    """Builds ``prerequest`` / ``test`` script blocks from OpenAPI-derived hints."""

    @staticmethod
    def build_events(operation_spec: dict[str, Any]) -> list[dict[str, Any]]:
        """Return Postman ``event`` array for a single request item."""
        prereq = PostmanTestScriptEngine._prerequest_exec(operation_spec)
        tests = PostmanTestScriptEngine._test_exec(operation_spec)
        return [
            {
                "listen": "prerequest",
                "script": {
                    "id": PostmanTestScriptEngine._new_script_id(),
                    "type": "text/javascript",
                    "exec": prereq,
                },
            },
            {
                "listen": "test",
                "script": {
                    "id": PostmanTestScriptEngine._new_script_id(),
                    "type": "text/javascript",
                    "exec": tests,
                },
            },
        ]

    @staticmethod
    def _new_script_id() -> str:
        """Unique id per script block (Postman accepts any string on import)."""
        return str(uuid.uuid4())

    @staticmethod
    def _prerequest_exec(spec: dict[str, Any]) -> list[str]:
        name_js = json.dumps(spec.get("display_name") or "request")
        oid = spec.get("operation_id")
        path_js = json.dumps(spec.get("openapi_path") or "")
        method_js = json.dumps(str(spec.get("method") or "GET").upper())
        if oid:
            oid_js = json.dumps(oid)
            oid_line = f"console.info('[FastMVC] ' + {method_js} + ' ' + {path_js} + ' — ' + {name_js} + ' — operationId: ' + {oid_js});"
        else:
            oid_line = f"console.info('[FastMVC] ' + {method_js} + ' ' + {path_js} + ' — ' + {name_js});"
        return [
            "// FastMVC — auto-generated prerequest (imported with collection)",
            oid_line,
            "pm.request.headers.upsert({ key: 'Accept', value: 'application/json' });",
            "(function () {",
            "    const u = pm.request.url && pm.request.url.toString ? pm.request.url.toString() : '';",
            "    if (!u || u.length < 4) { console.error('[FastMVC] Missing or invalid request URL'); }",
            "}());",
            "(function () {",
            "    const m = pm.request.method;",
            "    if (!m || typeof m !== 'string') { console.error('[FastMVC] Missing HTTP method'); }",
            "}());",
        ]

    @staticmethod
    def _test_exec(spec: dict[str, Any]) -> list[str]:
        display = spec.get("display_name") or "Request"
        label_js = json.dumps(display)
        method = str(spec.get("method") or "GET").upper()
        method_js = json.dumps(method)
        success_codes = spec.get("success_response_codes") or [200]
        success_codes_js = json.dumps(success_codes)
        all_codes = spec.get("response_codes") or success_codes
        all_codes_js = json.dumps(all_codes)
        required_keys: list[str] = spec.get("response_required_keys") or []
        required_keys_js = json.dumps(required_keys)
        prop_types: dict[str, str] = spec.get("response_property_types") or {}
        prop_types_js = json.dumps(prop_types)
        root_kind = spec.get("response_json_root_kind") or "unknown"
        root_kind_js = json.dumps(root_kind)
        primary_code = spec.get("primary_success_code")
        primary_code_js = json.dumps(primary_code)
        needs_bearer = bool(spec.get("needs_bearer"))
        needs_bearer_js = "true" if needs_bearer else "false"
        no_body_codes_js = json.dumps([204, 304])

        # Build as single exec array; Postman concatenates lines.
        lines = [
            "// FastMVC — exhaustive auto-generated tests (Collection Runner)",
            f"const __label = {label_js};",
            f"const __method = {method_js};",
            f"const __successCodes = {success_codes_js};",
            f"const __documentedCodes = {all_codes_js};",
            f"const __noBodyCodes = {no_body_codes_js};",
            f"const __requiredKeys = {required_keys_js};",
            f"const __propTypes = {prop_types_js};",
            f"const __rootKind = {root_kind_js};",
            f"const __primarySuccess = {primary_code_js};",
            f"const __needsBearer = {needs_bearer_js};",
            "",
            "pm.test(__label + ': HTTP status is a valid code', function () {",
            "    const c = pm.response.code;",
            "    pm.expect(c).to.be.a('number');",
            "    pm.expect(c).to.be.at.least(100);",
            "    pm.expect(c).to.be.below(600);",
            "});",
            "",
            "pm.test(__label + ': response time under SLA (15s)', function () {",
            "    pm.expect(pm.response.responseTime).to.be.below(15000);",
            "});",
            "",
            "pm.test(__label + ': response time soft budget (5s) — informational', function () {",
            "    const t = pm.response.responseTime;",
            "    if (t > 5000) {",
            "        console.warn('[FastMVC] Slow response ' + t + 'ms for ' + __label);",
            "    }",
            "    pm.expect(t).to.be.a('number');",
            "});",
            "",
            "pm.test(__label + ': status is among OpenAPI-documented responses', function () {",
            "    if (__documentedCodes.length === 0) { pm.expect.fail('No response codes in OpenAPI'); }",
            "    pm.expect(__documentedCodes, 'got ' + pm.response.code).to.include(pm.response.code);",
            "});",
            "",
            "pm.test(__label + ': single declared success code matches response', function () {",
            "    if (__primarySuccess === null || __primarySuccess === undefined) return;",
            "    if (__successCodes.length !== 1) return;",
            "    pm.expect(pm.response.code).to.eql(__primarySuccess);",
            "});",
            "",
            "pm.test(__label + ': any 2xx returned is listed as success in OpenAPI', function () {",
            "    const c = pm.response.code;",
            "    if (c < 200 || c >= 300) return;",
            "    pm.expect(__successCodes, 'unexpected 2xx ' + c).to.include(c);",
            "});",
            "",
            "pm.test(__label + ': no HTML error page when JSON expected (2xx)', function () {",
            "    if (!__successCodes.includes(pm.response.code)) return;",
            "    if (__noBodyCodes.includes(pm.response.code)) return;",
            "    const raw = (pm.response.text() || '').trim();",
            "    pm.expect(raw.startsWith('<'), 'body looks like HTML').to.be.false;",
            "});",
            "",
            "pm.test(__label + ': JSON body or empty for no-content codes', function () {",
            "    if (__noBodyCodes.includes(pm.response.code)) {",
            "        const t = pm.response.text();",
            "        pm.expect(t === '' || t === undefined || t === null).to.be.true;",
            "        return;",
            "    }",
            "    pm.response.to.have.jsonBody();",
            "});",
            "",
            "pm.test(__label + ': JSON parses without throw (2xx with body)', function () {",
            "    if (!__successCodes.includes(pm.response.code)) return;",
            "    if (__noBodyCodes.includes(pm.response.code)) return;",
            "    let parsed;",
            "    pm.expect(function () { parsed = pm.response.json(); }).to.not.throw();",
            "    pm.expect(parsed).to.not.eql(undefined);",
            "});",
            "",
            "pm.test(__label + ': Content-Type declares JSON when body present', function () {",
            "    if (__noBodyCodes.includes(pm.response.code)) return;",
            "    const ct = (pm.response.headers.get('Content-Type') || '').toLowerCase();",
            "    pm.expect(ct, 'Content-Type').to.include('json');",
            "});",
            "",
            "pm.test(__label + ': response has non-zero size when body expected', function () {",
            "    if (__noBodyCodes.includes(pm.response.code)) return;",
            "    pm.expect(pm.response.responseSize, 'responseSize').to.be.above(0);",
            "});",
            "",
            "pm.test(__label + ': root JSON kind (OpenAPI)', function () {",
            "    if (!__successCodes.includes(pm.response.code)) return;",
            "    if (__noBodyCodes.includes(pm.response.code)) return;",
            "    const body = pm.response.json();",
            "    if (__rootKind === 'array') {",
            "        pm.expect(body).to.be.an('array');",
            "    } else if (__rootKind === 'object') {",
            "        pm.expect(body).to.be.an('object');",
            "        pm.expect(body).to.not.be.an('array');",
            "    }",
            "});",
            "",
            "pm.test(__label + ': required top-level keys (OpenAPI)', function () {",
            "    if (!__successCodes.includes(pm.response.code)) return;",
            "    if (__noBodyCodes.includes(pm.response.code)) return;",
            "    const body = pm.response.json();",
            "    if (!body || typeof body !== 'object' || Array.isArray(body)) return;",
            "    __requiredKeys.forEach(function (k) {",
            "        pm.expect(body, 'missing required key: ' + k).to.have.property(k);",
            "    });",
            "});",
            "",
            "pm.test(__label + ': top-level property types (OpenAPI, when key present)', function () {",
            "    if (!__successCodes.includes(pm.response.code)) return;",
            "    if (__noBodyCodes.includes(pm.response.code)) return;",
            "    const body = pm.response.json();",
            "    if (!body || typeof body !== 'object' || Array.isArray(body)) return;",
            "    Object.keys(__propTypes).forEach(function (k) {",
            "        if (!Object.prototype.hasOwnProperty.call(body, k)) return;",
            "        const v = body[k];",
            "        const t = __propTypes[k];",
            "        if (v === null || v === undefined) return;",
            "        if (t === 'string') pm.expect(v, k).to.be.a('string');",
            "        else if (t === 'integer' || t === 'number') pm.expect(v, k).to.be.a('number');",
            "        else if (t === 'boolean') pm.expect(v, k).to.be.a('boolean');",
            "        else if (t === 'array') pm.expect(v, k).to.be.an('array');",
            "        else if (t === 'object') pm.expect(v, k).to.be.an('object');",
            "    });",
            "});",
            "",
            "pm.test(__label + ': FastMVC API envelope (when fields present)', function () {",
            "    if (!__successCodes.includes(pm.response.code)) return;",
            "    if (__noBodyCodes.includes(pm.response.code)) return;",
            "    let body;",
            "    try { body = pm.response.json(); } catch (e) { return; }",
            "    if (!body || typeof body !== 'object' || Array.isArray(body)) return;",
            "    if ('transactionUrn' in body) pm.expect(body.transactionUrn).to.be.a('string');",
            "    if ('status' in body) pm.expect(body.status).to.be.a('string');",
            "    if ('responseKey' in body) pm.expect(body.responseKey).to.be.a('string');",
            "    if ('responseMessage' in body) pm.expect(body.responseMessage).to.be.a('string');",
            "    if ('data' in body) pm.expect(body.data !== undefined).to.be.true;",
            "});",
            "",
            "pm.test(__label + ': 4xx/5xx error payload is JSON with diagnostic fields', function () {",
            "    const c = pm.response.code;",
            "    if (c < 400) return;",
            "    pm.response.to.have.jsonBody();",
            "    const b = pm.response.json();",
            "    pm.expect(b).to.be.an('object');",
            "    const diag = ['errors', 'detail', 'message', 'responseMessage', 'responseKey', 'msg', 'error', 'title', 'type'];",
            "    const ok = diag.some(function (k) { return Object.prototype.hasOwnProperty.call(b, k); });",
            "    pm.expect(ok, 'error body should include a known diagnostic field').to.be.true;",
            "});",
            "",
            "pm.test(__label + ': correlation / security headers sanity', function () {",
            "    const h = pm.response.headers;",
            "    const pick = function (name) { return h.get(name) || h.get(name.toLowerCase()) || h.get(name.toUpperCase()); };",
            "    const txn = pick('x-transaction-urn') || pick('X-Transaction-URN');",
            "    if (__successCodes.includes(pm.response.code) && txn) {",
            "        pm.expect(txn).to.be.a('string').and.not.empty;",
            "    }",
            "    const ref = pick('x-reference-urn') || pick('X-Reference-URN');",
            "    if (__successCodes.includes(pm.response.code) && ref) {",
            "        pm.expect(ref).to.be.a('string');",
            "    }",
            "    if (__needsBearer && (pm.response.code === 401 || pm.response.code === 403)) {",
            "        const bodyLen = pm.response.text().length;",
            "        const www = pm.response.headers.get('WWW-Authenticate') || pm.response.headers.get('www-authenticate');",
            "        pm.expect(bodyLen >= 1 || !!www, '401/403 should include body or WWW-Authenticate').to.be.true;",
            "    }",
            "});",
            "",
        ]

        if method in ("POST", "PUT", "PATCH", "DELETE"):
            lines.extend(
                [
                    "pm.test(__label + ': mutating method uses documented status', function () {",
                    "    pm.expect(__documentedCodes).to.include(pm.response.code);",
                    "});",
                    "",
                ]
            )

        lines.extend(PostmanTestScriptEngine._negative_request_variation_tests(spec))
        return lines

    @staticmethod
    def _negative_request_variation_tests(spec: dict[str, Any]) -> list[str]:
        """Extra ``pm.sendRequest`` checks: null/empty/malformed body, auth, query, path."""
        flag = os.getenv("POSTMAN_NEGATIVE_TESTS", "true").strip().lower()
        if flag in ("0", "false", "no", "off"):
            return []

        method = str(spec.get("method") or "GET").upper()
        needs_bearer = bool(spec.get("needs_bearer"))
        has_json = bool(spec.get("negative_has_json_body"))
        sample_is_object = isinstance(spec.get("json_body"), dict)
        jb = spec.get("json_body") if isinstance(spec.get("json_body"), dict) else {}
        body_literal = json.dumps(jb)
        req_root = spec.get("request_body_root_kind") or "unknown"
        req_body_required = spec.get("request_body_required_keys") or []
        required_query = spec.get("required_query_names") or []
        query_keys = spec.get("query_keys_for_negatives") or []
        openapi_path = spec.get("openapi_path") or ""

        lines: list[str] = [
            "",
            "// --- FastMVC negative / generic validation (pm.sendRequest) ---",
            "(function () {",
            "    function __negHeaders() {",
            "        const out = [];",
            "        pm.request.headers.each(function (h) {",
            "            if (h && h.key && h.disabled !== true) { out.push({ key: h.key, value: h.value }); }",
            "        });",
            "        return out;",
            "    }",
            "    function __negSend(title, opts, check) {",
            "        pm.test(__label + ' [NEG] ' + title, function (done) {",
            "            const base = {",
            "                url: pm.request.url.toString(),",
            "                method: pm.request.method,",
            "                header: __negHeaders(),",
            "            };",
            "            pm.sendRequest(Object.assign(base, opts), function (err, res) {",
            "                try {",
            "                    if (err) { console.warn('[FastMVC NEG] ' + title + ': ' + err); }",
            "                    check(err, res);",
            "                } finally { done(); }",
            "            });",
            "        });",
            "    }",
            "    function __dropQueryKey(urlStr, key) {",
            "        const q = urlStr.indexOf('?');",
            "        if (q < 0) return urlStr;",
            "        const base = urlStr.slice(0, q);",
            "        const sp = new URLSearchParams(urlStr.slice(q + 1));",
            "        sp.delete(key);",
            "        const s = sp.toString();",
            "        return s ? base + '?' + s : base;",
            "    }",
            "    function __setQueryKey(urlStr, key, val) {",
            "        const q = urlStr.indexOf('?');",
            "        const base = q < 0 ? urlStr : urlStr.slice(0, q);",
            "        const sp = new URLSearchParams(q < 0 ? '' : urlStr.slice(q + 1));",
            "        sp.set(key, val);",
            "        const s = sp.toString();",
            "        return s ? base + '?' + s : base;",
            "    }",
            "    function __mangleLastPathSegment(urlStr) {",
            "        const q = urlStr.indexOf('?');",
            "        const main = q < 0 ? urlStr : urlStr.slice(0, q);",
            "        const qs = q < 0 ? '' : urlStr.slice(q);",
            "        const last = main.lastIndexOf('/');",
            "        if (last < 0 || last >= main.length - 1) return urlStr;",
            "        return main.slice(0, last + 1) + '___invalid_path_segment___' + qs;",
            "    }",
            f"    const __negBodySample = {body_literal};",
        ]

        if needs_bearer:
            lines.extend(
                [
                    "    __negSend('auth: missing Authorization header', {",
                    "        header: __negHeaders().filter(function (h) {",
                    "            return String(h.key).toLowerCase() !== 'authorization';",
                    "        }),",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code).to.be.oneOf([401, 403]);",
                    "    });",
                ]
            )

        if openapi_path.strip() not in ("", "/"):
            lines.extend(
                [
                    "    __negSend('path: invalid final segment', {",
                    "        url: __mangleLastPathSegment(pm.request.url.toString()),",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code).to.be.at.least(400);",
                    "    });",
                ]
            )

        for qn in required_query[:4]:
            qn_js = json.dumps(qn)
            lines.extend(
                [
                    f"    __negSend('query: omit required param {qn_js}', {{",
                    "        url: __dropQueryKey(pm.request.url.toString(), "
                    + qn_js
                    + "),",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code).to.be.at.least(400);",
                    "    });",
                ]
            )

        for qk in query_keys[:4]:
            qk_js = json.dumps(qk)
            lines.extend(
                [
                    f"    __negSend('query: empty string for {qk_js}', {{",
                    "        url: __setQueryKey(pm.request.url.toString(), "
                    + qk_js
                    + ", ''),",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code, 'empty query param').to.be.below(500);",
                    "    });",
                ]
            )

        if query_keys:
            q0_js = json.dumps(query_keys[0])
            lines.extend(
                [
                    "    __negSend('query: wrong-type probe (non-numeric string)', {",
                    "        url: __setQueryKey(pm.request.url.toString(), "
                    + q0_js
                    + ", 'not-a-number'),",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code, 'wrong-type query').to.be.below(500);",
                    "    });",
                ]
            )

        if method in ("POST", "PUT", "PATCH") and has_json:
            lines.extend(
                [
                    "    __negSend('JSON: no payload (empty raw body)', {",
                    "        body: { mode: 'raw', raw: '' },",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code).to.be.at.least(400);",
                    "    });",
                    "    __negSend('JSON: whitespace-only body', {",
                    "        body: { mode: 'raw', raw: '   \\n\\t  ' },",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code).to.be.at.least(400);",
                    "    });",
                    "    __negSend('JSON: malformed (truncated)', {",
                    "        body: { mode: 'raw', raw: '{\"x\":' },",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code).to.be.at.least(400);",
                    "    });",
                    "    __negSend('JSON: literal null only', {",
                    "        body: { mode: 'raw', raw: 'null' },",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code).to.be.at.least(400);",
                    "    });",
                    "    __negSend('JSON: string primitive instead of object', {",
                    "        body: { mode: 'raw', raw: '\"not-an-object\"' },",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code).to.be.at.least(400);",
                    "    });",
                    "    __negSend('Content-Type text/plain with JSON-looking body', {",
                    "        header: __negHeaders().filter(function (h) {",
                    "            return String(h.key).toLowerCase() !== 'content-type';",
                    "        }).concat([{ key: 'Content-Type', value: 'text/plain' }]),",
                    "        body: { mode: 'raw', raw: '{}' },",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code).to.be.at.least(400);",
                    "    });",
                ]
            )
            if req_root == "object":
                lines.extend(
                    [
                        "    __negSend('JSON: array root instead of object', {",
                        "        body: { mode: 'raw', raw: '[]' },",
                        "    }, function (e, r) {",
                        "        pm.expect(r.code).to.be.at.least(400);",
                        "    });",
                    ]
                )
            if req_root == "array":
                lines.extend(
                    [
                        "    __negSend('JSON: object root instead of array', {",
                        "        body: { mode: 'raw', raw: '{}' },",
                        "    }, function (e, r) {",
                        "        pm.expect(r.code).to.be.at.least(400);",
                        "    });",
                    ]
                )

        if method in ("POST", "PUT", "PATCH") and has_json and sample_is_object:
            for rk in req_body_required[:5]:
                rk_js = json.dumps(rk)
                lines.extend(
                    [
                        "    __negSend('JSON: omit required field ' + " + rk_js + ", {",
                        "        body: {",
                        "            mode: 'raw',",
                        "            raw: JSON.stringify((function () {",
                        "                const o = JSON.parse(JSON.stringify(__negBodySample));",
                        f"                delete o[{rk_js}];",
                        "                return o;",
                        "            })()),",
                        "        },",
                        "    }, function (e, r) {",
                        "        pm.expect(r.code).to.be.at.least(400);",
                        "    });",
                    ]
                )

        if method in ("POST", "PUT", "PATCH") and has_json and sample_is_object:
            lines.extend(
                [
                    "    __negSend('JSON: null value for first required-like key', {",
                    "        body: {",
                    "            mode: 'raw',",
                    "            raw: JSON.stringify((function () {",
                    "                const o = JSON.parse(JSON.stringify(__negBodySample));",
                    "                const keys = Object.keys(o);",
                    "                if (keys.length) { o[keys[0]] = null; }",
                    "                return o;",
                    "            })()),",
                    "        },",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code).to.be.at.least(400);",
                    "    });",
                    "    __negSend('JSON: empty string for first string-like key', {",
                    "        body: {",
                    "            mode: 'raw',",
                    "            raw: JSON.stringify((function () {",
                    "                const o = JSON.parse(JSON.stringify(__negBodySample));",
                    "                Object.keys(o).forEach(function (k) {",
                    "                    if (typeof o[k] === 'string') { o[k] = ''; }",
                    "                });",
                    "                return o;",
                    "            })()),",
                    "        },",
                    "    }, function (e, r) {",
                    "        pm.expect(r.code).to.be.at.least(400);",
                    "    });",
                ]
            )

        lines.append("}());")
        return lines

    @staticmethod
    def build_collection_events(collection_title: str) -> list[dict[str, Any]]:
        """Root-level collection ``event`` scripts (imported with the collection)."""
        title_js = json.dumps(collection_title)
        prereq = [
            "// FastMVC — collection prerequest",
            f"console.info('[FastMVC] Collection: ' + {title_js});",
            "if (!pm.environment.get('base_url') && !pm.collectionVariables.get('base_url')) {",
            "    console.warn('[FastMVC] Set base_url in the active environment.');",
            "}",
        ]
        coll_test = [
            "// FastMVC — collection-level test hook (runs after each request in Runner)",
            "// Per-request tests live on each request item.",
        ]
        return [
            {
                "listen": "prerequest",
                "script": {
                    "type": "text/javascript",
                    "exec": prereq,
                },
            },
            {
                "listen": "test",
                "script": {
                    "type": "text/javascript",
                    "exec": coll_test,
                },
            },
        ]


def extract_openapi_response_codes(operation: dict[str, Any]) -> list[int]:
    """Collect numeric HTTP status codes from an OpenAPI operation ``responses`` map."""
    codes: list[int] = []
    responses = operation.get("responses")
    if not isinstance(responses, dict):
        return codes
    for key in responses:
        if key == "default":
            continue
        m = re.match(r"^(\d{3})", str(key).strip())
        if m:
            codes.append(int(m.group(1)))
    return sorted(set(codes))


def success_response_codes(codes: list[int]) -> list[int]:
    """Prefer documented 2xx; if none, treat all documented codes as acceptable."""
    ok = [c for c in codes if 200 <= c < 300]
    if ok:
        return ok
    return codes if codes else [200]


def _openapi_property_type(prop_schema: Any, components: dict[str, Any]) -> str | None:
    """Map a JSON Schema property sub-schema to a simple OpenAPI ``type`` string."""
    if not isinstance(prop_schema, dict):
        return None
    t = prop_schema.get("type")
    if isinstance(t, list):
        for x in t:
            if x != "null" and isinstance(x, str):
                t = x
                break
        else:
            t = None
    if isinstance(t, str) and t != "null":
        return t
    ref = prop_schema.get("$ref")
    if isinstance(ref, str):
        resolved = _resolve_schema({"$ref": ref}, components)
        if isinstance(resolved, dict):
            return _openapi_property_type(resolved, components)
    if prop_schema.get("properties"):
        return "object"
    if prop_schema.get("items"):
        return "array"
    return None


def collect_success_response_schema_hints(
    operation: dict[str, Any], components: dict[str, Any], *, max_props: int = 28
) -> dict[str, Any]:
    """Merge hints from 200/201/202/203 ``application/json`` success response schemas."""
    required_order: list[str] = []
    seen_r: set[str] = set()
    prop_types: dict[str, str] = {}
    root_kind = "unknown"

    responses = operation.get("responses")
    if not isinstance(responses, dict):
        return {"required_keys": [], "property_types": {}, "root_kind": "unknown"}

    for status in ("200", "201", "202", "203"):
        block = responses.get(status)
        if not isinstance(block, dict):
            continue
        content = block.get("content")
        if not isinstance(content, dict):
            continue
        media = content.get("application/json")
        if not isinstance(media, dict):
            continue
        schema = media.get("schema")
        if not isinstance(schema, dict):
            continue
        resolved = _resolve_schema(schema, components)
        if not isinstance(resolved, dict):
            continue

        rt = resolved.get("type")
        if isinstance(rt, list):
            rt = next((x for x in rt if x != "null"), None)
        if rt == "array":
            root_kind = "array"
        elif rt == "object" or isinstance(resolved.get("properties"), dict):
            if root_kind != "array":
                root_kind = "object"

        req = resolved.get("required")
        if isinstance(req, list):
            for k in req:
                if isinstance(k, str) and k not in seen_r:
                    seen_r.add(k)
                    required_order.append(k)

        props = resolved.get("properties")
        if isinstance(props, dict):
            for pk, sub in props.items():
                if len(prop_types) >= max_props:
                    break
                if pk in prop_types:
                    continue
                ot = _openapi_property_type(sub, components)
                if ot in ("string", "integer", "number", "boolean", "array", "object"):
                    prop_types[pk] = ot

    return {
        "required_keys": required_order,
        "property_types": prop_types,
        "root_kind": root_kind,
    }


def _resolve_schema(
    schema: dict[str, Any], components: dict[str, Any]
) -> dict[str, Any] | None:
    ref = schema.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
        name = ref.rsplit("/", 1)[-1]
        target = components.get("schemas", {}).get(name)
        if isinstance(target, dict):
            return _resolve_schema(target, components) or target
    return schema


def openapi_has_json_request_body(operation: dict[str, Any]) -> bool:
    rb = operation.get("requestBody")
    if not isinstance(rb, dict):
        return False
    content = rb.get("content")
    return isinstance(content, dict) and "application/json" in content


def extract_json_request_body_required_keys(
    operation: dict[str, Any], components: dict[str, Any]
) -> list[str]:
    rb = operation.get("requestBody")
    if not isinstance(rb, dict):
        return []
    content = rb.get("content")
    if not isinstance(content, dict):
        return []
    media = content.get("application/json")
    if not isinstance(media, dict):
        return []
    schema = media.get("schema")
    if not isinstance(schema, dict):
        return []
    resolved = _resolve_schema(schema, components)
    if not isinstance(resolved, dict):
        return []
    req = resolved.get("required")
    if isinstance(req, list):
        return [str(x) for x in req if isinstance(x, str)]
    return []


def extract_request_body_root_kind(
    operation: dict[str, Any], components: dict[str, Any]
) -> str:
    rb = operation.get("requestBody")
    if not isinstance(rb, dict):
        return "unknown"
    content = rb.get("content")
    if not isinstance(content, dict):
        return "unknown"
    media = content.get("application/json")
    if not isinstance(media, dict):
        return "unknown"
    schema = media.get("schema")
    if not isinstance(schema, dict):
        return "unknown"
    resolved = _resolve_schema(schema, components)
    if not isinstance(resolved, dict):
        return "unknown"
    rt = resolved.get("type")
    if isinstance(rt, list):
        rt = next((x for x in rt if x != "null"), None)
    if rt == "array":
        return "array"
    if rt == "object" or isinstance(resolved.get("properties"), dict):
        return "object"
    return "unknown"


def extract_required_query_parameter_names(
    operation: dict[str, Any], path_level_parameters: list[Any] | None
) -> list[str]:
    merged: list[Any] = []
    if isinstance(path_level_parameters, list):
        merged.extend(path_level_parameters)
    op_params = operation.get("parameters")
    if isinstance(op_params, list):
        merged.extend(op_params)
    out: list[str] = []
    for p in merged:
        if not isinstance(p, dict):
            continue
        if p.get("in") != "query":
            continue
        if p.get("required") is True:
            n = p.get("name")
            if isinstance(n, str):
                out.append(n)
    return out


def enrich_operation_spec_for_tests(
    spec: dict[str, Any],
    openapi_operation: dict[str, Any],
    components: dict[str, Any],
    path_level_parameters: list[Any] | None = None,
) -> dict[str, Any]:
    """Mutate ``spec`` with fields consumed by :class:`PostmanTestScriptEngine`."""
    codes = extract_openapi_response_codes(openapi_operation)
    if not codes:
        codes = [200]
    spec["response_codes"] = codes
    s_codes = success_response_codes(codes)
    spec["success_response_codes"] = s_codes
    spec["primary_success_code"] = s_codes[0] if len(s_codes) == 1 else None

    hints = collect_success_response_schema_hints(openapi_operation, components)
    spec["response_required_keys"] = hints["required_keys"]
    spec["response_property_types"] = hints["property_types"]
    spec["response_json_root_kind"] = hints["root_kind"]

    spec["negative_has_json_body"] = openapi_has_json_request_body(openapi_operation)
    spec["request_body_required_keys"] = extract_json_request_body_required_keys(
        openapi_operation, components
    )[:6]
    spec["request_body_root_kind"] = extract_request_body_root_kind(
        openapi_operation, components
    )
    spec["required_query_names"] = extract_required_query_parameter_names(
        openapi_operation, path_level_parameters
    )[:5]
    qi = spec.get("query_items") or []
    spec["query_keys_for_negatives"] = [
        str(x["key"]) for x in qi if isinstance(x, dict) and "key" in x
    ][:5]
    return spec
