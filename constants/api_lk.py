"""API Logical Keys (APILK) Module.

This module defines logical key constants for identifying API operations
throughout the application. These keys are used for routing, logging,
metrics collection, and operation identification.

Route metadata for HTTP handlers lives in :class:`APIDefinition` entries
nested under :class:`APILK` (e.g. :attr:`APILK.Product.FETCH`).

Usage:
    >>> from constants.api_lk import APILK
    >>> if api_name == APILK.LOGIN:
    ...     # Handle login-specific logic
    ...     pass
"""

from http import HTTPStatus
from typing import Final, NamedTuple


class APIDefinition(NamedTuple):
    """Metadata for a single HTTP route (one logical API, one method).

    ``NAME`` and ``METHOD`` are required. ``PATH`` is the path segment on the
    parent :class:`~fastapi.APIRouter` (e.g. ``\"/fetch\"``).

    ``SUMMARY``, ``TAGS``, and ``STATUS_CODE`` may be ``None`` when unused.

    Attributes:
        NAME: FastAPI operation name (``name=`` on the route).
        METHOD: Upper-case HTTP verb (e.g. ``\"GET\"``); exactly one method per API.
        PATH: Path relative to the parent router.
        SUMMARY: OpenAPI summary, or None.
        TAGS: Route tags, or None.
        STATUS_CODE: Response status code, or None for framework default.

    """

    NAME: str
    METHOD: str
    PATH: str
    SUMMARY: str | None = None
    TAGS: tuple[str, ...] | None = None
    STATUS_CODE: int | None = None


class APILK:
    """API Logical Keys for operation identification.

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

    REFRESH: Final[str] = "REFRESH"
    """Logical key for token refresh operations."""

    class PRODUCT:
        """Route definitions for ``apis/product/...``."""

        FETCH: Final[APIDefinition] = APIDefinition(
            NAME="apis_product_fetch",
            METHOD="GET",
            PATH="/fetch",
            SUMMARY="Product fetch (apis/product/fetch)",
            TAGS=("apis-product-fetch",),
            STATUS_CODE=HTTPStatus.OK,
        )
