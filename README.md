# pyfastmvc

**Production-grade MVC tooling for FastAPI** — Beautiful interactive CLInterface for project scaffolding, entity generation, Alembic migrations, and the reference framework layout that ties together the FastMVC ecosystem (SQLAlchemy, Redis, JWT, and optional integrations).

**Python:** 3.10+

**Package name on PyPI:** `pyfastmvc`  
**Version:** see `[project]` in [`pyproject.toml`](pyproject.toml).

## Capabilities

- **Interactive CLI** — Beautiful terminal UI with Rich library for project generation
- **Auto venv setup** — Creates virtual environment, installs dependencies, updates `.gitignore`
- **VS Code integration** — Pre-configured debug profiles, tasks, and recommended extensions
- **Makefile** — Common development commands (dev, test, lint, migrate, docker)
- **Entity generation** — Scaffold controllers, services, repositories, and DTOs
- **Alembic migrations** — DataI migration management via CLI
- **App template** — FastAPI app structure, configuration, middleware, and services expected by extension packages (`fast_*`)
- **Batteries** — FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, Redis, JWT, bcrypt, etc.

### New Features

- **DataI Migration CLI** — `fastmvc db migrate/upgrade/downgrade/reset`
- **Testing Framework** — ItemFactory, pytest fixtures, auth mocks
- **Docker Compose Stack** — One-command full setup (Postgres + Redis + FastAPI)
- **GitHub Actions CI/CD** — Auto-generated workflows for every project
- **Dark-themed API Docs** — FastMVC-branded Swagger UI with dark mode
- **Production Health Checks** — Kubernetes-ready endpoints

## Install

```bash
pip install pyfastmvc

# For best interactive experience
pip install pyfastmvc[interactive]
```

Editable from this directory (when developing the framework):

```bash
pip install -e .
```

## CLI Usage

### Interactive Project Generation

```bash
# Run the wizard
fastmvc generate

# Or with options
fastmvc generate --name my_api --author "John Doe"

# Quick start with defaults
fastmvc quickstart --name my_api
```

### Generated Project Features

Every generated project includes:

- **Virtual environment** — Auto-created at `.venv/` (configurable)
- **VS Code settings** — Debug configs, tasks, recommended extensions
- **Makefile** — `make dev`, `make test`, `make lint`, `make migrate`
- **Example API** — Working Item CRUD at `/items`
- **Test structure** — Unit and integration test setup

### Development Commands

```bash
cd my_api

# Using Makefile
make dev              # Start development server
make test             # Run tests
make lint             # Run linter
make format           # Format code
make migrate msg=""   # Create migration
make upgrade          # Apply migrations
make docker-up        # Start with Docker

# Using VS Code
# Press F5 to debug or Cmd/Ctrl+Shift+P → "Tasks: Run Task"
```

## Feature Details

### DataI Migration CLI

Manage dataI migrations directly from the CLI:

```bash
# Create migration from model changes
fastmvc db migrate -m "Add users table"

# Apply migrations
fastmvc db upgrade

# Rollback one migration
fastmvc db downgrade

# Reset dataI (development only)
fastmvc db reset --seed

# Check status
fastmvc db status
```

### Docker Compose Stack

One command starts the full stack:

```bash
# Start everything (Postgres, Redis, FastAPI + migrations)
make docker-up

# Start with development tools (PgAdmin, Redis Insight)
make docker-up-dev

# Access points:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - PgAdmin: http://localhost:5050
# - Redis Insight: http://localhost:5540
```

### Testing Framework

Generated projects include comprehensive testing utilities:

```python
from testing.item import ItemFactory
from testing.item.fixtures import item_client  # or rely on tests/conftest.py

# Generate fake test data
item = ItemFactory.create(name="Test Item")
payload = ItemFactory.create_dict(completed=True)

# Use fixtures in tests
def test_create_item(item_client, create_item_payload, mock_auth):
    with mock_auth:
        response = item_client.post("/items", json=create_item_payload)
        assert response.status_code == 201
```

### GitHub Actions CI/CD

Auto-generated workflows include:

- **CI/CD workflow** — Test, lint, build Docker images
- **PR Checks** — Fast validation and test runs
- **Release workflow** — Build and push on version tags

### API Documentation

- Dark-themed Swagger UI at `/docs`
- FastMVC branding with cyan/fuchsia color scheme
- Kubernetes health endpoints at `/health`, `/health/live`, `/health/ready`

## Links

- **Repository:** [github.com/shregar1/fastMVC](https://github.com/shregar1/fastMVC) (see `[project.urls]` in `pyproject.toml`).
- **Docs:** [fastapi-mvc.dev](https://fastapi-mvc.dev/docs) (when published).

## Extension packages

The **`fast_*`** libraries in the monorepo are optional add-ons (DB, queues, LLM, storage, …). See the [parent README](../README.md) for the full package table and [`install_packages.sh`](../install_packages.sh) to install them in editable mode.

## Tooling

See [CONTRIBUTING.md](CONTRIBUTING.md), [Makefile](Makefile), and [PUBLISHING.md](PUBLISHING.md).

---

## Documentation

| Document | Purpose |
|----------|---------|
| [CONTRIBUTING.md](CONTRIBUTING.md) | Dev setup, tests, monorepo sync |
| [PUBLISHING.md](PUBLISHING.md) | PyPI and releases |
| [SECURITY.md](SECURITY.md) | Reporting vulnerabilities |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

**Monorepo:** [../README.md](../README.md) · **Coverage:** [../docs/COVERAGE.md](../docs/COVERAGE.md)
