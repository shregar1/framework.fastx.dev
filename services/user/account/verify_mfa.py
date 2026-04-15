"""Verify-MFA Service – exchanges MFA challenge token + code for full JWT."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import jwt
from sqlalchemy.orm import Session

from constants.api_status import APIStatus
from dtos.requests.user.account.verify_mfa import VerifyMFARequestDTO
from dtos.responses.base import BaseResponseDTO
from fast_database.persistence.models.user import User
from fast_platform.errors import BadInputError, UnauthorizedError
from services.mfa import MFAService
from services.user.token_issuance import TokenIssuanceService
from start_utils import ALGORITHM, SECRET_KEY, logger


class VerifyMFAService:
    """Verify an MFA code against a challenge token and issue full JWTs."""

    def __init__(
        self,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Any = None,
        session: Optional[Session] = None,
        token_issuance_service: Optional[TokenIssuanceService] = None,
    ) -> None:
        self._urn = urn or ""
        self._user_urn = user_urn
        self._api_name = api_name or "AUTH_VERIFY_MFA"
        self._user_id = user_id
        self._session = session
        self._token_issuance_service = token_issuance_service
        self._logger = logger.bind(urn=self._urn, api_name=self._api_name)

    async def run(self, request_dto: VerifyMFARequestDTO) -> BaseResponseDTO:
        try:
            payload = jwt.decode(
                request_dto.mfa_challenge_token, SECRET_KEY, algorithms=[ALGORITHM],
            )
        except Exception as err:
            raise UnauthorizedError(
                responseMessage="Invalid or expired MFA challenge token.",
                responseKey="error_authentication_error",
            ) from err
        if payload.get("purpose") != "mfa_challenge":
            raise UnauthorizedError(
                responseMessage="Invalid token.",
                responseKey="error_authentication_error",
            )

        user_id = payload.get("user_id")
        user_urn = payload.get("user_urn")
        user = (
            self._session.query(User)
            .filter(User.id == user_id, User.is_deleted.is_(False))
            .first()
        )
        if not user:
            raise UnauthorizedError(
                responseMessage="User not found.",
                responseKey="error_authentication_error",
            )

        mfa_svc = MFAService(
            urn=self._urn, user_urn=user_urn, api_name=self._api_name,
            user_id=int(user_id) if user_id else None,
        )
        secret = getattr(user, "mfa_secret", None)
        code_ok = bool(secret and mfa_svc.verify_totp(secret, request_dto.code))
        if not code_ok:
            backup_hash = getattr(user, "mfa_backup_codes_hash", None) or ""
            matched, remaining = mfa_svc.verify_backup_code(request_dto.code, backup_hash)
            if matched:
                user.mfa_backup_codes_hash = remaining
                code_ok = True
        if not code_ok:
            raise BadInputError(
                responseMessage="Invalid MFA code.",
                responseKey="error_bad_input",
            )

        user.is_logged_in = True
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        # NOTE: commit is owned by the caller / UoW. Do not commit here.

        tokens = await self._token_issuance_service.issue(
            user_id=user.id,
            user_urn=user.urn,
            email=user.email,
            public_key_pem=getattr(user, "public_key_pem", None),
        )

        return BaseResponseDTO(
            transactionUrn=self._urn,
            status=APIStatus.SUCCESS,
            responseMessage="Successfully logged in.",
            responseKey="success_user_login",
            data={"status": True, **tokens},
        )


__all__ = ["VerifyMFAService"]
