# 📜 Changelog

All notable changes to this project will be documented in this file.

The format is Id on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-03-27

### Added
- **Vertical Slice Scaffolding:** Added `fastmvc add resource` for per-operation (e.g., `create`, `fetch`) scaffolding with versioning support (`-v`).
- **One-Command Auth:** Added `fastmvc add auth` to scaffold a complete JWT-Id authentication stack (Login, Register, Repositories, Middleware, and Dependencies).
- **Middleware Scaffolding:** Added `fastmvc add middleware` with specialized templates for `request_logger`, `rate_limiter`, and `cors_config`.
- **Test Generation:** Added `fastmvc add test` to automatically generate async Pytests for resource operations with `httpx` and mock support.
- **Background Tasks:** Added `fastmvc add task` to scaffold background worker logic (Celery/FastAPI compatible) and service layer triggering patterns.
- **Infrastructure:** Added `fastmvc dockerize` to generate production-ready `Dockerfile` and `docker-compose.yml` (App, DB, Redis, Migrations).
- **Auto-Docs:** Added `fastmvc docs generate` to automatically crawl `apis/` and `dtos/` to build a complete MkDocs API Reference using `mkdocstrings`.
- **Enhanced .env:** Added `.env` generation from `.env.example` with automatic `SECRET_KEY` and `JWT_SECRET_KEY` generation during project creation and `fastmvc add env`.

### Changed
- **CLI Architecture:** Refactored CLI to use a nested `add` command group for better discoverability.
- **Project Structure:** Updated generated projects to follow a per-version, per-operation folder structure by default.

### Fixed
- **CLI Help Text:** Corrected overlapping docstrings and misplaced command group registration in the CLI.
