"""Reset-password service – validates JWT reset token and updates password."""

from __future__ import annotations

import os
from typing import Optional

import bcrypt
import jwt
from sqlalchemy.orm import Session

from constants.api_status import APIStatus
from dtos.responses.base import BaseResponseDTO
from fast_platform.errors import BadInputError
from repositories.user.user_repository import UserRepository
from start_utils import ALGORITHM, SECRET_KEY, logger
from structured_log import log_event


def _hash_password(password: str) -> str:
    salt = os.getenv("BCRYPT_SALT")
    if not salt:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        return bcrypt.hashpw(password.encode("utf-8"), salt.encode("utf-8")).decode("utf-8")
    except ValueError:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


class ResetPasswordService:
    """Orchestrates the reset-password confirmation flow."""

    def __init__(
        self,
        urn: Optional[str] = None,
        api_name: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> None:
        self._urn = urn or ""
        self._api_name = api_name or "reset_password"
        self._session = session
        self._logger = logger.bind(urn=self._urn, api_name=self._api_name)

    async def run(self, token: str, new_password: str) -> BaseResponseDTO:
        try:
            payload = jwt.decode(token.strip(), SECRET_KEY, algorithms=[ALGORITHM])
        except Exception as err:
            raise BadInputError(
                responseMessage="Invalid or expired reset token.",
                responseKey="error_invalid_reset_token",
            ) from err

        if payload.get("purpose") != "password_reset":
            raise BadInputError(
                responseMessage="Invalid reset token.",
                responseKey="error_invalid_reset_token",
            )

        email = payload.get("email")
        if not email or not isinstance(email, str):
            raise BadInputError(
                responseMessage="Invalid reset token.",
                responseKey="error_invalid_reset_token",
            )

        repo = UserRepository(
            urn=self._urn,
            api_name=self._api_name,
            session=self._session,
        )
        user = repo.retrieve_record_by_email(email.strip().lower(), is_deleted=False)
        if not user:
            raise BadInputError(
                responseMessage="Invalid or expired reset token.",
                responseKey="error_invalid_reset_token",
            )

        repo.update_password(user, _hash_password(new_password))

        log_event("reset_password.success", urn=self._urn, email=email)

        return BaseResponseDTO(
            transactionUrn=self._urn,
            status=APIStatus.SUCCESS,
            responseMessage="Password has been reset. You can log in with your new password.",
            responseKey="success_password_reset_confirm",
            data={},
        )


__all__ = ["ResetPasswordService"]
