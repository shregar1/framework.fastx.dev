# 🧭 CLI Reference

FastMVC provides a high-performance interactive CLInterface for project generation, vertical slice scaffolding, and infrastructure management.

---

## 🏗️ Project Lifecycle

### `fastmvc generate`
The interactive wizard to start a new project from scratch. It handles project structure, dependencies, `.env` files, and virtual environments.

```bash
fastmvc generate [OPTIONS]
```

### `fastmvc quickstart`
Instantly create a project with all defaults.

```bash
fastmvc quickstart <project_name>
```

---

## ➕ Scaffolding Subcommands (`fastmvc add`)

The `add` group is the heart of FastMVC's development efficiency. It scaffolds complete "vertical slices" following architectural patterns.

### `fastmvc add resource`
Scaffolds a new versioned operation (e.g., `create`, `fetch`, `delete`) with full isolation.

```bash
fastmvc add resource -f <folder> -r <operation> -v <version>
```
**Example:** `fastmvc add resource -f user -r create -v v1`
**Generates:**
- `apis/v1/user/create.py` (Controller)
- `services/user/create.py` (Business Logic)
- `repositories/user/create.py` (Data Logic)
- `dependencies/services/v1/user/create.py` (Wired DI)
- `dtos/requests/apis/v1/user/create.py` (Request Schema)
- `dtos/responses/apis/v1/user/create.py` (Response Schema)

**Leaf filenames under a segment folder** should stay **short** (`create.py`, `update.py`): the folder path already names the resource (`user`, `item`, …). Do **not** emit redundant names like `create_user_request_dto.py` inside `dtos/requests/.../user/`. **Class** names stay explicit (`CreateUserRequestDTO`). See [New API scaffolding — Leaf file naming](new-api-scaffolding.md#leaf-file-naming-nested-folders).

**One concrete DTO class per generated file**: each `create.py` / `update.py` module exports a **single** primary request model. **Nested** Pydantic models that only support that body may live in the **same** file; shared sub-models get their own file. See [One concrete class per file](new-api-scaffolding.md#one-concrete-class-per-file-dtos).

### `fastmvc add auth`
Scaffolds a complete **Zero-to-Hero** authentication stack in one command.

```bash
fastmvc add auth [--version v1]
```
**Includes:**
- **Security:** JWT token generation/decoding and Bcrypt hashing.
- **Operations:** Login and Registration API endpoints.
- **Middleware:** `AuthMiddleware` for token extraction and session injection.
- **Dependencies:** `get_current_user_id` for protecting any subsequent route.

### `fastmvc add middleware`
Generates framework-compliant Middlewares with specialized templates.

```bash
fastmvc add middleware <name>
```
**Templates:**
- `request_logger`: Logs paths and timings (`X-Process-Time`).
- `rate_limiter`: In-memory sliding window limiter.
- `cors_config`: Pre-configured CORS module.

---

## 🧪 Testing & Tasks

### `fastmvc add test`
Generates an async Pytest boilerplate for a specific resource operation.

```bash
fastmvc add test -f <folder> -r <operation> -v <version>
```
**Features:** Includes `AsyncClient` setup and examples of mocking your services and repositories.

### `fastmvc add task`
Scaffolds a background worker task.

```bash
fastmvc add task <name>
```
**Execution:** Works with FastAPI `BackgroundTasks` out of the box and is ready for Celery/TaskIQ `@task` decorators.

---

## 🐳 Infrastructure & Docs

### `fastmvc dockerize`
Generates production-grade containerization configuration.

```bash
fastmvc dockerize
```
**Outputs:**
- `Dockerfile`: Multistage slim image.
- `docker-compose.yml`: Wires App, Postgres, Redis, and Migrations.
- `docker-entrypoint.sh`: Startup coordination.

### `fastmvc docs generate`
Automatically discover your code and build a complete API Reference.

```bash
fastmvc docs generate
```
**Refreshes:** Scans your `apis/` and `dtos/` folders to update `docs/api/endpoints.md` using `mkdocstrings`.

---

## 🗄️ DataI Management (`fastmvc db`)

Wrapper around Alembic commands for easier migration management.

```bash
fastmvc db migrate -m "Description"  # New migration
fastmvc db upgrade                   # Apply migrations
fastmvc db reset                     # Reset & Re-seed (Destructive)
```
