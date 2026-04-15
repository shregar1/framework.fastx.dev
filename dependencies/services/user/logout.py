"""User Logout Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.logout import UserLogoutService


class UserLogoutServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for UserLogoutService."""

    service_cls = UserLogoutService


__all__ = ["UserLogoutServiceDependency"]
