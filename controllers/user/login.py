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

Response:
    {
        "transactionUrn": "urn:request:abc123",
        "status": "SUCCESS",
        "responseMessage": "Login successful",
        "responseKey": "success_login",
        "data": {
            "token": "eyJhbG...",
            "user": {...}
        }
    }
"""

from collections.abc import Callable
from http import HTTPStatus

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from constants.api_lk import APILK
from constants.api_status import APIStatus
from controllers.user.abstraction import IUserController
from dependencies.db import DBDependency
from dependencies.repositiories.user import UserRepositoryDependency
from dependencies.services.user.login import UserLoginServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dependencies.utilities.jwt import JWTUtilityDependency
from dtos.requests.user.login import UserLoginRequestDTO
from dtos.responses.base import BaseResponseDTO
from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from errors.unexpected_response_error import UnexpectedResponseError
from repositories.user import UserRepository
from utilities.dictionary import DictionaryUtility
from utilities.jwt import JWTUtility


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

    def __init__(self, urn: str = None) -> None:
        """
        Initialize the login controller.

        Args:
            urn (str, optional): Unique Request Number. Defaults to None.
        """
        super().__init__(urn)
        self._urn = urn
        self._user_urn = None
        self._api_name = APILK.LOGIN
        self._user_id = None
        self._logger = self.logger
        self._dictionary_utility = None
        self._jwt_utility = None

    @property
    def urn(self) -> str:
        """str: Get the Unique Request Number."""
        return self._urn

    @urn.setter
    def urn(self, value: str) -> None:
        """Set the Unique Request Number."""
        self._urn = value

    @property
    def user_urn(self) -> str:
        """str: Get the user's unique resource name."""
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value: str) -> None:
        """Set the user's unique resource name."""
        self._user_urn = value

    @property
    def api_name(self) -> str:
        """str: Get the API endpoint name."""
        return self._api_name

    @api_name.setter
    def api_name(self, value: str) -> None:
        """Set the API endpoint name."""
        self._api_name = value

    @property
    def user_id(self) -> int:
        """int: Get the user's database identifier."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: int) -> None:
        """Set the user's database identifier."""
        self._user_id = value

    @property
    def logger(self):
        """loguru.Logger: Get the structured logger instance."""
        return self._logger

    @logger.setter
    def logger(self, value) -> None:
        """Set the structured logger instance."""
        self._logger = value

    @property
    def dictionary_utility(self) -> DictionaryUtility:
        """DictionaryUtility: Get the dictionary utility for response formatting."""
        return self._dictionary_utility

    @dictionary_utility.setter
    def dictionary_utility(self, value: DictionaryUtility) -> None:
        """Set the dictionary utility."""
        self._dictionary_utility = value

    @property
    def jwt_utility(self) -> JWTUtility:
        """JWTUtility: Get the JWT utility for token operations."""
        return self._jwt_utility

    @jwt_utility.setter
    def jwt_utility(self, value: JWTUtility) -> None:
        """Set the JWT utility."""
        self._jwt_utility = value

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
        try:
            self.logger.debug("Fetching request URN")
            self.urn = request.state.urn
            self.user_id = getattr(request.state, "user_id", None)
            self.user_urn = getattr(request.state, "user_urn", None)
            self.logger = self.logger.bind(
                urn=self.urn, user_urn=self.user_urn, api_name=self.api_name
            )
            self.dictionary_utility: DictionaryUtility = (
                dictionary_utility(
                    urn=self.urn,
                    user_urn=self.user_urn,
                    api_name=self.api_name,
                    user_id=self.user_id,
                )
            )
            self.jwt_utility: JWTUtility = jwt_utility(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
            )
            self.user_repository: UserRepository = user_repository(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
            )

            self.logger.debug("Validating request")
            await self.validate_request(
                urn=self.urn,
                user_urn=self.user_urn,
                request_payload=request_payload.model_dump(),
                request_headers=dict(request.headers.mutablecopy()),
                api_name=self.api_name,
                user_id=self.user_id,
            )
            self.logger.debug("Verified request")

            self.logger.debug("Running login user service")
            response_dto: BaseResponseDTO = await user_login_service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                jwt_utility=self.jwt_utility,
                user_repository=self.user_repository,
            ).run(request_dto=request_payload)

            self.logger.debug("Preparing response metadata")
            httpStatusCode = HTTPStatus.OK
            self.logger.debug("Prepared response metadata")

        except (BadInputError, UnexpectedResponseError, NotFoundError) as err:
            self.logger.error(
                f"{err.__class__} error occured while logging in user: {err}"
            )
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.FAILED,
                responseMessage=err.responseMessage,
                responseKey=err.responseKey,
                data={},
            )
            httpStatusCode = err.httpStatusCode
            self.logger.debug("Prepared response metadata")

        except Exception as err:
            self.logger.error(
                f"{err.__class__} error occured while logging in user: {err}"
            )

            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.FAILED,
                responseMessage="Failed to login users.",
                responseKey="error_internal_server_error",
                data={},
            )
            httpStatusCode = HTTPStatus.INTERNAL_SERVER_ERROR
            self.logger.debug("Prepared response metadata")

        return JSONResponse(
            content=self.dictionary_utility.convert_dict_keys_to_camel_case(
                response_dto.model_dump()
            ),
            status_code=httpStatusCode,
        )
