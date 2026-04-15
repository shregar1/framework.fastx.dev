"""GET /user/mfa/status – Return whether MFA is enabled for current user."""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from constants.api_lk import APILK
from controllers.apis.v1.abstraction import IV1APIController
from dependencies.db import DBDependency
from dependencies.services.user.mfa.status import MFAStatusServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency


class MFAStatusController(IV1APIController):
    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name=APILK.MFA_STATUS, *args, **kwargs)

    async def get(
        self,
        request: Request,
        session: Session = Depends(DBDependency.derive),
        service_factory: Callable = Depends(MFAStatusServiceDependency.derive),
        dictionary_utility: Callable = Depends(DictionaryUtilityDependency.derive),
    ) -> JSONResponse:
        """GET /user/mfa/status – Return whether MFA is enabled for the current user."""
        self.bind_request_context(
            request,
            dictionary_utility_factory=dictionary_utility,
        )

        try:
            service = service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
            )
            response_dto = await service.run()
            http_status = HTTPStatus.OK
        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="mfa.status",
                session=session,
                force_http_ok=False,
                fallback_message="Failed to fetch MFA status.",
            )

        return self.build_json_response(response_dto, status_code=http_status)


__all__ = ["MFAStatusController"]
