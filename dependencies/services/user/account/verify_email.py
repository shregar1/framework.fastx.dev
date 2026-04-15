"""Verify-Email Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.account.verify_email import VerifyEmailService


class VerifyEmailServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for VerifyEmailService."""

    service_cls = VerifyEmailService


__all__ = ["VerifyEmailServiceDependency"]
