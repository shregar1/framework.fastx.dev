"""
Base Response DTO Module.

This module defines the standard response structure for all API endpoints.
Every API response should use BaseResponseDTO to ensure consistent
response formatting across the application.

Usage:
    >>> from dtos.responses.base import BaseResponseDTO
    >>> from constants.api_status import APIStatus
    >>>
    >>> response = BaseResponseDTO(
    ...     transactionUrn="urn:req:123",
    ...     status=APIStatus.SUCCESS,
    ...     responseMessage="User created successfully",
    ...     responseKey="success_user_created",
    ...     data={"user_id": "user-456"}
    ... )
"""


from pydantic import BaseModel


class BaseResponseDTO(BaseModel):
    """
    Standard response DTO for all API endpoints.

    This DTO defines the consistent response structure used across
    all API endpoints in the FastMVC application. It includes
    transaction tracking, status indication, and flexible data payloads.

    Attributes:
        transactionUrn (str): Unique identifier for the request/transaction.
            Used for distributed tracing and log correlation.
        status (str): Status of the operation ("SUCCESS" or "FAILED").
            Use constants from constants.api_status.APIStatus.
        responseMessage (str): Human-readable message describing the result.
            Suitable for display to end users.
        responseKey (str): Machine-readable key for programmatic handling.
            Useful for i18n and client-side error handling.
        data (List | Dict, optional): Main response payload on success.
            Contains the requested data or created resource details.
        errors (List | Dict, optional): Error details on failure.
            Contains validation errors or additional error context.

    Example (Success):
        >>> response = BaseResponseDTO(
        ...     transactionUrn="urn:req:abc123",
        ...     status="SUCCESS",
        ...     responseMessage="Login successful",
        ...     responseKey="success_login",
        ...     data={
        ...         "token": "eyJhbG...",
        ...         "user": {"id": "123", "email": "user@example.com"}
        ...     }
        ... )

    Example (Error):
        >>> response = BaseResponseDTO(
        ...     transactionUrn="urn:req:abc123",
        ...     status="FAILED",
        ...     responseMessage="Invalid credentials",
        ...     responseKey="error_invalid_credentials",
        ...     data={},
        ...     errors=[{"field": "password", "message": "Incorrect password"}]
        ... )

    JSON Output:
        ```json
        {
            "transactionUrn": "urn:req:abc123",
            "status": "SUCCESS",
            "responseMessage": "Operation completed",
            "responseKey": "success_operation",
            "data": {...},
            "errors": null
        }
        ```

    Note:
        Controllers use DictionaryUtility.convert_dict_keys_to_camel_case()
        to convert snake_case field names to camelCase in the final response.
    """

    transactionUrn: str
    """Unique identifier for request tracing and correlation."""

    status: str
    """Operation status: "SUCCESS" or "FAILED"."""

    responseMessage: str
    """Human-readable message describing the result."""

    responseKey: str
    """Machine-readable key for programmatic handling and i18n."""

    data: list | dict | None = None
    """Main response payload (success data or empty dict on error)."""

    errors: list | dict | None = None
    """Error details when status is FAILED."""
