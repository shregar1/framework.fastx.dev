"""
User Login Controller Module.

This module handles user authentication via login credentials.
It validates user input, authenticates against the database,
and returns a JWT token on successful authentication.

Endpoint:
    POST /user/login

Request Body:
    {
        "email": "user@example.com",
        "password": "SecureP@ss123"
    }

Response (success, no MFA):
    {
        "transactionUrn": "urn:request:abc123",
        "status": "SUCCESS",
        "responseMessage": "Successfully logged in the user.",
        "responseKey": "success_user_login",
        "data": {
            "status": true,
            "token": "eyJhbG...",
            "refreshToken": "eyJhbG...",
            "userUrn": "urn:user:...",
            "userId": 1,
            "publicKeyPem": "-----BEGIN PUBLIC KEY-----\\n..."
        }
    }

Response (MFA required):
    data.requiresMFA true, data.mfaChallengeToken, data.userUrn, data.publicKeyPem; no token/refreshToken.
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
from dependencies.services.user.login import UserLoginServiceDependency
from dependencies.services.user.token_issuance import (
    TokenIssuanceServiceDependency,
)
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dependencies.utilities.jwt import JWTUtilityDependency
from dtos.requests.user.login import UserLoginRequestDTO
from dtos.responses.base import BaseResponseDTO
from repositories.user.refresh_token_repository import RefreshTokenRepository
from repositories.user.user_repository import UserRepository
from structured_log import log_event
from utilities.audit import log_audit
from utilities.dictionary import DictionaryUtility
from utilities.jwt import JWTUtility
from utilities.request_utils import get_client_ip

class UserLoginController(IUserController):
    """
    Controller for user login/authentication.

    Handles POST requests to /user/login endpoint. Validates credentials,
    authenticates the user, and returns a JWT token for subsequent requests.

    Attributes:
        urn (str): Unique Request Number for this request.
        user_urn (str): User's unique resource name (set after auth).
        api_name (str): Always set to APILK.LOGIN.
        user_id (int): User's database ID (set after auth).
        dictionary_utility (DictionaryUtility): For response formatting.
        jwt_utility (JWTUtility): For token generation.

    Example:
        >>> controller = UserLoginController()
        >>> response = await controller.post(request, credentials)
    """

    def __init__(self, urn: str | None = None, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the login controller.

        Args:
            urn (str, optional): Unique Request Number. Defaults to None.
            *args: Additional positional arguments forwarded to parent.
            **kwargs: Additional keyword arguments forwarded to parent.
        """

        super().__init__(urn=urn, api_name=APILK.LOGIN, *args, **kwargs)
        self._jwt_utility = None

    async def post(
        self,
        request: Request,
        request_payload: UserLoginRequestDTO,
        session: Session = Depends(DBDependency.derive),
        user_repository: UserRepository = Depends(
            UserRepositoryDependency.derive
        ),
        user_login_service_factory: Callable = Depends(
            UserLoginServiceDependency.derive
        ),
        token_issuance_service_factory: Callable = Depends(
            TokenIssuanceServiceDependency.derive
        ),
        dictionary_utility: DictionaryUtility = Depends(
            DictionaryUtilityDependency.derive
        ),
        jwt_utility: JWTUtility = Depends(
            JWTUtilityDependency.derive
        )
    ) -> JSONResponse:
        """
        Handle POST request for user login.

        Authenticates user credentials and returns a JWT token on success.
        All errors are caught and returned as structured error responses.

        Args:
            request (Request): FastAPI request object with state.urn.
            request_payload (UserLoginRequestDTO): Login credentials.
            session (Session): Database session from dependency injection.
            user_repository (UserRepository): User data access dependency.
            user_login_service_factory (Callable): Factory for login service.
            dictionary_utility (DictionaryUtility): Response formatting utility.
            jwt_utility (JWTUtility): JWT token utility.

        Returns:
            JSONResponse: Contains:
                - transactionUrn: Request tracking ID
                - status: SUCCESS or FAILED
                - responseMessage: Human-readable message
                - responseKey: Machine-readable key for i18n
                - data: Token and user info on success

        Raises:
            No exceptions are raised; all errors return JSONResponse with
            appropriate HTTP status codes.

        HTTP Status Codes:
            - 200 OK: Login successful
            - 400 Bad Request: Invalid input
            - 404 Not Found: User not found
            - 500 Internal Server Error: Unexpected error
        """

        # Ensure we always have a safe fallback response even if setup fails early.
        response_dto = BaseResponseDTO(
            transactionUrn=getattr(request.state, "urn", "") or "",
            status=APIStatus.FAILED,
            responseMessage="Failed to login users.",
            responseKey="error_internal_server_error",
            data={},
        )
        httpStatusCode = HTTPStatus.OK

        def _txn_urn() -> str:
            """Best-effort URN for envelopes when setup failed before self.urn is set."""

            return (
                getattr(request.state, "urn", None)
                or self.urn
                or ""
            )

        try:
            self.logger.debug("Fetching request URN")
            self.bind_request_context(
                request,
                dictionary_utility_factory=dictionary_utility,
                jwt_utility_factory=jwt_utility,
            )
            self.user_repository: UserRepository = user_repository(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
            )
            refresh_token_repo = RefreshTokenRepository(session=session)

            self.logger.debug("Validating request")
            await self.validate_request(
                urn=self.urn or "",
                user_urn=self.user_urn or "",
                request_payload=request_payload.model_dump(),
                request_headers=dict(request.headers.mutablecopy()),
                api_name=self.api_name or "",
                user_id=self.user_id,
            )
            self.logger.debug("Verified request")

            self.logger.debug("Running login user service")
            token_issuance_service = token_issuance_service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                jwt_utility=self.jwt_utility,
                refresh_token_repository=refresh_token_repo,
            )
            response_dto: BaseResponseDTO = await user_login_service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                jwt_utility=self.jwt_utility,
                user_repository=self.user_repository,
                refresh_token_repository=refresh_token_repo,
                token_issuance_service=token_issuance_service,
            ).run(request_dto=request_payload)

            self.logger.debug("Preparing response metadata")
            httpStatusCode = HTTPStatus.OK
            data_dict = response_dto.data if isinstance(response_dto.data, dict) else {}
            if response_dto.status == APIStatus.SUCCESS and data_dict:
                try:
                    uid = data_dict.get("user_id")
                    log_audit(
                        session,
                        "login.success",
                        "user",
                        actor_id=uid,
                        actor_urn=data_dict.get("user_urn"),
                        resource_id=str(uid),
                        ip=get_client_ip(request),
                    )
                    log_event(
                        "login.success",
                        user_id=uid,
                        urn=self.urn,
                        user_urn=data_dict.get("user_urn"),
                    )
                except Exception:
                    pass
            self.logger.debug("Prepared response metadata")

        except Exception as err:
            response_dto, httpStatusCode = self.handle_exception(
                err,
                request,
                event_name="login",
                session=session,
                fallback_message="Failed to login users.",
            )

        return self.build_json_response(response_dto, status_code=httpStatusCode)
