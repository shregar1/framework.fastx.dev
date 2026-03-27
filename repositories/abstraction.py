"""Application repository abstraction.

Inheritance: :class:`IRepository` → :class:`abstractions.repository.IRepository` →
:class:`core.utils.context.ContextMixin`.
"""

from typing import Any, Optional

from abstractions.repository import IRepository as FrameworkRepository


class IRepository(FrameworkRepository):
    """Root repository interface for this application."""

    def __init__(
        self,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Optional[str] = None,
        session: Any = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the application repository base.

        Args:
            urn: Unique Request Number for tracing. Defaults to None.
            user_urn: User's URN. Defaults to None.
            api_name: API name. Defaults to None.
            user_id: User's database ID. Defaults to None.
            session: Database session when applicable. Defaults to None.
            **kwargs: Forwarded to the framework repository (e.g. ``logger``).

        """
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            session=session,
            **kwargs,
        )

    @property
    def urn(self) -> Optional[str]:
        """str: Get the Unique Request Number."""
        return self._urn

    @urn.setter
    def urn(self, value: str) -> None:
        """Set the Unique Request Number."""
        self._urn = value

    @property
    def user_urn(self) -> Optional[str]:
        """str: Get the user's unique resource name."""
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value: str) -> None:
        """Set the user's unique resource name."""
        self._user_urn = value

    @property
    def api_name(self) -> Optional[str]:
        """str: Get the API endpoint name."""
        return self._api_name

    @api_name.setter
    def api_name(self, value: str) -> None:
        """Set the API endpoint name."""
        self._api_name = value

    @property
    def user_id(self) -> Optional[str]:
        """str: Get the user's database identifier."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        """Set the user's database identifier."""
        self._user_id = value

    @property
    def logger(self) -> Any:
        """loguru.Logger: Get the structured logger instance."""
        return self._logger

    @logger.setter
    def logger(self, value: Any) -> None:
        """Set the structured logger instance."""
        self._logger = value
