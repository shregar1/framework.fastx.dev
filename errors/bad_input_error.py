"""
Bad Input Error Module.

This module defines the BadInputError exception for handling invalid
input scenarios. It is raised when user input fails validation or
doesn't meet expected criteria.

Usage:
    >>> from errors.bad_input_error import BadInputError
    >>> from http import HTTPStatus
    >>>
    >>> raise BadInputError(
    ...     responseMessage="Invalid email format",
    ...     responseKey="error_invalid_email",
    ...     httpStatusCode=HTTPStatus.BAD_REQUEST
    ... )
"""

from abstractions.error import IError


class BadInputError(IError):
    """
    Exception for invalid input errors.

    Raised when user-provided input fails validation, is malformed,
    or doesn't meet business requirements. This error typically
    results in a 400 Bad Request HTTP response.

    Attributes:
        responseMessage (str): Human-readable error description.
            Displayed to the end user.
        responseKey (str): Machine-readable key for programmatic handling.
            Used for i18n and client-side error handling.
        httpStatusCode (int): HTTP status code to return.
            Typically HTTPStatus.BAD_REQUEST (400).

    Inherits:
        IError: Base error class with request context and logging.

    Example:
        >>> from errors.bad_input_error import BadInputError
        >>> from http import HTTPStatus
        >>>
        >>> # Email validation failed
        >>> raise BadInputError(
        ...     responseMessage="Please provide a valid email address",
        ...     responseKey="error_invalid_email_format",
        ...     httpStatusCode=HTTPStatus.BAD_REQUEST
        ... )
        >>>
        >>> # Password too weak
        >>> raise BadInputError(
        ...     responseMessage="Password does not meet security requirements",
        ...     responseKey="error_weak_password",
        ...     httpStatusCode=HTTPStatus.BAD_REQUEST
        ... )

    Common Use Cases:
        - Invalid email format
        - Password validation failures
        - Missing required fields
        - Invalid data types
        - Business rule violations
        - Malformed request payloads
    """

    def __init__(
        self,
        responseMessage: str,
        responseKey: str,
        httpStatusCode: int
    ) -> None:
        """
        Initialize the BadInputError.

        Args:
            responseMessage (str): Human-readable error description.
            responseKey (str): Machine-readable error key for i18n.
            httpStatusCode (int): HTTP status code (typically 400).
        """
        super().__init__()
        self.responseMessage = responseMessage
        self.responseKey = responseKey
        self.httpStatusCode = httpStatusCode
