"""User Registration Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.register import UserRegistrationService


class UserRegistrationServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for UserRegistrationService."""

    service_cls = UserRegistrationService


__all__ = ["UserRegistrationServiceDependency"]
