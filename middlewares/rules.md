# Middleware Rules

Middlewares wrap every request/response. A bug here is a site-wide incident — keep them small, deterministic, and fast.

## Do

- **Short-circuit cheaply** — reject bad input (auth missing, rate limit hit) before any downstream work happens.
- **Set `request.state` fields** that downstream code reads: `state.urn`, `state.user_id`, `state.user_urn`. Controllers read them via `bind_request_context`.
- **Make the happy path branchless** — one `if` for the bypass (health checks, docs), one for the reject, then `await call_next(request)`.
- **Propagate typed errors** — raise from `fast_platform.errors` so the error handler returns a consistent envelope.
- **Use `urn` for correlation** — attach it to every log line emitted inside the middleware.

## Don't

- Don't read the request body in a middleware unless you absolutely must — it forces FastAPI to re-buffer the stream and breaks streaming endpoints.
- Don't do DB queries for auth on every request — cache the JWT verification result per-request in `request.state`.
- Don't mutate headers the client sent — copy, transform, read-only.
- Don't block the event loop. No `time.sleep`, no sync HTTP, no sync Redis.
- Don't re-implement a utility — import from `utilities/` (e.g. `get_client_ip`, `JWTUtility`).

## Order Matters

Middlewares run in **reverse** registration order for the request, and forward order for the response. Register carefully — put security-critical middlewares (auth, rate limit, CORS) at the right spot in `app.py`.

## File Layout

```
middlewares/
  auth.py                  # JWT verification, user_id injection
  docs_auth.py             # protect /docs in prod
  request_id.py            # URN generation + request.state.urn
  rate_limit.py
  security_headers.py
```

## Testing

Every middleware has a test that hits a trivial handler through the full `TestClient` stack — not by constructing the middleware directly. Unit-testing `dispatch()` in isolation misses ordering bugs.
