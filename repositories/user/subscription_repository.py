"""Concrete Subscription repository."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select

from repositories.user.abstraction import IUserRepository


class SubscriptionRepository(IUserRepository):
    """Repository for subscription lookups.

    The actual ``subscriptions`` model is expected to be defined
    in the host application.  When absent the repository methods
    return ``None`` gracefully.
    """

    def __init__(
        self,
        session: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(session=session, *args, **kwargs)
        self.session = session
        self._model = None
        try:
            from fast_database.persistence.models.subscription import Subscription
            self._model = Subscription
        except ImportError:
            pass

    @property
    def model(self):
        return self._model

    def get_active_for_user(self, user_id: int) -> Any | None:
        """Return the active subscription for *user_id*, or ``None``."""
        if self.session is None or self._model is None:
            return None
        return self.session.scalars(
            select(self._model).where(
                self._model.user_id == user_id,
                self._model.is_active == True,
            )
        ).first()


__all__ = ["SubscriptionRepository"]
