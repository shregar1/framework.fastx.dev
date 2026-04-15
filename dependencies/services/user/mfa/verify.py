"""MFA Verify Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.mfa.verify import MFAVerifyService


class MFAVerifyServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for MFAVerifyService."""

    service_cls = MFAVerifyService


__all__ = ["MFAVerifyServiceDependency"]
