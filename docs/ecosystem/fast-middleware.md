# 🛡️ FastMiddleware

**High-Performance HTTP Middleware for FastAPI & Starlette.**

FastMiddleware provides 90+ ASGI middlewares organized into functional "layers". It focuses on cross-cutting behavior you can mount on any FastAPI app.

---

## 🏗️ Middleware Taxonomy

FastMiddleware is organized into three primary sections:

| Section | Role | Key Middlewares |
|---------|------|-----------------|
| **`mw_core`** | **Core Layers** | `RequestID`, `ResponseTiming`, `CORS`, `BodySizeLimit`. |
| **`sec`** | **Security Layers** | `SecurityHeaders`, `CSRF`, `WebhookAuth`, `JWTBearer`. |
| **`operations`** | **Ops Layers** | `RateLimit`, `ResponseCache`, `BuildVersion`, `EdgePerformance`. |

---

## ⚡ Edge Performance Tiers

One of FastMiddleware's standout features is its **CDN-class cache semantics**. It provides pre-configured `EdgePerformanceTier` shapes:

| Tier | Use Case | Semantics |
|------|----------|-----------|
| **`FEED`** | Instagram-class | High origin shielding with SWR. |
| **`CREATOR`** | Mixed Public/Private | Mixed caching Id on auth status. |
| **`LIVE`** | Twitch-class | Low-latency, short-TTL caching. |
| **`VOD`** | Netflix-class | Long edge SWR on metadata, private playback APIs. |

---

## 🚀 Quick Usage

Mounting middlewares is straightforward:
```python
from fastmiddleware import RequestIDMiddleware, SecurityHeadersMiddleware, ResponseTimingMiddleware

app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ResponseTimingMiddleware)
```

---

## 🛡️ Security Headers

Includes a pre-configured `SecurityHeadersConfig` for best practices:
- **HSTS:** `max-age=31536000`.
- **CSP:** `frame-ancestors 'self'`.
- **Referrer-Policy:** `strict-origin-when-cross-origin`.
- **XSS-Protection:** `1; mode=block`.

---

## 🛠️ Installation

FastMiddleware can be installed in any FastAPI or Starlette project:
```bash
pip install fast-middleware
```
The installable package is **`fastmiddleware`** (no hyphen in import).
