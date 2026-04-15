"""POST /user/reset-password – Confirm a password reset with token + new password.

Public (unauthenticated) endpoint. Validates the JWT reset token, hashes the
new password, and updates the user record.
"""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from controllers.auth.user.abstraction import IUserController
from dependencies.db import DBDependency
from dependencies.services.user.reset_password import ResetPasswordServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dtos.requests.user.reset_password import ResetPasswordRequestDTO


class ResetPasswordController(IUserController):
    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name="USER_RESET_PASSWORD", *args, **kwargs)

    async def post(
        self,
        request: Request,
        body: ResetPasswordRequestDTO,
        session: Session = Depends(DBDependency.derive),
        service_factory: Callable = Depends(ResetPasswordServiceDependency.derive),
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
            response_dto = await service.run(
                token=body.token, new_password=body.new_password,
            )
        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="reset_password",
                session=session,
                force_http_ok=False,
                fallback_message="Failed to reset password.",
            )

        return self.build_json_response(response_dto, status_code=http_status)


__all__ = ["ResetPasswordController"]
