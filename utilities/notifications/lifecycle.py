"""Lifecycle email helpers – welcome, verification, password reset.

Functions are ``async`` so controllers can ``await`` them. When the
notification provider is not configured the calls log a warning and
return silently (fire-and-forget semantics).
"""

from __future__ import annotations

from typing import Optional

from constants.default import Default
from fast_platform.errors import ServiceUnavailableError
from start_utils import logger


async def send_welcome_email(email: str) -> None:
    """Send a welcome / onboarding email after registration."""
    try:
        from fast_platform.notifications import send_email  # type: ignore

        await send_email(
            to=email,
            template="welcome",
            subject="Welcome!",
        )
    except ImportError:
        logger.warning("Notification provider not available – skipping welcome email to %s", email)
        return
    except Exception as err:
        logger.exception("welcome email send failed for %s", email)
        raise ServiceUnavailableError(
            responseMessage="Failed to send notification email.",
            responseKey="error_notification_send_failed",
        ) from err


async def send_password_reset_email(
    email: str,
    reset_link: str,
    *,
    expires_minutes: int = Default.EMAIL_TOKEN_EXPIRY_MINUTES,
) -> None:
    """Send a password-reset link email."""
    try:
        from fast_platform.notifications import send_email  # type: ignore

        await send_email(
            to=email,
            template="password_reset",
            subject="Reset your password",
            context={"reset_link": reset_link, "expires_minutes": expires_minutes},
        )
    except ImportError:
        logger.warning("Notification provider not available – skipping reset email to %s", email)
        return
    except Exception as err:
        logger.exception("password reset email send failed for %s", email)
        raise ServiceUnavailableError(
            responseMessage="Failed to send notification email.",
            responseKey="error_notification_send_failed",
        ) from err


async def send_verification_email(
    email: str,
    verify_link: str,
    *,
    expires_minutes: int = Default.EMAIL_TOKEN_EXPIRY_MINUTES,
) -> None:
    """Send an email-verification link."""
    try:
        from fast_platform.notifications import send_email  # type: ignore

        await send_email(
            to=email,
            template="email_verification",
            subject="Verify your email",
            context={"verify_link": verify_link, "expires_minutes": expires_minutes},
        )
    except ImportError:
        logger.warning("Notification provider not available – skipping verification email to %s", email)
        return
    except Exception as err:
        logger.exception("verification email send failed for %s", email)
        raise ServiceUnavailableError(
            responseMessage="Failed to send notification email.",
            responseKey="error_notification_send_failed",
        ) from err


# Alias used by controllers/auth/user/account/send_verification_email.py
send_verify_email = send_verification_email

__all__ = [
    "send_welcome_email",
    "send_password_reset_email",
    "send_verification_email",
    "send_verify_email",
]
