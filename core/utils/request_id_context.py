"""Request ID Context Management.

Provides context variables for tracking request IDs across async contexts.
"""

from contextvars import ContextVar
from typing import Optional

# Context variable for storing the current request ID
_request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIdContext:
    """Manager for request ID context variables.

    This class provides a way to store and retrieve the current request ID
    in an async-safe manner using context variables.

    Example:
        >>> RequestIdContext.set("req-123")
        >>> current_id = RequestIdContext.get()
        >>> print(current_id)  # "req-123"

    """

    @staticmethod
    def get() -> Optional[str]:
        """Get the current request ID from context."""
        return _request_id_var.get()

    @staticmethod
    def set(request_id: str) -> None:
        """Set the current request ID in context."""
        _request_id_var.set(request_id)

    @staticmethod
    def reset() -> None:
        """Reset the request ID context."""
        _request_id_var.set(None)
