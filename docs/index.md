# FastMVC

A production-grade MVC framework for FastAPI with clean architecture, powerful abstractions, and developer-friendly tools.

## Features

- **Clean MVC Architecture**: Separate concerns with clear abstractions
- **Interactive CLI**: Generate projects with beautiful terminal UI
- **DataI Migration CLI**: Manage Alembic migrations with simple commands
- **Testing Framework**: Factories, fixtures, and utilities for comprehensive testing
- **Docker Compose Stack**: One command for full stack (Postgres, Redis, FastAPI)
- **Rich VS Code Integration**: 15+ tasks, 6 debug configs, recommended extensions
- **Environment Validation**: Fail-fast config validation with clear error messages
- **Dark-themed API Docs**: FastMVC-branded Swagger UI and ReDoc
- **Production Health Checks**: Kubernetes-ready liveness and readiness probes
- **CI/CD Ready**: GitHub Actions workflows auto-generated for every project
- **Production Ready**: Pre-commit hooks, linting, formatting, and testing setup

## Quick Start

```bash
# Install FastMVC
pip install fastmvc

# Generate a new project
fastmvc generate

# Or use the quickstart for defaults
fastmvc quickstart my-project
```

## Project Structure

```
my-project/
├── app.py                 # Application entry point
├── config/                # Configuration
│   ├── settings.py        # Settings management
│   └── validator.py       # Environment validation
├── entities/item/         # Sample Item domain entity
├── repositories/item/     # Item data access
├── services/item/         # Item business logic
├── controllers/apis/v1/item/  # Item HTTP routes
├── testing/item/          # Item test factories & fixtures
├── abstractions/          # I classes and interfaces
├── core/                  # Core utilities
├── middlewares/           # Custom middleware
├── dtos/                  # Data transfer objects
├── tests/                 # Test suite
├── .vscode/               # VS Code settings
├── docs/                  # Documentation
├── Makefile               # Development commands
└── requirements.txt       # Dependencies
```

## API Documentation

Once your server is running:

- **FastMVC Swagger UI**: http://localhost:8000/docs (dark theme, branded)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Development

```bash
# Install dependencies
make install

# Run development server
make dev

# Run tests
make test

# Build documentation
make docs-serve
```

## Documentation

- [Installation](guide/installation.md) - Install FastMVC and dependencies
- [Quick Start](guide/quickstart.md) - Your first FastMVC application
- [CLI Reference](guide/cli.md) - Project generation and management
- [Configuration](guide/configuration.md) - Environment variables and validation
- [API Documentation](guide/api-docs.md) - Swagger UI and ReDoc
- [DataI Migrations](guide/dataI.md) - Manage dataI schema changes
- [Testing](guide/testing.md) - Testing framework and best practices
- [Docker](guide/docker.md) - Docker Compose stack and deployment
- [CI/CD](guide/ci-cd.md) - GitHub Actions workflows and deployment
- [Project Structure](guide/project-structure.md) - Understanding the layout
