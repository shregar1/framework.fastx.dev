"""GET /user/auth/verify-email?token=... – Verify account via link sent to email."""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from constants.api_lk import APILK
from controllers.apis.v1.abstraction import IV1APIController
from dependencies.db import DBDependency
from dependencies.services.user.account.verify_email import VerifyEmailServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency


class VerifyEmailController(IV1APIController):
    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name=APILK.AUTH_VERIFY_EMAIL, *args, **kwargs)

    async def get(
        self,
        request: Request,
        token: str = Query(..., description="Verification token from the email link."),
        session: Session = Depends(DBDependency.derive),
        service_factory: Callable = Depends(VerifyEmailServiceDependency.derive),
        dictionary_utility: Callable = Depends(DictionaryUtilityDependency.derive),
    ) -> JSONResponse:
        """Verify email using the token from the verification link."""
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
            response_dto = await service.run(token=token)
        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="auth.verify_email",
                session=session,
                force_http_ok=False,
                fallback_message="Invalid or expired verification link.",
            )

        return self.build_json_response(response_dto, status_code=http_status)


__all__ = ["VerifyEmailController"]
