"""
User Registration Service Dependency Module.

This module provides FastAPI dependency injection for UserRegistrationService.
It returns a factory function that creates service instances with
request-specific context.

Usage:
    >>> from fastapi import Depends
    >>> from dependencies.services.user.register import UserRegistrationServiceDependency
    >>>
    >>> async def register(
    ...     service_factory: Callable = Depends(UserRegistrationServiceDependency.derive)
    ... ):
    ...     service = service_factory(urn=urn, user_repository=repo, ...)
    ...     result = await service.run(request_dto)
"""

from collections.abc import Callable

from abstractions.dependency import IDependency
from services.user.registration import UserRegistrationService
from start_utils import logger


class UserRegistrationServiceDependency(IDependency):
    """
    FastAPI dependency provider for UserRegistrationService.

    This class provides a factory pattern for creating UserRegistrationService
    instances with request-specific context and dependencies.

    Inherits from IDependency to follow the application's dependency
    abstraction pattern.

    The factory pattern enables:
        - Request context propagation (URN, user info)
        - Proper dependency injection of repositories
        - Easy testing with mock factories

    Example:
        >>> from dependencies.services.user.register import UserRegistrationServiceDependency
        >>>
        >>> service_factory = Depends(UserRegistrationServiceDependency.derive)
        >>> service = service_factory(
        ...     urn=request.state.urn,
        ...     user_urn=None,
        ...     api_name="REGISTRATION",
        ...     user_id=None,
        ...     user_repository=user_repo
        ... )
        >>> result = await service.run(registration_dto)
    """

    @staticmethod
    def derive() -> Callable:
        """
        Provide a factory function for creating UserRegistrationService instances.

        Returns a factory that accepts request context and dependencies,
        returning a configured UserRegistrationService instance.

        Returns:
            Callable: Factory function with signature:
                factory(urn, user_urn, api_name, user_id,
                       user_repository) -> UserRegistrationService

        Factory Parameters:
            urn (str): Unique Request Number for tracing.
            user_urn (str): User's unique resource name.
            api_name (str): Name of the API endpoint.
            user_id (str): User's database identifier.
            user_repository (UserRepository): User data access instance.

        Example:
            >>> factory = UserRegistrationServiceDependency.derive()
            >>> service = factory(
            ...     urn="urn:req:123",
            ...     user_urn=None,
            ...     api_name="REGISTRATION",
            ...     user_id=None,
            ...     user_repository=user_repo
            ... )
        """
        logger.debug("UserRegistrationServiceDependency factory created")

        def factory(
            urn: str,
            user_urn: str,
            api_name: str,
            user_id: str,
            user_repository,
        ) -> UserRegistrationService:
            """
            Create a UserRegistrationService instance with dependencies.

            Args:
                urn (str): Unique Request Number for tracing.
                user_urn (str): User's unique resource name.
                api_name (str): Name of the API endpoint.
                user_id (str): User's database identifier.
                user_repository: Repository for user data access.

            Returns:
                UserRegistrationService: Configured service instance.
            """
            logger.info("Instantiating UserRegistrationService")
            return UserRegistrationService(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
                user_repository=user_repository,
            )

        return factory
