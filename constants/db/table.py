"""
Database Table Name Constants Module.

This module defines constants for database table names. Using these
constants instead of string literals prevents typos and enables
easy refactoring of table names.

Usage:
    >>> from constants.db.table import Table
    >>> class User(Base):
    ...     __tablename__ = Table.USER
"""

from typing import Final


class Table:
    """
    Database table name constants.

    This class provides centralized constants for all database table names
    used in the application. Using these constants ensures consistency
    and makes table name changes easier to manage.

    Attributes:
        USER (str): Table name for user accounts.

    Example:
        >>> from constants.db.table import Table
        >>> from sqlalchemy import Column, Integer, String
        >>> from sqlalchemy.ext.declarative import declarative_base
        >>>
        >>> Base = declarative_base()
        >>>
        >>> class User(Base):
        ...     __tablename__ = Table.USER
        ...     id = Column(Integer, primary_key=True)
        ...     email = Column(String, unique=True)

    Note:
        Add new table name constants here as the application grows.
        Follow the pattern: TABLE_NAME: Final[str] = "table_name"
    """

    USER: Final[str] = "user"
    """Table name for user accounts and authentication data."""
