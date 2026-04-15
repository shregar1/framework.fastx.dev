"""Verify-Email Service – validates JWT email link and marks user verified."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import jwt
from sqlalchemy.orm import Session

from constants.api_status import APIStatus
from dtos.responses.base import BaseResponseDTO
from fast_platform.errors import BadInputError
from repositories.user.user_repository import UserRepository
from start_utils import ALGORITHM, SECRET_KEY, logger


class VerifyEmailService:
    """Validate the email-verification token and flip ``email_verified_at``."""

    def __init__(
        self,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Any = None,
        session: Optional[Session] = None,
    ) -> None:
        self._urn = urn or ""
        self._user_urn = user_urn
        self._api_name = api_name or "AUTH_VERIFY_EMAIL"
        self._user_id = user_id
        self._session = session
        self._logger = logger.bind(urn=self._urn, api_name=self._api_name)

    async def run(self, token: str) -> BaseResponseDTO:
        if not token or not token.strip():
            raise BadInputError(
                responseMessage="Invalid or expired verification link.",
                responseKey="error_verify_email_invalid",
            )
        try:
            payload = jwt.decode(
                token.strip(), SECRET_KEY, algorithms=[ALGORITHM],
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as err:
            raise BadInputError(
                responseMessage="Invalid or expired verification link.",
                responseKey="error_verify_email_invalid",
            ) from err

        if payload.get("purpose") != "email_verification":
            raise BadInputError(
                responseMessage="Invalid or expired verification link.",
                responseKey="error_verify_email_invalid",
            )
        email = payload.get("email")
        if not email:
            raise BadInputError(
                responseMessage="Invalid or expired verification link.",
                responseKey="error_verify_email_invalid",
            )

        repo = UserRepository(
            urn=self._urn,
            user_urn=self._user_urn,
            api_name=self._api_name,
            session=self._session,
            user_id=None,
        )
        user = repo.retrieve_record_by_email(email, is_deleted=False)
        if not user:
            raise BadInputError(
                responseMessage="Invalid or expired verification link.",
                responseKey="error_verify_email_invalid",
            )

        if getattr(user, "email_verified_at", None) is not None:
            return BaseResponseDTO(
                transactionUrn=self._urn,
                status=APIStatus.SUCCESS,
                responseMessage="Email is already verified.",
                responseKey="success_email_already_verified",
                data={
                    "email_verified_at": user.email_verified_at.isoformat()
                    if user.email_verified_at
                    else None,
                },
            )

        now = datetime.now(timezone.utc)
        repo.mark_email_verified(user, now)

        return BaseResponseDTO(
            transactionUrn=self._urn,
            status=APIStatus.SUCCESS,
            responseMessage="Email verified successfully.",
            responseKey="success_email_verified",
            data={"email_verified_at": now.isoformat()},
        )


__all__ = ["VerifyEmailService"]
