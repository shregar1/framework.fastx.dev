"""Phone OTP Utility – generate and verify one-time passwords via SMS/Redis."""

from __future__ import annotations

import secrets
from typing import Any, Optional

from abstractions.utility import IUtility
from start_utils import logger


class PhoneOtpUtility(IUtility):
    """Generates 6-digit OTPs, stores in Redis, and triggers SMS delivery."""

    OTP_LENGTH: int = 6
    OTP_TTL_SECONDS: int = 300  # 5 minutes

    def __init__(
        self,
        *args: Any,
        redis_client: Any = None,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._redis = redis_client
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._logger = logger.bind(urn=urn, api_name=api_name)

    def _redis_key(self, phone: str, purpose: str) -> str:
        return f"otp:{phone}:{purpose}"

    def generate_otp(self) -> str:
        """Generate a cryptographically random numeric OTP."""
        return "".join(str(secrets.randbelow(10)) for _ in range(self.OTP_LENGTH))

    def store_otp(self, phone: str, purpose: str, otp: str) -> None:
        """Store OTP in Redis with TTL."""
        if self._redis is None:
            raise RuntimeError("Redis is required for OTP storage.")
        key = self._redis_key(phone, purpose)
        self._redis.setex(key, self.OTP_TTL_SECONDS, otp)
        self._logger.debug("OTP stored for %s (%s)", phone, purpose)

    def verify_otp(self, phone: str, purpose: str, otp: str) -> bool:
        """Verify OTP from Redis. Deletes on successful match."""
        if self._redis is None:
            raise RuntimeError("Redis is required for OTP verification.")
        key = self._redis_key(phone, purpose)
        stored = self._redis.get(key)
        if stored is None:
            return False
        stored_str = stored.decode("utf-8") if isinstance(stored, bytes) else str(stored)
        if secrets.compare_digest(stored_str, otp.strip()):
            self._redis.delete(key)
            return True
        return False

    async def create_and_send_otp(self, phone: str, purpose: str) -> bool:
        """Generate, store, and deliver an OTP for the given phone/purpose."""
        otp = self.generate_otp()
        self.store_otp(phone, purpose, otp)
        await self.send_otp(phone, otp)
        return True

    async def send_otp(self, phone: str, otp: str) -> None:
        """Send OTP via SMS provider. Falls back to logging."""
        try:
            from fast_platform.notifications import send_sms  # type: ignore

            await send_sms(to=phone, message=f"Your verification code is: {otp}")
        except ImportError:
            self._logger.warning(
                "SMS provider not configured – OTP for %s: %s (logged only)", phone, otp
            )
        except Exception as exc:
            self._logger.error("Failed to send OTP to %s: %s", phone, exc)


__all__ = ["PhoneOtpUtility"]
