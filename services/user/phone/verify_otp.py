"""Phone Verify-OTP Service – verify OTP and (optionally) issue tokens."""

from __future__ import annotations

from typing import Any, Optional

from dtos.requests.user.phone_verify_otp import PhoneVerifyOtpRequestDTO
from dtos.responses.base import BaseResponseDTO
from fast_platform.errors import ServiceUnavailableError
from utilities.phone_otp import PhoneOtpUtility
from services.user.phone_verify_service import verify_otp_and_issue_tokens
from start_utils import logger


class PhoneVerifyOtpService:
    """Verify a phone OTP and, for login/register, issue JWT tokens."""

    def __init__(
        self,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Any = None,
        session: Any = None,
        redis_client: Any = None,
        user_repository: Any = None,
        jwt_utility: Any = None,
        refresh_token_repository: Any = None,
    ) -> None:
        self._urn = urn or ""
        self._user_urn = user_urn
        self._api_name = api_name or "PHONE_VERIFY_OTP"
        self._user_id = user_id
        self._session = session
        self._redis = redis_client
        self._user_repository = user_repository
        self._jwt_utility = jwt_utility
        self._refresh_token_repository = refresh_token_repository
        self._logger = logger.bind(urn=self._urn, api_name=self._api_name)

    async def run(self, request_dto: PhoneVerifyOtpRequestDTO) -> BaseResponseDTO:
        if self._redis is None:
            raise ServiceUnavailableError(
                responseMessage="OTP verification is temporarily unavailable.",
                responseKey="error_service_unavailable",
            )
        otp_service = PhoneOtpUtility(
            redis_client=self._redis,
            urn=self._urn,
            user_urn=self._user_urn,
            api_name=self._api_name,
        )
        return await verify_otp_and_issue_tokens(
            phone=request_dto.phone,
            otp=request_dto.otp,
            purpose=request_dto.purpose,
            otp_service=otp_service,
            user_repository=self._user_repository,
            jwt_utility=self._jwt_utility,
            refresh_token_repository=self._refresh_token_repository,
            session=self._session,
            urn=self._urn,
        )


__all__ = ["PhoneVerifyOtpService"]
