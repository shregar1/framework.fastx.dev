"""
Cache Dependency Module.

This module provides FastAPI dependency injection for Redis cache sessions.
It enables controllers to access the shared Redis connection pool.

Usage:
    >>> from fastapi import Depends
    >>> from dependencies.cache import CacheDependency
    >>>
    >>> async def my_endpoint(cache: Redis = Depends(CacheDependency.derive)):
    ...     cache.set("key", "value")
"""

from redis import Redis

from start_utils import logger, redis_session


class CacheDependency:
    """
    FastAPI dependency provider for Redis cache sessions.

    This class provides a static method that returns the shared Redis
    session instance for use in FastAPI dependency injection.

    The Redis session is initialized once at application startup
    (in start_utils) and reused across all requests for efficiency.

    Example:
        >>> from fastapi import Depends
        >>> from dependencies.cache import CacheDependency
        >>>
        >>> @router.get("/cached-data")
        >>> async def get_cached_data(
        ...     cache: Redis = Depends(CacheDependency.derive)
        ... ):
        ...     value = cache.get("my_key")
        ...     return {"value": value}

    Note:
        The Redis session is a connection pool, so it's safe to use
        across multiple concurrent requests.
    """

    @staticmethod
    def derive() -> Redis:
        """
        Provide the shared Redis session instance.

        This method is designed to be used with FastAPI's Depends()
        for dependency injection.

        Returns:
            Redis: The shared Redis client instance configured at startup.

        Example:
            >>> cache = CacheDependency.derive()
            >>> cache.set("user:123", '{"name": "John"}', ex=3600)
            >>> cache.get("user:123")
        """
        logger.debug("CacheDependency: returning redis_session instance")
        return redis_session
