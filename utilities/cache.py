"""
Caching Utilities for FastMVC.

This module provides caching decorators and utilities for improving
application performance through Redis-based caching.

Features:
    - Function result caching with configurable TTL
    - Cache key generation with argument hashing
    - Cache invalidation patterns
    - Async and sync support

Classes:
    CacheUtility: Main caching utility class with decorators.

Example:
    >>> from utilities.cache import CacheUtility
    >>>
    >>> cache = CacheUtility(redis_client)
    >>>
    >>> @cache.cached(ttl=300, prefix="user")
    >>> async def get_user(user_id: int):
    ...     return await db.fetch_user(user_id)
    >>>
    >>> # Cache is automatically managed
    >>> user = await get_user(123)  # Cache miss - fetches from DB
    >>> user = await get_user(123)  # Cache hit - returns cached
"""

import asyncio
import functools
import hashlib
import json
import pickle
from collections.abc import Callable
from typing import Any, TypeVar

from loguru import logger
from redis import Redis

from abstractions.utility import IUtility

T = TypeVar("T")


class CacheUtility(IUtility):
    """
    Redis-based caching utility with decorator support.

    This utility provides a clean interface for caching function results
    in Redis with automatic key generation and TTL management.

    Attributes:
        redis_client (Redis): Redis client instance.
        default_ttl (int): Default time-to-live in seconds.
        key_prefix (str): Global prefix for all cache keys.
        enabled (bool): Whether caching is enabled.

    Example:
        >>> cache = CacheUtility(redis_client, default_ttl=3600)
        >>>
        >>> # As a decorator
        >>> @cache.cached(ttl=600)
        >>> def expensive_operation(x, y):
        ...     return x ** y
        >>>
        >>> # Manual cache operations
        >>> cache.set("my_key", {"data": "value"}, ttl=300)
        >>> data = cache.get("my_key")
        >>> cache.delete("my_key")
    """

    def __init__(
        self,
        redis_client: Redis = None,
        default_ttl: int = 3600,
        key_prefix: str = "fastmvc",
        enabled: bool = True,
    ):
        """
        Initialize the cache utility.

        Args:
            redis_client: Redis client instance.
            default_ttl: Default TTL in seconds (default: 1 hour).
            key_prefix: Prefix for all cache keys.
            enabled: Whether caching is enabled.
        """
        self._redis = redis_client
        self._default_ttl = default_ttl
        self._key_prefix = key_prefix
        self._enabled = enabled
        self.logger = logger.bind(utility="CacheUtility")

    @property
    def redis(self) -> Redis:
        """Get Redis client."""
        return self._redis

    @redis.setter
    def redis(self, value: Redis):
        """Set Redis client."""
        self._redis = value

    @property
    def enabled(self) -> bool:
        """Check if caching is enabled."""
        return self._enabled and self._redis is not None

    @enabled.setter
    def enabled(self, value: bool):
        """Enable or disable caching."""
        self._enabled = value

    def _make_key(self, *parts: str) -> str:
        """
        Create a cache key from parts.

        Args:
            *parts: Key components to join.

        Returns:
            Full cache key with prefix.
        """
        return f"{self._key_prefix}:{':'.join(str(p) for p in parts)}"

    def _hash_args(self, args: tuple, kwargs: dict) -> str:
        """
        Create a hash of function arguments for cache key.

        Args:
            args: Positional arguments.
            kwargs: Keyword arguments.

        Returns:
            MD5 hash of serialized arguments.
        """
        try:
            # Try JSON serialization first (more readable keys)
            key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            key_data = pickle.dumps({"args": args, "kwargs": kwargs})

        return hashlib.md5(key_data.encode() if isinstance(key_data, str) else key_data).hexdigest()[:16]

    def get(self, key: str) -> Any | None:
        """
        Get a value from cache.

        Args:
            key: Cache key (without prefix).

        Returns:
            Cached value or None if not found.
        """
        if not self.enabled:
            return None

        try:
            full_key = self._make_key(key)
            data = self._redis.get(full_key)

            if data is None:
                self.logger.debug(f"Cache miss: {key}")
                return None

            self.logger.debug(f"Cache hit: {key}")
            return pickle.loads(data)

        except Exception as e:
            self.logger.warning(f"Cache get error: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """
        Set a value in cache.

        Args:
            key: Cache key (without prefix).
            value: Value to cache.
            ttl: Time-to-live in seconds (uses default if None).

        Returns:
            True if successful, False otherwise.
        """
        if not self.enabled:
            return False

        try:
            full_key = self._make_key(key)
            ttl = ttl or self._default_ttl
            data = pickle.dumps(value)

            self._redis.setex(full_key, ttl, data)
            self.logger.debug(f"Cache set: {key} (ttl={ttl}s)")
            return True

        except Exception as e:
            self.logger.warning(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete a value from cache.

        Args:
            key: Cache key (without prefix).

        Returns:
            True if deleted, False otherwise.
        """
        if not self.enabled:
            return False

        try:
            full_key = self._make_key(key)
            result = self._redis.delete(full_key)
            self.logger.debug(f"Cache delete: {key} (found={bool(result)})")
            return bool(result)

        except Exception as e:
            self.logger.warning(f"Cache delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Key pattern with wildcards (e.g., "user:*").

        Returns:
            Number of keys deleted.
        """
        if not self.enabled:
            return 0

        try:
            full_pattern = self._make_key(pattern)
            keys = list(self._redis.scan_iter(match=full_pattern))

            if keys:
                count = self._redis.delete(*keys)
                self.logger.debug(f"Cache delete pattern: {pattern} (deleted={count})")
                return count

            return 0

        except Exception as e:
            self.logger.warning(f"Cache delete pattern error: {e}")
            return 0

    def clear(self) -> bool:
        """
        Clear all cached values with our prefix.

        Returns:
            True if successful.
        """
        return self.delete_pattern("*") >= 0

    def cached(
        self,
        ttl: int | None = None,
        prefix: str | None = None,
        key_func: Callable[..., str] | None = None,
    ):
        """
        Decorator to cache function results.

        This decorator caches the return value of a function based on
        its arguments. Supports both sync and async functions.

        Args:
            ttl: Cache TTL in seconds (uses default if None).
            prefix: Key prefix (uses function name if None).
            key_func: Custom function to generate cache key.

        Returns:
            Decorated function with caching.

        Example:
            >>> @cache.cached(ttl=300, prefix="user")
            >>> def get_user(user_id: int):
            ...     return db.query(User).get(user_id)
            >>>
            >>> # With custom key function
            >>> @cache.cached(key_func=lambda u: f"user:{u.id}")
            >>> def process_user(user: User):
            ...     return expensive_computation(user)
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            func_prefix = prefix or func.__name__

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                if not self.enabled:
                    return func(*args, **kwargs)

                # Generate cache key
                if key_func:
                    cache_key = f"{func_prefix}:{key_func(*args, **kwargs)}"
                else:
                    arg_hash = self._hash_args(args, kwargs)
                    cache_key = f"{func_prefix}:{arg_hash}"

                # Check cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Execute function
                result = func(*args, **kwargs)

                # Cache result
                self.set(cache_key, result, ttl)

                return result

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                if not self.enabled:
                    return await func(*args, **kwargs)

                # Generate cache key
                if key_func:
                    cache_key = f"{func_prefix}:{key_func(*args, **kwargs)}"
                else:
                    arg_hash = self._hash_args(args, kwargs)
                    cache_key = f"{func_prefix}:{arg_hash}"

                # Check cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Execute function
                result = await func(*args, **kwargs)

                # Cache result
                self.set(cache_key, result, ttl)

                return result

            # Return appropriate wrapper
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator

    def invalidate(self, prefix: str):
        """
        Decorator to invalidate cache after function execution.

        Use this on functions that modify data to ensure cache
        is cleared after changes.

        Args:
            prefix: Cache prefix pattern to invalidate.

        Example:
            >>> @cache.invalidate("user:*")
            >>> def update_user(user_id: int, data: dict):
            ...     return db.update_user(user_id, data)
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                result = func(*args, **kwargs)
                self.delete_pattern(prefix)
                return result

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                result = await func(*args, **kwargs)
                self.delete_pattern(prefix)
                return result

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator


# Convenience function for creating a cache instance
def create_cache(
    redis_client: Redis,
    default_ttl: int = 3600,
    key_prefix: str = "fastmvc",
) -> CacheUtility:
    """
    Create a configured CacheUtility instance.

    Args:
        redis_client: Redis client instance.
        default_ttl: Default cache TTL in seconds.
        key_prefix: Global key prefix.

    Returns:
        Configured CacheUtility instance.

    Example:
        >>> from start_utils import redis_session
        >>> cache = create_cache(redis_session, default_ttl=600)
    """
    return CacheUtility(
        redis_client=redis_client,
        default_ttl=default_ttl,
        key_prefix=key_prefix,
    )

