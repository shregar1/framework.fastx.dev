"""User Login Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.login import UserLoginService


class UserLoginServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for UserLoginService."""

    service_cls = UserLoginService


__all__ = ["UserLoginServiceDependency"]
