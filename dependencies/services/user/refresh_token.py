"""User Refresh Token Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.refresh_token import UserRefreshTokenService


class UserRefreshTokenServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for UserRefreshTokenService."""

    service_cls = UserRefreshTokenService


__all__ = ["UserRefreshTokenServiceDependency"]
