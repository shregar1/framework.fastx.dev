# Migrate call sites incrementally.
"""Centralized responseKey constants for i18n and consistency."""

from typing import Final


class ResponseKey:
    """Centralized response key constants for i18n and consistency.

    Import and use these instead of string literals for responseKey values.
    Existing constants from response_key.py are re-exported here as well.
    """

    # ── General / Infrastructure ────────────────────────────────────────
    ERROR_INTERNAL_SERVER_ERROR: Final[str] = "error_internal_server_error"
    ERROR_BAD_INPUT: Final[str] = "error_bad_input"
    ERROR_UNKNOWN: Final[str] = "error_unknown"
    ERROR_SERVICE_UNAVAILABLE: Final[str] = "error_service_unavailable"
    ERROR_UNAUTHORIZED: Final[str] = "error_unauthorized"
    UNAUTHORIZED: Final[str] = "error_unauthorized"  # legacy alias

    # ── Health ──────────────────────────────────────────────────────────
    SUCCESS_HEALTH: Final[str] = "success_health"
    ERROR_HEALTH_UNHEALTHY: Final[str] = "error_health_unhealthy"
    SUCCESS_HEALTH_LIVE: Final[str] = "success_health_live"
    SUCCESS_HEALTH_READY: Final[str] = "success_health_ready"
    ERROR_HEALTH_NOT_READY: Final[str] = "error_health_not_ready"

    # ── Auth / Login / Logout ───────────────────────────────────────────
    SUCCESS_USER_LOGIN: Final[str] = "success_user_login"
    SUCCESS_LOGOUT: Final[str] = "success_logout"
    SUCCESS_REGISTRATION: Final[str] = "success_registration"
    SUCCESS_MFA_REQUIRED: Final[str] = "success_mfa_required"
    ERROR_INVALID_CREDENTIALS: Final[str] = "error_invalid_credentials"
    ERROR_AUTHENTICATION_ERROR: Final[str] = "error_authentication_error"
    ERROR_AUTHENTICATION_REQUIRED: Final[str] = "error_authentication_required"
    ERROR_USER_NOT_FOUND: Final[str] = "error_user_not_found"
    ERROR_DUPLICATE_EMAIL: Final[str] = "error_duplicate_email"

    # ── Token / Refresh ─────────────────────────────────────────────────
    SUCCESS_REFRESH_TOKEN: Final[str] = "success_refresh_token"
    ERROR_INVALID_REFRESH_TOKEN: Final[str] = "error_invalid_refresh_token"
    ERROR_INVALID_TOKEN_TYPE: Final[str] = "error_invalid_token_type"
    ERROR_TOKEN_REVOKED: Final[str] = "error_token_revoked"

    # ── Password Reset ──────────────────────────────────────────────────
    SUCCESS_PASSWORD_RESET_REQUEST: Final[str] = "success_password_reset_request"
    SUCCESS_PASSWORD_RESET_CONFIRM: Final[str] = "success_password_reset_confirm"
    ERROR_INVALID_RESET_TOKEN: Final[str] = "error_invalid_reset_token"

    # ── Email Verification ──────────────────────────────────────────────
    SUCCESS_EMAIL_VERIFIED: Final[str] = "success_email_verified"
    SUCCESS_EMAIL_ALREADY_VERIFIED: Final[str] = "success_email_already_verified"
    SUCCESS_VERIFICATION_EMAIL_SENT: Final[str] = "success_verification_email_sent"
    ERROR_VERIFY_EMAIL_INVALID: Final[str] = "error_verify_email_invalid"
    ERROR_NO_EMAIL: Final[str] = "error_no_email"
    ERROR_SEND_FAILED: Final[str] = "error_send_failed"

    # ── MFA ─────────────────────────────────────────────────────────────
    SUCCESS_MFA_SETUP: Final[str] = "success_mfa_setup"
    SUCCESS_MFA_ENABLED: Final[str] = "success_mfa_enabled"
    SUCCESS_MFA_DISABLED: Final[str] = "success_mfa_disabled"
    SUCCESS_MFA_STATUS: Final[str] = "success_mfa_status"

    # ── Phone / OTP ─────────────────────────────────────────────────────
    SUCCESS_OTP_SENT: Final[str] = "success_otp_sent"
    SUCCESS_OTP_VERIFIED: Final[str] = "success_otp_verified"
    ERROR_INVALID_OTP: Final[str] = "error_invalid_otp"

    # ── Item ────────────────────────────────────────────────────────────
    ERROR_ITEM_NOT_FOUND: Final[str] = "error_item_not_found"

    # ── Subscription ────────────────────────────────────────────────────
    SUCCESS_NO_SUBSCRIPTION: Final[str] = "success_no_subscription"
    SUCCESS_GET_SUBSCRIPTION: Final[str] = "success_get_subscription"

    # ── User Profile / Fetch ────────────────────────────────────────────
    SUCCESS_USER_PROFILE: Final[str] = "success_user_profile"
    SUCCESS_USER_FETCH: Final[str] = "success_user_fetch"

    # ── Example ─────────────────────────────────────────────────────────
    SUCCESS_EXAMPLE_CREATED: Final[str] = "success_example_created"


__all__ = ["ResponseKey"]
