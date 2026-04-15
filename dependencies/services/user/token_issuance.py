"""Token Issuance Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.token_issuance import TokenIssuanceService


class TokenIssuanceServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for TokenIssuanceService."""

    service_cls = TokenIssuanceService


__all__ = ["TokenIssuanceServiceDependency"]
