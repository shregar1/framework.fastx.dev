# Factories

## What this module does

The **`factories`** package holds **reusable builders** for test data and local tooling: dictionaries and Pydantic DTOs that match production request/response shapes. The **folder layout mirrors** the API and DTO trees so you can find the factory for an endpoint next to the same path under **`dtos/requests/apis/...`** and conceptually next to **`controllers/apis/...`**.

It complements **`testing/item/`** (`ItemFactory`, pytest fixtures) and **`core/testing/factories.py`** (generic helpers).

## Layout (`factories/apis/v1/example`)

| Module | HTTP verb (typical) | DTO |
|--------|---------------------|-----|
| `common.py` | — | `new_reference_number()` helper |
| `fetch.py` | GET | `FetchUserRequestDTO` (`dtos/requests/apis/v1/user/fetch`) |
| `create.py` | POST | `ExampleCreateRequestDTO` |
| `update.py` | PUT/PATCH (generic) | `ExampleUpdateRequestDTO` (explicit fields) |
| `patch.py` | PATCH | `ExampleUpdateRequestDTO` (partial defaults) |
| `put.py` | PUT | `ExampleUpdateRequestDTO` (full replacement defaults) |
| `delete.py` | DELETE | `ExampleDeleteRequestDTO` |

```
factories/apis/v1/example/
├── common.py
├── fetch.py
├── create.py
├── update.py
├── patch.py
├── put.py
├── delete.py
└── __init__.py
```

## Example usage

```python
from factories.apis.v1.example import (
    ExampleCreateRequestFactory,
    ExampleDeleteRequestFactory,
    ExampleFetchRequestFactory,
    ExamplePatchRequestFactory,
    ExamplePutRequestFactory,
    ExampleUpdateRequestFactory,
)

# Re-exported from ``factories`` root as well
from factories import ExamplePutRequestFactory

post_body = ExampleCreateRequestFactory.build()
patch_body = ExamplePatchRequestFactory.build(name="only-this")
put_body = ExamplePutRequestFactory.build()
delete_body = ExampleDeleteRequestFactory.build()
custom = ExampleUpdateRequestFactory.build(name="n", description="d")
get_body = ExampleFetchRequestFactory.build()
```

**Pytest:** **`fetch_example_request_payload`** in `tests/conftest.py` uses **`ExampleFetchRequestFactory`**. See **`tests/factories/apis/v1/example/test_factories_example.py`** for all verbs.

## Adding a new factory

1. Add **`factories/apis/v1/<area>/<operation>.py`** (or deeper nesting to match DTOs).
2. Re-export from **`factories/apis/v1/<segment>/__init__.py`** and **`factories/__init__.py`** if desired.
3. Add tests under **`tests/`**, mirroring **`factories/...`** (e.g. **`tests/factories/apis/v1/example/`**).

## Related

- `dtos/requests/example/` — `create.py`, `update.py`, `delete.py` (one **concrete** DTO class per module; see `dtos/README.md`)  
- `testing/item/factories.py` — Item-focused factories for the sample CRUD API  
- `core/testing/factories.py` — Generic `Factory` / `FactoryField` helpers  
- `tests/README.md` — fixtures and discovery  
