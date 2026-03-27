"""DataI table name constants.

Re-exports Table from fast_db for backward compatibility.

Usage:
    >>> from constants.db.table import Table
    >>> class User(I):
    ...     __tablename__ = Table.USER
"""

from fast_db import Table

__all__ = ["Table"]
