"""
Dictionary Utility Dependency Module.

This module provides FastAPI dependency injection for DictionaryUtility.
It returns a factory function that creates utility instances with
request-specific context.

Usage:
    >>> from fastapi import Depends
    >>> from dependencies.utilities.dictionary import DictionaryUtilityDependency
    >>>
    >>> async def my_endpoint(
    ...     util_factory: Callable = Depends(DictionaryUtilityDependency.derive)
    ... ):
    ...     util = util_factory(urn=urn, ...)
    ...     result = util.convert_dict_keys_to_camel_case(data)
"""

from collections.abc import Callable

from start_utils import logger
from utilities.dictionary import DictionaryUtility


class DictionaryUtilityDependency:
    """
    FastAPI dependency provider for DictionaryUtility.

    This class provides a factory pattern for creating DictionaryUtility
    instances with request-specific context for logging and tracing.

    The factory pattern enables:
        - Request context propagation (URN for logging)
        - Consistent utility instantiation across the app
        - Easy testing with mock factories

    Example:
        >>> from dependencies.utilities.dictionary import DictionaryUtilityDependency
        >>>
        >>> util_factory = Depends(DictionaryUtilityDependency.derive)
        >>> util = util_factory(
        ...     urn=request.state.urn,
        ...     user_urn=user_urn,
        ...     api_name="LOGIN",
        ...     user_id=user_id
        ... )
        >>> camel_data = util.convert_dict_keys_to_camel_case(snake_data)
    """

    @staticmethod
    def derive() -> Callable:
        """
        Provide a factory function for creating DictionaryUtility instances.

        Returns a factory that accepts request context and returns a
        configured DictionaryUtility instance.

        Returns:
            Callable: Factory function with signature:
                factory(urn, user_urn, api_name, user_id) -> DictionaryUtility

        Factory Parameters:
            urn (str): Unique Request Number for tracing.
            user_urn (str): User's unique resource name.
            api_name (str): Name of the API endpoint.
            user_id (str): User's database identifier.

        Example:
            >>> factory = DictionaryUtilityDependency.derive()
            >>> util = factory(
            ...     urn="urn:req:123",
            ...     user_urn="urn:user:456",
            ...     api_name="LOGIN",
            ...     user_id="user-789"
            ... )
        """
        logger.debug("DictionaryUtilityDependency factory created")

        def factory(
            urn: str,
            user_urn: str,
            api_name: str,
            user_id: str,
        ) -> DictionaryUtility:
            """
            Create a DictionaryUtility instance with request context.

            Args:
                urn (str): Unique Request Number for tracing.
                user_urn (str): User's unique resource name.
                api_name (str): Name of the API endpoint.
                user_id (str): User's database identifier.

            Returns:
                DictionaryUtility: Configured utility instance.
            """
            logger.info("Instantiating DictionaryUtility")
            return DictionaryUtility(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
            )

        return factory
