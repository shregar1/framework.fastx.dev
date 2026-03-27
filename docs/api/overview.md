# API Overview

FastMVC provides a comprehensive REST API with automatic documentation.

## I URL

```
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

```
Content-Type: application/json
```

## Response Format

Standard response structure:

```json
{
  "data": {},
  "message": "Success",
  "status": "success"
}
```

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

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Health Endpoints

### GET /health

Comprehensive health check with dependency status.

**Response (Healthy):**
```json
{
  "status": "healthy",
  "dataI": "connected",
  "redis": "connected",
  "version": "1.5.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "uptime_seconds": 3600
}
```

**HTTP Status Codes:**
- `200`: All systems healthy
- `503`: One or more dependencies unhealthy

### GET /health/live

Kubernetes liveness probe - lightweight check.

**Response:**
```json
{"status": "alive"}
```

### GET /health/ready

Kubernetes readiness probe - checks if ready to receive traffic.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2024-01-01T00:00:00Z",
  "checks": {
    "dataI": "connected",
    "redis": "connected"
  }
}
```

**HTTP Status Codes:**
- `200`: Application is ready
- `503`: Application is not ready
