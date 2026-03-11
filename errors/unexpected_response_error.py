"""
Unexpected Response Error Module.

This module defines the UnexpectedResponseError exception for handling
unexpected scenarios in the application. It is raised when an operation
produces an unexpected result or encounters an unforeseen condition.

Usage:
    >>> from errors.unexpected_response_error import UnexpectedResponseError
    >>> from http import HTTPStatus
    >>>
    >>> raise UnexpectedResponseError(
    ...     responseMessage="An unexpected error occurred",
    ...     responseKey="error_unexpected",
    ...     httpStatusCode=HTTPStatus.INTERNAL_SERVER_ERROR
    ... )
"""

from abstractions.error import IError


class UnexpectedResponseError(IError):
    """
    Exception for unexpected response/behavior errors.

    Raised when an operation encounters an unexpected condition or
    produces an unexpected result. This can include external service
    failures, data inconsistencies, or other unforeseen issues.

    Attributes:
        responseMessage (str): Human-readable error description.
            Displayed to the end user.
        responseKey (str): Machine-readable key for programmatic handling.
            Used for i18n and client-side error handling.
        httpStatusCode (int): HTTP status code to return.
            Varies based on the specific error condition.

    Inherits:
        IError: Base error class with request context and logging.

    Example:
        >>> from errors.unexpected_response_error import UnexpectedResponseError
        >>> from http import HTTPStatus
        >>>
        >>> # External service returned unexpected response
        >>> raise UnexpectedResponseError(
        ...     responseMessage="External service returned an invalid response",
        ...     responseKey="error_external_service_failure",
        ...     httpStatusCode=HTTPStatus.BAD_GATEWAY
        ... )
        >>>
        >>> # Data inconsistency
        >>> raise UnexpectedResponseError(
        ...     responseMessage="Data inconsistency detected",
        ...     responseKey="error_data_inconsistency",
        ...     httpStatusCode=HTTPStatus.INTERNAL_SERVER_ERROR
        ... )

    Common Use Cases:
        - External API failures
        - Database inconsistencies
        - Unexpected null values
        - Invalid state transitions
        - Configuration errors
        - Third-party service errors
    """

    def __init__(
        self,
        responseMessage: str,
        responseKey: str,
        httpStatusCode: int
    ) -> None:
        """
        Initialize the UnexpectedResponseError.

        Args:
            responseMessage (str): Human-readable error description.
            responseKey (str): Machine-readable error key for i18n.
            httpStatusCode (int): HTTP status code.
        """
        super().__init__()
        self.responseMessage = responseMessage
        self.responseKey = responseKey
        self.httpStatusCode = httpStatusCode
