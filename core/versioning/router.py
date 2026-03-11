"""
API Versioning Implementation.

Provides versioned routing for FastAPI applications.
"""

import contextvars
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable for current API version
_current_version: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "api_version", default=None
)


class VersioningStrategy(str, Enum):
    """API versioning strategies."""

    URL_PATH = "url_path"  # /api/v1/users
    HEADER = "header"  # Accept: application/vnd.api+json;version=1
    QUERY = "query"  # /users?api_version=1


@dataclass
class APIVersion:
    """
    API Version representation.

    Attributes:
        version: Version string (e.g., "v1", "v2").
        deprecated: Whether this version is deprecated.
        sunset_date: Date when version will be removed.
        description: Version description.
    """

    version: str
    deprecated: bool = False
    sunset_date: Optional[str] = None
    description: str = ""

    @property
    def major(self) -> int:
        """Get major version number."""
        match = re.match(r"v?(\d+)", self.version)
        return int(match.group(1)) if match else 0

    def __str__(self) -> str:
        return self.version


def get_api_version() -> Optional[str]:
    """Get current API version from context."""
    return _current_version.get()


def set_api_version(version: str) -> contextvars.Token:
    """Set current API version in context."""
    return _current_version.set(version)


class VersionedAPIRouter(APIRouter):
    """
    FastAPI router with version support.

    Usage:
        router = VersionedAPIRouter(prefix="/users")

        @router.get("/", versions=["v1", "v2"])
        async def get_users():
            version = get_api_version()
            if version == "v2":
                return {"users": [], "meta": {}}
            return {"users": []}

        # Or with separate handlers
        @router.get("/", version="v1")
        async def get_users_v1():
            return {"users": []}

        @router.get("/", version="v2")
        async def get_users_v2():
            return {"users": [], "meta": {}}
    """

    def __init__(
        self,
        *args: Any,
        default_version: str = "v1",
        available_versions: Optional[list[str]] = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._default_version = default_version
        self._available_versions = available_versions or ["v1"]
        self._version_handlers: dict[str, dict[str, Callable]] = {}

    def _versioned_route(
        self,
        path: str,
        method: str,
        version: Optional[str] = None,
        versions: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Callable:
        """Create a versioned route decorator."""

        def decorator(func: Callable) -> Callable:
            route_versions = versions or ([version] if version else self._available_versions)

            for v in route_versions:
                key = f"{method}:{path}"
                if key not in self._version_handlers:
                    self._version_handlers[key] = {}
                self._version_handlers[key][v] = func

            return func

        return decorator

    def get(
        self,
        path: str,
        version: Optional[str] = None,
        versions: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Callable:
        """Add versioned GET route."""
        if version or versions:
            return self._versioned_route(path, "GET", version, versions, **kwargs)
        return super().get(path, **kwargs)

    def post(
        self,
        path: str,
        version: Optional[str] = None,
        versions: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Callable:
        """Add versioned POST route."""
        if version or versions:
            return self._versioned_route(path, "POST", version, versions, **kwargs)
        return super().post(path, **kwargs)

    def put(
        self,
        path: str,
        version: Optional[str] = None,
        versions: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Callable:
        """Add versioned PUT route."""
        if version or versions:
            return self._versioned_route(path, "PUT", version, versions, **kwargs)
        return super().put(path, **kwargs)

    def delete(
        self,
        path: str,
        version: Optional[str] = None,
        versions: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Callable:
        """Add versioned DELETE route."""
        if version or versions:
            return self._versioned_route(path, "DELETE", version, versions, **kwargs)
        return super().delete(path, **kwargs)


def versioned_router(
    prefix: str = "",
    default_version: str = "v1",
    versions: Optional[list[str]] = None,
    **kwargs: Any,
) -> VersionedAPIRouter:
    """
    Create a versioned API router.

    Usage:
        router = versioned_router(prefix="/users", versions=["v1", "v2"])
    """
    return VersionedAPIRouter(
        prefix=prefix,
        default_version=default_version,
        available_versions=versions,
        **kwargs,
    )


class VersioningMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API version detection.

    Supports multiple versioning strategies:
    - URL path: /api/v1/users
    - Header: Accept-Version: v1
    - Query: ?api_version=v1
    """

    def __init__(
        self,
        app: Any,
        strategy: VersioningStrategy = VersioningStrategy.URL_PATH,
        default_version: str = "v1",
        available_versions: Optional[list[str]] = None,
        header_name: str = "Accept-Version",
        query_param: str = "api_version",
        version_prefix: str = "v",
    ):
        super().__init__(app)
        self._strategy = strategy
        self._default = default_version
        self._available = available_versions or ["v1"]
        self._header_name = header_name
        self._query_param = query_param
        self._version_prefix = version_prefix

    def _extract_version_from_path(self, path: str) -> tuple[Optional[str], str]:
        """Extract version from URL path."""
        # Match patterns like /api/v1/users or /v1/users
        pattern = rf"/(?:api/)?({self._version_prefix}\d+)(/.*)?$"
        match = re.match(pattern, path)
        if match:
            version = match.group(1)
            remaining_path = match.group(2) or "/"
            return version, remaining_path
        return None, path

    def _extract_version_from_header(self, request: Request) -> Optional[str]:
        """Extract version from header."""
        version = request.headers.get(self._header_name)
        if version:
            # Handle format like "application/vnd.api+json;version=1"
            if "version=" in version:
                match = re.search(r"version=(\d+)", version)
                if match:
                    return f"{self._version_prefix}{match.group(1)}"
            return version
        return None

    def _extract_version_from_query(self, request: Request) -> Optional[str]:
        """Extract version from query parameter."""
        version = request.query_params.get(self._query_param)
        if version:
            if not version.startswith(self._version_prefix):
                return f"{self._version_prefix}{version}"
            return version
        return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        version: Optional[str] = None

        # Extract version based on strategy
        if self._strategy == VersioningStrategy.URL_PATH:
            version, _ = self._extract_version_from_path(request.url.path)
        elif self._strategy == VersioningStrategy.HEADER:
            version = self._extract_version_from_header(request)
        elif self._strategy == VersioningStrategy.QUERY:
            version = self._extract_version_from_query(request)

        # Use default if not found
        version = version or self._default

        # Validate version
        if version not in self._available:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid API version: {version}. Available: {self._available}",
            )

        # Set version in context
        token = set_api_version(version)

        # Set on request state
        request.state.api_version = version

        try:
            response = await call_next(request)

            # Add version to response headers
            response.headers["X-API-Version"] = version

            return response
        finally:
            _current_version.reset(token)


def require_version(*versions: str) -> Callable:
    """
    Dependency to require specific API versions.

    Usage:
        @router.get("/new-feature", dependencies=[Depends(require_version("v2", "v3"))])
        async def new_feature():
            pass
    """

    async def check_version(request: Request) -> None:
        current = get_api_version() or getattr(request.state, "api_version", None)
        if current not in versions:
            raise HTTPException(
                status_code=400,
                detail=f"This endpoint requires API version: {', '.join(versions)}",
            )

    return check_version


def deprecated_in_version(
    version: str,
    sunset_date: Optional[str] = None,
    alternative: Optional[str] = None,
) -> Callable:
    """
    Dependency to mark endpoint as deprecated in specific version.

    Usage:
        @router.get(
            "/old-endpoint",
            dependencies=[Depends(deprecated_in_version("v2", sunset_date="2025-01-01"))]
        )
        async def old_endpoint():
            pass
    """

    async def add_deprecation_headers(request: Request, response: Response) -> None:
        current = get_api_version()
        if current == version:
            response.headers["Deprecation"] = "true"
            if sunset_date:
                response.headers["Sunset"] = sunset_date
            if alternative:
                response.headers["Link"] = f'<{alternative}>; rel="successor-version"'

    return add_deprecation_headers
