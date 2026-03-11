from datetime import datetime
from http import HTTPStatus
from typing import Optional

import bcrypt

from constants.api_status import APIStatus
from dtos.requests.user.login import UserLoginRequestDTO
from dtos.responses.base import BaseResponseDTO
from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from models.user import User
from repositories.user import UserRepository
from services.user.abstraction import IUserService
from utilities.jwt import JWTUtility


class UserLoginService(IUserService):
    """
    Service to handle user login, authentication, and token issuance.
    """
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
        user_repository: UserRepository = None,
        jwt_utility: JWTUtility = None,
    ) -> None:
        super().__init__(urn, user_urn, api_name)
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._user_repository = user_repository
        self._jwt_utility = jwt_utility
        self.logger.debug(
            f"UserLoginService initialized for "
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

    @property
    def jwt_utility(self):
        return self._jwt_utility

    @jwt_utility.setter
    def jwt_utility(self, value):
        self._jwt_utility = value

    async def run(self, request_dto: UserLoginRequestDTO) -> dict:

        self.logger.debug("Validating login payload")
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

        self.logger.debug("Fetching user")
        user: User = (
            self.user_repository.retrieve_record_by_email(
                email=email,
                is_deleted=False,
            )
        )
        self.logger.debug("Fetched user")

        if not user:
            raise NotFoundError(
                responseMessage="User not Found. Incorrect email.",
                responseKey="error_authorisation_failed",
                httpStatusCode=HTTPStatus.NOT_FOUND,
            )

        if not bcrypt.checkpw(password.encode("utf8"), user.password.encode("utf8")):
            raise BadInputError(
                responseMessage="Incorrect password.",
                responseKey="error_authorisation_failed",
                httpStatusCode=HTTPStatus.BAD_REQUEST,
            )

        self.logger.debug("Updating logged in status")
        user: User = self.user_repository.update_record(
            id=user.id,
            new_data={
                "is_logged_in": True,
                "last_login": datetime.now(),
                "updated_on": datetime.now(),
            },
        )
        self.logger.debug("Updated logged in status")

        payload = {
            "user_id": user.id,
            "user_urn": user.urn,
            "user_email": user.email,
            "last_login": str(user.updated_on),
        }
        token: str = self.jwt_utility.create_access_token(data=payload)

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="Successfully logged in the user.",
            responseKey="success_user_login",
            data={
                "status": True,
                "token": token,
                "user_urn": user.urn,
            },
        )
