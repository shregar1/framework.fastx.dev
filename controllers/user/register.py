"""
User Registration Controller Module.

This module handles new user account creation. It validates user input,
checks for duplicate accounts, and creates new user records.

Endpoint:
    POST /user/register

Request Body:
    {
        "email": "user@example.com",
        "password": "SecureP@ss123",
        "name": "John Doe"
    }

Response:
    {
        "transactionUrn": "urn:request:abc123",
        "status": "SUCCESS",
        "responseMessage": "Registration successful",
        "responseKey": "success_registration",
        "data": {
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
from dependencies.services.user.register import (
    UserRegistrationServiceDependency,
)
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dtos.requests.user.registration import UserRegistrationRequestDTO
from dtos.responses.base import BaseResponseDTO
from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from errors.unexpected_response_error import UnexpectedResponseError
from repositories.user import UserRepository
from utilities.dictionary import DictionaryUtility


class UserRegistrationController(IUserController):
    """
    Controller for new user registration.

    Handles POST requests to /user/register endpoint. Validates input,
    checks for existing accounts, and creates new user records.

    Attributes:
        urn (str): Unique Request Number for this request.
        user_urn (str): User's unique resource name (set after creation).
        api_name (str): Always set to APILK.REGISTRATION.
        user_id (str): User's database ID (set after creation).
        dictionary_utility (DictionaryUtility): For response formatting.

    Example:
        >>> controller = UserRegistrationController()
        >>> response = await controller.post(request, registration_data)
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ) -> None:
        """
        Initialize the registration controller.

        Args:
            urn (str, optional): Unique Request Number. Defaults to None.
            user_urn (str, optional): User's URN. Defaults to None.
            api_name (str, optional): API name. Defaults to None.
            user_id (str, optional): User's database ID. Defaults to None.
        """
        super().__init__(urn)
        self._urn: str = urn
        self._user_urn: str = user_urn
        self._api_name: str = APILK.REGISTRATION
        self._user_id: str = user_id
        self._logger = self.logger
        self._dictionary_utility: DictionaryUtility = None

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
    def user_id(self) -> str:
        """str: Get the user's database identifier."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
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
        """DictionaryUtility: Get the dictionary utility."""
        return self._dictionary_utility

    @dictionary_utility.setter
    def dictionary_utility(self, value: DictionaryUtility) -> None:
        """Set the dictionary utility."""
        self._dictionary_utility = value

    async def post(
        self,
        request: Request,
        request_payload: UserRegistrationRequestDTO,
        session: Session = Depends(DBDependency.derive),
        user_repository: UserRepository = Depends(
            UserRepositoryDependency.derive
        ),
        user_registration_service_factory: Callable = Depends(
            UserRegistrationServiceDependency.derive
        ),
        dictionary_utility: DictionaryUtility = Depends(
            DictionaryUtilityDependency.derive
        ),
    ) -> JSONResponse:
        """
        Handle POST request for user registration.

        Creates a new user account after validating input and checking
        for duplicate accounts. All errors are caught and returned as
        structured error responses.

        Args:
            request (Request): FastAPI request object with state.urn.
            request_payload (UserRegistrationRequestDTO): Registration data.
            session (Session): Database session from dependency injection.
            user_repository (UserRepository): User data access dependency.
            user_registration_service_factory (Callable): Factory for service.
            dictionary_utility (DictionaryUtility): Response formatting utility.

        Returns:
            JSONResponse: Contains:
                - transactionUrn: Request tracking ID
                - status: SUCCESS or FAILED
                - responseMessage: Human-readable message
                - responseKey: Machine-readable key
                - data: User info on success

        HTTP Status Codes:
            - 200 OK: Registration successful
            - 400 Bad Request: Invalid input or duplicate email
            - 500 Internal Server Error: Unexpected error
        """
        try:
            self.logger.debug("Fetching request URN")
            self.urn: str = request.state.urn
            self.user_id: str = getattr(request.state, "user_id", None)
            self.user_urn: str = getattr(request.state, "user_urn", None)
            self.logger = self.logger.bind(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
            )
            self.dictionary_utility: DictionaryUtility = (
                dictionary_utility(
                    urn=self.urn,
                    user_urn=self.user_urn,
                    api_name=self.api_name,
                    user_id=self.user_id,
                )
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

            self.logger.debug("Running registration user service")
            response_dto = await user_registration_service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                user_repository=self.user_repository,
            ).run(request_dto=request_payload)

            self.logger.debug("Preparing response metadata")
            httpStatusCode = HTTPStatus.OK
            self.logger.debug("Prepared response metadata")

        except (BadInputError, UnexpectedResponseError, NotFoundError) as err:
            self.logger.error(
                f"{err.__class__} error occured while registering user: {err}"
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
                f"{err.__class__} error occured while registering user: {err}"
            )

            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.FAILED,
                responseMessage="Failed to register users.",
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
