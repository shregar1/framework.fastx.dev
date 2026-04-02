# Project Structure

Understanding the FastMVC project layout and organization.

## Directory Overview

```text
my-project/
├── app.py                      # Application entry point
├── pyproject.toml             # Project metadata and dependencies
├── requirements.txt           # Optional dev tooling, ecosystem packages, and docs
├── Makefile                   # Development commands
├── .env                       # Environment variables (git-ignored)
├── .env.example               # Example environment file
├── .pre-commit-config.yaml    # Pre-commit hooks
├── docker-compose.yml         # Docker services
├── Dockerfile                 # Container definition
│
├── abstractions/              # I classes and interfaces
│   ├── controller.py         # I controller with CRUD
│   ├── repository.py         # I repository pattern
│   ├── service.py            # I service layer
│   └── entity.py             # I entity/model
│
├── config/                    # Configuration
│   ├── settings.py           # Pydantic settings
│   └── validator.py          # Environment validation
│
├── constants/                 # Application constants
│   ├── http.py               # HTTP status codes
│   ├── messages.py           # Response messages
│   └── default.py            # Default values
│
├── core/                      # Core utilities
│   ├── database.py           # DataI connection
│   ├── cache.py              # Caching utilities
│   ├── logging.py            # Logging configuration
│   ├── exceptions.py         # Custom exceptions
│   ├── pagination.py         # Pagination helpers
│   ├── responses.py          # Response utilities
│   ├── docs.py               # API documentation setup
│   └── testing/              # Testing utilities
│       └── fixtures.py
│
├── dependencies/              # FastAPI dependencies
│   ├── database.py           # DB session injection
│   └── auth.py               # Authentication deps
│
├── docs/                      # Documentation
│   ├── index.md
│   ├── guide/
│   ├── api/
│   └── stylesheets/
│
├── dtos/                      # Data Transfer Objects
│   ├── I.py               # I DTO classes
│   ├── request.py            # Request DTOs
│   └── response.py           # Response DTOs
│
├── models/                    # Domain models (e.g. models/item.py for Item)
├── controllers/apis/v1/       # Versioned HTTP controllers (e.g. item/, example/)
├── testing/                   # Pytest factories/fixtures per domain (e.g. testing/item/)
│
├── factories/                 # Test/tooling factories (mirror apis/… and dtos/requests/apis/…)
│   └── apis/v1/example/     # fetch, create, patch, put, update, delete, common
│
├── middlewares/               # FastAPI middleware
│   ├── request_logging.py    # Request logging
│   ├── error_handling.py     # Error handling
│   ├── rate_limiting.py      # Rate limiting
│   ├── cors.py               # CORS setup
│   └── timing.py             # Request timing
│
├── static/                    # Static files
│   └── swagger.html          # Custom Swagger UI
│
├── _maint/                    # CRITICAL — see guide/maint-folder.md (do not move/rename casually)
│   ├── init-scripts/
│   ├── nginx/
│   └── scripts/
│
├── tests/                     # Test suite (mirrors app: controllers, services, dtos, …)
│   ├── conftest.py           # Pytest configuration
│   ├── controllers/apis/v1/item/  # HTTP tests for sample Item API (see guide/new-api-scaffolding.md)
│   ├── factories/            # Tests for factories/ (same subpaths as prod)
│   └── …                     # abstractions, apis, config, middlewares, repositories, …
│
└── .vscode/                   # VS Code settings
    ├── settings.json
    ├── launch.json
    ├── tasks.json
    └── extensions.json
```

!!! warning "`_maint` is infrastructure, not app code"
    The **`_maint`** folder holds Docker/nginx, DB bootstrap SQL, seeds, and hook scripts. **Do not change it** in routine feature work without reading [**The `_maint` folder (critical)**](maint-folder.md). Misplaced edits break compose, entrypoints, and pre-commit.

## Layer Explanation

### 1. Abstractions Layer

I classes that define the contract for each layer:

- **Entity**: Domain models
- **Repository**: Data access interface
- **Service**: Business logic interface
- **Controller**: HTTP handling interface

### 2. Core Layer

Shared utilities and infrastructure:

- **DataI**: Connection management, sessions
- **Cache**: Redis integration
- **Logging**: Structured logging setup
- **Exceptions**: Custom exception classes
- **Responses**: Standard response formats

### 3. Feature layer (per resource)

Each feature follows the MVC pattern across packages, for example the **Item** sample:

```text
models/item.py              # Item (domain model for Item)
repositories/item.py        # ItemRepository (inherits IRepository directly)
services/item/              # ItemService
controllers/apis/v1/item/   # Router + ItemController
dtos/requests/item/         # create.py, update.py — one concrete class per file (nested helpers optional)
dtos/responses/item/        # Response DTOs
testing/item/               # ItemFactory, pytest fixtures
```

See [**New API scaffolding**](new-api-scaffolding.md) for a generator-oriented checklist.

## Design Principles

### Separation of Concerns

Each layer has a single responsibility:

- **Controller**: Handles HTTP requests/responses
- **Service**: Contains business logic
- **Repository**: Handles data persistence
- **Entity**: Defines data structure

### Dependency Inversion

Higher-level modules depend on abstractions:

```python
# Service depends on Repository abstraction
class ItemService(IService):
    def __init__(self, repository: IRepository):
        self.repository = repository

# Repository depends on Entity
class ItemRepository(IRepository):
    def __init__(self, entity_class: Type[IEntity]):
        self.entity_class = entity_class
```

### Dependency Injection

FastAPI's dependency system wires everything together:

```python
@router.get("/items")
async def list_items(
    service: ItemService = Depends(get_item_service)
):
    return await service.list()
```

## Adding New Features

To add a new feature (e.g., `users`):

1. **Create the feature directory**:

   ```bash
   mkdir users
   touch users/__init__.py
   ```

2. **Define the entity**:

   ```python
   # users/entity.py
   from abstractions.entity import IEntity

   class User(IEntity):
       id: int
       email: str
       name: str
   ```

3. **Create the repository**:

   ```python
   # users/repository.py
   from abstractions.repository import IRepository
   from users.entity import User

   class UserRepository(IRepository[User]):
       pass
   ```

4. **Create the service**:

   ```python
   # users/service.py
   from abstractions.service import IService
   from users.repository import UserRepository

   class UserService(IService[User]):
       def __init__(self, repository: UserRepository):
           super().__init__(repository)
   ```

5. **Create the controller**:

   ```python
   # users/controller.py
   from fastapi import APIRouter
   from abstractions.controller import IController
   from users.service import UserService

   router = APIRouter(prefix="/users")
   controller = IController(UserService, User)

   @router.get("")
   async def list_users():
       return await controller.list()
   ```

6. **Register in app.py**:

   ```python
   from users.controller import router as users_router
   app.include_router(users_router, tags=["users"])
   ```

## Best Practices

1. **Keep controllers thin**: Only HTTP-related logic
2. **Keep services pure**: No HTTP or DB dependencies
3. **Use DTOs**: Separate request/response models from entities
4. **Handle errors**: Use custom exceptions and middleware
5. **Write tests**: Test each layer independently
6. **Document APIs**: Use docstrings and type hints
