"""POST /user/forgot-password – Request a password-reset email.

Public (unauthenticated) endpoint. Always returns the same success response
to prevent email enumeration.
"""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from controllers.auth.user.abstraction import IUserController
from dependencies.db import DBDependency
from dependencies.services.user.forgot_password import ForgotPasswordServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dtos.requests.user.forgot_password import ForgotPasswordRequestDTO


class ForgotPasswordController(IUserController):
    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name="USER_FORGOT_PASSWORD", *args, **kwargs)

    async def post(
        self,
        request: Request,
        body: ForgotPasswordRequestDTO,
        session: Session = Depends(DBDependency.derive),
        service_factory: Callable = Depends(ForgotPasswordServiceDependency.derive),
        dictionary_utility: Callable = Depends(DictionaryUtilityDependency.derive),
    ) -> JSONResponse:
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
            response_dto = await service.run(email=body.email)
        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="forgot_password",
                session=session,
                force_http_ok=True,
                fallback_message="If that email is registered, you will receive a reset link.",
                fallback_key="success_password_reset_request",
            )

        return self.build_json_response(response_dto, status_code=http_status)


__all__ = ["ForgotPasswordController"]
