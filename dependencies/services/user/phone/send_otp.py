"""Phone Send-OTP Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.phone.send_otp import PhoneSendOtpService


class PhoneSendOtpServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for PhoneSendOtpService."""

    service_cls = PhoneSendOtpService


__all__ = ["PhoneSendOtpServiceDependency"]
