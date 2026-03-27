# Middlewares

## Overview

Generic HTTP middleware (request ID, security headers, rate limiting, CORS, timing, body-size limits, etc.) comes from **`fast-middleware`** on PyPI (`fast_middleware` imports) and, in full templates, the extended **`fastmiddleware`** stack used in `app.py`.

This directory only contains **app-specific** wiring:

- **`authentication.py`** — Subclasses `JWTBearerAuthMiddleware` from `fast_middleware`, binding JWT decode, user repository session checks, and `IResponseDTO` error payloads.

Import the app middleware as:

```python
from middlewares import AuthenticationMiddleware
```

Use the packaged stack in `app.py`, for example:

```python
from fastmiddleware import (
    CORSMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
    TimingMiddleware,
    TrustedHostMiddleware,
)

app.add_middleware(RequestContextMiddleware)
# ... trusted host, CORS, security headers, rate limit, logging, timing ...
app.add_middleware(AuthenticationMiddleware)
```

## Generic JWT middleware (library)

`JWTBearerAuthMiddleware` lives in **`fast_middleware.jwt_bearer_auth`**. It takes injectable callables (`decode_bearer`, `load_user`, `build_error_response`, …) so other apps can reuse it without depending on FastMVC’s repositories or DTOs.

```python
from fast_middleware import JWTBearerAuthMiddleware, ErrorKind
```

See the `fast-middleware` package README for `BodySizeLimitMiddleware`, `SecurityHeadersMiddleware`, `RequestIDMiddleware`, and related helpers.
