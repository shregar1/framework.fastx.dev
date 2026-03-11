"""
Multi-Tenancy Module.

Provides multi-tenancy support for SaaS applications:
- Tenant context management
- Automatic query scoping
- Tenant-aware middleware
- Tenant isolation

Usage:
    from core.tenancy import TenantContext, get_current_tenant

    # In middleware, set tenant context
    async def tenant_middleware(request: Request, call_next):
        tenant = await resolve_tenant(request)
        with TenantContext(tenant):
            return await call_next(request)

    # In services/repositories
    tenant = get_current_tenant()
    users = await repo.get_all(tenant_id=tenant.id)
"""

from core.tenancy.context import (
    Tenant,
    TenantContext,
    get_current_tenant,
    get_current_tenant_id,
    set_current_tenant,
)
from core.tenancy.middleware import TenantMiddleware, TenantResolver

__all__ = [
    "Tenant",
    "TenantContext",
    "get_current_tenant",
    "get_current_tenant_id",
    "set_current_tenant",
    "TenantMiddleware",
    "TenantResolver",
]
