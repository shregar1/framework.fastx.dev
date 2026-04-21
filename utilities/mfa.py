"""MFA (Multi-Factor Authentication) Utility.

Provides TOTP secret generation, code verification, and backup-code
management.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import struct
import time
from typing import Any, Optional

from abstractions.utility import IUtility
from constants.default import Default
from start_utils import logger


class MFAUtility(IUtility):
    """Handles TOTP generation, verification, and backup codes."""

    def __init__(
        self,
        *args: Any,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._logger = logger.bind(urn=urn, user_urn=user_urn, api_name=api_name)

    # ── Secret generation ────────────────────────────────────────────

    @staticmethod
    def generate_secret() -> str:
        """Generate a base32-encoded TOTP secret (160 bits)."""
        import base64
        raw = secrets.token_bytes(20)
        return base64.b32encode(raw).decode(Default.ENCODING_UTF8)

    @staticmethod
    def get_provisioning_uri(
        secret: str,
        email: str,
        issuer: Optional[str] = None,
    ) -> str:
        """Build an ``otpauth://`` provisioning URI for authenticator apps."""
        if issuer is None:
            issuer = os.getenv("APP_NAME", "FastMVC")
        from urllib.parse import quote
        label = quote(f"{issuer}:{email}", safe="")
        params = f"secret={secret}&issuer={quote(issuer)}"
        return f"otpauth://totp/{label}?{params}"

    # ── TOTP verification ────────────────────────────────────────────

    @staticmethod
    def _hotp(secret_b32: str, counter: int) -> str:
        """Compute a 6-digit HOTP value from *secret_b32* and *counter*."""
        import base64
        key = base64.b32decode(secret_b32, casefold=True)
        msg = struct.pack(">Q", counter)
        digest = hmac.new(key, msg, hashlib.sha1).digest()
        offset = digest[-1] & 0x0F
        code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
        return str(code % 10**6).zfill(6)

    @classmethod
    def verify_totp(cls, secret: str, code: str, *, window: int = 1) -> bool:
        """Verify a TOTP code against *secret* within ±*window* steps."""
        if not secret or not code:
            return False
        counter = int(time.time()) // Default.MFA_TIME_STEP_SECONDS
        for offset in range(-window, window + 1):
            if hmac.compare_digest(cls._hotp(secret, counter + offset), code.strip()):
                return True
        return False

    # ── Backup codes ─────────────────────────────────────────────────

    @staticmethod
    def generate_backup_codes(count: int = 10) -> list[str]:
        """Generate *count* single-use backup codes (8 hex chars each)."""
        return [secrets.token_hex(4).upper() for _ in range(count)]

    @staticmethod
    def hash_backup_codes(codes: list[str]) -> str:
        """Hash a list of backup codes into a single storable string.

        Each code is SHA-256 hashed and joined with ``|``.
        """
        return "|".join(
            hashlib.sha256(c.strip().upper().encode()).hexdigest() for c in codes
        )

    @staticmethod
    def verify_backup_code(code: str, hashed_codes_str: str) -> tuple[bool, str]:
        """Check *code* against *hashed_codes_str*.

        Returns ``(matched, updated_hash_str)`` where the used code is
        removed from the hash string.
        """
        if not code or not hashed_codes_str:
            return False, hashed_codes_str
        code_hash = hashlib.sha256(code.strip().upper().encode()).hexdigest()
        parts = hashed_codes_str.split("|")
        for i, h in enumerate(parts):
            if hmac.compare_digest(h, code_hash):
                remaining = parts[:i] + parts[i + 1 :]
                return True, "|".join(remaining)
        return False, hashed_codes_str


__all__ = ["MFAUtility"]
