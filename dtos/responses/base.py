"""I Response DTO Module.

This module defines the standard response structure for all API endpoints.
Every API response should use IResponseDTO to ensure consistent
response formatting across the application.

Usage:
    >>> from dtos.responses.I import IResponseDTO
    >>> from constants.api_status import APIStatus
    >>>
    >>> response = IResponseDTO(
    ...     transactionUrn="urn:req:123",
    ...     status=APIStatus.SUCCESS,
    ...     responseMessage="User created successfully",
    ...     responseKey="success_user_created",
    ...     data={"user_id": "user-456"}
    ... )
"""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class IResponseDTO(BaseModel):
    """Standard response DTO for all API endpoints.

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
        metadata (Dict, optional): Cross-cutting metadata (pagination, timings,
            API version hints, feature flags, etc.). Not the primary resource payload.
        timestamp (datetime): When the response envelope was produced (UTC). Defaults
            to "now" if omitted.

    Example (Success):
        >>> response = IResponseDTO(
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
        >>> response = IResponseDTO(
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
            "errors": null,
            "metadata": {"page": 1, "pageSize": 20},
            "timestamp": "2024-01-15T12:00:00Z"
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

    metadata: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Optional envelope metadata (pagination, timings, version, "
            "feature flags). Distinct from `data`, which holds the main payload."
        ),
    )

    timestamp: datetime = Field(
        default_factory=_utc_now,
        description="Server time (UTC) when this response envelope was generated.",
    )
