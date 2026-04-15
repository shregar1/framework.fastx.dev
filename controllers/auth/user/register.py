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
from typing import Any
from uuid import uuid4

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from constants.api_lk import APILK
from constants.api_status import APIStatus
from constants.events import WebhookEventType
from controllers.auth.user.abstraction import IUserController
from dependencies.db import DBDependency
from utilities.notifications.lifecycle import send_welcome_email
from utilities.webhook_dispatcher import dispatch_webhook_event
from dependencies.repositiories.user import UserRepositoryDependency
from dependencies.services.user.register import (
    UserRegistrationServiceDependency,
)
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dtos.requests.user.registration import UserRegistrationRequestDTO
from dtos.responses.base import BaseResponseDTO
from repositories.user.user_repository import UserRepository
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
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: int | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the registration controller.

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
            api_name=api_name or APILK.REGISTRATION,
            user_id=user_id,
            *args,
            **kwargs,
        )

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
            self.bind_request_context(
                request,
                dictionary_utility_factory=dictionary_utility,
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
            if response_dto.status == APIStatus.SUCCESS and getattr(response_dto, "data", None):
                user_id = response_dto.data.get("user_id")
                user_email = response_dto.data.get("user_email")
                if user_email:
                    try:
                        await send_welcome_email(user_email)
                    except Exception as mail_err:
                        self.logger.warning("Welcome email send failed: %s", mail_err)
                if user_id is not None:
                    try:
                        event_id = str(uuid4())
                        dispatch_webhook_event(
                            session,
                            WebhookEventType.USER_CREATED,
                            event_id,
                            {"user_id": user_id, "email": user_email or ""},
                            user_id=user_id,
                        )
                    except Exception as wh_err:
                        self.logger.warning("user.created webhook dispatch failed: %s", wh_err)
            self.logger.debug("Prepared response metadata")

        except Exception as err:
            response_dto, httpStatusCode = self.handle_exception(
                err,
                request,
                event_name="register",
                session=session,
                fallback_message="Failed to register users.",
            )

        return self.build_json_response(response_dto, status_code=httpStatusCode)
