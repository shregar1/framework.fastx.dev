"""POST /user/phone/send-otp – Send OTP to phone for login or register."""

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
from dependencies.services.user.phone.send_otp import PhoneSendOtpServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dtos.requests.user.phone_send_otp import PhoneSendOtpRequestDTO


class PhoneSendOtpController(IV1APIController):
    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name=APILK.PHONE_SEND_OTP, *args, **kwargs)

    async def post(
        self,
        request: Request,
        body: PhoneSendOtpRequestDTO,
        session: Session = Depends(DBDependency.derive),
        redis_client: Optional[Redis] = Depends(CacheDependency.derive),
        service_factory: Callable = Depends(PhoneSendOtpServiceDependency.derive),
        dictionary_utility: Callable = Depends(DictionaryUtilityDependency.derive),
    ) -> JSONResponse:
        """Send a 6-digit OTP to the given phone. Always returns the same
        response message to avoid phone-number enumeration."""
        self.bind_request_context(
            request,
            dictionary_utility_factory=dictionary_utility,
        )

        http_status = HTTPStatus.OK
        try:
            service = service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
                redis_client=redis_client,
            )
            response_dto = await service.run(body.phone, body.purpose)
        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="phone.send_otp",
                session=session,
                force_http_ok=True,
                fallback_message="If this number is valid, you will receive an OTP shortly.",
                fallback_key="success_otp_sent",
            )

        return self.build_json_response(response_dto, status_code=http_status)


__all__ = ["PhoneSendOtpController"]
