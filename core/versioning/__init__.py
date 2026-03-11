"""
API Versioning Module.

Provides API versioning support for FastAPI applications:
- URL path versioning (/api/v1/users, /api/v2/users)
- Header versioning (Accept: application/vnd.api+json;version=2)
- Query parameter versioning (/users?version=2)

Usage:
    from core.versioning import APIVersion, versioned_router

    router = versioned_router(prefix="/users")

    @router.get("/", version="v1")
    async def get_users_v1():
        pass

    @router.get("/", version="v2")
    async def get_users_v2():
        pass
"""

from core.versioning.router import (
    APIVersion,
    VersionedAPIRouter,
    VersioningMiddleware,
    VersioningStrategy,
    get_api_version,
    versioned_router,
)

__all__ = [
    "APIVersion",
    "VersionedAPIRouter",
    "VersioningMiddleware",
    "VersioningStrategy",
    "versioned_router",
    "get_api_version",
]
