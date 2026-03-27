"""Context utilities for request tracking and logging.

Provides mixins and helpers for managing request context,
including URN tracking and user information.
"""

from typing import Any, Dict, Optional

# Use loguru logger if available, otherwise use standard logging
try:
    from loguru import logger as _default_logger
except ImportError:
    import logging

    _default_logger = logging.getLogger("fast_mvc")


class ContextMixin:
    """Mixin class that provides request context attributes.

    This mixin is used by controllers, services, and other components
    to access common request context information like the request URN
    and user identifier.

    Attributes:
        urn (str): Unique Request Number for tracking
        user_urn (str): User identifier for the current request
        api_name (str): Name of the API endpoint
        user_id (str): Database identifier of the user
        context (dict): Additional context data

    Example:
        >>> class MyController(IController, ContextMixin):
        ...     async def handle(self, request):
        ...         logger.info(f"Processing request {self.urn}")

    """

    def __init__(
        self,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Optional[str] = None,
        logger: Any = None,
        **kwargs: Any,
    ) -> None:
        """Execute __init__ operation.

        Args:
            urn: The urn parameter.
            user_urn: The user_urn parameter.
            api_name: The api_name parameter.
            user_id: The user_id parameter.
            logger: The logger parameter.
        """
        self._urn: Optional[str] = urn
        self._user_urn: Optional[str] = user_urn
        self._api_name: Optional[str] = api_name
        self._user_id: Optional[str] = user_id
        self._logger: Any = logger or _default_logger
        self._context: Dict[str, Any] = kwargs

    @property
    def urn(self) -> Optional[str]:
        """Get the Unique Request Number."""
        return self._urn

    @urn.setter
    def urn(self, value: str) -> None:
        """Set the Unique Request Number."""
        self._urn = value

    @property
    def user_urn(self) -> Optional[str]:
        """Get the User URN."""
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value: str) -> None:
        """Set the User URN."""
        self._user_urn = value

    @property
    def api_name(self) -> Optional[str]:
        """Get the API name."""
        return self._api_name

    @api_name.setter
    def api_name(self, value: str) -> None:
        """Set the API name."""
        self._api_name = value

    @property
    def user_id(self) -> Optional[str]:
        """Get the User ID."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        """Set the User ID."""
        self._user_id = value

    @property
    def logger(self) -> Any:
        """Get the logger."""
        return self._logger

    @logger.setter
    def logger(self, value: Any) -> None:
        """Set the logger."""
        self._logger = value

    @property
    def context(self) -> Dict[str, Any]:
        """Get the context dictionary."""
        return self._context

    def set_context(self, **kwargs) -> None:
        """Set multiple context values at once."""
        self._context.update(kwargs)

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value by key."""
        return self._context.get(key, default)
