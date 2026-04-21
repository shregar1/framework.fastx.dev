"""POST /user/mfa/verify – Verify TOTP code and enable MFA (returns backup codes once)."""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from constants.api_lk import APILK
from controllers.apis.v1.abstraction import IV1APIController
from dependencies.db import DBDependency
from dependencies.repositiories.user import UserRepositoryDependency
from dependencies.services.mfa import MFAUtilityDependency as MFAServiceDependency
from dependencies.services.user.mfa.verify import MFAVerifyServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dtos.requests.user.mfa.verify import MFAVerifyRequestDTO


class MFAVerifyController(IV1APIController):
    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name=APILK.MFA_VERIFY, *args, **kwargs)

    async def post(
        self,
        request: Request,
        body: MFAVerifyRequestDTO,
        session: Session = Depends(DBDependency.derive),
        service_factory: Callable = Depends(MFAVerifyServiceDependency.derive),
        mfa_service_factory: Callable = Depends(MFAServiceDependency.derive),
        user_repository_factory: Callable = Depends(UserRepositoryDependency.derive),
        dictionary_utility: Callable = Depends(DictionaryUtilityDependency.derive),
    ) -> JSONResponse:
        """POST /user/mfa/verify – Verify TOTP code and enable MFA."""
        self.bind_request_context(
            request,
            dictionary_utility_factory=dictionary_utility,
        )

        try:
            mfa_service = mfa_service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
            )
            user_repository = user_repository_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
            )
            service = service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                user_repository=user_repository,
                mfa_service=mfa_service,
            )
            response_dto = await service.run(body.code)
            http_status = HTTPStatus.OK
        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="mfa.verify",
                session=session,
                force_http_ok=False,
                fallback_message="MFA verification failed.",
            )

        return self.build_json_response(response_dto, status_code=http_status)


__all__ = ["MFAVerifyController"]
