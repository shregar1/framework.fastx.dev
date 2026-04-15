"""POST /user/mfa/disable – Disable MFA (requires current TOTP or backup code)."""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from constants.api_lk import APILK
from controllers.apis.v1.abstraction import IV1APIController
from dependencies.db import DBDependency
from dependencies.services.mfa import MFAServiceDependency
from dependencies.services.user.mfa.disable import MFADisableServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dtos.requests.user.mfa.disable import MFADisableRequestDTO


class MFADisableController(IV1APIController):
    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name=APILK.MFA_DISABLE, *args, **kwargs)

    async def post(
        self,
        request: Request,
        body: MFADisableRequestDTO,
        session: Session = Depends(DBDependency.derive),
        service_factory: Callable = Depends(MFADisableServiceDependency.derive),
        mfa_service_factory: Callable = Depends(MFAServiceDependency.derive),
        dictionary_utility: Callable = Depends(DictionaryUtilityDependency.derive),
    ) -> JSONResponse:
        """POST /user/mfa/disable – Disable MFA (requires current TOTP or backup code)."""
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
            service = service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
                mfa_service=mfa_service,
            )
            response_dto = await service.run(body.code)
            http_status = HTTPStatus.OK
        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="mfa.disable",
                session=session,
                force_http_ok=False,
                fallback_message="MFA disable failed.",
            )

        return self.build_json_response(response_dto, status_code=http_status)


__all__ = ["MFADisableController"]
