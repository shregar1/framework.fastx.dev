"""
User Refresh Token Controller Module.

Handles exchange of a refresh token for new access and refresh tokens.
No authentication required; client sends refresh token in request body.

Endpoint:
    POST /user/refresh

Request Body:
    {
        "reference_number": "550e8400-e29b-41d4-a716-446655440000",
        "refreshToken": "eyJhbG..."
    }

Response:
    {
        "transactionUrn": "urn:request:abc123",
        "status": "SUCCESS",
        "responseMessage": "Tokens refreshed successfully.",
        "responseKey": "success_refresh_token",
        "data": {
            "token": "eyJhbG...",
            "refreshToken": "eyJhbG...",
            "user_urn": "urn:user:..."
        }
    }
"""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from constants.api_lk import APILK
from constants.api_status import APIStatus
from controllers.auth.user.abstraction import IUserController
from dependencies.db import DBDependency
from dependencies.repositiories.user import UserRepositoryDependency
from dependencies.services.user.refresh_token import UserRefreshTokenServiceDependency
from dependencies.services.user.token_issuance import (
    TokenIssuanceServiceDependency,
)
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dependencies.utilities.jwt import JWTUtilityDependency
from dtos.requests.user.refresh import RefreshTokenRequestDTO
from dtos.responses.base import BaseResponseDTO
from repositories.user.refresh_token_repository import RefreshTokenRepository
from repositories.user.user_repository import UserRepository
from utilities.audit import log_audit
from utilities.dictionary import DictionaryUtility
from utilities.jwt import JWTUtility
from utilities.request_utils import get_client_ip

class UserRefreshTokenController(IUserController):
    """
    Controller for refresh token exchange.

    Handles POST /user/refresh. Validates refresh token and returns
    new access and refresh tokens. Unauthenticated route.
    """

    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(urn=urn, api_name=APILK.REFRESH, *args, **kwargs)

    async def post(
        self,
        request: Request,
        request_payload: RefreshTokenRequestDTO,
        session: Session = Depends(DBDependency.derive),
        user_repository: UserRepository = Depends(UserRepositoryDependency.derive),
        refresh_service_factory: Callable = Depends(
            UserRefreshTokenServiceDependency.derive
        ),
        token_issuance_service_factory: Callable = Depends(
            TokenIssuanceServiceDependency.derive
        ),
        dictionary_utility: DictionaryUtility = Depends(
            DictionaryUtilityDependency.derive
        ),
        jwt_utility: JWTUtility = Depends(JWTUtilityDependency.derive),
    ) -> JSONResponse:
        """Handle POST /user/refresh: exchange refresh token for new tokens."""

        try:
            self.bind_request_context(
                request,
                dictionary_utility_factory=dictionary_utility,
                jwt_utility_factory=jwt_utility,
            )
            self.user_repository = user_repository(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
            )
            refresh_token_repo = RefreshTokenRepository(session=session)

            await self.validate_request(
                urn=self.urn or "",
                user_urn=self.user_urn or "",
                request_payload=request_payload.model_dump(),
                request_headers=dict(request.headers.mutablecopy()),
                api_name=self.api_name or "",
                user_id=self.user_id,
            )

            token_issuance_service = token_issuance_service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                jwt_utility=self.jwt_utility,
                refresh_token_repository=refresh_token_repo,
            )
            response_dto: BaseResponseDTO = await refresh_service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                jwt_utility=self.jwt_utility,
                user_repository=self.user_repository,
                refresh_token_repository=refresh_token_repo,
                token_issuance_service=token_issuance_service,
            ).run(request_dto=request_payload)

            http_status = HTTPStatus.OK
            data_dict = response_dto.data if isinstance(response_dto.data, dict) else {}
            if response_dto.status == APIStatus.SUCCESS and data_dict:
                try:
                    uid = data_dict.get("user_id")
                    log_audit(
                        session,
                        "token.refresh",
                        "user",
                        actor_id=uid,
                        actor_urn=data_dict.get("user_urn"),
                        resource_id=str(uid) if uid else None,
                        ip=get_client_ip(request),
                    )
                except Exception:
                    pass

        except Exception as err:
            response_dto, http_status = self.handle_exception(
                err,
                request,
                event_name="token.refresh",
                session=session,
                force_http_ok=False,
                fallback_message="Failed to refresh tokens.",
            )

        return self.build_json_response(response_dto, status_code=http_status)
