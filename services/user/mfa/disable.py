"""MFA Disable Service – turn off MFA after validating current code."""

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


class MFADisableService:
    """Disable MFA after verifying either a current TOTP or a backup code."""

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
        self._api_name = api_name or "MFA_DISABLE"
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
        if not getattr(user, "mfa_enabled", False):
            raise BadInputError(
                responseMessage="MFA is not enabled.",
                responseKey="error_bad_input",
            )

        secret = getattr(user, "mfa_secret", None)
        code_ok = bool(secret and self._mfa.verify_totp(secret, code))

        if not code_ok:
            backup_hash = getattr(user, "mfa_backup_codes_hash", None) or ""
            matched, remaining = self._mfa.verify_backup_code(code, backup_hash)
            if matched:
                user.mfa_backup_codes_hash = remaining
                code_ok = True

        if not code_ok:
            raise BadInputError(
                responseMessage="Invalid code.",
                responseKey="error_bad_input",
            )

        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes_hash = None
        log_audit(
            self._session,
            "mfa.disabled",
            "user",
            actor_id=int(self._user_id),
            actor_urn=getattr(user, "urn", None),
            resource_id=str(user.id),
        )

        return BaseResponseDTO(
            transactionUrn=self._urn,
            status=APIStatus.SUCCESS,
            responseMessage="MFA disabled.",
            responseKey="success_mfa_disabled",
            data={"enabled": False},
        )


__all__ = ["MFADisableService"]
