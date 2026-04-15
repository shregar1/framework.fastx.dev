# Utility Rules

Utilities are stateless-ish helpers: JWT, dictionary conversion, hashing, JSON-Web-Key loading, HTTP client wrappers, email, audit, client-IP extraction, etc. They're the glue between services and external tech.

## Structure

1. **Extend `IUtility`** when the helper holds per-request context (`JWTUtility`, `DictionaryUtility`). Standalone pure helpers (e.g. `get_client_ip`) are plain functions.
2. **Class utilities take context in `__init__`** — `urn`, `user_urn`, `api_name`, `user_id`. Forward `*args, **kwargs` to `super().__init__(...)`.
3. **Pure functions live at module level** — no class wrapper for a one-liner.

## Do

- Make every utility injectable via a dependency factory in `dependencies/utilities/<x>.py` — that's how controllers get per-request instances.
- Raise typed errors from `fast_platform.errors` (`UnexpectedResponseError`, `ServiceUnavailableError`) on external failures — never leak raw `requests`/`httpx`/`smtplib` exceptions.
- Treat external I/O as failable: timeouts, retries, and a `try/except` that surfaces a typed error.
- Log at `debug` for normal operation, `warning` when a retryable call fails, `error` when the helper gives up.
- Keep return shapes simple — dict, DTO, or primitive. No SQLAlchemy objects, no FastAPI types.

## Don't

- Don't touch the DB session. If you need persistence, you belong in a repository.
- Don't import controllers or services — utilities are leaves in the dependency graph.
- Don't cache on a module-level mutable (`_cache = {}`) without a TTL or explicit invalidation path.
- Don't read environment variables at call time — read them once at module import (or use the `config/` layer) so tests can patch cleanly.
- Don't swallow exceptions — convert them, don't hide them.

## Dependency Factory Contract

Every injectable utility must have a matching `dependencies/utilities/<x>.py`:

```python
class XxxUtilityDependency:
    @classmethod
    def derive(cls) -> Callable[..., XxxUtility]:
        def factory(urn, user_urn, api_name, user_id) -> XxxUtility:
            return XxxUtility(urn=urn, user_urn=user_urn,
                              api_name=api_name, user_id=user_id)
        return factory
```

Controllers then `Depends(XxxUtilityDependency.derive)` and pass the factory into `bind_request_context(...)`.

## File Layout

```
utilities/
  jwt.py
  dictionary.py
  audit.py
  request_utils.py         # pure functions (get_client_ip, ...)
  notifications/
    lifecycle.py           # domain-shaped helpers
```
