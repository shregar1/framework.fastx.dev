"""User Refresh Token Service."""

from __future__ import annotations

from typing import Any

from constants.api_status import APIStatus
from dtos.requests.user.refresh import RefreshTokenRequestDTO
from dtos.responses.base import BaseResponseDTO
from fast_platform.errors import UnauthorizedError
from services.user.abstraction import IUserService
from services.user.token_issuance import TokenIssuanceService
from start_utils import logger


class UserRefreshTokenService(IUserService):
    """Exchanges a refresh token for new access + refresh tokens."""

    def __init__(
        self,
        user_repository: Any = None,
        jwt_utility: Any = None,
        refresh_token_repository: Any = None,
        token_issuance_service: TokenIssuanceService | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.user_repository = user_repository
        self.jwt_utility = jwt_utility
        self.refresh_token_repository = refresh_token_repository
        self._token_issuance_service = token_issuance_service

    async def run(self, request_dto: RefreshTokenRequestDTO) -> BaseResponseDTO:
        """Validate refresh token and issue new pair."""
        # Decode and validate the token
        try:
            payload = self.jwt_utility.decode_token(request_dto.refreshToken)
        except Exception:
            raise UnauthorizedError(
                responseMessage="Invalid or expired refresh token.",
                responseKey="error_invalid_refresh_token",
            )

        if payload.get("type") != "refresh":
            raise UnauthorizedError(
                responseMessage="Invalid token type.",
                responseKey="error_invalid_token_type",
            )

        user_id = payload.get("user_id")

        # Verify token exists in the database (not revoked)
        if self.refresh_token_repository:
            try:
                stored = self.refresh_token_repository.find_by_token(
                    token=request_dto.refreshToken
                )
                if not stored:
                    raise UnauthorizedError(
                        responseMessage="Refresh token has been revoked.",
                        responseKey="error_token_revoked",
                    )
            except UnauthorizedError:
                raise
            except Exception as exc:
                logger.warning("Refresh token lookup failed: %s", exc)

        # Look up user
        user = self.user_repository.retrieve_record_by_id(user_id) if user_id else None
        if not user:
            raise UnauthorizedError(
                responseMessage="User not found.",
                responseKey="error_user_not_found",
            )

        user_urn = getattr(user, "urn", None) or ""

        # Revoke the old refresh token before issuing a new pair.
        if self.refresh_token_repository:
            try:
                self.refresh_token_repository.revoke(token=request_dto.refreshToken)
            except Exception as exc:
                logger.warning(
                    "Failed to revoke old refresh token for user %s: %s",
                    user.id,
                    exc,
                )

        tokens = await self._token_issuance_service.issue(
            user_id=user.id,
            user_urn=user_urn,
            email=user.email,
        )

        return BaseResponseDTO(
            transactionUrn=self.urn or "",
            status=APIStatus.SUCCESS,
            responseMessage="Tokens refreshed successfully.",
            responseKey="success_refresh_token",
            data=tokens,
        )


__all__ = ["UserRefreshTokenService"]
