# Changelog

All notable changes to **pyfastmvc** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `fastmvc doctor` — Python version, core imports, project `.env` hints, optional `--check-db`.
- `fastmvc generate`: `--template-pack minimal|standard|full`, `--with-docker-compose` / `--no-docker-compose`, `--export-openapi`.
- `fastmvc init`: template pack prompt, docker-compose toggle, optional `openapi.json` export, license/CODEOWNERS prompts (with shared scaffold helpers); `--ci` non-interactive profile; optional `docker-compose.health.yml` when Docker assets are included.
- Hooks: `post_generate` / `pre_run` from `fastmvc.toml` or `[tool.fastmvc.hooks]` in `pyproject.toml`, plus `FASTMVC_HOOKS_PATH` for extra plugin paths.
- `fastmvc version --check-pypi` (or `FASTMVC_CHECK_PYPI=1`) for optional PyPI latest vs installed.
- `fastmvc lint` — `ruff check .` from project root; `mypy` when `[tool.mypy]` exists in `pyproject.toml`.
- `fastmvc run` — runs `pre_run` hooks then `python -m uvicorn` (defaults: `app:app`, `--reload`).
- `fastmvc migrate *` — resolves `alembic.ini` by walking up from cwd and runs Alembic with `-c` and correct working directory.
- Tooling aligned with the FastMVC monorepo (`Makefile`, pre-commit, Ruff, etc.).

