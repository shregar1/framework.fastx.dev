# Repository Rules

Repositories are the only layer that talks to the database. They expose domain-shaped methods — not raw SQL or ORM query builders — to services.

## Structure

1. **Extend `IRepository`** (or a nested interface like `IUserRepository`).
2. **Constructor takes `session: Session` plus context** (`urn`, `user_urn`, `api_name`, `user_id`). Forward `*args, **kwargs` to `super().__init__(...)`.
3. **Methods return entities or primitives** — never ORM `Query` objects, never `Result` proxies.

## Do

- Name methods after the domain action: `find_by_email`, `get_active_subscription`, `insert_user`, `mark_refresh_token_revoked`.
- Let the session flush/commit be owned by the caller (controller or unit-of-work) — don't call `session.commit()` from a repository unless it's the documented single-op pattern for that repo.
- Raise `NotFoundError` when a required record is missing; return `None` only when the caller explicitly handles absence.
- Keep queries narrow — `select` the columns or entity you actually need.
- Index every column used in a `WHERE` clause; document it in a comment on the model if it isn't obvious.
- Use SQLAlchemy 2.0 style (`select(...)`, `session.scalars(...)`) — no legacy `query(...)` API.

## Don't

- Don't accept a `request` or `request_payload` — repositories are transport-agnostic.
- Don't build the response DTO — services wrap the repository result into envelopes.
- Don't put business rules here ("a user can only subscribe if …"). That's service logic.
- Don't open a second session — use the one passed in.
- Don't emit audit logs or webhooks — that's orchestration, which belongs in the service.
- Don't do eager N+1 loads in a loop — use `selectinload` / `joinedload` or batch fetch.

## Transactions

- Read methods: no `commit`, no `flush`.
- Single-write helpers (e.g. `RefreshTokenRepository.mark_revoked`): document whether they commit. Default to *not* committing.
- Multi-step work: the service coordinates; the repository exposes the building blocks.

## File Layout

```
repositories/
  abstraction.py           # IRepository base
  <domain>/
    abstraction.py         # optional IXxxRepository
    <resource>_repository.py
```
