# pyfastmvc (`fast_mvc_main`)

**Production-oriented MVC framework for FastAPI** — project generator, entity scaffolding, migrations, and conventions for controllers, services, repositories, DTOs, and tests.

| | |
|---|---|
| **Distribution name** | `pyfastmvc` |
| **Python** | ≥ 3.10 |
| **License** | MIT (see package metadata) |

This directory is the **main CLI and framework template** that ties the optional `fast_*` packages together. The rest of the monorepo provides integrations (DB, queues, storage, …); **`pyfastmvc`** is what you install to **create and evolve** applications.

---

## What you get

- **CLI commands** to generate projects, modules, entities, and Alembic migrations
- **Opinionated layout**: controllers, services, repositories, models, DTOs, errors
- **Documentation** for conventions: see `docs/RULES_*.md` in this folder (routing, controllers, services, repositories, DTOs, models, tests, config, dependencies, errors)
- **FastAPI-first** patterns with clear boundaries between layers

---

## Installation

From the monorepo root (editable install for development):

```bash
python -m pip install -e ./fast_mvc_main
```

Verify:

```bash
pyfastmvc --help
```

(Exact command name follows `entry_points` in package metadata.)

---

## Relationship to `fast_*` packages

- **`pyfastmvc`** scaffolds the app shell and patterns.
- **`fast_platform`**, **`fast_db`**, **`fast_dataI`**, etc. are **optional libraries** you add to `pyproject.toml` / `requirements.txt` when your generated app needs them.

The monorepo’s [`install_packages.sh`](../install_packages.sh) installs `fast_platform` through `fast_media` (and more) plus `pyfastmvc` for local integration testing.

---

## Links

- Upstream project URLs, issue tracker, and changelog are listed in `pyfastmvc.egg-info/PKG-INFO` / PyPI when published.
- Monorepo overview: [../README.md](../README.md)

---

## Development

Work inside `fast_mvc_main/` with your virtualenv active; reinstall with `pip install -e .` after metadata or entry point changes.
