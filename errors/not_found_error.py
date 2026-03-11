"""
Not Found Error Module.

This module defines the NotFoundError exception for handling resource
not found scenarios. It is raised when a requested resource doesn't
exist in the system.

Usage:
    >>> from errors.not_found_error import NotFoundError
    >>> from http import HTTPStatus
    >>>
    >>> raise NotFoundError(
    ...     responseMessage="User not found",
    ...     responseKey="error_user_not_found",
    ...     httpStatusCode=HTTPStatus.NOT_FOUND
    ... )
"""

from abstractions.error import IError


class NotFoundError(IError):
    """
    Exception for resource not found errors.

    Raised when a requested resource (user, record, file, etc.) cannot
    be found in the system. This error typically results in a
    404 Not Found HTTP response.

    Attributes:
        responseMessage (str): Human-readable error description.
            Displayed to the end user.
        responseKey (str): Machine-readable key for programmatic handling.
            Used for i18n and client-side error handling.
        httpStatusCode (int): HTTP status code to return.
            Typically HTTPStatus.NOT_FOUND (404).

    Inherits:
        IError: Base error class with request context and logging.

    Example:
        >>> from errors.not_found_error import NotFoundError
        >>> from http import HTTPStatus
        >>>
        >>> # User not found during login
        >>> raise NotFoundError(
        ...     responseMessage="No account found with this email",
        ...     responseKey="error_user_not_found",
        ...     httpStatusCode=HTTPStatus.NOT_FOUND
        ... )
        >>>
        >>> # Resource not found
        >>> raise NotFoundError(
        ...     responseMessage="The requested resource does not exist",
        ...     responseKey="error_resource_not_found",
        ...     httpStatusCode=HTTPStatus.NOT_FOUND
        ... )

    Common Use Cases:
        - User account not found
        - Database record not found
        - File or resource not found
        - API endpoint resource missing
        - Invalid ID or URN references
    """

    def __init__(
        self,
        responseMessage: str,
        responseKey: str,
        httpStatusCode: int
    ) -> None:
        """
        Initialize the NotFoundError.

        Args:
            responseMessage (str): Human-readable error description.
            responseKey (str): Machine-readable error key for i18n.
            httpStatusCode (int): HTTP status code (typically 404).
        """
        super().__init__()
        self.responseMessage = responseMessage
        self.responseKey = responseKey
        self.httpStatusCode = httpStatusCode
