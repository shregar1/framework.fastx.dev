"""Verify-MFA Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.account.verify_mfa import VerifyMFAService


class VerifyMFAServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for VerifyMFAService."""

    service_cls = VerifyMFAService


__all__ = ["VerifyMFAServiceDependency"]
