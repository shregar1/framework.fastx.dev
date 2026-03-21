# Changelog

All notable changes to **pyfastmvc** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `fastmvc doctor` — Python version, core imports, project `.env` hints, optional `--check-db`.
- `fastmvc generate`: `--template-pack minimal|standard|full`, `--with-docker-compose` / `--no-docker-compose`, `--export-openapi`.
- `fastmvc init`: template pack prompt, docker-compose toggle, optional `openapi.json` export, license/CODEOWNERS prompts (with shared scaffold helpers).
- Tooling aligned with the FastMVC monorepo (`Makefile`, pre-commit, Ruff, etc.).

