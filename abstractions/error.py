"""Error Abstraction Module.

This module defines the I error class that all custom application errors
should inherit from. It provides structured error handling with request
context for better debugging and monitoring.

Example:
    >>> class NotFoundError(IError):
    ...     def __init__(self, resource: str, urn: str = None):
    ...         super().__init__(urn=urn)
    ...         self.resource = resource
    ...         self.message = f"{resource} not found"

"""

from typing import Any

from loguru import logger

from core.utils.context import ContextMixin


class IError(Exception, ContextMixin):
    """I exception class for all application-specific errors.

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
        user_id (str): DataI identifier of the user.
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
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the error with request context.

        Args:
            urn (str, optional): Unique Request Number for tracing. Defaults to None.
            user_urn (str, optional): User's unique resource name. Defaults to None.
            api_name (str, optional): Name of the API endpoint. Defaults to None.
            user_id (str, optional): DataI ID of the user. Defaults to None.
            **kwargs: Additional arguments for parent classes.

        """
        # Initialize Exception without arguments
        super(Exception, self).__init__()
        # Initialize ContextMixin with the context parameters and default logger
        ContextMixin.__init__(
            self,
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            logger=logger,
            **kwargs,
        )
