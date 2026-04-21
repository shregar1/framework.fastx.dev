"""User Login Service."""

from __future__ import annotations

from typing import Any

import bcrypt

from constants.api_status import APIStatus
from constants.default import Default
from constants.response_keys import ResponseKey
from dtos.requests.user.login import UserLoginRequestDTO
from dtos.responses.base import BaseResponseDTO
from fast_platform.errors import (
    NotFoundError,
    UnauthorizedError,
)
from services.user.abstraction import IUserService
from services.user.token_issuance import TokenIssuanceService


class UserLoginService(IUserService):
    """Authenticates a user by email/password and returns tokens.

    If the user has MFA enabled, returns an MFA challenge token instead
    of full access/refresh tokens.
    """

    def __init__(
        self,
        user_repository: Any = None,
        jwt_utility: Any = None,
        refresh_token_repository: Any = None,
        token_issuance_service: TokenIssuanceService | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.user_repository = user_repository
        self.jwt_utility = jwt_utility
        self.refresh_token_repository = refresh_token_repository
        self._token_issuance_service = token_issuance_service

    async def run(self, request_dto: UserLoginRequestDTO) -> BaseResponseDTO:
        """Authenticate user and return token response DTO."""
        user = self.user_repository.retrieve_record_by_email(
            request_dto.email, is_deleted=False
        )
        if not user:
            raise NotFoundError(
                responseMessage="Invalid email or password.",
                responseKey=ResponseKey.ERROR_INVALID_CREDENTIALS,
                httpStatusCode=404,
            )

        stored_hash = user.password
        if not isinstance(stored_hash, bytes):
            stored_hash = stored_hash.encode("utf-8")

        if not bcrypt.checkpw(
            request_dto.password.encode("utf-8"),
            stored_hash,
        ):
            raise UnauthorizedError(
                responseMessage="Invalid email or password.",
                responseKey=ResponseKey.ERROR_INVALID_CREDENTIALS,
            )

        user_urn = getattr(user, "urn", None) or ""
        user_id = user.id

        # MFA flow
        if getattr(user, "mfa_enabled", False):
            mfa_token = self.jwt_utility.generate_token(
                {"user_id": user_id, "email": user.email, "purpose": "mfa_challenge"},
                expires_minutes=Default.MFA_TOKEN_EXPIRY_MINUTES,
            )
            public_key_pem = getattr(user, "public_key_pem", None)
            data: dict[str, Any] = {
                "requiresMFA": True,
                "mfaChallengeToken": mfa_token,
                "userUrn": user_urn,
            }
            if public_key_pem:
                data["publicKeyPem"] = public_key_pem
            return BaseResponseDTO(
                transactionUrn=self.urn or "",
                status=APIStatus.SUCCESS,
                responseMessage="MFA verification required.",
                responseKey=ResponseKey.SUCCESS_MFA_REQUIRED,
                data=data,
            )

        # Standard token flow — delegated to TokenIssuanceService.
        public_key_pem = getattr(user, "public_key_pem", None)
        tokens = await self._token_issuance_service.issue(
            user_id=user_id,
            user_urn=user_urn,
            email=user.email,
            public_key_pem=public_key_pem,
        )

        # Update login state via repository (caller owns commit)
        try:
            self.user_repository.touch_last_login(user)
        except Exception:
            pass

        data = {
            "status": True,
            **tokens,
            "userUrn": user_urn,
            "userId": user_id,
        }

        return BaseResponseDTO(
            transactionUrn=self.urn or "",
            status=APIStatus.SUCCESS,
            responseMessage="Successfully logged in the user.",
            responseKey=ResponseKey.SUCCESS_USER_LOGIN,
            data=data,
        )


__all__ = ["UserLoginService"]
