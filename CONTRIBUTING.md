# Contributing to pyfastmvc

Thank you for your interest in contributing.

## Monorepo layout

This package usually lives inside the **FastMVC** monorepo. From the repo root, install in editable mode:

```bash
cd fast_mvc_main
pip install -e ".[dev]" || pip install -e .
pip install -r requirements.txt
pre-commit install
```

Standalone clone (if this package is its own git remote):

```bash
git clone https://github.com/shregar1/fastMVC.git
cd pyfastmvc
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]" || pip install -e .
pip install -r requirements.txt
pre-commit install
```

Canonical repository URL from `pyproject.toml`: `https://github.com/shregar1/fastMVC`.

## `_maint` (do not touch casually)

The **`_maint/`** directory is **critical infrastructure** (Docker nginx, DB `init-scripts`, seed/tooling scripts). It is **not** part of the application feature tree. **Do not rename, relocate, or edit** it without updating every reference (`docker-compose.yml`, `docker-entrypoint.sh`, `.pre-commit-config.yaml`, docs) and without maintainer review.

Authoritative doc: `docs/guide/maint-folder.md` (also published under **Getting Started** in MkDocs).

To copy EditorConfig, pre-commit config, and other shared files from `fast_middleware/` into every package:

```bash
# from monorepo root
python3 scripts/sync_package_tooling.py
```

## Test coverage

Many FastMVC libraries enforce **≥95% line coverage** via `pytest-cov` (`fail_under` in `pyproject.toml`). From this package directory:

```bash
python3 -m pytest tests/ -q --cov=src --cov-fail-under=95
```

(`fast_dataI` may use `--cov=fast_dataI`; `fast_dashboards` often uses `--cov=src/fast_dashboards` — see that package’s `pyproject.toml`.)

Overview: [../docs/COVERAGE.md](../docs/COVERAGE.md).

## DTOs (one class per file)

Under `dtos/requests/<segment>/`, keep **one concrete Pydantic model per module** (e.g. `create.py` → `ExampleCreateRequestDTO`). **Nested** models that only support a single parent may live in the **same** file. Shared bases live in `abstraction.py`. Details: [docs/guide/new-api-scaffolding.md](docs/guide/new-api-scaffolding.md#one-concrete-class-per-file-dtos), [dtos/README.md](dtos/README.md#one-concrete-class-per-file).

## Quality checks

```bash
make test
make lint
make format
```

See `Makefile` for all targets.

## Commits

Use clear commit messages (e.g. conventional commits: `feat:`, `fix:`, `docs:`).

Pull requests against `main` are welcome.
