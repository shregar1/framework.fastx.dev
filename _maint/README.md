# `_maint` — maintenance & infrastructure

## What this folder is

**`_maint`** holds **operational assets** that the **hosting and developer workflow** depend on: Docker-related **nginx** configuration, PostgreSQL **bootstrap SQL**, and **scripts** (seeding, git metadata hooks). It is **not** part of the FastAPI application’s feature code (`controllers`, `services`, etc.).

Think of `_maint` as the **“how we run and provision the system”** layer: change it when you change **compose**, **reverse proxy**, **DB init**, or **automation**—not when you add a new business endpoint.

## Why it exists separately

- **Clear boundary** — Application code stays portable; infra stays explicit.  
- **Safer reviews** — Changes here affect deployments and hooks; they deserve focused review.  
- **Documentation** — See **`docs/guide/maint-folder.md`** (also in MkDocs: *The `_maint` folder (critical)*).

## Contents

| Path | Purpose |
|------|---------|
| **`nginx/`** | `nginx.conf` and `ssl/` for the optional nginx service in `docker-compose.yml`. |
| **`init-scripts/`** | SQL executed on **first** PostgreSQL init (mounted as `docker-entrypoint-initdb.d`). |
| **`scripts/`** | `seed.py`, `git_log_recorder.py`, and similar; referenced from **`docker-entrypoint.sh`** and **`.pre-commit-config.yaml`**. |

## Critical warning

**Do not rename, move, or delete** this directory or its subpaths without updating **every** reference:

- `docker-compose.yml` (volume mounts)  
- `docker-entrypoint.sh`  
- `.pre-commit-config.yaml`  
- Documentation under `docs/guide/`  

Misplaced edits break **local Docker**, **database init**, and **git hooks** without touching Python imports.

## Who should edit this

- **Platform / DevOps** or maintainers responsible for deployment.  
- **Not** typical feature development—unless the task is explicitly infrastructure-related.

## See also

- [`docs/guide/maint-folder.md`](../docs/guide/maint-folder.md) — full policy and checklist  
- [README.md — Contributing](../README.md#contributing) — contributor note on `_maint`  
