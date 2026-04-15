"""MFA Setup Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.mfa.setup import MFASetupService


class MFASetupServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for MFASetupService."""

    service_cls = MFASetupService


__all__ = ["MFASetupServiceDependency"]
