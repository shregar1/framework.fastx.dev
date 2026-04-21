"""Phone Send-OTP Service Dependency."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from abstractions.dependency_factory import ServiceDependencyFactory
from abstractions.service import IService
from services.user.phone.send_otp import PhoneSendOtpService
from utilities.phone_otp import PhoneOtpUtility


class PhoneSendOtpServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for PhoneSendOtpService."""

    service_cls = PhoneSendOtpService

    @classmethod
    def derive(cls) -> Callable[..., IService]:
        """Return a factory that injects a PhoneOtpUtility into PhoneSendOtpService."""

        def factory(
            urn: str | None = None,
            user_urn: str | None = None,
            api_name: str | None = None,
            user_id: Any = None,
            **deps: Any,
        ) -> IService:
            redis_client = deps.get("redis_client")
            phone_otp_service = PhoneOtpUtility(
                redis_client=redis_client,
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
            )
            return PhoneSendOtpService(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
                phone_otp_service=phone_otp_service,
                **deps,
            )

        return factory


__all__ = ["PhoneSendOtpServiceDependency"]
