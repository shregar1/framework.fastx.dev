"""MFA QR-Code Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.mfa.qr_code import MFAQrCodeService


class MFAQrCodeServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for MFAQrCodeService."""

    service_cls = MFAQrCodeService


__all__ = ["MFAQrCodeServiceDependency"]
