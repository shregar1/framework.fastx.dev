"""Concrete RefreshToken repository."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, update

from repositories.user.abstraction import IUserRepository


class RefreshTokenRepository(IUserRepository):
    """Repository for the ``refresh_tokens`` table."""

    def __init__(
        self,
        session: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(session=session, *args, **kwargs)
        self.session = session
        try:
            from fast_database.persistence.models.refresh_token import RefreshToken
            self._model = RefreshToken
        except ImportError:
            self._model = None

    @property
    def model(self):
        return self._model

    def store(self, user_id: int, token: str) -> Any:
        """Persist a new refresh token."""
        if self.session is None or self._model is None:
            raise RuntimeError("Database session is required.")
        record = self._model(
            token=token,
            user_id=user_id,
            revoked=False,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(record)
        self.session.commit()
        return record

    def create(
        self,
        jti: str,
        user_id: int,
        family_id: str,
        expires_at: datetime,
    ) -> Any:
        """Create a refresh token with explicit JTI and family."""
        if self.session is None or self._model is None:
            raise RuntimeError("Database session is required.")
        record = self._model(
            jti=jti,
            user_id=user_id,
            family_id=family_id,
            token=jti,
            revoked=False,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(record)
        self.session.commit()
        return record

    def find_by_token(self, token: str) -> Any | None:
        """Find a refresh token record by token value."""
        if self.session is None or self._model is None:
            return None
        return self.session.scalars(
            select(self._model).where(
                self._model.token == token,
                self._model.revoked == False,
            )
        ).first()

    def revoke(self, token: str) -> None:
        """Revoke a single refresh token."""
        if self.session is None or self._model is None:
            return
        record = self.session.scalars(
            select(self._model).where(self._model.token == token)
        ).first()
        if record:
            record.revoked = True
            self.session.commit()

    def revoke_all(self, user_id: int | str) -> None:
        """Revoke all refresh tokens for a user."""
        if self.session is None or self._model is None:
            return
        self.session.execute(
            update(self._model)
            .where(
                self._model.user_id == int(user_id),
                self._model.revoked == False,
            )
            .values(revoked=True)
        )
        self.session.commit()


__all__ = ["RefreshTokenRepository"]
