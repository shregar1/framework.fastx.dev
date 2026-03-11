"""
Payload Type Constants Module.

This module defines constants for request and response payload types.
These are used throughout the application to specify content types
and handle different data formats consistently.

Usage:
    >>> from constants.payload_type import RequestPayloadType, ResponsePayloadType
    >>> if request_type == RequestPayloadType.JSON:
    ...     data = request.json()
"""

from typing import Final


class RequestPayloadType:
    """
    Constants for supported request payload types.

    These constants identify how incoming request data should be parsed
    and processed by the application.

    Attributes:
        JSON (str): JSON-encoded request body (application/json).
        FORM (str): Form-encoded data (application/x-www-form-urlencoded).
        FILES (str): Multipart file uploads (multipart/form-data).
        QUERY (str): URL query parameters.

    Example:
        >>> from constants.payload_type import RequestPayloadType
        >>>
        >>> def parse_request(payload_type: str, request):
        ...     if payload_type == RequestPayloadType.JSON:
        ...         return request.json()
        ...     elif payload_type == RequestPayloadType.FORM:
        ...         return request.form()
        ...     elif payload_type == RequestPayloadType.QUERY:
        ...         return dict(request.query_params)
    """

    JSON: Final[str] = "json"
    """JSON-encoded request body (Content-Type: application/json)."""

    FORM: Final[str] = "form"
    """Form-encoded data (Content-Type: application/x-www-form-urlencoded)."""

    FILES: Final[str] = "files"
    """Multipart file uploads (Content-Type: multipart/form-data)."""

    QUERY: Final[str] = "query"
    """URL query string parameters (?key=value&...)."""


class ResponsePayloadType:
    """
    Constants for supported response payload types.

    These constants identify how outgoing response data should be
    formatted and serialized.

    Attributes:
        JSON (str): JSON-encoded response (application/json).
        TEXT (str): Plain text response (text/plain).
        CONTENT (str): Binary/raw content response.

    Example:
        >>> from constants.payload_type import ResponsePayloadType
        >>>
        >>> def format_response(payload_type: str, data):
        ...     if payload_type == ResponsePayloadType.JSON:
        ...         return JSONResponse(data)
        ...     elif payload_type == ResponsePayloadType.TEXT:
        ...         return PlainTextResponse(str(data))

    Note:
        The class name has a typo (ResponsePlayloadType -> ResponsePayloadType)
        that is preserved for backward compatibility.
    """

    JSON: Final[str] = "json"
    """JSON-encoded response (Content-Type: application/json)."""

    TEXT: Final[str] = "text"
    """Plain text response (Content-Type: text/plain)."""

    CONTENT: Final[str] = "content"
    """Binary or raw content response (various Content-Types)."""
