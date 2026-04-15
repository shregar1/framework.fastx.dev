"""MFA Verify Service – verify TOTP code and enable MFA."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from constants.api_status import APIStatus
from dtos.responses.base import BaseResponseDTO
from fast_database.persistence.models.user import User
from fast_platform.errors import BadInputError, NotFoundError, UnauthorizedError
from services.mfa import MFAService
from start_utils import logger
from utilities.audit import log_audit


class MFAVerifyService:
    """Verify a TOTP code against the pending secret and enable MFA."""

    def __init__(
        self,
        *args: Any,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Any = None,
        session: Optional[Session] = None,
        mfa_service: MFAService,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self._urn = urn or ""
        self._user_urn = user_urn
        self._api_name = api_name or "MFA_VERIFY"
        self._user_id = user_id
        self._session = session
        self._mfa_service = mfa_service
        self._mfa = mfa_service
        self._logger = logger.bind(urn=self._urn, api_name=self._api_name)

    async def run(self, code: str) -> BaseResponseDTO:
        if not self._user_id:
            raise UnauthorizedError(
                responseMessage="Unauthorized.",
                responseKey="error_authentication_error",
            )
        user = self._session.query(User).filter(User.id == self._user_id).first()
        if not user:
            raise NotFoundError(
                responseMessage="User not found.",
                responseKey="error_user_not_found",
            )

        secret = getattr(user, "mfa_secret", None)
        if not secret:
            raise BadInputError(
                responseMessage="Call setup first.",
                responseKey="error_bad_input",
            )
        if not self._mfa.verify_totp(secret, code):
            raise BadInputError(
                responseMessage="Invalid code.",
                responseKey="error_bad_input",
            )

        backup_codes = self._mfa.generate_backup_codes()
        user.mfa_enabled = True
        user.mfa_backup_codes_hash = self._mfa.hash_backup_codes(backup_codes)
        log_audit(
            self._session,
            "mfa.enabled",
            "user",
            actor_id=int(self._user_id),
            actor_urn=getattr(user, "urn", None),
            resource_id=str(user.id),
        )

        return BaseResponseDTO(
            transactionUrn=self._urn,
            status=APIStatus.SUCCESS,
            responseMessage="MFA enabled. Store backup codes securely; they will not be shown again.",
            responseKey="success_mfa_enabled",
            data={"enabled": True, "backupCodes": backup_codes},
        )


__all__ = ["MFAVerifyService"]
