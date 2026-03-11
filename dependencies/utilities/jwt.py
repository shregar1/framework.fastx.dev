"""
JWT Utility Dependency Module.

This module provides FastAPI dependency injection for JWTUtility.
It returns a factory function that creates utility instances with
request-specific context.

Usage:
    >>> from fastapi import Depends
    >>> from dependencies.utilities.jwt import JWTUtilityDependency
    >>>
    >>> async def login(
    ...     jwt_factory: Callable = Depends(JWTUtilityDependency.derive)
    ... ):
    ...     jwt_util = jwt_factory(urn=urn, ...)
    ...     token = jwt_util.generate_token(payload)
"""

from collections.abc import Callable

from start_utils import logger
from utilities.jwt import JWTUtility


class JWTUtilityDependency:
    """
    FastAPI dependency provider for JWTUtility.

    This class provides a factory pattern for creating JWTUtility
    instances with request-specific context for logging and tracing.

    The factory pattern enables:
        - Request context propagation (URN for logging)
        - Consistent utility instantiation across the app
        - Easy testing with mock factories

    Example:
        >>> from dependencies.utilities.jwt import JWTUtilityDependency
        >>>
        >>> jwt_factory = Depends(JWTUtilityDependency.derive)
        >>> jwt_util = jwt_factory(
        ...     urn=request.state.urn,
        ...     user_urn=user_urn,
        ...     api_name="LOGIN",
        ...     user_id=user_id
        ... )
        >>> token = jwt_util.generate_token({"user_id": user_id})
    """

    @staticmethod
    def derive() -> Callable:
        """
        Provide a factory function for creating JWTUtility instances.

        Returns a factory that accepts request context and returns a
        configured JWTUtility instance.

        Returns:
            Callable: Factory function with signature:
                factory(urn, user_urn, api_name, user_id) -> JWTUtility

        Factory Parameters:
            urn (str): Unique Request Number for tracing.
            user_urn (str): User's unique resource name.
            api_name (str): Name of the API endpoint.
            user_id (str): User's database identifier.

        Example:
            >>> factory = JWTUtilityDependency.derive()
            >>> jwt_util = factory(
            ...     urn="urn:req:123",
            ...     user_urn="urn:user:456",
            ...     api_name="LOGIN",
            ...     user_id="user-789"
            ... )
        """
        logger.debug("JWTUtilityDependency factory created")

        def factory(
            urn: str,
            user_urn: str,
            api_name: str,
            user_id: str,
        ) -> JWTUtility:
            """
            Create a JWTUtility instance with request context.

            Args:
                urn (str): Unique Request Number for tracing.
                user_urn (str): User's unique resource name.
                api_name (str): Name of the API endpoint.
                user_id (str): User's database identifier.

            Returns:
                JWTUtility: Configured utility instance.
            """
            logger.info("Instantiating JWTUtility")
            return JWTUtility(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
            )

        return factory
