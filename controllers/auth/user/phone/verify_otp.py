"""POST /user/phone/verify-otp – Verify OTP and log in or complete registration."""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any, Optional

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from redis import Redis
from sqlalchemy.orm import Session

from constants.api_lk import APILK
from controllers.apis.v1.abstraction import IV1APIController
from dependencies.cache import CacheDependency
from dependencies.db import DBDependency
from dependencies.repositiories.user import UserRepositoryDependency
from dependencies.services.user.phone.verify_otp import PhoneVerifyOtpServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dependencies.utilities.jwt import JWTUtilityDependency
from dtos.requests.user.phone_verify_otp import PhoneVerifyOtpRequestDTO
from repositories.user.refresh_token_repository import RefreshTokenRepository
from repositories.user.user_repository import UserRepository


class PhoneVerifyOtpController(IV1APIController):
    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name=APILK.PHONE_VERIFY_OTP, *args, **kwargs)

    async def post(
        self,
        request: Request,
        body: PhoneVerifyOtpRequestDTO,
        session: Session = Depends(DBDependency.derive),
        redis_client: Optional[Redis] = Depends(CacheDependency.derive),
        user_repository: UserRepository = Depends(UserRepositoryDependency.derive),
        service_factory: Callable = Depends(PhoneVerifyOtpServiceDependency.derive),
        jwt_utility: Callable = Depends(JWTUtilityDependency.derive),
        dictionary_utility: Callable = Depends(DictionaryUtilityDependency.derive),
    ) -> JSONResponse:
        """Verify OTP. Purpose must match send-otp. Issues tokens on success."""
        self.bind_request_context(
            request,
            dictionary_utility_factory=dictionary_utility,
            jwt_utility_factory=jwt_utility,
        )

        http_status = HTTPStatus.OK
        try:
            repo = user_repository(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
            )
            refresh_repo = RefreshTokenRepository(session) if session else None
            service = service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
                redis_client=redis_client,
                user_repository=repo,
                jwt_utility=self.jwt_utility,
                refresh_token_repository=refresh_repo,
            )
            response_dto = await service.run(request_dto=body)
        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="phone.verify_otp",
                session=session,
                force_http_ok=False,
                fallback_message="Verification failed.",
            )

        return self.build_json_response(response_dto, status_code=http_status)


__all__ = ["PhoneVerifyOtpController"]
