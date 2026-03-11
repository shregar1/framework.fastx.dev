"""
Dependency Abstraction Module.

This module defines the base interface for FastAPI dependency injection.
Dependencies are reusable components that can be injected into route handlers,
providing services like database sessions, authentication, and utilities.

Example:
    >>> class DatabaseDependency(IDependency):
    ...     def __init__(self, urn: str):
    ...         super().__init__(urn=urn)
    ...         self.session = create_session()
"""

from abc import ABC

from loguru import logger


class IDependency(ABC):
    """
    Abstract base class for FastAPI dependencies.

    The IDependency class provides a standardized interface for creating
    injectable dependencies in the FastMVC framework. Dependencies encapsulate
    reusable logic and resources that can be injected into route handlers.

    Common use cases:
        - Database session management
        - Authentication/authorization
        - External API clients
        - Caching mechanisms
        - Rate limiting

    Attributes:
        urn (str): Unique Request Number for request tracing.
        user_urn (str): User's unique resource name.
        api_name (str): Name of the API endpoint using this dependency.
        user_id (str): Database identifier of the authenticated user.
        logger: Structured logger bound with request context.

    Example:
        >>> class AuthDependency(IDependency):
        ...     def __init__(self, urn: str, user_urn: str):
        ...         super().__init__(urn=urn, user_urn=user_urn)
        ...
        ...     async def validate_token(self, token: str) -> bool:
        ...         # Token validation logic
        ...         return True
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ) -> None:
        """
        Initialize the dependency with request context.

        Args:
            urn (str, optional): Unique Request Number for tracing. Defaults to None.
            user_urn (str, optional): User's unique resource name. Defaults to None.
            api_name (str, optional): Name of the API endpoint. Defaults to None.
            user_id (str, optional): Database ID of the user. Defaults to None.
        """
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._logger = logger.bind(
            urn=self._urn, user_urn=self._user_urn, api_name=self._api_name
        )

    @property
    def urn(self) -> str:
        """str: Get the Unique Request Number."""
        return self._urn

    @urn.setter
    def urn(self, value: str) -> None:
        """Set the Unique Request Number."""
        self._urn = value

    @property
    def user_urn(self) -> str:
        """str: Get the user's unique resource name."""
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value: str) -> None:
        """Set the user's unique resource name."""
        self._user_urn = value

    @property
    def api_name(self) -> str:
        """str: Get the API endpoint name."""
        return self._api_name

    @api_name.setter
    def api_name(self, value: str) -> None:
        """Set the API endpoint name."""
        self._api_name = value

    @property
    def logger(self):
        """loguru.Logger: Get the structured logger instance."""
        return self._logger

    @logger.setter
    def logger(self, value) -> None:
        """Set the structured logger instance."""
        self._logger = value

    @property
    def user_id(self) -> str:
        """str: Get the user's database identifier."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        """Set the user's database identifier."""
        self._user_id = value
