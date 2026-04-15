# Service Rules

Services hold business logic. They orchestrate repositories, utilities, and external calls — they are the only layer allowed to encode policy.

## Structure

1. **Extend `IService`** (or a nested domain interface like `IUserService`).
2. **One service per use case** — `UserLoginService.run()`, not `UserService.login()/logout()/register()`. One class, one verb.
3. **Constructor takes dependencies, not primitives** — repositories, utilities, and context fields (`urn`, `user_urn`, `api_name`, `user_id`). Forward `*args, **kwargs` to `super().__init__(...)`.
4. **Entry point is `async def run(self, request_dto)`** — returns a `BaseResponseDTO`.

## Do

- Validate business invariants here; raise typed errors (`BadInputError`, `ConflictError`, `NotFoundError`, `UnauthorizedError`, `RateLimitError`, `ServiceUnavailableError`, `UnexpectedResponseError`).
- Build the `BaseResponseDTO` with `transactionUrn=self.urn`, `status=APIStatus.SUCCESS`, plus `responseMessage` and `responseKey`.
- Put every external call (SMTP, Redis, webhook, 3rd-party HTTP) behind a utility and assume it can fail — raise `ServiceUnavailableError` or `UnexpectedResponseError` on failure.
- Keep repository access through the injected repository instance — never open a new session.
- Log at `info` for happy-path milestones, `warning` for handled failures, `error` only for unrecoverable bugs.
- Make services stateless across calls — everything lives on the injected context and inputs.

## Don't

- Don't touch `request.state` — if you need a field, take it as a constructor arg.
- Don't import `fastapi` — services are transport-agnostic. No `Request`, no `JSONResponse`, no `HTTPException`.
- Don't catch exceptions to return a "FAILED" DTO — raise typed errors; the controller's `handle_exception` is the single error translator.
- Don't commit/rollback the session — the repository or the unit-of-work owns the transaction boundary.
- Don't instantiate another service inside a service — compose via the dependency factory or split the use case.
- Don't cache context on the class (`UserLoginService.current_user`) — pass it through explicitly.
- Don't take `*_factory` callables — services receive already-constructed dependencies.

## Dependency Factory Contract

Every service must have a matching `dependencies/services/.../<service>.py` that exposes a `XxxServiceDependency` with a `derive()` classmethod returning a callable:

```python
def factory(urn, user_urn, api_name, user_id, **deps) -> XxxService: ...
```

The controller calls this factory; the service's `__init__` signature must stay compatible with it.

## File Layout

```
services/
  <domain>/                # user, item, example
    abstraction.py         # IXyzService
    <use_case>.py          # one class per use case
```
