"""Send-Verification-Email Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.account.send_verification_email import SendVerificationEmailService


class SendVerificationEmailServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for SendVerificationEmailService."""

    service_cls = SendVerificationEmailService


__all__ = ["SendVerificationEmailServiceDependency"]
