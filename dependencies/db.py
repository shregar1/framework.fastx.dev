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

# Optional fast_db dependency
try:
    from fast_db import DBDependency
except ImportError:
    # Fallback when fast_db is not installed
    class _DBDependencyFallback:
        """Fallback DBDependency when fast_db is not installed."""

        @staticmethod
        def derive() -> Any:
            """Raise informative error about missing dependency."""
            raise ImportError(
                "fast_db is required for database dependencies. "
                "Install with: pip install pyfastmvc[platform]"
            )

    DBDependency = _DBDependencyFallback  # type: ignore

__all__ = ["DBDependency"]
