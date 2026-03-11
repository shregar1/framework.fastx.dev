"""
Error Abstraction Module.

This module defines the base error class that all custom application errors
should inherit from. It provides structured error handling with request
context for better debugging and monitoring.

Example:
    >>> class NotFoundError(IError):
    ...     def __init__(self, resource: str, urn: str = None):
    ...         super().__init__(urn=urn)
    ...         self.resource = resource
    ...         self.message = f"{resource} not found"
"""

from loguru import logger


class IError(BaseException):
    """
    Base exception class for all application-specific errors.

    The IError class provides a standardized error interface with built-in
    support for request context tracking and structured logging. All custom
    application exceptions should inherit from this class.

    Features:
        - Request context preservation (URN, user info)
        - Structured logging with error context
        - Consistent error handling across the application

    Attributes:
        urn (str): Unique Request Number for error tracing.
        user_urn (str): User's unique resource name when error occurred.
        api_name (str): Name of the API endpoint where error occurred.
        user_id (str): Database identifier of the user.
        logger: Structured logger bound with error context.

    Example:
        >>> class ValidationError(IError):
        ...     def __init__(self, field: str, message: str, **kwargs):
        ...         super().__init__(**kwargs)
        ...         self.field = field
        ...         self.message = message
        ...
        >>> raise ValidationError("email", "Invalid format", urn="req-123")
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ) -> None:
        """
        Initialize the error with request context.

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
    def user_id(self) -> str:
        """str: Get the user's database identifier."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
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
