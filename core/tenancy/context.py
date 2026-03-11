"""
Tenant Context Management.

Provides context-aware tenant management using context variables.
"""

import contextvars
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

# Context variable for current tenant
_current_tenant: contextvars.ContextVar[Optional["Tenant"]] = contextvars.ContextVar(
    "current_tenant", default=None
)


@dataclass
class TenantConfig:
    """Tenant-specific configuration."""

    max_users: Optional[int] = None
    max_storage_mb: Optional[int] = None
    features: list[str] = field(default_factory=list)
    custom_domain: Optional[str] = None
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class Tenant:
    """
    Tenant representation.

    Attributes:
        id: Unique tenant identifier.
        name: Tenant display name.
        slug: URL-safe identifier.
        is_active: Whether tenant is active.
        created_at: Creation timestamp.
        config: Tenant-specific configuration.
        metadata: Additional metadata.
    """

    id: str
    name: str
    slug: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    config: TenantConfig = field(default_factory=TenantConfig)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "config": {
                "max_users": self.config.max_users,
                "max_storage_mb": self.config.max_storage_mb,
                "features": self.config.features,
                "custom_domain": self.config.custom_domain,
                "settings": self.config.settings,
            },
            "metadata": self.metadata,
        }

    def has_feature(self, feature: str) -> bool:
        """Check if tenant has a feature enabled."""
        return feature in self.config.features


def get_current_tenant() -> Optional[Tenant]:
    """
    Get the current tenant from context.

    Returns:
        Current tenant or None if not set.
    """
    return _current_tenant.get()


def get_current_tenant_id() -> Optional[str]:
    """
    Get the current tenant ID from context.

    Returns:
        Current tenant ID or None if not set.
    """
    tenant = get_current_tenant()
    return tenant.id if tenant else None


def set_current_tenant(tenant: Optional[Tenant]) -> contextvars.Token:
    """
    Set the current tenant in context.

    Args:
        tenant: Tenant to set.

    Returns:
        Token for resetting context.
    """
    return _current_tenant.set(tenant)


def clear_current_tenant() -> None:
    """Clear the current tenant from context."""
    _current_tenant.set(None)


class TenantContext:
    """
    Context manager for tenant operations.

    Usage:
        tenant = Tenant(id="t1", name="Acme", slug="acme")
        with TenantContext(tenant):
            # All operations in this block use this tenant
            current = get_current_tenant()
    """

    def __init__(self, tenant: Tenant):
        """
        Initialize context with tenant.

        Args:
            tenant: Tenant for this context.
        """
        self._tenant = tenant
        self._token: Optional[contextvars.Token] = None

    def __enter__(self) -> "TenantContext":
        self._token = set_current_tenant(self._tenant)
        return self

    def __exit__(self, *args: Any) -> None:
        if self._token:
            _current_tenant.reset(self._token)

    async def __aenter__(self) -> "TenantContext":
        return self.__enter__()

    async def __aexit__(self, *args: Any) -> None:
        self.__exit__(*args)


class TenantStore:
    """Base class for tenant storage."""

    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        pass

    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        pass

    async def get_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by custom domain."""
        pass

    async def create(self, tenant: Tenant) -> Tenant:
        """Create a new tenant."""
        pass

    async def update(self, tenant: Tenant) -> Tenant:
        """Update tenant."""
        pass

    async def delete(self, tenant_id: str) -> None:
        """Delete tenant."""
        pass

    async def list_all(self, active_only: bool = True) -> list[Tenant]:
        """List all tenants."""
        return []


class InMemoryTenantStore(TenantStore):
    """In-memory tenant store for development/testing."""

    def __init__(self):
        self._tenants: dict[str, Tenant] = {}
        self._slug_index: dict[str, str] = {}
        self._domain_index: dict[str, str] = {}

    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        return self._tenants.get(tenant_id)

    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        tenant_id = self._slug_index.get(slug)
        return self._tenants.get(tenant_id) if tenant_id else None

    async def get_by_domain(self, domain: str) -> Optional[Tenant]:
        tenant_id = self._domain_index.get(domain)
        return self._tenants.get(tenant_id) if tenant_id else None

    async def create(self, tenant: Tenant) -> Tenant:
        self._tenants[tenant.id] = tenant
        self._slug_index[tenant.slug] = tenant.id
        if tenant.config.custom_domain:
            self._domain_index[tenant.config.custom_domain] = tenant.id
        return tenant

    async def update(self, tenant: Tenant) -> Tenant:
        # Update indexes if needed
        old_tenant = self._tenants.get(tenant.id)
        if old_tenant:
            if old_tenant.slug != tenant.slug:
                del self._slug_index[old_tenant.slug]
            if old_tenant.config.custom_domain != tenant.config.custom_domain:
                if old_tenant.config.custom_domain:
                    del self._domain_index[old_tenant.config.custom_domain]

        self._tenants[tenant.id] = tenant
        self._slug_index[tenant.slug] = tenant.id
        if tenant.config.custom_domain:
            self._domain_index[tenant.config.custom_domain] = tenant.id
        return tenant

    async def delete(self, tenant_id: str) -> None:
        tenant = self._tenants.get(tenant_id)
        if tenant:
            del self._slug_index[tenant.slug]
            if tenant.config.custom_domain:
                del self._domain_index[tenant.config.custom_domain]
            del self._tenants[tenant_id]

    async def list_all(self, active_only: bool = True) -> list[Tenant]:
        tenants = list(self._tenants.values())
        if active_only:
            tenants = [t for t in tenants if t.is_active]
        return tenants
