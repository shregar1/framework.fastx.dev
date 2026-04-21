"""Phone OTP verification and token-issuance helper.

Used by :class:`controllers.auth.user.phone.verify_otp.PhoneVerifyOtpController`
to verify an OTP and, when the purpose is ``login`` or ``register``,
issue JWT tokens.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from constants.api_status import APIStatus
from dtos.responses.base import BaseResponseDTO
from utilities.phone_otp import PhoneOtpUtility
from start_utils import logger


@dataclass
class _PhoneUserDTO:
    """Lightweight transient user representation for phone registration flow."""

    id: Any = None
    urn: str = ""
    email: str = ""
    phone: str = ""
    is_logged_in: bool = False
    last_login: Optional[datetime] = None


async def verify_otp_and_issue_tokens(
    *,
    phone: str,
    otp: str,
    purpose: str,
    otp_service: PhoneOtpUtility,
    user_repository: Any = None,
    jwt_utility: Any = None,
    refresh_token_repository: Any = None,
    session: Any = None,
    urn: str = "",
) -> BaseResponseDTO:
    """Verify OTP and conditionally issue tokens.

    Args:
        phone: Phone number the OTP was sent to.
        otp: The code entered by the user.
        purpose: The OTP purpose (``login``, ``register``, ``verify_phone``, ``reset_password``).
        otp_service: :class:`PhoneOtpUtility` instance with Redis.
        user_repository: Repository for user lookup / creation.
        jwt_utility: JWT utility for token generation.
        refresh_token_repository: For persisting refresh tokens.
        session: SQLAlchemy session.
        urn: Transaction URN for tracing.

    Returns:
        :class:`BaseResponseDTO` with tokens (for login/register) or
        verified flag (for other purposes).
    """
    from fast_platform.errors import BadInputError, NotFoundError

    if not otp_service.verify_otp(phone, purpose, otp):
        raise BadInputError(
            responseMessage="Invalid or expired OTP.",
            responseKey="error_invalid_otp",
        )

    # For non-auth purposes, just confirm verification
    if purpose not in ("login", "register"):
        return BaseResponseDTO(
            transactionUrn=urn,
            status=APIStatus.SUCCESS,
            responseMessage="OTP verified.",
            responseKey="success_otp_verified",
            data={"verified": True},
        )

    # Login flow — look up user by phone
    if purpose == "login":
        user = user_repository.retrieve_record_by_phone(phone) if user_repository else None
        if not user:
            raise NotFoundError(
                responseMessage="No account found for this phone number.",
                responseKey="error_user_not_found",
                httpStatusCode=404,
            )

    # Register flow — create user if not existing
    elif purpose == "register":
        user = user_repository.retrieve_record_by_phone(phone) if user_repository else None
        if not user:
            user_data = user_repository.create_record({"phone": phone, "email": "", "password": "", "name": ""})
            if session:
                session.commit()
                session.refresh(user_data)
            user = user_data if not isinstance(user_data, dict) else _PhoneUserDTO(**{k: v for k, v in user_data.items() if k in _PhoneUserDTO.__dataclass_fields__})

    user_id = getattr(user, "id", None)
    user_urn = getattr(user, "urn", None) or ""
    user_email = getattr(user, "email", "")

    token_payload = {"user_id": user_id, "email": user_email, "user_urn": user_urn}
    access_token = jwt_utility.generate_token(token_payload)
    refresh_token = jwt_utility.generate_refresh_token(token_payload)

    if refresh_token_repository:
        try:
            refresh_token_repository.store(user_id=user_id, token=refresh_token)
        except Exception as exc:
            logger.warning("Failed to persist refresh token for user %s: %s", user_id, exc)

    try:
        user.is_logged_in = True
        user.last_login = datetime.now(timezone.utc)
    except Exception:
        pass

    return BaseResponseDTO(
        transactionUrn=urn,
        status=APIStatus.SUCCESS,
        responseMessage="Login successful.",
        responseKey="success_user_login",
        data={
            "token": access_token,
            "refreshToken": refresh_token,
            "user_urn": user_urn,
            "user_id": user_id,
        },
    )


__all__ = ["verify_otp_and_issue_tokens"]
