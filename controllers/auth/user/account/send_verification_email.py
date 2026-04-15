"""POST /user/auth/send-verification-email – Send verification link to current user's email."""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from constants.api_lk import APILK
from controllers.apis.v1.abstraction import IV1APIController
from dependencies.db import DBDependency
from dependencies.services.user.account.send_verification_email import (
    SendVerificationEmailServiceDependency,
)
from dependencies.utilities.dictionary import DictionaryUtilityDependency


class SendVerificationEmailController(IV1APIController):
    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name=APILK.AUTH_SEND_VERIFICATION_EMAIL, *args, **kwargs)

    async def post(
        self,
        request: Request,
        session: Session = Depends(DBDependency.derive),
        service_factory: Callable = Depends(
            SendVerificationEmailServiceDependency.derive,
        ),
        dictionary_utility: Callable = Depends(DictionaryUtilityDependency.derive),
    ) -> JSONResponse:
        """Send account verification link to the authenticated user's email."""
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
            )
            response_dto = await service.run()
        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="auth.send_verification_email",
                session=session,
                force_http_ok=False,
                fallback_message="Failed to send verification email.",
            )

        return self.build_json_response(response_dto, status_code=http_status)


__all__ = ["SendVerificationEmailController"]
