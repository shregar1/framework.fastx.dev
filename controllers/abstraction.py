"""Application controller abstraction.

Inheritance: layered interfaces under ``controllers.*`` → :class:`IController` →
:class:`abstractions.controller.IController` (framework) → :class:`core.utils.context.ContextMixin`.
"""

from typing import Any

from abstractions.controller import IController as FrameworkController


class IController(FrameworkController):
    """Root controller interface for this application; all controllers extend this or a nested interface."""

    def __init__(
        self,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the application controller base.

        Args:
            urn: Unique Request Number for tracing. Defaults to None.
            user_urn: User's URN. Defaults to None.
            api_name: API name. Defaults to None.
            user_id: User's database ID. Defaults to None.
            **kwargs: Forwarded to the framework controller (e.g. ``logger``).

        """
        super().__init__(
            urn=urn,  # type: ignore[arg-type]
            user_urn=user_urn,  # type: ignore[arg-type]
            api_name=api_name,  # type: ignore[arg-type]
            user_id=user_id,  # type: ignore[arg-type]
            **kwargs,
        )

    @property
    def urn(self) -> str | None:
        """str: Get the Unique Request Number."""
        return self._urn

    @urn.setter
    def urn(self, value: str) -> None:
        """Set the Unique Request Number."""
        self._urn = value

    @property
    def user_urn(self) -> str | None:
        """str: Get the user's unique resource name."""
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value: str) -> None:
        """Set the user's unique resource name."""
        self._user_urn = value

    @property
    def api_name(self) -> str | None:
        """str: Get the API endpoint name."""
        return self._api_name

    @api_name.setter
    def api_name(self, value: str) -> None:
        """Set the API endpoint name."""
        self._api_name = value

    @property
    def user_id(self) -> str | None:
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
