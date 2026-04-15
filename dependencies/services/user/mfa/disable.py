"""MFA Disable Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.mfa.disable import MFADisableService


class MFADisableServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for MFADisableService."""

    service_cls = MFADisableService


__all__ = ["MFADisableServiceDependency"]
