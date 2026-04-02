# FastX (`fastx` on PyPI)

**Production-grade MVC tooling for FastAPI** — Interactive CLI for project scaffolding, entity generation, Alembic migrations, and a reference framework layout that ties together the FastX ecosystem (SQLAlchemy, Redis, JWT, and optional integrations).

FastX is a **project generator for FastAPI** with a clean MVC stack and a **menu of production features** you can turn on from the CLI (or from a visual configurator on your site: collect options, then paste the generated `fastx generate …` command). Generated projects stay **lean**: only the services you enable are scaffolded; the rest is pruned.

**Python:** 3.10+

**Package name on PyPI:** `fastx` (the name `fastx` is already used on PyPI by another project)  
**Version:** see `[project]` in [`pyproject.toml`](pyproject.toml).

## Capabilities

- **Interactive CLI** — Terminal UI (Rich) for project generation: `fastx generate`, `fastx quickstart`, and ecosystem commands such as `fastx init` / `fastx add entity` where provided by your CLI install.
- **Auto venv setup** — Virtual environment, dependencies, `.gitignore` updates.
- **VS Code integration** — Debug profiles, tasks, recommended extensions.
- **Makefile** — `make dev`, `test`, `lint`, `migrate`, `docker`, etc.
- **Entity generation** — Controllers, services, repositories, DTOs.
- **Alembic migrations** — `fastx db migrate/upgrade/downgrade/reset` (see below).
- **App template** — FastAPI structure, config, middleware, and hooks expected by extension packages (`fast_*`).
- **Batteries** — FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, Redis, JWT, bcrypt, optional dashboards, observability, payments, and more via flags (see [Optional platform features](#optional-platform-features)).

### New features (high level)

- **DataI migration CLI** — `fastx db migrate/upgrade/downgrade/reset`
- **Testing** — Factories, pytest fixtures, auth mocks
- **Docker Compose** — Postgres, Redis, FastAPI, optional dev tools
- **GitHub Actions** — CI/CD templates in generated projects
- **Dark-themed API docs** — FastX-branded Swagger/ReDoc
- **Production health** — `/health`, `/health/live`, `/health/ready`
- **Dashboards** (when enabled) — e.g. `/dashboard/health`, `/dashboard/api` for health and API activity samples

## Install

```bash
pip install fastx

# For best interactive experience
pip install fastx[interactive]
```

Editable from this directory (when developing the framework):

```bash
pip install -e .
```

## CLI usage

### Interactive project generation

```bash
# Run the wizard
fastx generate

# Or with options
fastx generate --name my_api --author "John Doe"

# Quick start with defaults
fastx quickstart --name my_api
```

### Generated project features

Every generated project includes:

- **Virtual environment** — Auto-created at `.venv/` (configurable)
- **VS Code settings** — Debug configs, tasks, recommended extensions
- **Makefile** — `make dev`, `make test`, `make lint`, `make migrate`
- **Example API** — Working Item CRUD at `/items` (typical template)
- **Test structure** — Unit and integration layout

### Development commands

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

## Feature details

### DataI migration CLI

Manage database migrations directly from the CLI:

```bash
# Create migration from model changes
fastx db migrate -m "Add users table"

# Apply migrations
fastx db upgrade

# Rollback one migration
fastx db downgrade

# Reset database (development only)
fastx db reset --seed

# Check status
fastx db status
```

### Docker Compose stack

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

### Testing framework

Generated projects include testing utilities:

```python
from tests.factories.apis.v1.item import ItemFactory
# Shared fixtures: tests/conftest.py (Item API + shared pytest fixtures)

# Generate fake test data
item = ItemFactory.create(name="Test Item", completed=True)

# Use fixtures in tests
def test_create_item(item_client, create_item_payload, mock_auth):
    with mock_auth:
        response = item_client.post("/items", json=create_item_payload)
        assert response.status_code == 201
```

### GitHub Actions CI/CD

Auto-generated workflows often include:

- **CI/CD** — Test, lint, build Docker images
- **PR checks** — Fast validation
- **Release** — Build and push on version tags

### API documentation

- Dark-themed Swagger UI at `/docs`
- FastX branding (cyan/fuchsia)
- Kubernetes health endpoints at `/health`, `/health/live`, `/health/ready`

### Postman collection

The repo may include `postman/postman_collection.json` (and optionally `postman/postman_environment.json`). They follow the same export path as application startup (`lifespan` → `RouteExportEngine`), so OpenAPI-derived requests and tests stay aligned with `core/route_export_engine.py`. Prefer **regenerating** over hand-editing structure.

**Regenerate** (same Python environment as `make dev`; run from this directory):

```bash
make postman-export
# or: python3 _maint/scripts/export_postman_collection.py
```

If startup validation blocks the import, ensure `.env` exists (see `.env.example`) or set `VALIDATE_CONFIG=false` for a one-off export.

**Environment variables** (also listed in the `app.py` module docstring; values match what the server uses on boot):

| Variable | Purpose |
|----------|---------|
| `POSTMAN_EXPORT_ENVIRONMENT` | Set to `1` or `true` to also write the environment JSON (default is collection-only). |
| `POSTMAN_OUTPUT_DIR` | Directory for exports (default: `postman`). |
| `POSTMAN_COLLECTION_FILE` | Path to collection JSON (default: `postman/postman_collection.json`). |
| `POSTMAN_COLLECTION_NAME` | Override the collection/environment title (default: APP_NAME from env → git repository folder name → fastx). |
| `POSTMAN_BASE_URL` | Override the `base_url` variable (default: `http://HOST:PORT` from env). |
| `POSTMAN_ENV_FILE` | Environment JSON path or basename under `POSTMAN_OUTPUT_DIR` (default: `postman/postman_environment.json`). |
| `POSTMAN_NEGATIVE_TESTS` | Set to `0` or `false` to skip extra per-request `pm.sendRequest` “negative” scripts. |

On startup, the app logs the written paths and variable names, for example: `variables: base_url, reference_urn, reference_number, token, refresh_token`.

**Login responses (`data.tokens`)** — After a successful login that returns the standard envelope with JWTs under `data` (e.g. `data.tokens.accessToken`, `data.tokens.refreshToken`), the collection **test** script fills the `token` and `refresh_token` collection variables so `Authorization: Bearer {{token}}` works on later requests. Supports camelCase (`accessToken`) and snake_case (`access_token`) field names.

**After importing into Postman** (quick verification):

- Open the collection **Variables** tab and confirm `base_url` is the server you intend to hit (e.g. `http://localhost:8000`).
- Send one request and confirm `{{reference_urn}}` on `x-reference-urn` and JSON bodies behave as expected; run login first or set `token` manually if the route uses Bearer auth.
- **Collection Runner** executes tests, including negative cases that issue additional HTTP calls to `{{base_url}}`. Use a dev or staging URL before running the full collection against a shared or production API.

---

## Optional platform features

The sections below describe **optional** stacks and `--with-*` flags your generator or website configurator can expose. Not every flag exists in every CLI version; treat this as the intended matrix for the full FastX ecosystem.

### Built-in dashboards (when enabled)

**Service health — `/dashboard/health`**

- Status cards for primary DB (Postgres/MySQL/SQLite), Redis, and optional backends (MongoDB, Cassandra, ScyllaDB, DynamoDB, Cosmos DB, Elasticsearch, Kafka, etc., as you extend).
- Shows **Healthy / Unhealthy / Skipped** based on config and env.

**API activity — `/dashboard/api`**

- Lists endpoints registered via `register_endpoint_sample(...)`.
- Configure method, path, description, sample JSON body, query params, headers.
- Run sample requests from the UI; see status codes and latency.

### Datastores and cache

**Primary database** — PostgreSQL, MySQL, or SQLite via wizard / `config/db` and `.env`.

**Optional datastores** (typical CLI flags; exact names may vary by CLI version):

| Feature | Typical flag |
|---------|----------------|
| Redis (cache, rate limit, sessions) | `--with-redis` / `--no-redis` |
| MongoDB | `--with-mongo` |
| Cassandra | `--with-cassandra` |
| ScyllaDB | `--with-scylla` |
| DynamoDB | `--with-dynamo` |
| Azure Cosmos DB | `--with-cosmos` |
| Elasticsearch | `--with-elasticsearch` |

Grouped configuration in code often uses DTOs such as `DatastoresConfigurationDTO` (DB, cache, mongo, cassandra, scylla, dynamo, cosmos, elasticsearch).

### Communications and notifications

- **Email (SMTP / SendGrid)** — `EmailService`; `--with-email`
- **Slack** — `SlackService`; `--with-slack`
- **Push (APNS / FCM)** — scaffolding via `PushNotificationService` / config

Grouped DTOs may live under `CommunicationsConfigurationDTO` (email, slack, push).

### Observability and telemetry

- **Core** — Structured logging, metrics, tracing hooks.
- **Datadog** (optional) — `configure_datadog()`, `DATADOG_ENABLED`, `--with-datadog`
- **OpenTelemetry** (optional) — `configure_otel(app)`, `TELEMETRY_ENABLED`, `--with-telemetry`

### Payments

Stripe, Razorpay, PayPal, PayU, pay-by-link — high-level `PaymentService` patterns, `config/payments`, provider DTOs, `--with-payments`.

### CLI flags summary

| Category | Feature | Typical flag |
|----------|---------|----------------|
| Datastore | Redis | `--with-redis` / `--no-redis` |
| Datastore | MongoDB | `--with-mongo` |
| Datastore | Cassandra | `--with-cassandra` |
| Datastore | ScyllaDB | `--with-scylla` |
| Datastore | DynamoDB | `--with-dynamo` |
| Datastore | Cosmos DB | `--with-cosmos` |
| Datastore | Elasticsearch | `--with-elasticsearch` |
| Communications | Email | `--with-email` |
| Communications | Slack | `--with-slack` |
| Observability | Datadog | `--with-datadog` |
| Observability | OpenTelemetry | `--with-telemetry` |
| Payments | Providers | `--with-payments` |

Other common generator options: `--output-dir`, `--git` / `--no-git`, `--venv` / `--no-venv`, `--install` / `--no-install`.

### Building a website configurator (command assembly)

1. Collect inputs: `projectName`, optional `outputDir`, booleans for git/venv/install, and toggles for Redis, Mongo, Cassandra, Scylla, Dynamo, Cosmos, Elasticsearch, email, Slack, Datadog, telemetry, payments.
2. Start with: `fastx generate <projectName>`.
3. Append flags, e.g. `--output-dir`, `--no-git`, `--venv`, `--install`.
4. Append `--with-*` / `--no-redis` as above.
5. Join into the final shell command for users to copy/paste.

Example:

```bash
fastx generate my_api \
  --output-dir ./projects \
  --with-redis \
  --with-mongo \
  --with-elasticsearch \
  --with-email \
  --with-slack \
  --with-datadog \
  --with-telemetry \
  --with-payments
```

### End-to-end quick start (generated app)

```bash
pip install fastx
fastx generate my_api   # add your flags
cd my_api
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Then open `http://localhost:8000/docs`, and when dashboards are enabled, `/dashboard/health` and `/dashboard/api`.

---

## Links

- **Repository:** [github.com/shregar1/fastMVC](https://github.com/shregar1/fastMVC) (see `[project.urls]` in `pyproject.toml`).
- **Docs:** [fastapi-mvc.dev](https://fastapi-mvc.dev/docs) (when published).

## Extension packages

The **`fast_*`** libraries in the monorepo are optional add-ons (DB, queues, LLM, storage, …). See the [parent README](../README.md) for the full package table and [`install_packages.sh`](../install_packages.sh) to install them in editable mode.

Day-to-day commands: see [`Makefile`](Makefile) (`make test`, `make lint`, `make format`, `make build`, …).

---

## Contributing

Thank you for contributing to **FastX** (`fastx`).

### Monorepo layout

This package usually lives inside the **FastX** monorepo. From the repo root, install in editable mode:

```bash
cd fast_mvc_main
pip install -e ".[dev]" || pip install -e .
pip install -r requirements.txt
pre-commit install
```

Standalone clone (if this package is its own git remote):

```bash
git clone https://github.com/shregar1/fastMVC.git
cd fast_mvc
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]" || pip install -e .
pip install -r requirements.txt
pre-commit install
```

Canonical repository URL from `pyproject.toml`: `https://github.com/shregar1/fastMVC`.

### `_maint` (do not touch casually)

The **`_maint/`** directory is **critical infrastructure** (Docker nginx, DB `init-scripts`, seed/tooling scripts). It is **not** part of the application feature tree. **Do not rename, relocate, or edit** it without updating every reference (`docker-compose.yml`, `docker-entrypoint.sh`, `.pre-commit-config.yaml`, docs) and without maintainer review.

Authoritative doc: [`docs/guide/maint-folder.md`](docs/guide/maint-folder.md) (also published under **Getting Started** in MkDocs).

To copy EditorConfig, pre-commit config, and other shared files from `fast_middleware/` into every package (from monorepo root):

```bash
python3 scripts/sync_package_tooling.py
```

### Test coverage

Many FastX libraries enforce **≥95% line coverage** via `pytest-cov` (`fail_under` in `pyproject.toml`). From this package directory:

```bash
python3 -m pytest tests/ -q --cov=src --cov-fail-under=95
```

(`fast_database` may use different `--cov=` paths — see that package’s `pyproject.toml`.)

Overview: [../docs/COVERAGE.md](../docs/COVERAGE.md).

### DTOs (one class per file)

Under `dtos/requests/<segment>/`, keep **one concrete Pydantic model per module** (e.g. `create.py` → `ExampleCreateRequestDTO`). **Nested** models that only support a single parent may live in the **same** file. Shared bases live in `abstraction.py`. Details: [`docs/guide/new-api-scaffolding.md`](docs/guide/new-api-scaffolding.md#one-concrete-class-per-file-dtos), [`dtos/README.md`](dtos/README.md#one-concrete-class-per-file).

### Quality checks

```bash
make test
make lint
make format
```

### Commits

Use clear commit messages (e.g. conventional commits: `feat:`, `fix:`, `docs:`). Pull requests against `main` are welcome.

---

## Publishing to PyPI

### Prerequisites

- PyPI account and [API token](https://pypi.org/manage/account/token/)
- `pip install build twine` (or use your environment / `requirements.txt`)

### Version and changelog

1. Bump `version` in `pyproject.toml`.
2. Update `CHANGELOG.md` under `## [Unreleased]` and add a dated section when you tag a release.

### Monorepo releases

If you use the **FastX** monorepo scripts, see [../RELEASE.md](../RELEASE.md) and `scripts/release_all.sh` at the repository root.

### Package upload (this project)

1. Run tests: `make test` or `pytest`.
2. Build: `make build` or `python -m build`.
3. Upload:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<pypi-token>
twine upload dist/*
```

- **PyPI project name:** `fastx`
- **Repository / homepage:** https://github.com/shregar1/fastMVC

---

## Documentation

| Document | Purpose |
|----------|---------|
| [SECURITY.md](SECURITY.md) | Reporting vulnerabilities |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

**Contributing & PyPI:** sections [Contributing](#contributing) and [Publishing to PyPI](#publishing-to-pypi) in this file.

**Monorepo:** [../README.md](../README.md) · **Coverage:** [../docs/COVERAGE.md](../docs/COVERAGE.md)
