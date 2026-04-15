"""Concrete User repository – extends IUserRepository with domain finders."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select

from repositories.user.abstraction import IUserRepository


class UserRepository(IUserRepository):
    """Repository for the ``users`` table."""

    def __init__(
        self,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Optional[int] = None,
        session: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            session=session,
            *args,
            **kwargs,
        )
        self.session = session
        try:
            from fast_database.persistence.models.user import User
            self._model = User
        except ImportError:
            self._model = None

    @property
    def model(self):
        return self._model

    # ── Domain finders ──────────────────────────────────────────────

    def retrieve_record_by_email(
        self, email: str, is_deleted: bool = False
    ) -> Any | None:
        """Look up a user by email address."""
        if self.session is None or self._model is None:
            return None
        return self.session.scalars(
            select(self._model).where(
                self._model.email == email,
                self._model.is_deleted == is_deleted,
            )
        ).first()

    def retrieve_record_by_phone(self, phone: str) -> Any | None:
        """Look up a user by phone number."""
        if self.session is None or self._model is None:
            return None
        return self.session.scalars(
            select(self._model).where(
                self._model.phone == phone,
                self._model.is_deleted == False,
            )
        ).first()

    def create_record(self, data: dict | Any) -> Any:
        """Create a new user record.

        Accepts either a dict (controller convenience) or a model instance.
        """
        if self.session is None or self._model is None:
            raise RuntimeError("Database session is required to create records.")

        if isinstance(data, dict):
            record = self._model(**data)
        else:
            record = data

        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def retrieve_record_by_id(self, id: str | int, is_deleted: bool = False) -> Any | None:
        """Look up a user by primary key."""
        if self.session is None or self._model is None:
            return None
        return self.session.scalars(
            select(self._model).where(
                self._model.id == int(id),
                self._model.is_deleted == is_deleted,
            )
        ).first()

    # ── Single-op writes (repo owns commit) ─────────────────────────

    def mark_email_verified(self, user: Any, verified_at: Any) -> Any:
        """Set ``email_verified_at`` on the given user and persist.

        Single-op write: repository owns the commit boundary.
        """
        if self.session is None:
            raise RuntimeError("Database session is required to update records.")
        user.email_verified_at = verified_at
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_password(self, user: Any, password_hash: str) -> Any:
        """Update a user's password hash and persist.

        Single-op write: repository owns the commit boundary.
        """
        if self.session is None:
            raise RuntimeError("Database session is required to update records.")
        user.password = password_hash
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user


__all__ = ["UserRepository"]
