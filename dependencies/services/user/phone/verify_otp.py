"""Phone Verify-OTP Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.phone.verify_otp import PhoneVerifyOtpService


class PhoneVerifyOtpServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for PhoneVerifyOtpService."""

    service_cls = PhoneVerifyOtpService


__all__ = ["PhoneVerifyOtpServiceDependency"]
