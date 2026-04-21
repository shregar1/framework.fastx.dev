"""Phone Send-OTP Service – generates and dispatches a one-time passcode."""

from __future__ import annotations

from typing import Any, Optional

from constants.api_status import APIStatus
from dtos.responses.base import BaseResponseDTO
from fast_platform.errors import ServiceUnavailableError
from utilities.phone_otp import PhoneOtpUtility
from start_utils import logger


class PhoneSendOtpService:
    """Issue a phone OTP for login / register / verify-phone / reset-password."""

    def __init__(
        self,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: int | None = None,
        session: Any = None,
        redis_client: Any = None,
        phone_otp_service: PhoneOtpUtility | None = None,
    ) -> None:
        self._urn = urn or ""
        self._user_urn = user_urn
        self._api_name = api_name or "PHONE_SEND_OTP"
        self._user_id = user_id
        self._session = session
        self._redis = redis_client
        self._phone_otp_service = phone_otp_service
        self._logger = logger.bind(urn=self._urn, api_name=self._api_name)

    async def run(self, phone: str, purpose: str) -> BaseResponseDTO:
        if self._redis is None:
            raise ServiceUnavailableError(
                responseMessage="OTP service is temporarily unavailable.",
                responseKey="error_service_unavailable",
            )
        if self._phone_otp_service is None:
            raise ServiceUnavailableError(
                responseMessage="OTP service is temporarily unavailable.",
                responseKey="error_service_unavailable",
            )
        await self._phone_otp_service.create_and_send_otp(phone, purpose)
        return BaseResponseDTO(
            transactionUrn=self._urn,
            status=APIStatus.SUCCESS,
            responseMessage="If this number is valid, you will receive an OTP shortly.",
            responseKey="success_otp_sent",
            data={},
        )


__all__ = ["PhoneSendOtpService"]
