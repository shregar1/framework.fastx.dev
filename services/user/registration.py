import os
from datetime import datetime
from http import HTTPStatus
from typing import Optional

import bcrypt
import ulid

from constants.api_status import APIStatus
from dtos.requests.user.registration import UserRegistrationRequestDTO
from dtos.responses.base import BaseResponseDTO
from errors.bad_input_error import BadInputError
from models.user import User
from repositories.user import UserRepository
from services.user.abstraction import IUserService


# Backwards-compatible alias for tests that patch `services.user.registration.ULID`
ULID = ulid.ULID


class UserRegistrationService(IUserService):
    """
    Service to handle user registration and new user creation.
    """
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
        user_repository: UserRepository = None,
    ) -> None:
        super().__init__(urn, user_urn, api_name)
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._user_repository = user_repository
        self.logger.debug(
            f"UserRegistrationService initialized for "
            f"user_id={user_id}, urn={urn}, api_name={api_name}"
        )

    @property
    def urn(self):
        return self._urn

    @urn.setter
    def urn(self, value):
        self._urn = value

    @property
    def user_urn(self):
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value):
        self._user_urn = value

    @property
    def api_name(self):
        return self._api_name

    @api_name.setter
    def api_name(self, value):
        self._api_name = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def user_repository(self):
        return self._user_repository

    @user_repository.setter
    def user_repository(self, value):
        self._user_repository = value

    async def run(self, request_dto: UserRegistrationRequestDTO) -> dict:

        self.logger.debug("Validating registration payload")
        email: Optional[str] = request_dto.email
        password: Optional[str] = request_dto.password

        if not email or not isinstance(email, str):
            raise BadInputError(
                responseMessage="Email is required.",
                responseKey="error_email_required",
                httpStatusCode=HTTPStatus.BAD_REQUEST,
            )

        if not password or not isinstance(password, str):
            raise BadInputError(
                responseMessage="Password is required.",
                responseKey="error_password_required",
                httpStatusCode=HTTPStatus.BAD_REQUEST,
            )

        self.logger.debug("Checking if user exists")
        user: User = self.user_repository.retrieve_record_by_email(
            email=email
        )

        if user:

            self.logger.debug("User already exists")
            raise BadInputError(
                responseMessage="Email already registered.",
                responseKey="error_email_already_registered",
                httpStatusCode=HTTPStatus.BAD_REQUEST,
            )

        bcrypt_salt = os.getenv("BCRYPT_SALT")
        if not bcrypt_salt:
            raise RuntimeError("BCRYPT_SALT environment variable is not set.")

        self.logger.debug("Preparing user data")
        user: User = User(
            urn=str(ulid.new()),
            email=email,
            password=bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt_salt.encode("utf8"),
            ).decode("utf8"),
            is_deleted=False,
            created_by=1,
            created_on=datetime.now(),
        )

        user: User = self.user_repository.create_record(record=user)
        self.logger.debug("Preparing user data")

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="Successfully registered the user.",
            responseKey="success_user_register",
            data={
                "user_email": user.email,
                "created_at": str(user.created_on),
            },
        )
