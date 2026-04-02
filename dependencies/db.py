"""DataI Dependency Module.

Re-exports DBDependency from fast_db for backward compatibility.

Usage:
    >>> from fastapi import Depends
    >>> from dependencies.db import DBDependency
    >>>
    >>> async def my_endpoint(session: Session = Depends(DBDependency.derive)):
    ...     users = session.query(User).all()
"""

from typing import Any, Optional

try:
    from dependencies.db import DatabaseDependency
except ImportError:

    class _DatabaseDependencyFallback:
        """Fallback DatabaseDependency when fast_database is not installed."""

        @staticmethod
        def derive() -> Any:
            """Raise informative error about missing dependency."""
            raise ImportError(
                "fast_db is required for database dependencies. "
                "Install with: pip install fastx-mvc[platform]"
            )

    DatabaseDependency = _DatabaseDependencyFallback  # type: ignore

__all__ = ["DatabaseDependency"]
