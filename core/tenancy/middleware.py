"""
Tenant Middleware.

Provides FastAPI middleware for automatic tenant resolution and context.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.tenancy.context import Tenant, TenantStore, set_current_tenant


class TenantResolver(ABC):
    """
    Abstract base class for tenant resolution.

    Implement this to define how tenants are resolved from requests.
    """

    @abstractmethod
    async def resolve(self, request: Request) -> Optional[Tenant]:
        """
        Resolve tenant from request.

        Args:
            request: FastAPI request.

        Returns:
            Resolved tenant or None.
        """
        pass


class HeaderTenantResolver(TenantResolver):
    """
    Resolve tenant from request header.

    Usage:
        resolver = HeaderTenantResolver(
            store=tenant_store,
            header_name="X-Tenant-ID"
        )
    """

    def __init__(
        self,
        store: TenantStore,
        header_name: str = "X-Tenant-ID",
    ):
        self._store = store
        self._header_name = header_name

    async def resolve(self, request: Request) -> Optional[Tenant]:
        tenant_id = request.headers.get(self._header_name)
        if tenant_id:
            return await self._store.get_by_id(tenant_id)
        return None


class SubdomainTenantResolver(TenantResolver):
    """
    Resolve tenant from subdomain.

    Example: tenant1.example.com -> tenant1

    Usage:
        resolver = SubdomainTenantResolver(
            store=tenant_store,
            base_domain="example.com"
        )
    """

    def __init__(
        self,
        store: TenantStore,
        base_domain: str,
        excluded_subdomains: Optional[list[str]] = None,
    ):
        self._store = store
        self._base_domain = base_domain
        self._excluded = excluded_subdomains or ["www", "api", "admin"]

    async def resolve(self, request: Request) -> Optional[Tenant]:
        host = request.headers.get("host", "")

        # Extract subdomain
        if host.endswith(f".{self._base_domain}"):
            subdomain = host.replace(f".{self._base_domain}", "")
            if subdomain and subdomain not in self._excluded:
                return await self._store.get_by_slug(subdomain)

        return None


class PathTenantResolver(TenantResolver):
    """
    Resolve tenant from URL path.

    Example: /tenant1/api/users -> tenant1

    Usage:
        resolver = PathTenantResolver(store=tenant_store, prefix="/t/")
    """

    def __init__(
        self,
        store: TenantStore,
        prefix: str = "/",
    ):
        self._store = store
        self._prefix = prefix

    async def resolve(self, request: Request) -> Optional[Tenant]:
        path = request.url.path

        if path.startswith(self._prefix):
            remaining = path[len(self._prefix):]
            parts = remaining.split("/", 1)
            if parts:
                tenant_slug = parts[0]
                return await self._store.get_by_slug(tenant_slug)

        return None


class JWTTenantResolver(TenantResolver):
    """
    Resolve tenant from JWT token claims.

    Usage:
        resolver = JWTTenantResolver(
            store=tenant_store,
            claim_name="tenant_id"
        )
    """

    def __init__(
        self,
        store: TenantStore,
        claim_name: str = "tenant_id",
    ):
        self._store = store
        self._claim_name = claim_name

    async def resolve(self, request: Request) -> Optional[Tenant]:
        # Check if user info is set by auth middleware
        user = getattr(request.state, "user", None)
        if user and hasattr(user, self._claim_name):
            tenant_id = getattr(user, self._claim_name)
            return await self._store.get_by_id(tenant_id)
        return None


class ChainedTenantResolver(TenantResolver):
    """
    Try multiple resolvers in order.

    Usage:
        resolver = ChainedTenantResolver([
            HeaderTenantResolver(store, "X-Tenant-ID"),
            SubdomainTenantResolver(store, "example.com"),
            PathTenantResolver(store),
        ])
    """

    def __init__(self, resolvers: list[TenantResolver]):
        self._resolvers = resolvers

    async def resolve(self, request: Request) -> Optional[Tenant]:
        for resolver in self._resolvers:
            tenant = await resolver.resolve(request)
            if tenant:
                return tenant
        return None


class TenantMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for tenant context.

    Sets tenant context for each request based on resolver.

    Usage:
        from core.tenancy import TenantMiddleware, HeaderTenantResolver

        resolver = HeaderTenantResolver(store, "X-Tenant-ID")
        app.add_middleware(
            TenantMiddleware,
            resolver=resolver,
            required=True
        )
    """

    def __init__(
        self,
        app: Any,
        resolver: TenantResolver,
        required: bool = False,
        exclude_paths: Optional[set[str]] = None,
    ):
        """
        Initialize tenant middleware.

        Args:
            app: FastAPI application.
            resolver: Tenant resolver implementation.
            required: Whether tenant is required for all requests.
            exclude_paths: Paths to exclude from tenant requirement.
        """
        super().__init__(app)
        self._resolver = resolver
        self._required = required
        self._exclude_paths = exclude_paths or {"/health", "/metrics", "/docs", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip excluded paths
        if request.url.path in self._exclude_paths:
            return await call_next(request)

        # Resolve tenant
        tenant = await self._resolver.resolve(request)

        if tenant is None and self._required:
            raise HTTPException(
                status_code=400,
                detail="Tenant not found or not specified",
            )

        if tenant and not tenant.is_active:
            raise HTTPException(
                status_code=403,
                detail="Tenant is not active",
            )

        # Set tenant context
        token = set_current_tenant(tenant)

        # Also set on request state for easy access
        request.state.tenant = tenant
        request.state.tenant_id = tenant.id if tenant else None

        try:
            response = await call_next(request)

            # Add tenant ID to response headers (optional)
            if tenant:
                response.headers["X-Tenant-ID"] = tenant.id

            return response
        finally:
            # Reset context (automatic with contextvars, but explicit is clearer)
            pass
