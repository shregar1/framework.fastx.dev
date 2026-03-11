"""
API Status Constants Module.

This module defines status constants for API responses. These standardized
status values ensure consistent response formatting across all endpoints.

Usage:
    >>> from constants.api_status import APIStatus
    >>> return {"status": APIStatus.SUCCESS, "data": result}
"""

from typing import Final


class APIStatus:
    """
    Standardized status values for API responses.

    These constants provide consistent status indicators for API responses,
    making it easier for clients to parse and handle different response states.

    Attributes:
        SUCCESS (str): Indicates the operation completed successfully.
        FAILED (str): Indicates the operation failed.
        PENDING (str): Indicates the operation is still in progress.

    Example:
        >>> from constants.api_status import APIStatus
        >>>
        >>> def create_response(success: bool, data: dict) -> dict:
        ...     return {
        ...         "status": APIStatus.SUCCESS if success else APIStatus.FAILED,
        ...         "data": data
        ...     }

    Response Format:
        ```json
        {
            "status": "SUCCESS",
            "data": {...},
            "message": "Operation completed"
        }
        ```

    Note:
        These status values are distinct from HTTP status codes. HTTP codes
        indicate transport-level success/failure, while these indicate
        business-logic success/failure.
    """

    SUCCESS: Final[str] = "SUCCESS"
    """Operation completed successfully."""

    FAILED: Final[str] = "FAILED"
    """Operation failed due to an error or validation issue."""

    PENDING: Final[str] = "PENDING"
    """Operation is in progress or awaiting completion."""
