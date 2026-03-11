"""
Database Dependency Module.

This module provides FastAPI dependency injection for SQLAlchemy database
sessions. It enables controllers to access the shared database connection.

Usage:
    >>> from fastapi import Depends
    >>> from dependencies.db import DBDependency
    >>>
    >>> async def my_endpoint(session: Session = Depends(DBDependency.derive)):
    ...     users = session.query(User).all()
"""

from sqlalchemy.orm import Session

from start_utils import db_session, logger


class DBDependency:
    """
    FastAPI dependency provider for SQLAlchemy database sessions.

    This class provides a static method that returns the shared database
    session instance for use in FastAPI dependency injection.

    The database session is initialized once at application startup
    (in start_utils) and manages connections via SQLAlchemy's session pool.

    Example:
        >>> from fastapi import Depends
        >>> from dependencies.db import DBDependency
        >>>
        >>> @router.get("/users")
        >>> async def get_users(
        ...     session: Session = Depends(DBDependency.derive)
        ... ):
        ...     users = session.query(User).all()
        ...     return {"users": users}

    Note:
        The session handles connection pooling internally.
        Transactions are managed per-request.
    """

    @staticmethod
    def derive() -> Session:
        """
        Provide the shared SQLAlchemy database session.

        This method is designed to be used with FastAPI's Depends()
        for dependency injection.

        Returns:
            Session: The SQLAlchemy session instance for database operations.

        Example:
            >>> session = DBDependency.derive()
            >>> user = session.query(User).filter_by(id=1).first()
        """
        logger.debug("DBDependency: returning db_session instance")
        return db_session
