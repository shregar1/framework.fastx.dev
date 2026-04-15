"""GET /user/mfa/setup/qr-code – Return QR code image for authenticator app setup."""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import Depends, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from constants.api_lk import APILK
from controllers.apis.v1.abstraction import IV1APIController
from dependencies.db import DBDependency
from dependencies.services.mfa import MFAServiceDependency
from dependencies.services.user.mfa.qr_code import MFAQrCodeServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency


class MFASetupQrCodeController(IV1APIController):
    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name=APILK.MFA_SETUP_QR_CODE, *args, **kwargs)

    async def get(
        self,
        request: Request,
        session: Session = Depends(DBDependency.derive),
        service_factory: Callable = Depends(MFAQrCodeServiceDependency.derive),
        mfa_service_factory: Callable = Depends(MFAServiceDependency.derive),
        dictionary_utility: Callable = Depends(DictionaryUtilityDependency.derive),
    ) -> Response:
        """GET /user/mfa/setup/qr-code – Return a PNG QR code for pending MFA setup."""
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
            png_bytes, mime_type = await service.run()
            return Response(content=png_bytes, media_type=mime_type)
        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="mfa.setup.qr_code",
                session=session,
                force_http_ok=False,
                fallback_message="Failed to render MFA QR code.",
            )

        return self.build_json_response(response_dto, status_code=http_status)


__all__ = ["MFASetupQrCodeController"]
