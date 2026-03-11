# Changelog

All notable changes to FastMVC will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Async SQLAlchemy repository option
- WebSocket support
- OpenTelemetry tracing integration

## [1.2.0] - 2026-01-18

### Added
- **Enhanced README for Generated Projects** - Modern, visually appealing README with:
  - Architecture diagrams
  - Quick start guide
  - CLI command reference
  - Middleware stack documentation
  - Security features table
- **Improved CLI Output** - Better formatted help messages with emojis and visual separators
- **fastmiddleware Support in Generated Entities** - Controllers now use `get_request_id()` from fastmiddleware with fallback

### Changed
- Updated `fastmvc info` command with visual formatting and middleware documentation
- Generated controllers now import and use `fastmiddleware.request_context.get_request_id()` for request tracking
- Improved entity generator templates with better fastmiddleware integration

### Fixed
- Request URN handling in generated controllers now supports both fastmiddleware and legacy request.state.urn

## [1.1.0] - 2026-01-18

### Added
- **fastmiddleware Integration** - Integrated [fastmvc-middleware](https://pypi.org/project/fastmvc-middleware/) package with 90+ production-ready middleware components
  - SecurityHeadersMiddleware with enhanced configuration
  - RateLimitMiddleware with sliding window algorithm
  - RequestContextMiddleware for request tracking
  - TimingMiddleware for response time headers
  - LoggingMiddleware for structured request/response logging
  - CORSMiddleware and TrustedHostMiddleware
- Compatibility layer in AuthenticationMiddleware to work with fastmiddleware's RequestContextMiddleware
- Enhanced README with middleware documentation and visual diagrams

### Changed
- Updated middleware stack to use fastmiddleware package components
- Improved request URN handling to support both local and fastmiddleware request IDs

### Dependencies
- Added `fastmvc-middleware>=0.5.0` as core dependency

## [1.0.0] - 2026-01-18

### Added
- **CLI Tool** - Full command-line interface with `fastmvc` command
  - `fastmvc generate <project>` - Create new FastMVC projects
  - `fastmvc add entity <name>` - Generate CRUD scaffolding for entities
  - `fastmvc migrate` - Database migration commands (generate, upgrade, downgrade, status, history)
  - `fastmvc info` - Display framework information
  - `fastmvc version` - Show version
- **Project Generator** - Complete project scaffolding with:
  - MVC directory structure
  - Docker and docker-compose configuration
  - Environment configuration templates
  - Git initialization
  - Virtual environment creation (optional)
- **Entity Generator** - Full CRUD scaffolding including:
  - SQLAlchemy model with common fields
  - Repository with CRUD operations
  - Service layer with business logic
  - Controller with REST endpoints
  - Request/Response DTOs
  - Dependency injection factories
  - Unit tests
- **Database Migrations** - Alembic integration for schema management
- **Caching Utilities** - Redis-based caching with decorators
  - `@cache.cached()` - Cache function results
  - `@cache.invalidate()` - Invalidate cache after modifications
  - Pattern-based cache invalidation
- **Product Example Entity** - Complete CRUD example with tests

### Changed
- Updated documentation with comprehensive examples
- Improved README with CLI usage instructions
- Enhanced pyproject.toml for PyPI publishing

### Security
- JWT authentication middleware
- Rate limiting with sliding window algorithm
- Security headers middleware (CSP, HSTS, X-Frame-Options)
- Input validation and sanitization
- SQL injection prevention
- XSS prevention
- Path traversal prevention

## [0.1.0] - 2025-01-01

### Added
- Initial release
- MVC architecture pattern for FastAPI
- User authentication (login, logout, register)
- SQLAlchemy ORM integration
- Redis caching integration
- Pydantic v2 validation
- Structured logging with Loguru
- Docker support
- Comprehensive documentation

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.2.0 | 2026-01-18 | Enhanced CLI, improved generators, better fastmiddleware integration |
| 1.1.0 | 2026-01-18 | fastmiddleware integration with 90+ middleware components |
| 1.0.0 | 2026-01-18 | Major release with CLI, entity generator, migrations |
| 0.1.0 | 2025-01-01 | Initial release |

## Upgrade Guide

### From 0.1.0 to 1.0.0

1. Update your installation:
   ```bash
   pip install --upgrade fastmvc
   ```

2. Add Alembic configuration:
   ```bash
   # Copy alembic.ini and migrations/ from a new project
   fastmvc generate temp_project
   cp temp_project/alembic.ini .
   cp -r temp_project/migrations .
   rm -rf temp_project
   ```

3. Update your models to use the new base:
   ```python
   from models import Base  # Now includes alembic support
   ```

4. Generate initial migration:
   ```bash
   fastmvc migrate generate "initial schema"
   fastmvc migrate upgrade
   ```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to FastMVC.

## License

MIT License - see [LICENSE](LICENSE) for details.

