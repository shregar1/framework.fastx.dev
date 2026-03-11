# Middlewares

## Overview

FastMVC leverages the **[fastmvc-middleware](https://pypi.org/project/fastmvc-middleware/)** package - a comprehensive collection of **90+ production-ready middleware components** for FastAPI/Starlette applications.

This directory also contains app-specific middlewares (like custom JWT authentication) that integrate with your application's user repository and business logic.

## 🚀 Quick Start

```python
from fastmiddleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestContextMiddleware,
    TimingMiddleware,
    LoggingMiddleware,
    CORSMiddleware,
)

# Add to your FastAPI app
app.add_middleware(SecurityHeadersMiddleware, config=security_config)
app.add_middleware(RateLimitMiddleware, config=rate_limit_config)
app.add_middleware(RequestContextMiddleware)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     HTTP Request                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               RequestContextMiddleware                       │
│              (Add URN, timestamp)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 TimingMiddleware                             │
│           (Track response time)                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                RateLimitMiddleware                           │
│           (Check rate limits, add headers)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              AuthenticationMiddleware                        │
│           (Validate JWT, set user context)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              SecurityHeadersMiddleware                       │
│           (Add CSP, HSTS, X-Frame-Options)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Route Handler                              │
└─────────────────────────────────────────────────────────────┘
```

## 📦 fastmiddleware Package Components

### Categories Available (90+ Middlewares)

| Category | Examples |
|----------|----------|
| **Core** | CORS, Logging, Timing, Request ID |
| **Security** | SecurityHeaders, CSRF, HTTPS Redirect, IP Filter, Honeypot, Sanitization |
| **Rate Limiting** | RateLimit, Quota, Load Shedding, Bulkhead, Request Dedup |
| **Authentication** | JWT Auth, API Key, Basic Auth, Bearer Auth, Route Auth |
| **Session & Context** | Session, Request Context, Correlation, Tenant, Context |
| **Caching** | Response Cache, ETag, Conditional Request, No Cache |
| **Resilience** | Circuit Breaker, Timeout, Graceful Shutdown, Retry After |
| **Observability** | Metrics, Profiling, Server Timing, Request Logger |
| **Content** | Compression, Content Negotiation, JSON Schema, Payload Size |
| **Routing** | Path Rewrite, Redirect, Trailing Slash, Method Override |

### Usage Example

```python
from fastmiddleware import (
    # Security
    SecurityHeadersMiddleware,
    SecurityHeadersConfig,
    CSRFMiddleware,
    IPFilterMiddleware,
    
    # Rate Limiting
    RateLimitMiddleware,
    RateLimitConfig,
    
    # Authentication
    AuthenticationMiddleware,
    JWTAuthBackend,
    
    # Observability
    LoggingMiddleware,
    TimingMiddleware,
    MetricsMiddleware,
    
    # Context
    RequestContextMiddleware,
    CorrelationMiddleware,
)

# Configure and add middlewares
security_config = SecurityHeadersConfig(
    enable_hsts=True,
    hsts_max_age=31536000,
    x_frame_options="DENY",
    content_security_policy="default-src 'self'",
)
app.add_middleware(SecurityHeadersMiddleware, config=security_config)

rate_config = RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=1000,
    strategy="sliding",
)
app.add_middleware(RateLimitMiddleware, config=rate_config)
```

## 🏠 Local Middlewares

This directory contains app-specific middlewares that require application logic:

### AuthenticationMiddleware (`authetication.py`)

Custom JWT authentication that integrates with your user repository.

```python
from middlewares.authetication import AuthenticationMiddleware

app.add_middleware(AuthenticationMiddleware)
```

**Features:**
- Skips unprotected routes and OPTIONS requests
- Validates JWT from Authorization header
- Verifies user is logged in via database
- Sets `request.state.user_id` and `request.state.user_urn`
- Returns 401 Unauthorized for invalid/missing tokens

**Error Response:**
```json
{
    "transactionUrn": "...",
    "status": "FAILED",
    "responseMessage": "JWT Authentication failed.",
    "responseKey": "error_authetication_error"
}
```

### RequestContextMiddleware (`request_context.py`)

Local implementation for request tracking (can use fastmiddleware version instead).

```python
from middlewares.request_context import RequestContextMiddleware

app.add_middleware(RequestContextMiddleware)
```

**Features:**
- Generates ULID-based URN for each request
- Adds `request.state.urn` for downstream access
- Tracks request start time
- Adds `X-Process-Time` and `X-Request-URN` response headers

### RateLimitMiddleware (`rate_limit.py`)

Local rate limiting implementation (can use fastmiddleware version instead).

```python
from middlewares.rate_limit import RateLimitMiddleware, RateLimitConfig

config = RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=1000,
    burst_limit=10
)

app.add_middleware(RateLimitMiddleware, config=config)
```

### SecurityHeadersMiddleware (`security_headers.py`)

Local security headers implementation (can use fastmiddleware version instead).

```python
from middlewares.security_headers import SecurityHeadersMiddleware

app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=True,
    enable_csp=True
)
```

## 🔧 Configuration

### SecurityHeadersConfig (fastmiddleware)

```python
from fastmiddleware import SecurityHeadersConfig

config = SecurityHeadersConfig(
    x_content_type_options="nosniff",
    x_frame_options="DENY",
    x_xss_protection="1; mode=block",
    referrer_policy="strict-origin-when-cross-origin",
    enable_hsts=True,
    hsts_max_age=31536000,
    hsts_include_subdomains=True,
    hsts_preload=False,
    content_security_policy="default-src 'self'",
    permissions_policy="camera=(), microphone=()",
    remove_server_header=True,
)
```

### RateLimitConfig (fastmiddleware)

```python
from fastmiddleware import RateLimitConfig

config = RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=1000,
    burst_limit=10,
    window_size=60,
    strategy="sliding",  # or "fixed", "token_bucket"
    key_func=None,  # Custom key function
)
```

## ⚙️ Protected vs Unprotected Routes

Routes are configured in `start_utils.py`:

```python
unprotected_routes = {
    "/user/login",
    "/user/register",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health"
}

callback_routes = set()  # Webhook endpoints
```

## 📁 File Structure

```
middlewares/
├── __init__.py
├── README.md
├── authetication.py       # Custom JWT auth (app-specific)
├── rate_limit.py          # Local rate limiting
├── request_context.py     # Local request context
└── security_headers.py    # Local security headers

# fastmiddleware package provides 90+ additional middlewares
# via: from fastmiddleware import ...
```

## 🔗 Resources

- [fastmvc-middleware on PyPI](https://pypi.org/project/fastmvc-middleware/)
- [fastmiddleware Documentation](https://github.com/shregar1/fastmvc-middleware)
- [FastAPI Middleware Guide](https://fastapi.tiangolo.com/tutorial/middleware/)
