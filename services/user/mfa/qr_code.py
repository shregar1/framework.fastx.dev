"""MFA QR-Code Service – render the provisioning URI as a PNG."""

from __future__ import annotations

import io
from typing import Any, Optional

from sqlalchemy.orm import Session

from fast_database.persistence.models.user import User
from fast_platform.errors import (
    BadInputError,
    NotFoundError,
    ServiceUnavailableError,
    UnauthorizedError,
)
from services.mfa import MFAService
from start_utils import logger

try:
    import qrcode  # type: ignore[import-not-found]
except ImportError:
    qrcode = None  # type: ignore


class MFAQrCodeService:
    """Produce a PNG QR code for the user's pending MFA provisioning URI."""

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
        self._api_name = api_name or "MFA_SETUP_QR_CODE"
        self._user_id = user_id
        self._session = session
        self._mfa_service = mfa_service
        self._mfa = mfa_service
        self._logger = logger.bind(urn=self._urn, api_name=self._api_name)

    async def run(self) -> tuple[bytes, str]:
        """Return ``(png_bytes, mime_type)`` for the pending setup secret."""
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
        if getattr(user, "mfa_enabled", False):
            raise BadInputError(
                responseMessage="MFA is already enabled.",
                responseKey="error_bad_input",
            )

        secret = getattr(user, "mfa_secret", None)
        if not secret:
            raise BadInputError(
                responseMessage="Call POST /mfa/setup first.",
                responseKey="error_bad_input",
            )

        if qrcode is None:
            raise ServiceUnavailableError(
                responseMessage=(
                    "QR code generation not available. Use the provisioningUri from "
                    "POST /mfa/setup to generate a QR client-side."
                ),
                responseKey="error_service_unavailable",
            )

        uri = self._mfa.get_provisioning_uri(secret, user.email or "user")
        img = qrcode.make(uri)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.read(), "image/png"


__all__ = ["MFAQrCodeService"]
