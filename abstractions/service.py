"""
Service Abstraction Module.

This module defines the base service interface that all business logic
services must inherit from. Services encapsulate domain logic and
orchestrate operations between repositories and external systems.

Example:
    >>> class UserRegistrationService(IService):
    ...     def __init__(self, user_repo: UserRepository, **kwargs):
    ...         super().__init__(**kwargs)
    ...         self.user_repo = user_repo
    ...
    ...     def run(self, request_dto: RegistrationDTO) -> dict:
    ...         # Business logic here
    ...         return {"status": "success"}
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from start_utils import logger


class IService(ABC):
    """
    Abstract base class for business logic services.

    The IService class provides a standardized interface for implementing
    business logic in the FastMVC framework. Services are the core of the
    application, containing domain rules and orchestrating data flow.

    Key responsibilities:
        - Implement business rules and validation
        - Coordinate between repositories and external APIs
        - Transform data between layers
        - Handle business-level error conditions

    Attributes:
        urn (str): Unique Request Number for tracing.
        user_urn (str): User's unique resource name.
        api_name (str): Name of the API endpoint.
        user_id (int): Database identifier of the user.
        logger: Structured logger bound with service context.

    Abstract Methods:
        run: Execute the service's main business logic.

    Example:
        >>> class OrderProcessingService(IService):
        ...     def __init__(self, order_repo, payment_client, **kwargs):
        ...         super().__init__(**kwargs)
        ...         self.order_repo = order_repo
        ...         self.payment_client = payment_client
        ...
        ...     def run(self, request_dto: OrderDTO) -> dict:
        ...         # Validate order
        ...         # Process payment
        ...         # Create order record
        ...         return {"order_id": "...", "status": "confirmed"}
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
    ) -> None:
        """
        Initialize the service with request context.

        Args:
            urn (str, optional): Unique Request Number for tracing. Defaults to None.
            user_urn (str, optional): User's unique resource name. Defaults to None.
            api_name (str, optional): Name of the API endpoint. Defaults to None.
            user_id (int, optional): Database ID of the user. Defaults to None.
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
    def user_id(self) -> int:
        """int: Get the user's database identifier."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: int) -> None:
        """Set the user's database identifier."""
        self._user_id = value

    @property
    def logger(self):
        """loguru.Logger: Get the structured logger instance."""
        return self._logger

    @logger.setter
    def logger(self, value) -> None:
        """Set the structured logger instance."""
        self._logger = value

    @abstractmethod
    def run(self, request_dto: BaseModel) -> dict:
        """
        Execute the service's main business logic.

        This is the primary entry point for the service. Subclasses must
        implement this method to define their specific business operations.

        Args:
            request_dto (BaseModel): Pydantic model containing request data.

        Returns:
            dict: Result of the business operation, typically containing
                status information and any relevant data.

        Raises:
            IError: For business logic errors (subclass-specific).
            ValidationError: If request data validation fails.

        Example:
            >>> def run(self, request_dto: UserDTO) -> dict:
            ...     user = self.user_repo.find_by_email(request_dto.email)
            ...     if user:
            ...         raise BadInputError("Email already exists")
            ...     new_user = self.user_repo.create(request_dto)
            ...     return {"user_id": new_user.id, "status": "created"}
        """
        pass
