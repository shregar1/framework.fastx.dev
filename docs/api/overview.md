# API Overview

FastMVC provides a comprehensive REST API with automatic documentation.

## I URL

```text
http://localhost:8000
```

## Authentication

The example API uses Bearer token authentication:

```bash
curl http://localhost:8000/items \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Content Type

All requests should include:

```http
Content-Type: application/json
```

## Response format (`IResponseDTO`)

Many endpoints return the standard envelope from `dtos.responses.I.IResponseDTO`:

| Field | Description |
|-------|-------------|
| `transactionUrn` | Server request / trace id (from request context) |
| `status` | `SUCCESS` or `FAILED` (`constants.api_status.APIStatus`) |
| `responseMessage` | Human-readable summary |
| `responseKey` | Machine-readable key (i18n / clients) |
| `data` | Main payload (object or list) |
| `errors` | Present when `status` is `FAILED` |
| `metadata` | Optional cross-cutting metadata |
| `timestamp` | UTC time the envelope was generated |
| `referenceUrn` | Echo of client correlation id when provided (e.g. request body `reference_number`) |

Clients may also send and receive correlation via the **`x-reference-urn`** header (echoed on responses when set).

Example (success):

```json
{
  "transactionUrn": "urn:req:abc123",
  "status": "SUCCESS",
  "responseMessage": "Operation completed",
  "responseKey": "success_example_created",
  "data": {},
  "errors": null,
  "metadata": null,
  "timestamp": "2024-01-15T12:00:00Z",
  "referenceUrn": null
}
```

Item-style JSON responses that return only resource fields may omit the full envelope; health endpoints (below) use the envelope consistently.

## Error Format

Error responses follow this format:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Success |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Validation Error - Invalid data |
| 500 | Server Error - Internal error |

## Pagination

List endpoints support pagination:

```bash
GET /items?skip=0&limit=10
```

Response includes:

```json
{
  "data": [...],
  "total": 100,
  "skip": 0,
  "limit": 10
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- 100 requests per minute per IP
- 1000 requests per hour per API key

Rate limit headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Health endpoints

`GET /health`, `GET /health/live`, and `GET /health/ready` return the same **`IResponseDTO`** envelope as other API surfaces. Operational details live in **`data`**; `status` is `SUCCESS` or `FAILED`; HTTP status is `200` or `503` when dependencies fail.

### GET /health

Comprehensive health check with dependency status.

**Response (healthy, abbreviated):**

```json
{
  "transactionUrn": "urn:req:…",
  "status": "SUCCESS",
  "responseMessage": "All dependencies report healthy.",
  "responseKey": "success_health",
  "data": {
    "status": "healthy",
    "version": "1.5.0",
    "timestamp": "2024-01-01T00:00:00+00:00",
    "database": "connected",
    "redis": "connected",
    "uptimeSeconds": 3600
  },
  "errors": null,
  "metadata": null,
  "timestamp": "2024-01-01T12:00:00+00:00",
  "referenceUrn": null
}
```

**HTTP status codes:** `200` all healthy, `503` one or more dependencies unhealthy.

### GET /health/live

Kubernetes liveness probe. **`data.status`** is `"alive"`.

### GET /health/ready

Kubernetes readiness probe. **`data`** includes `status` (`ready` / `not_ready`), `checkedAt`, and `checks` (e.g. `database`, `redis`).

**HTTP status codes:** `200` ready, `503` not ready.

For restricting **Swagger / ReDoc / OpenAPI** to developers, see [API Documentation](../guide/api-docs.md) (section *Securing Swagger, ReDoc, and OpenAPI*).
