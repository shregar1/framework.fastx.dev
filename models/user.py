"""
User Model Module.

This module defines the SQLAlchemy ORM model for the user table,
which stores user accounts and authentication information.

Table: user

Usage:
    >>> from models.user import User
    >>> from sqlalchemy.orm import Session
    >>>
    >>> # Create a new user
    >>> user = User(
    ...     urn="urn:user:abc123",
    ...     email="user@example.com",
    ...     password="hashed_password",
    ...     created_by=1
    ... )
    >>> session.add(user)
    >>> session.commit()
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Index,
    String,
)

from constants.db.table import Table
from models import Base


class User(Base):
    """
    SQLAlchemy ORM model for user accounts.

    This model represents the user table in the database, storing
    account information, authentication status, and audit fields.

    Table Name:
        user (from constants.db.table.Table.USER)

    Attributes:
        id (BigInteger): Auto-generated primary key.
        urn (str): Unique Resource Name for the user (e.g., "urn:user:abc123").
            Used for external references and API responses.
        email (str): User's email address. Must be unique.
        password (str): Bcrypt-hashed password. Never store plaintext.
        is_deleted (bool): Soft delete flag. True = user is deleted.
        last_login (datetime): Timestamp of last successful login.
        is_logged_in (bool): Current login status. Used for session management.
        created_on (datetime): When the record was created.
        created_by (BigInteger): User ID who created this record.
        updated_on (datetime): When the record was last updated.
        updated_by (BigInteger): User ID who last updated this record.

    Indexes:
        - ix_user_urn: Index on urn for fast lookups
        - ix_user_email: Unique index on email for uniqueness and lookups
        - ix_user_created_on: Index on created_on for sorting

    Example:
        >>> from models.user import User
        >>> from datetime import datetime
        >>>
        >>> # Create a new user
        >>> new_user = User(
        ...     urn="urn:user:01ARZ3NDEKTSV4RRFFQ69G5FAV",
        ...     email="john.doe@example.com",
        ...     password="$2b$12$...",  # Bcrypt hash
        ...     is_deleted=False,
        ...     is_logged_in=False,
        ...     created_on=datetime.utcnow(),
        ...     created_by=1  # System user or admin
        ... )
        >>>
        >>> # Query users
        >>> active_users = session.query(User).filter(
        ...     User.is_deleted == False,
        ...     User.is_logged_in == True
        ... ).all()

    Note:
        - Passwords must be hashed before storage (use bcrypt)
        - Use soft deletes (is_deleted=True) instead of hard deletes
        - The urn field should be generated using ULID or UUID
    """

    __tablename__ = Table.USER
    """Database table name from constants."""

    id = Column(BigInteger, primary_key=True)
    """Auto-incrementing primary key."""

    urn = Column(String, nullable=False, index=True)
    """Unique Resource Name for external identification."""

    email = Column(String, unique=True, nullable=False, index=True)
    """User's email address (unique constraint enforced)."""

    password = Column(String, nullable=False)
    """Bcrypt-hashed password (never store plaintext)."""

    is_deleted = Column(Boolean, nullable=False, default=False)
    """Soft delete flag. True indicates the user is deleted."""

    last_login = Column(DateTime(timezone=True))
    """Timestamp of the user's last successful login."""

    is_logged_in = Column(Boolean, nullable=False, default=False)
    """Current login status for session management."""

    created_on = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        default=datetime.utcnow
    )
    """Record creation timestamp (auto-set on insert)."""

    created_by = Column(BigInteger, nullable=False)
    """User ID of the creator (1 for system/self-registration)."""

    updated_on = Column(DateTime(timezone=True))
    """Timestamp of the last update (null if never updated)."""

    updated_by = Column(BigInteger)
    """User ID of the last updater."""


# Additional indexes for optimized queries
Index('ix_user_urn', User.urn)
Index('ix_user_email', User.email, unique=True)
Index('ix_user_created_on', User.created_on)
