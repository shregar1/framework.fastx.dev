"""
User Logout Controller Module.

This module handles user session termination. It invalidates the
user's current session/token and clears any associated state.

Endpoint:
    POST /user/logout

Request Headers:
    Authorization: Bearer <token>

Response:
    {
        "transactionUrn": "urn:request:abc123",
        "status": "SUCCESS",
        "responseMessage": "Logout successful",
        "responseKey": "success_logout",
        "data": {}
    }
"""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from constants.api_lk import APILK
from constants.http_header import HttpHeader
from constants.api_status import APIStatus
from controllers.auth.user.abstraction import IUserController
from dependencies.db import DBDependency
from dependencies.repositiories.user import UserRepositoryDependency
from dependencies.services.user.logout import UserLogoutServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dependencies.utilities.jwt import JWTUtilityDependency
from dtos.requests.user.logout import UserLogoutRequestDTO
from dtos.responses.base import BaseResponseDTO
from repositories.user.refresh_token_repository import RefreshTokenRepository
from repositories.user.user_repository import UserRepository
from structured_log import log_event
from utilities.dictionary import DictionaryUtility
from utilities.jwt import JWTUtility

class UserLogoutController(IUserController):
    """
    Controller for user logout/session termination.

    Handles POST requests to /user/logout endpoint. Invalidates the
    user's current authentication token and clears session state.

    Attributes:
        urn (str): Unique Request Number for this request.
        user_urn (str): User's unique resource name.
        api_name (str): Always set to APILK.LOGOUT.
        user_id (str): User's database ID.
        dictionary_utility (DictionaryUtility): For response formatting.

    Example:
        >>> controller = UserLogoutController()
        >>> response = await controller.post(request, payload)
    """

    def __init__(
        self,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: int | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the logout controller.

        Args:
            urn (str, optional): Unique Request Number. Defaults to None.
            user_urn (str, optional): User's URN. Defaults to None.
            api_name (str, optional): API name. Defaults to None.
            user_id (str, optional): User's database ID. Defaults to None.
            *args: Additional positional arguments forwarded to parent.
            **kwargs: Additional keyword arguments forwarded to parent.
        """

        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name or APILK.LOGOUT,
            user_id=user_id,
            *args,
            **kwargs,
        )

    async def post(
        self,
        request: Request,
        request_payload: UserLogoutRequestDTO,
        session: Session = Depends(DBDependency.derive),
        user_repository: UserRepository = Depends(
            UserRepositoryDependency.derive
        ),
        user_logout_service_factory: Callable = Depends(
            UserLogoutServiceDependency.derive
        ),
        dictionary_utility: DictionaryUtility = Depends(
            DictionaryUtilityDependency.derive
        ),
        jwt_utility: JWTUtility = Depends(
            JWTUtilityDependency.derive
        )
    ) -> JSONResponse:
        """
        Handle POST request for user logout.

        Terminates the user's session and invalidates their token.
        All errors are caught and returned as structured error responses.

        Args:
            request (Request): FastAPI request object with auth state.
            request_payload (UserLogoutRequestDTO): Logout request data.
            session (Session): Database session from dependency injection.
            user_repository (UserRepository): User data access dependency.
            user_logout_service_factory (Callable): Factory for logout service.
            dictionary_utility (DictionaryUtility): Response formatting utility.
            jwt_utility (JWTUtility): JWT token utility.

        Returns:
            JSONResponse: Contains:
                - transactionUrn: Request tracking ID
                - status: SUCCESS or FAILED
                - responseMessage: Human-readable message
                - responseKey: Machine-readable key
                - data: Empty on logout

        HTTP Status Codes:
            - 200 OK: Logout successful
            - 400 Bad Request: Invalid input
            - 404 Not Found: User not found
            - 500 Internal Server Error: Unexpected error
        """

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

            self.logger.debug("Validating request")
            self.request_payload = request_payload.model_dump()
            self.request_payload.update({"user_id": request.state.user_id})

            await self.validate_request(
                urn=self.urn or "",
                user_urn=self.user_urn or "",
                request_payload=self.request_payload,
                request_headers=dict(request.headers.mutablecopy()),
                api_name=self.api_name or "",
                user_id=self.user_id,
            )
            self.logger.debug("Verified request")

            auth_header = request.headers.get("authorization", "")
            auth_token = None
            if auth_header.lower().startswith("bearer "):
                auth_token = auth_header[
                    HttpHeader.AUTHORIZATION_BEARER_PREFIX_LENGTH:
                ].strip()

            refresh_token_repo = RefreshTokenRepository(session=session)

            self.logger.debug("Running logout service")
            response_dto: BaseResponseDTO = await user_logout_service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                jwt_utility=self.jwt_utility,
                user_repository=self.user_repository,
                refresh_token_repository=refresh_token_repo,
                auth_token=auth_token,
            ).run()

            self.logger.debug("Preparing response metadata")
            log_event(
                "logout.success",
                user_id=self.user_id,
                urn=self.urn,
                user_urn=self.user_urn,
            )
            httpStatusCode = HTTPStatus.OK
            self.logger.debug("Prepared response metadata")

        except Exception as err:
            response_dto, httpStatusCode = self.handle_exception(
                err,
                request,
                event_name="logout",
                session=session,
                force_http_ok=False,
                fallback_message="Failed to logout users.",
            )

        return self.build_json_response(response_dto, status_code=httpStatusCode)
