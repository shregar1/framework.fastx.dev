# Repositories

## What this module does

The **`repositories`** package implements the **data access layer**: it hides how entities are loaded, saved, updated, and queried (SQL, ORM, filters, pagination). The rest of the app talks to **repository interfaces** from **`abstractions`** (`IRepository`); concrete classes here provide the implementation for your database and tables.

Repositories are the **only** place that should know about persistence details (sessions, queries, table names). Services call repositories; controllers should not call repositories directly unless your architecture explicitly allows it for simple reads.

## Responsibilities

| Concern | Handled here |
|--------|----------------|
| CRUD and queries | Create, read, update, delete, filtered lists |
| Mapping | Between DB models/rows and domain entities or dicts (as per your conventions) |
| Transactions | Uses sessions passed in or created per unit-of-work (framework-dependent) |
| Filter operators | Often via `constants.filter_operator` and `IRepository` helpers |

## Layout (conceptual)

```text
repositories/
├── abstraction.py            # App-level repository base (extends framework IRepository)
├── item.py                   # Example: ItemRepository(IRepository) — one file per resource model
├── example/                  # Example/stub domain (abstraction.py, example_repository.py)
└── user/                     # Feature-specific repositories (e.g. user/fetch)
```

For a simple resource, use a **single module** per model (e.g. `item.py`, `product.py`) whose repository class inherits **`IRepository`** directly. Reserve a subfolder + `abstraction.py` only when you need a dedicated `I*Repository` interface.

## How it fits in the stack

```text
Controller → Service → Repository → Database (SQLAlchemy / fast_database)
```

Services depend on repository **instances** or factories; repositories depend on **sessions** and **configuration** supplied by **`dependencies`** and **`config`**.

## Related documentation

- `abstractions/README.md` — `IRepository` contract  
- `constants/README.md` — table names, filter operators  
- `dependencies/README.md` — DB session injection  

## Practices

1. **One repository** per aggregate or bounded context (avoid “god” repositories).  
2. **No business rules** that belong in services (e.g. “user must be active” before a generic `get`).  
3. **Keep methods focused** (`retrieve_record_by_id`, `create_record`, …) aligned with `IRepository`.  
4. **Test** with in-memory or fake DB in `tests/`; mock repositories when testing services.
