## FastMVC – Full Documentation (Single Page)

This file combines the main FastMVC docs into a single Markdown document, suitable for importing into a documentation website, knowledge base, or PDF generator.

---

## 1. Introduction

FastMVC is a **project generator and MVC framework for FastAPI** that lets you spin up a production-ready backend in minutes:

- Clean MVC architecture: controllers, services, repositories, models, DTOs.
- Rich middleware stack: security headers, logging, rate limiting, request context, CORS.
- Built-in dashboards: health and API activity (if enabled).
- Optional integrations: Redis, MongoDB, Cassandra, Scylla, DynamoDB, Cosmos DB, Elasticsearch, email, Slack, Datadog, OpenTelemetry, payments, identity/SSO.

**What this document covers:**

- How to install FastMVC and generate a new project.
- CLI commands and options.
- The MVC architecture and middleware pipeline.
- Configuration model (JSON configs, DTOs, environment variables).
- Overview of major modules and packages.

---

## 2. Getting Started

### 2.1 Install FastMVC

You need Python 3.10+.

**Using `uv` (recommended):**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install pyfastmvc
```

**Using `pip`:**

```bash
pip install pyfastmvc
```

Verify the CLI:

```bash
fastmvc --version
```

### 2.2 Generate a New Project

Use the non-interactive `generate` command:

```bash
fastmvc generate my_api
```

This creates a full FastAPI project with:

- MVC structure (`controllers/`, `services/`, `repositories/`, `models/`, `dtos/`).
- Middleware stack (security headers, logging, rate limiting, etc.).
- Configurations and `.env.example`.
- Testing and migrations wiring.

You can also provide options:

```bash
fastmvc generate my_api \
  --output-dir ./projects \
  --git \
  --venv \
  --install
```

### 2.3 Set Up Dependencies

Change into the generated project:

```bash
cd my_api
```

**With `uv`:**

```bash
uv sync
uv run fastmvc migrate upgrade
```

**With `pip`:**

```bash
pip install -r requirements.txt
cp .env.example .env
```

Customize `.env` with your database, Redis, and security settings.

### 2.4 Start Infrastructure (Optional)

If you use Postgres and Redis, you can bring them up via Docker:

```bash
docker-compose up -d
```

### 2.5 Run the API

```bash
python -m uvicorn app:app --reload
```

Default endpoints:

- API root: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Dashboards (if enabled in your template):
  - Health: `http://localhost:8000/dashboard/health`
  - API activity: `http://localhost:8000/dashboard/api`

### 2.6 Next Steps

- Generate entities: `fastmvc add entity <Name>` to scaffold full CRUD.
- Explore architecture: see Section 4.
- Configure datastores and integrations: see Section 5.

---

## 3. CLI Reference

The `fastmvc` CLI is the main entry point for generating and managing FastMVC projects. It is implemented in `fastmvc_cli/cli.py`.

### 3.1 Overview

```bash
fastmvc [COMMAND] [OPTIONS]
```

Available commands:

- `generate` – Create a new FastMVC project from the template.
- `init` – Interactive wizard to generate a project (TUI-style).
- `add` – Add components (entities, infrastructure services) to an existing project.
- `migrate` – Database migrations via Alembic.
- `info` – Show FastMVC feature overview and links.
- `version` – Print current FastMVC version.

### 3.2 `fastmvc generate`

Non-interactive project generator suitable for scripts and CI.

```bash
fastmvc generate PROJECT_NAME [OPTIONS]
```

Core options:

- `--output-dir, -o PATH` – Where to create the project (default: current directory).
- `--git / --no-git` – Initialize a git repository (default: `--git`).
- `--venv / --no-venv` – Create a virtual environment (default: `--no-venv`).
- `--install / --no-install` – Install dependencies after generation (default: `--no-install`).

Datastore options:

- `--with-redis / --no-redis` (default: with Redis).
- `--with-mongo / --no-mongo`.
- `--with-cassandra / --no-cassandra`.
- `--with-scylla / --no-scylla`.
- `--with-dynamo / --no-dynamo`.
- `--with-cosmos / --no-cosmos`.
- `--with-elasticsearch / --no-elasticsearch`.

Communications:

- `--with-email / --no-email`.
- `--with-slack / --no-slack`.

Observability & telemetry:

- `--with-datadog / --no-datadog`.
- `--with-telemetry / --no-telemetry`.

Payments & identity:

- `--with-payments / --no-payments`.
- `--with-identity / --no-identity`.

Example:

```bash
fastmvc generate my_api \
  --output-dir ./projects \
  --with-redis \
  --with-mongo \
  --with-elasticsearch \
  --with-email \
  --with-slack \
  --with-datadog \
  --with-telemetry \
  --with-payments \
  --with-identity
```

### 3.3 `fastmvc init`

Interactive, multi-step project initializer with a TUI-like experience:

```bash
fastmvc init
```

The wizard guides you through:

- Project details: name, output directory.
- Stack & features:
  - API preset: `auth_only`, `crud`, `admin`.
  - Database backend: `postgres`, `mysql`, `sqlite`.
  - Optional datastores, communications, observability, payments, identity.
  - Feature toggles: auth module, user management, example Product CRUD.
  - Layout: `monolith`, `backend-only`, `backend+worker`.
- Tooling:
  - Git, virtualenv, dependency installation.
  - Quality tools: ruff, black, isort, mypy.
  - Pre-commit config, GitHub Actions CI.
  - Optional git remote and initial push.
- Ports & secrets:
  - Application port (with conflict detection).
  - DB host/port/name (for non-SQLite).
  - Auto-generated JWT secret and bcrypt salt.
  - CORS origins.

It then generates the project and can also create:

- `LICENSE`
- `CONTRIBUTING.md`
- `CODEOWNERS`
- `pyproject.toml`
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`

### 3.4 `fastmvc add`

Group command to enhance an existing FastMVC project (must be run from the project root where `app.py` exists).

```bash
fastmvc add [SUBCOMMAND] ...
```

Subcommands:

- `fastmvc add entity` – generate full CRUD for an entity.
- `fastmvc add service` – copy infrastructure service configs and DTOs into an existing project.

#### 3.4.1 `fastmvc add entity`

```bash
fastmvc add entity ENTITY_NAME [--tests / --no-tests]
```

- `ENTITY_NAME` should be PascalCase (e.g. `Product`, `OrderItem`).
- `--tests / --no-tests` controls whether test files are generated (default: `--tests`).

Generated structure includes:

- `models/<entity>.py`
- `repositories/<entity>.py`
- `services/<entity>/`
- `controllers/<entity>/`
- `dtos/requests/<entity>/`
- `dependencies/repositories/<entity>.py`
- `tests/unit/.../test_<entity>.py`

You then:

- Import and register the router in `app.py`.
- Generate and apply a migration.

#### 3.4.2 `fastmvc add service`

```bash
fastmvc add service [mongo|cassandra|scylla|dynamo|cosmos|elasticsearch|email|slack|datadog|telemetry|payments|identity]
```

This copies config and DTOs from the FastMVC template into your existing project without overwriting existing files:

- For most services: adds `config/<service>/`, `configurations/<service>.py`, `dtos/configurations/<service>.py`.
- For `identity`: also adds `dtos/configurations/identity/` and `services/auth/`.
- For `email`: also adds `services/communications/`.

You then customize the corresponding `config/*/config.json` and restart your app.

### 3.5 `fastmvc migrate`

Group command for Alembic-based database migrations.

```bash
fastmvc migrate [generate|upgrade|downgrade|status|history] [...]
```

Requires `alembic.ini` in your project root.

- `fastmvc migrate generate "message"`:
  - Creates a new migration.
  - `--autogenerate / --no-autogenerate` (default: `--autogenerate`).
- `fastmvc migrate upgrade [revision]`:
  - Apply migrations (default: `head`).
- `fastmvc migrate downgrade [revision]`:
  - Roll back migrations (default: `-1`).
- `fastmvc migrate status`:
  - Show current migration revision.
- `fastmvc migrate history [--verbose]`:
  - Show migration history.

### 3.6 `fastmvc info`

```bash
fastmvc info
```

Prints:

- FastMVC version and Python version.
- High-level feature list (MVC, middleware stack, testing).
- Project layout overview.
- CLI command summary.
- Links to PyPI and documentation.

### 3.7 `fastmvc version`

```bash
fastmvc version
```

Outputs:

```text
FastMVC vX.Y.Z
```

---

## 4. Architecture

### 4.1 Layers

From top to bottom:

- Client (browser, mobile app, API consumer).
- FastAPI application (`app.py`).
- Controller layer (`controllers/`).
- Service layer (`services/`).
- Repository layer (`repositories/`).
- Data layer (PostgreSQL/MySQL/SQLite and optional datastores).

Controllers:

- Define route handlers.
- Bind request DTOs.
- Invoke services.
- Return standardized response DTOs.

Services:

- Implement business workflows and domain logic.
- Coordinate repositories, utilities, and external APIs.
- Raise custom errors for invalid states.

Repositories:

- Encapsulate data access (SQLAlchemy and optional backends).
- Support rich filtering, CRUD operations, and pagination.

### 4.2 Middleware Pipeline

FastMVC uses `fastmvc-middleware` to run a chain of middlewares for every request:

- RequestContextMiddleware – per-request URN and context.
- TimingMiddleware – adds processing time headers.
- RateLimitMiddleware – sliding window rate limiting.
- Authentication middleware – JWT-based auth for protected routes.
- LoggingMiddleware – structured JSON logging.
- SecurityHeadersMiddleware – CSP, HSTS, X-Frame-Options, X-Content-Type-Options.
- CORSMiddleware – cross-origin resource sharing.

These middlewares run before controllers, so your logic always sees a secure, observable context.

### 4.3 DTOs and Response Shape

Request DTOs (under `dtos/requests/`):

- Validate incoming data using Pydantic v2.
- Define shapes for endpoints (e.g. `UserLoginRequestDTO`).

Response DTOs (under `dtos/responses/`) wrap all responses in a consistent envelope:

```json
{
  "transactionUrn": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "status": "SUCCESS",
  "responseMessage": "User logged in successfully",
  "responseKey": "success_user_login",
  "data": {
    "user": { "id": 1, "email": "user@example.com" },
    "token": "..."
  }
}
```

### 4.4 Project Structure (Generated App)

```text
my_api/
├── app.py              # FastAPI entry point
├── start_utils.py      # Startup configuration
├── abstractions/       # Base interfaces (IController, IService, IRepository)
├── controllers/        # HTTP route handlers
├── services/           # Business logic
├── repositories/       # Data access layer
├── models/             # SQLAlchemy models
├── dtos/               # Request/response DTOs
├── middlewares/        # Custom middlewares
├── migrations/         # Alembic migrations
├── tests/              # Test suite
└── docker-compose.yml  # Optional infrastructure
```

### 4.5 Core Module

The `core/` package adds enterprise-grade building blocks:

- Health checks (Kubernetes-ready).
- Observability: structured logging, metrics, tracing, audit logging.
- Resilience: circuit breaker, retry with backoff.
- Background tasks and queues.
- Security: API keys, webhook verification, encryption helpers.
- Feature flags and A/B testing.
- Multi-tenancy (tenant context and middleware).
- API versioning (URL, header, or query based).
- Testing helpers (factories, mocks, fixtures).

---

## 5. Configuration

FastMVC centralizes configuration in:

- JSON config files under `config/**/config.json`.
- DTOs in `dtos/configurations/`.
- Manager classes in `configurations/`.
- Environment variables (`.env`).

### 5.1 Configuration Sources

JSON config files:

- `config/db/config.json`
- `config/cache/config.json`
- `config/security/config.json`
- Optional service configs such as:
  - `config/mongo/config.json`
  - `config/cassandra/config.json`
  - `config/scylla/config.json`
  - `config/dynamo/config.json`
  - `config/cosmos/config.json`
  - `config/elasticsearch/config.json`
  - `config/email/config.json`
  - `config/slack/config.json`
  - `config/datadog/config.json`
  - `config/telemetry/config.json`
  - `config/payments/config.json`
  - `config/identity/config.json`

DTOs (Pydantic models) in `dtos/configurations/`:

- Group related configs (datastores, communications, payments, identity, etc.).

Configuration managers in `configurations/`:

- `DBConfiguration`, `CacheConfiguration`, `SecurityConfiguration`, plus integration-specific managers.

Environment variables:

- `.env.example` generated by `ProjectGenerator`.
- `.env` you create per environment.

### 5.2 Database Configuration

`config/db/config.json`, `configurations/db.py`:

- Holds database connection parameters and SQLAlchemy connection string.
- Automatically adjusted by the project generator based on wizard choices (backend, host/port, database name).

Usage:

```python
from configurations.db import DBConfiguration

db_config = DBConfiguration()
dto = db_config.get_config()
connection_string = dto.connection_string
```

### 5.3 Cache / Redis

`config/cache/config.json`, `configurations/cache.py`:

- Redis host, port, password, db.
- Used for caching, rate limiting, sessions.

Usage:

```python
from configurations.cache import CacheConfiguration

cache_cfg = CacheConfiguration().get_config()
```

### 5.4 Security

`config/security/config.json`, `configurations/security.py`:

- Security headers: HSTS, CSP flags.
- Input validation rules.
- Authentication settings: JWT expiry, max login attempts.

Environment overrides (examples):

- `SECURITY_HSTS_MAX_AGE`
- `SECURITY_HSTS_INCLUDE_SUBDOMAINS`
- `SECURITY_ENABLE_CSP`
- `SECURITY_ENABLE_HSTS`
- `SECURITY_MAX_STRING_LENGTH`
- `SECURITY_MIN_PASSWORD_LENGTH`
- `SECURITY_JWT_EXPIRY_MINUTES`
- `SECURITY_MAX_LOGIN_ATTEMPTS`

### 5.5 Optional Integrations

Depending on CLI flags and `fastmvc add service`, you may also have configurations for:

- Datastores:
  - MongoDB, Cassandra, Scylla, DynamoDB, Cosmos DB, Elasticsearch.
- Communications:
  - Email (SMTP/SendGrid), Slack, push notifications.
- Observability:
  - Datadog, OpenTelemetry.
- Payments:
  - Stripe, Razorpay, PayPal, PayU, generic pay-by-link.
- Identity / SSO:
  - Google, GitHub, Azure AD, Okta, Auth0, SAML (via `config/identity` and `services/auth`).

Group DTOs (like `DatastoresConfigurationDTO`, `CommunicationsConfigurationDTO`, `PaymentsConfigurationDTO`) let you pass all related configs into initializers or services in one object.

### 5.6 Environment Variables and `.env`

The generator creates `.env.example` with sensible defaults:

- Application:
  - `APP_NAME`, `APP_ENV`, `APP_DEBUG`, `APP_HOST`, `APP_PORT`.
- Database:
  - `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`.
- Redis:
  - `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_DB` (or commented out if disabled).
- Optional datastores:
  - `MONGO_ENABLED`, `CASSANDRA_ENABLED`, etc., with default URIs.
- Communications:
  - `EMAIL_*`, `SLACK_*`.
- Observability:
  - `DATADOG_*`, `TELEMETRY_*`.
- Payments:
  - `PAYMENTS_ENABLED`, `PAYMENT_DEFAULT_PROVIDER`.
- Security:
  - `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRATION_HOURS`, `BCRYPT_SALT`.
- CORS:
  - `CORS_ORIGINS`, `CORS_ALLOW_METHODS`, `CORS_ALLOW_HEADERS`, `CORS_ALLOW_CREDENTIALS`.
- Rate limiting and logging settings.

You copy it per environment:

```bash
cp .env.example .env
```

and adjust values as needed.

### 5.7 Best Practices

- Keep secrets out of Git (commit `.env.example`, not `.env`).
- Use configuration DTOs instead of reading JSON directly.
- Let the generator prune unused configs via CLI flags.
- Use grouped DTOs to simplify wiring of multiple configs.

---

## 6. Modules Overview

### 6.1 Core Packages

- Abstractions (`abstractions/`):
  - Base interfaces and contracts: `IController`, `IService`, `IRepository`.
- Configurations (`configurations/`):
  - Configuration managers for DB, cache, security, and optional services.
- Constants (`constants/`):
  - Application constants and default values.
- Controllers (`controllers/`):
  - HTTP route handlers for your API endpoints.
- Dependencies (`dependencies/`):
  - Factory functions and dependency injection wiring for FastAPI.
- DTOs (`dtos/`):
  - Request and response DTOs, plus configuration DTOs under `dtos/configurations/`.
- Errors (`errors/`):
  - Custom exception types like `BadInputError`, `NotFoundError`.
- Middlewares (`middlewares/`):
  - Additional application-level middlewares.
- Migrations (`migrations/`):
  - Alembic migration scripts and configuration.
- Models (`models/`):
  - SQLAlchemy models for the data layer.
- Repositories (`repositories/`):
  - Data access layer over models and datastores.
- Services (`services/`):
  - Business logic layer implementing domain workflows.
- Utilities (`utilities/`):
  - Shared helpers and support functions.
- Core (`core/`):
  - Health checks, observability, resilience, tasks, security, feature flags, tenancy, versioning, testing helpers.

### 6.2 CLI Package

- `fastmvc_cli/`:
  - Implementation of the `fastmvc` CLI:
    - `generate` and `init` for project creation.
    - `add entity` and `add service` for scaffolding.
    - `migrate` for Alembic migrations.
    - `info` and `version` commands.

---

## 7. How to Use This File in a Docs Site

- As a **single-page reference**:
  - Import `docs/full-docs.md` into your docs framework as an “All-in-one” or “Printable” page.
- As a **content source**:
  - Split this file or reuse the existing `docs/index.md`, `docs/getting-started.md`, `docs/cli.md`, `docs/architecture.md`, `docs/configuration.md`, and `docs/modules.md` for multi-page navigation.

