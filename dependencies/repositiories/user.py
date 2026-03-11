"""
User Repository Dependency Module.

This module provides FastAPI dependency injection for UserRepository.
It returns a factory function that creates repository instances with
request-specific context.

Usage:
    >>> from fastapi import Depends
    >>> from dependencies.repositiories.user import UserRepositoryDependency
    >>>
    >>> async def my_endpoint(
    ...     repo_factory: Callable = Depends(UserRepositoryDependency.derive)
    ... ):
    ...     repo = repo_factory(urn=urn, session=session, ...)
    ...     user = repo.find_by_email("user@example.com")
"""

from collections.abc import Callable

from repositories.user import UserRepository
from start_utils import logger


class UserRepositoryDependency:
    """
    FastAPI dependency provider for UserRepository.

    This class provides a factory pattern for creating UserRepository
    instances with request-specific context (URN, user info, session).

    The factory pattern is used because:
        - Repository needs request context (URN for logging/tracing)
        - Database session is request-scoped
        - Allows proper dependency injection testing

    Example:
        >>> from fastapi import Depends
        >>> from dependencies.repositiories.user import UserRepositoryDependency
        >>>
        >>> @router.get("/user/{user_id}")
        >>> async def get_user(
        ...     user_id: str,
        ...     session: Session = Depends(DBDependency.derive),
        ...     repo_factory: Callable = Depends(UserRepositoryDependency.derive)
        ... ):
        ...     repo = repo_factory(
        ...         urn=request.state.urn,
        ...         user_urn=None,
        ...         api_name="GET_USER",
        ...         session=session,
        ...         user_id=user_id
        ...     )
        ...     return repo.retrieve_record_by_id(user_id)
    """

    @staticmethod
    def derive() -> Callable:
        """
        Provide a factory function for creating UserRepository instances.

        Returns a factory that accepts request context and returns a
        configured UserRepository instance.

        Returns:
            Callable: Factory function with signature:
                factory(urn, user_urn, api_name, session, user_id) -> UserRepository

        Factory Parameters:
            urn (str): Unique Request Number for tracing.
            user_urn (str): User's unique resource name.
            api_name (str): Name of the API endpoint.
            session (Session): SQLAlchemy database session.
            user_id (str): User's database identifier.

        Example:
            >>> factory = UserRepositoryDependency.derive()
            >>> repo = factory(
            ...     urn="urn:req:123",
            ...     user_urn="urn:user:456",
            ...     api_name="LOGIN",
            ...     session=db_session,
            ...     user_id="user-789"
            ... )
        """
        logger.debug("UserRepositoryDependency factory created")

        def factory(
            urn: str,
            user_urn: str,
            api_name: str,
            session,
            user_id: str,
        ) -> UserRepository:
            """
            Create a UserRepository instance with request context.

            Args:
                urn (str): Unique Request Number for tracing.
                user_urn (str): User's unique resource name.
                api_name (str): Name of the API endpoint.
                session: SQLAlchemy database session.
                user_id (str): User's database identifier.

            Returns:
                UserRepository: Configured repository instance.
            """
            logger.info("Instantiating UserRepository")
            return UserRepository(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                session=session,
                user_id=user_id,
            )

        return factory
