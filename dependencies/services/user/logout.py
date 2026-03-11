"""
User Logout Service Dependency Module.

This module provides FastAPI dependency injection for UserLogoutService.
It returns a factory function that creates service instances with
request-specific context.

Usage:
    >>> from fastapi import Depends
    >>> from dependencies.services.user.logout import UserLogoutServiceDependency
    >>>
    >>> async def logout(
    ...     service_factory: Callable = Depends(UserLogoutServiceDependency.derive)
    ... ):
    ...     service = service_factory(urn=urn, jwt_utility=jwt, ...)
    ...     result = await service.run()
"""

from collections.abc import Callable

from abstractions.dependency import IDependency
from services.user.logout import UserLogoutService
from start_utils import logger


class UserLogoutServiceDependency(IDependency):
    """
    FastAPI dependency provider for UserLogoutService.

    This class provides a factory pattern for creating UserLogoutService
    instances with request-specific context and dependencies.

    Inherits from IDependency to follow the application's dependency
    abstraction pattern.

    The factory pattern enables:
        - Request context propagation (URN, user info)
        - Proper dependency injection of utilities and repositories
        - Easy testing with mock factories

    Example:
        >>> from dependencies.services.user.logout import UserLogoutServiceDependency
        >>>
        >>> service_factory = Depends(UserLogoutServiceDependency.derive)
        >>> service = service_factory(
        ...     urn=request.state.urn,
        ...     user_urn=user_urn,
        ...     api_name="LOGOUT",
        ...     user_id=user_id,
        ...     jwt_utility=jwt_util,
        ...     user_repository=user_repo
        ... )
        >>> result = await service.run()
    """

    @staticmethod
    def derive() -> Callable:
        """
        Provide a factory function for creating UserLogoutService instances.

        Returns a factory that accepts request context and dependencies,
        returning a configured UserLogoutService instance.

        Returns:
            Callable: Factory function with signature:
                factory(urn, user_urn, api_name, user_id, jwt_utility,
                       user_repository) -> UserLogoutService

        Factory Parameters:
            urn (str): Unique Request Number for tracing.
            user_urn (str): User's unique resource name.
            api_name (str): Name of the API endpoint.
            user_id (str): User's database identifier.
            jwt_utility (JWTUtility): JWT token utility instance.
            user_repository (UserRepository): User data access instance.

        Example:
            >>> factory = UserLogoutServiceDependency.derive()
            >>> service = factory(
            ...     urn="urn:req:123",
            ...     user_urn="urn:user:456",
            ...     api_name="LOGOUT",
            ...     user_id="user-789",
            ...     jwt_utility=jwt_util,
            ...     user_repository=user_repo
            ... )
        """
        logger.debug("UserLogoutServiceDependency factory created")

        def factory(
            urn: str,
            user_urn: str,
            api_name: str,
            user_id: str,
            jwt_utility,
            user_repository,
        ) -> UserLogoutService:
            """
            Create a UserLogoutService instance with dependencies.

            Args:
                urn (str): Unique Request Number for tracing.
                user_urn (str): User's unique resource name.
                api_name (str): Name of the API endpoint.
                user_id (str): User's database identifier.
                jwt_utility: JWT utility for token operations.
                user_repository: Repository for user data access.

            Returns:
                UserLogoutService: Configured service instance.
            """
            logger.info("Instantiating UserLogoutService")
            return UserLogoutService(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
                user_repository=user_repository,
                jwt_utility=jwt_utility,
            )

        return factory
