"""
User Login Service Dependency Module.

This module provides FastAPI dependency injection for UserLoginService.
It returns a factory function that creates service instances with
request-specific context.

Usage:
    >>> from fastapi import Depends
    >>> from dependencies.services.user.login import UserLoginServiceDependency
    >>>
    >>> async def login(
    ...     service_factory: Callable = Depends(UserLoginServiceDependency.derive)
    ... ):
    ...     service = service_factory(urn=urn, jwt_utility=jwt, ...)
    ...     result = await service.run(request_dto)
"""

from collections.abc import Callable

from abstractions.dependency import IDependency
from services.user.login import UserLoginService
from start_utils import logger


class UserLoginServiceDependency(IDependency):
    """
    FastAPI dependency provider for UserLoginService.

    This class provides a factory pattern for creating UserLoginService
    instances with request-specific context and dependencies.

    Inherits from IDependency to follow the application's dependency
    abstraction pattern.

    The factory pattern enables:
        - Request context propagation (URN, user info)
        - Proper dependency injection of utilities and repositories
        - Easy testing with mock factories

    Example:
        >>> from dependencies.services.user.login import UserLoginServiceDependency
        >>>
        >>> service_factory = Depends(UserLoginServiceDependency.derive)
        >>> service = service_factory(
        ...     urn=request.state.urn,
        ...     user_urn=user_urn,
        ...     api_name="LOGIN",
        ...     user_id=None,
        ...     jwt_utility=jwt_util,
        ...     user_repository=user_repo
        ... )
        >>> result = await service.run(credentials_dto)
    """

    @staticmethod
    def derive() -> Callable:
        """
        Provide a factory function for creating UserLoginService instances.

        Returns a factory that accepts request context and dependencies,
        returning a configured UserLoginService instance.

        Returns:
            Callable: Factory function with signature:
                factory(urn, user_urn, api_name, user_id, jwt_utility,
                       user_repository) -> UserLoginService

        Factory Parameters:
            urn (str): Unique Request Number for tracing.
            user_urn (str): User's unique resource name.
            api_name (str): Name of the API endpoint.
            user_id (str): User's database identifier.
            jwt_utility (JWTUtility): JWT token utility instance.
            user_repository (UserRepository): User data access instance.

        Example:
            >>> factory = UserLoginServiceDependency.derive()
            >>> service = factory(
            ...     urn="urn:req:123",
            ...     user_urn=None,
            ...     api_name="LOGIN",
            ...     user_id=None,
            ...     jwt_utility=jwt_util,
            ...     user_repository=user_repo
            ... )
        """
        logger.debug("UserLoginServiceDependency factory created")

        def factory(
            urn: str,
            user_urn: str,
            api_name: str,
            user_id: str,
            jwt_utility,
            user_repository,
        ) -> UserLoginService:
            """
            Create a UserLoginService instance with dependencies.

            Args:
                urn (str): Unique Request Number for tracing.
                user_urn (str): User's unique resource name.
                api_name (str): Name of the API endpoint.
                user_id (str): User's database identifier.
                jwt_utility: JWT utility for token generation.
                user_repository: Repository for user data access.

            Returns:
                UserLoginService: Configured service instance.
            """
            logger.info("Instantiating UserLoginService")
            return UserLoginService(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
                user_repository=user_repository,
                jwt_utility=jwt_utility,
            )

        return factory
