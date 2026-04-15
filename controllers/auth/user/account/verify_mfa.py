"""POST /user/auth/verify-mfa – Verify MFA code and return full JWT. Public (uses mfa_challenge_token)."""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from constants.api_lk import APILK
from controllers.apis.v1.abstraction import IV1APIController
from dependencies.db import DBDependency
from dependencies.services.user.account.verify_mfa import VerifyMFAServiceDependency
from dependencies.services.user.token_issuance import (
    TokenIssuanceServiceDependency,
)
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dependencies.utilities.jwt import JWTUtilityDependency
from dtos.requests.user.account.verify_mfa import VerifyMFARequestDTO
from repositories.user.refresh_token_repository import RefreshTokenRepository
from utilities.jwt import JWTUtility


class VerifyMFAController(IV1APIController):
    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name=APILK.AUTH_VERIFY_MFA, *args, **kwargs)

    async def post(
        self,
        request: Request,
        body: VerifyMFARequestDTO,
        session: Session = Depends(DBDependency.derive),
        service_factory: Callable = Depends(VerifyMFAServiceDependency.derive),
        token_issuance_service_factory: Callable = Depends(
            TokenIssuanceServiceDependency.derive
        ),
        dictionary_utility: Callable = Depends(DictionaryUtilityDependency.derive),
        jwt_utility: JWTUtility = Depends(JWTUtilityDependency.derive),
    ) -> JSONResponse:
        """Exchange MFA challenge token + TOTP/backup code for full JWT."""
        self.bind_request_context(
            request,
            dictionary_utility_factory=dictionary_utility,
            jwt_utility_factory=jwt_utility,
        )

        http_status = HTTPStatus.OK
        try:
            refresh_token_repo = RefreshTokenRepository(session=session)
            token_issuance_service = token_issuance_service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                jwt_utility=self.jwt_utility,
                refresh_token_repository=refresh_token_repo,
            )
            service = service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
                token_issuance_service=token_issuance_service,
            )
            response_dto = await service.run(request_dto=body)
        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="auth.verify_mfa",
                session=session,
                force_http_ok=False,
                fallback_message="MFA verification failed.",
            )

        return self.build_json_response(response_dto, status_code=http_status)


__all__ = ["VerifyMFAController"]
