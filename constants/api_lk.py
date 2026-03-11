"""
API Logical Keys (APILK) Module.

This module defines logical key constants for identifying API operations
throughout the application. These keys are used for routing, logging,
metrics collection, and operation identification.

Usage:
    >>> from constants.api_lk import APILK
    >>> if api_name == APILK.LOGIN:
    ...     # Handle login-specific logic
    ...     pass
"""

from typing import Final


class APILK:
    """
    API Logical Keys for operation identification.

    These constants provide a centralized, type-safe way to identify
    different API operations. Using these keys instead of string literals
    prevents typos and enables IDE autocompletion.

    Attributes:
        LOGIN (str): Logical key for user login operations.
        REGISTRATION (str): Logical key for user registration operations.
        LOGOUT (str): Logical key for user logout operations.

    Example:
        >>> from constants.api_lk import APILK
        >>>
        >>> def process_request(api_name: str):
        ...     if api_name == APILK.LOGIN:
        ...         return handle_login()
        ...     elif api_name == APILK.REGISTRATION:
        ...         return handle_registration()

    Note:
        All keys are defined as Final[str] to prevent accidental modification
        and enable static type checking.
    """

    LOGIN: Final[str] = "LOGIN"
    """Logical key for user authentication/login operations."""

    REGISTRATION: Final[str] = "REGISTRATION"
    """Logical key for new user registration operations."""

    LOGOUT: Final[str] = "LOGOUT"
    """Logical key for user session termination operations."""
