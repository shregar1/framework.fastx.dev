"""
Factory Abstraction Module.

This module defines the base factory interface for implementing the
Factory design pattern. Factories are responsible for creating and
configuring complex objects with proper dependency injection.

Example:
    >>> class ServiceFactory(IFactory):
    ...     def create_user_service(self) -> UserService:
    ...         return UserService(
    ...             urn=self.urn,
    ...             repository=self.create_repository()
    ...         )
"""

from abc import ABC

from loguru import logger


class IFactory(ABC):
    """
    Abstract base class for implementing the Factory pattern.

    The IFactory class provides a standardized interface for object creation
    in the FastMVC framework. Factories encapsulate the complexity of object
    instantiation and dependency wiring.

    Use cases:
        - Creating service instances with dependencies
        - Building repository objects with database sessions
        - Constructing complex objects with multiple collaborators
        - Managing object lifecycle and configuration

    Attributes:
        urn (str): Unique Request Number for tracing created objects.
        user_urn (str): User's unique resource name.
        api_name (str): Name of the API endpoint.
        user_id (str): Database identifier of the user.
        logger: Structured logger bound with factory context.

    Example:
        >>> class RepositoryFactory(IFactory):
        ...     def __init__(self, session, **kwargs):
        ...         super().__init__(**kwargs)
        ...         self.session = session
        ...
        ...     def create_user_repository(self) -> UserRepository:
        ...         return UserRepository(
        ...             session=self.session,
        ...             urn=self.urn
        ...         )
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ) -> None:
        """
        Initialize the factory with request context.

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
            urn=self._urn,
            user_urn=self._user_urn,
            api_name=self._api_name,
            user_id=self._user_id,
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
