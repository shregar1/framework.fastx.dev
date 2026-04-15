# Dependency Rules

The `dependencies/` tree holds the FastAPI-facing dependency factories that wire repositories, services, and utilities into controllers. This is the only place where construction details live.

## Structure

1. **Mirror the target tree** — a service at `services/user/login.py` has a dependency at `dependencies/services/user/login.py`.
2. **One class, one `derive` classmethod** — returns a callable factory that takes context + collaborators and builds the target.
3. **No business logic** — dependencies are plumbing. If a condition affects what gets constructed, surface it via explicit params.

## The `derive` Pattern

```python
class UserLoginServiceDependency:
    @classmethod
    def derive(cls) -> Callable[..., UserLoginService]:
        def factory(
            urn: str | None,
            user_urn: str | None,
            api_name: str | None,
            user_id: int | None,
            jwt_utility: JWTUtility,
            user_repository: UserRepository,
            refresh_token_repository: RefreshTokenRepository,
        ) -> UserLoginService:
            return UserLoginService(
                urn=urn, user_urn=user_urn, api_name=api_name, user_id=user_id,
                jwt_utility=jwt_utility,
                user_repository=user_repository,
                refresh_token_repository=refresh_token_repository,
            )
        return factory
```

Controllers use it as `Depends(UserLoginServiceDependency.derive)`.

## Do

- Return a **callable factory** from `derive` — not the constructed instance. FastAPI calls `derive` once per request; the controller then calls the factory with the context tuple.
- Accept only **already-constructed collaborators** in the factory (a `Session`, a repository, a utility). No nested factories.
- Keep the factory signature in lock-step with the target's `__init__` signature. If you rename a param in the service, update the factory.
- Provide a dependency for every service, repository, and injectable utility — even one-liners. Consistency > terseness.

## Don't

- Don't put conditional logic inside `derive` ("if prod use X else Y"). Use config + subclasses.
- Don't open sessions here — take `Session` as a factory param (FastAPI resolves it via `DBDependency.derive`).
- Don't cache instances across requests — every request builds a fresh object.
- Don't import controllers or the FastAPI app — dependencies are upstream of the routing layer.

## File Layout

```
dependencies/
  db.py                    # DBDependency
  repositiories/           # legacy spelling; keep it
    <resource>.py
  services/
    <domain>/<use_case>.py
  utilities/
    <util>.py
```
