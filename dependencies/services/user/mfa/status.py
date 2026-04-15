"""MFA Status Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.mfa.status import MFAStatusService


class MFAStatusServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for MFAStatusService."""

    service_cls = MFAStatusService


__all__ = ["MFAStatusServiceDependency"]
