"""Token Issuance Service.

Single-responsibility helper that produces the access+refresh token pair
used by login, refresh-token, and MFA-verify flows. Does NOT commit the
session — transaction boundary is owned by the caller / UoW.
"""

from __future__ import annotations

from typing import Any

from services.user.abstraction import IUserService
from start_utils import logger


class TokenIssuanceService(IUserService):
    """Issues a fresh access+refresh token pair for a user.

    Single responsibility: produce the
    ``{token, refreshToken, user_urn, user_id, publicKeyPem}`` dict that
    login / refresh / MFA-verify all need. Does NOT commit the session;
    the caller (or UoW) owns the transaction boundary.
    """

    def __init__(
        self,
        *args: Any,
        jwt_utility: Any = None,
        refresh_token_repository: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._jwt_utility = jwt_utility
        self._refresh_token_repository = refresh_token_repository

    async def issue(
        self,
        *,
        user_id: int,
        user_urn: str,
        email: str | None = None,
        public_key_pem: str | None = None,
    ) -> dict:
        """Generate access + refresh tokens and persist the refresh token.

        Mirrors the existing logic in :class:`UserLoginService.run`. Does
        not commit the session — only the repository's ``store()`` call
        may commit (that is handled by a separate centralization task).
        """
        token_payload: dict[str, Any] = {
            "user_id": user_id,
            "user_urn": user_urn,
        }
        if email is not None:
            token_payload["email"] = email

        access_token = self._jwt_utility.generate_token(token_payload)
        refresh_token = self._jwt_utility.generate_refresh_token(token_payload)

        # Persist refresh token (best-effort; log on failure).
        if self._refresh_token_repository:
            try:
                self._refresh_token_repository.store(
                    user_id=user_id,
                    token=refresh_token,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Failed to persist refresh token for user %s: %s",
                    user_id,
                    exc,
                )

        data: dict[str, Any] = {
            "token": access_token,
            "refreshToken": refresh_token,
            "user_urn": user_urn,
            "user_id": user_id,
        }
        if public_key_pem:
            data["publicKeyPem"] = public_key_pem
        return data


__all__ = ["TokenIssuanceService"]
