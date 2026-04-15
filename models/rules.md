# Model Rules

Models are SQLAlchemy ORM classes — the single source of truth for DB schema. They are the lowest layer; only repositories should import them.

## Do

- Inherit from the project `Base` declared in `models/base.py` (or equivalent) so metadata is shared.
- Use SQLAlchemy 2.0 typing: `Mapped[str]`, `mapped_column(...)`. No legacy `Column(...)` at the class level.
- Add `__tablename__` explicitly — never rely on auto-naming.
- Index every column touched by a `WHERE`, `JOIN`, or `ORDER BY`. Composite indexes for multi-column filters.
- Add `server_default=func.now()` for `created_at` / `updated_at`. Use `onupdate=func.now()` for `updated_at`.
- Use `ULID` or `UUID` for public identifiers (`urn`, external IDs); reserve integer PKs for internal joins.
- Add `nullable=False` by default — opt into NULL explicitly when the column can legitimately be absent.
- Model relationships with `relationship(..., back_populates=...)` and declare the reverse side — both ends.

## Don't

- Don't put query methods on a model (`User.find_by_email(...)`). That's repository territory.
- Don't add business logic to models (`User.can_subscribe()`). Services own rules.
- Don't import `utilities/`, `services/`, or `controllers/` — models sit at the bottom of the graph.
- Don't generate migrations by editing the DB — always run `alembic revision --autogenerate` and review the diff.
- Don't drop columns without a two-step migration (ignore → drop) in production.
- Don't use `cascade="all, delete-orphan"` without auditing every caller — cascades silently destroy data.
- Don't mix ORM state and DTOs in the same class. If you need serialization, do it in the service or DTO layer.

## Migrations

1. Edit the model.
2. `alembic revision --autogenerate -m "short_reason"`.
3. Read every line of the generated migration — autogenerate misses constraints, server defaults, and index renames.
4. Add a `down_revision` downgrade path that actually works.
5. Test the migration on a copy of prod data before merging.

## File Layout

```
models/
  base.py                  # Base + common mixins (TimestampMixin, ...)
  <domain>/<entity>.py     # one class per file for anything non-trivial
```
