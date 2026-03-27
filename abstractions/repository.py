"""Repository Abstraction Module.

Provides the base IRepository interface for data access.
This module now works both with and without fast_database installed.

When fast_database is available, it re-exports from there for full functionality.
When fast_database is not available, it provides a minimal base implementation
that can be extended by the application.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypeVar

from core.utils.context import ContextMixin
from loguru import logger

# Try to import from fast_database for full functionality
try:
    from fast_database.persistence.repositories.abstraction import IRepository
    from constants.filter_operator import FilterOperator

    HAS_FAST_DATABASE = True
except ImportError:
    HAS_FAST_DATABASE = False

    # Provide minimal FilterOperator for compatibility
    class FilterOperator:
        """Filter operators for repository queries."""

        EQ = "eq"
        NE = "ne"
        LT = "lt"
        LE = "le"
        GT = "gt"
        GE = "ge"
        GTE = "ge"
        LTE = "le"
        IN = "in"
        NOT_IN = "not_in"
        LIKE = "like"
        ILIKE = "ilike"
        IS_NULL = "is_null"
        IS_NOT_NULL = "is_not_null"
        BETWEEN = "between"

    # Provide minimal IRepository base class
    T = TypeVar("T")

    class IRepository(ContextMixin):
        """Minimal base repository interface.

        This is a fallback implementation when fast_database is not installed.
        Applications should install pyfastmvc[platform] for full functionality.
        """

        def __init__(
            self, urn: Optional[str] = None, session: Any = None, **kwargs: Any
        ):
            """Initialize repository with context."""
            # Extract logger from kwargs if provided, otherwise use default
            logger_instance = kwargs.pop("logger", None) or logger
            super().__init__(urn=urn, logger=logger_instance, **kwargs)
            self._session = session

        @property
        def session(self) -> Any:
            """Get the database session."""
            return self._session

        @session.setter
        def session(self, value: Any) -> None:
            """Set the database session."""
            self._session = value

        def create_record(self, data: Dict[str, Any]) -> T:
            """Create a new record."""
            raise NotImplementedError(
                "Install pyfastmvc[platform] for full repository functionality"
            )

        def retrieve_record_by_id(self, id: Any) -> Optional[T]:
            """Retrieve a record by ID."""
            raise NotImplementedError(
                "Install pyfastmvc[platform] for full repository functionality"
            )

        def update_record(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
            """Update a record by ID."""
            raise NotImplementedError(
                "Install pyfastmvc[platform] for full repository functionality"
            )

        def delete_record(self, id: Any) -> bool:
            """Delete a record by ID."""
            raise NotImplementedError(
                "Install pyfastmvc[platform] for full repository functionality"
            )


__all__ = ["IRepository", "FilterOperator"]
