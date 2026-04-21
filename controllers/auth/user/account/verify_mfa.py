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
from dependencies.repositiories.user import UserRepositoryDependency
from dependencies.services.mfa import MFAUtilityDependency as MFAServiceDependency
from dependencies.services.user.account.verify_mfa import VerifyMFAServiceDependency
from dependencies.services.user.token_issuance import (
    TokenIssuanceServiceDependency,
)
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dependencies.utilities.jwt import JWTUtilityDependency
from dtos.requests.user.account.verify_mfa import VerifyMFARequestDTO
from dependencies.repositiories.refresh_token import RefreshTokenRepositoryDependency
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
        mfa_service_factory: Callable = Depends(MFAServiceDependency.derive),
        user_repository_factory: Callable = Depends(UserRepositoryDependency.derive),
        dictionary_utility: Callable = Depends(DictionaryUtilityDependency.derive),
        jwt_utility: JWTUtility = Depends(JWTUtilityDependency.derive),
        refresh_token_repository_factory: Callable = Depends(
            RefreshTokenRepositoryDependency.derive
        ),
    ) -> JSONResponse:
        """Exchange MFA challenge token + TOTP/backup code for full JWT."""
        self.bind_request_context(
            request,
            dictionary_utility_factory=dictionary_utility,
            jwt_utility_factory=jwt_utility,
        )

        http_status = HTTPStatus.OK
        try:
            refresh_token_repo = refresh_token_repository_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
            )
            token_issuance_service = token_issuance_service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                jwt_utility=self.jwt_utility,
                refresh_token_repository=refresh_token_repo,
            )
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
