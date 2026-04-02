"""Logical layout of the ``fastx-mvc`` application tree (aligned with ``fast_platform.taxonomy``).

The framework uses familiar top-level folders:

- **core** — app wiring, websockets, testing helpers
- **abstractions** — DDD-style ports (repository, service, controller, …)
- **controllers** — HTTP controllers
- **services** — application services
- **repositories** — data access
- **dtos** — request/response and configuration DTOs
- **middlewares** — FastAPI middleware
- **dependencies** — DI wiring
- **constants** — static constants
- **utilities** — helpers
- **fast_cli** — CLI and scaffolding (product tooling)

This maps conceptually to ``fast_platform`` sections (e.g. controllers/services → core;
repositories + models (via ``fast_dataI``) → persistence; middlewares → operations).
Physical folder names stay stable for the scaffolded app template.
"""

from __future__ import annotations

from enum import Enum
from typing import Final

__all__ = ["MvcSection", "FOLDER_TO_SECTION"]


class MvcSection(str, Enum):
    """Represents the MvcSection class."""

    CORE = "core"
    ABSTRACTIONS = "abstractions"
    CONTROLLERS = "controllers"
    SERVICES = "services"
    REPOSITORIES = "repositories"
    DTOS = "dtos"
    MIDDLEWARES = "middlewares"
    DEPENDENCIES = "dependencies"
    CONSTANTS = "constants"
    UTILITIES = "utilities"
    FAST_CLI = "fast_cli"


FOLDER_TO_SECTION: Final[dict[str, MvcSection]] = {
    "core": MvcSection.CORE,
    "abstractions": MvcSection.ABSTRACTIONS,
    "controllers": MvcSection.CONTROLLERS,
    "services": MvcSection.SERVICES,
    "repositories": MvcSection.REPOSITORIES,
    "dtos": MvcSection.DTOS,
    "middlewares": MvcSection.MIDDLEWARES,
    "dependencies": MvcSection.DEPENDENCIES,
    "constants": MvcSection.CONSTANTS,
    "utilities": MvcSection.UTILITIES,
    "fast_cli": MvcSection.FAST_CLI,
}
