"""
Feature Flags Implementation.

Provides feature flag management with support for:
- Boolean flags
- Percentage rollouts
- User/group targeting
- Environment-specific flags
"""

import functools
import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional, Union


class RolloutStrategy(str, Enum):
    """Feature rollout strategies."""

    ALL = "all"  # All users
    NONE = "none"  # No users
    PERCENTAGE = "percentage"  # Percentage of users
    USER_LIST = "user_list"  # Specific users
    GROUP_LIST = "group_list"  # Specific groups


@dataclass
class FeatureFlagConfig:
    """
    Feature flag configuration.

    Attributes:
        name: Flag name/key.
        enabled: Whether flag is enabled.
        strategy: Rollout strategy.
        percentage: Percentage of users (for percentage rollout).
        user_list: List of user IDs (for user targeting).
        group_list: List of group/tenant IDs.
        environments: Enabled environments (empty = all).
        start_date: When flag becomes active.
        end_date: When flag expires.
        metadata: Additional metadata.
    """

    name: str
    enabled: bool = True
    strategy: RolloutStrategy = RolloutStrategy.ALL
    percentage: float = 100.0
    user_list: list[str] = field(default_factory=list)
    group_list: list[str] = field(default_factory=list)
    environments: list[str] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "strategy": self.strategy.value,
            "percentage": self.percentage,
            "user_list": self.user_list,
            "group_list": self.group_list,
            "environments": self.environments,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "metadata": self.metadata,
        }


class FeatureFlagStore:
    """Base class for feature flag storage."""

    async def get(self, name: str) -> Optional[FeatureFlagConfig]:
        """Get flag configuration."""
        pass

    async def set(self, config: FeatureFlagConfig) -> None:
        """Set flag configuration."""
        pass

    async def delete(self, name: str) -> None:
        """Delete flag."""
        pass

    async def list_all(self) -> list[FeatureFlagConfig]:
        """List all flags."""
        return []


class InMemoryFeatureFlagStore(FeatureFlagStore):
    """In-memory feature flag store."""

    def __init__(self):
        self._flags: dict[str, FeatureFlagConfig] = {}

    async def get(self, name: str) -> Optional[FeatureFlagConfig]:
        return self._flags.get(name)

    async def set(self, config: FeatureFlagConfig) -> None:
        self._flags[config.name] = config

    async def delete(self, name: str) -> None:
        self._flags.pop(name, None)

    async def list_all(self) -> list[FeatureFlagConfig]:
        return list(self._flags.values())


class EnvironmentFeatureFlagStore(FeatureFlagStore):
    """
    Feature flag store using environment variables.

    Flags are read from environment variables with prefix.
    Example: FEATURE_NEW_CHECKOUT=true
    """

    def __init__(self, prefix: str = "FEATURE_"):
        self._prefix = prefix

    async def get(self, name: str) -> Optional[FeatureFlagConfig]:
        env_name = f"{self._prefix}{name.upper()}"
        value = os.environ.get(env_name)

        if value is None:
            return None

        # Parse value
        if value.lower() in ("true", "1", "yes", "on"):
            enabled = True
        elif value.lower() in ("false", "0", "no", "off"):
            enabled = False
        else:
            # Try parsing as JSON for complex config
            try:
                config = json.loads(value)
                return FeatureFlagConfig(
                    name=name,
                    enabled=config.get("enabled", True),
                    strategy=RolloutStrategy(config.get("strategy", "all")),
                    percentage=config.get("percentage", 100.0),
                    user_list=config.get("user_list", []),
                    group_list=config.get("group_list", []),
                )
            except json.JSONDecodeError:
                enabled = True

        return FeatureFlagConfig(name=name, enabled=enabled)

    async def set(self, config: FeatureFlagConfig) -> None:
        # Environment variables are read-only at runtime
        pass

    async def list_all(self) -> list[FeatureFlagConfig]:
        flags = []
        for key, value in os.environ.items():
            if key.startswith(self._prefix):
                name = key[len(self._prefix):].lower()
                flag = await self.get(name)
                if flag:
                    flags.append(flag)
        return flags


class FeatureFlags:
    """
    Feature flag manager.

    Usage:
        flags = FeatureFlags()

        # Set a flag
        flags.set("new_checkout", enabled=True, percentage=50)

        # Check if enabled
        if flags.is_enabled("new_checkout", user_id="user123"):
            use_new_checkout()

        # Get all flags
        all_flags = await flags.list_all()
    """

    def __init__(
        self,
        store: Optional[FeatureFlagStore] = None,
        environment: Optional[str] = None,
    ):
        """
        Initialize feature flags.

        Args:
            store: Feature flag store implementation.
            environment: Current environment (e.g., "production").
        """
        self._store = store or InMemoryFeatureFlagStore()
        self._environment = environment or os.environ.get("ENVIRONMENT", "development")
        self._cache: dict[str, FeatureFlagConfig] = {}

    def _hash_user_id(self, user_id: str, flag_name: str) -> float:
        """
        Compute consistent hash for user targeting.

        Returns value between 0-100 for percentage rollouts.
        """
        key = f"{flag_name}:{user_id}".encode()
        hash_value = int(hashlib.md5(key).hexdigest(), 16)
        return (hash_value % 10000) / 100

    async def get(self, name: str) -> Optional[FeatureFlagConfig]:
        """Get flag configuration."""
        if name in self._cache:
            return self._cache[name]

        config = await self._store.get(name)
        if config:
            self._cache[name] = config
        return config

    async def set(
        self,
        name: str,
        enabled: bool = True,
        strategy: RolloutStrategy = RolloutStrategy.ALL,
        percentage: float = 100.0,
        user_list: Optional[list[str]] = None,
        group_list: Optional[list[str]] = None,
        environments: Optional[list[str]] = None,
        **metadata: Any,
    ) -> FeatureFlagConfig:
        """
        Set or update a feature flag.

        Args:
            name: Flag name.
            enabled: Whether flag is enabled.
            strategy: Rollout strategy.
            percentage: Percentage for percentage rollout.
            user_list: List of user IDs for user targeting.
            group_list: List of group IDs for group targeting.
            environments: Enabled environments.
            **metadata: Additional metadata.

        Returns:
            Created/updated flag configuration.
        """
        config = FeatureFlagConfig(
            name=name,
            enabled=enabled,
            strategy=strategy,
            percentage=percentage,
            user_list=user_list or [],
            group_list=group_list or [],
            environments=environments or [],
            metadata=metadata,
        )

        await self._store.set(config)
        self._cache[name] = config
        return config

    async def delete(self, name: str) -> None:
        """Delete a feature flag."""
        await self._store.delete(name)
        self._cache.pop(name, None)

    async def is_enabled(
        self,
        name: str,
        user_id: Optional[str] = None,
        group_id: Optional[str] = None,
        default: bool = False,
    ) -> bool:
        """
        Check if feature flag is enabled.

        Args:
            name: Flag name.
            user_id: User ID for percentage rollout.
            group_id: Group/tenant ID for group targeting.
            default: Default value if flag not found.

        Returns:
            True if feature is enabled.
        """
        config = await self.get(name)

        if config is None:
            return default

        if not config.enabled:
            return False

        # Check environment
        if config.environments and self._environment not in config.environments:
            return False

        # Check date range
        now = datetime.utcnow()
        if config.start_date and now < config.start_date:
            return False
        if config.end_date and now > config.end_date:
            return False

        # Check strategy
        if config.strategy == RolloutStrategy.NONE:
            return False

        if config.strategy == RolloutStrategy.ALL:
            return True

        if config.strategy == RolloutStrategy.USER_LIST:
            return user_id in config.user_list if user_id else False

        if config.strategy == RolloutStrategy.GROUP_LIST:
            return group_id in config.group_list if group_id else False

        if config.strategy == RolloutStrategy.PERCENTAGE:
            if user_id:
                user_percentage = self._hash_user_id(user_id, name)
                return user_percentage < config.percentage
            return False

        return default

    def is_enabled_sync(
        self,
        name: str,
        user_id: Optional[str] = None,
        group_id: Optional[str] = None,
        default: bool = False,
    ) -> bool:
        """
        Synchronous version using cached values.

        Only works if flag was previously loaded.
        """
        config = self._cache.get(name)

        if config is None:
            return default

        if not config.enabled:
            return False

        # Same logic as async version
        if config.strategy == RolloutStrategy.PERCENTAGE and user_id:
            return self._hash_user_id(user_id, name) < config.percentage

        return config.enabled

    async def list_all(self) -> list[FeatureFlagConfig]:
        """List all feature flags."""
        return await self._store.list_all()

    def clear_cache(self) -> None:
        """Clear cached flags."""
        self._cache.clear()


# Global feature flags instance
_feature_flags: Optional[FeatureFlags] = None


def get_feature_flags() -> FeatureFlags:
    """Get global feature flags instance."""
    global _feature_flags
    if _feature_flags is None:
        _feature_flags = FeatureFlags()
    return _feature_flags


def feature_flag(
    name: str,
    default: bool = False,
    fallback: Optional[Callable] = None,
) -> Callable:
    """
    Decorator to gate a function behind a feature flag.

    Usage:
        @feature_flag("new_checkout", default=False)
        async def checkout_v2():
            pass

        # With fallback
        @feature_flag("new_api", fallback=old_api_handler)
        async def new_api_handler():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            flags = get_feature_flags()

            # Try to get user_id from kwargs
            user_id = kwargs.get("user_id") or kwargs.get("current_user_id")

            if await flags.is_enabled(name, user_id=user_id, default=default):
                return await func(*args, **kwargs)
            elif fallback:
                import asyncio
                if asyncio.iscoroutinefunction(fallback):
                    return await fallback(*args, **kwargs)
                return fallback(*args, **kwargs)
            else:
                return None

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            flags = get_feature_flags()
            user_id = kwargs.get("user_id")

            if flags.is_enabled_sync(name, user_id=user_id, default=default):
                return func(*args, **kwargs)
            elif fallback:
                return fallback(*args, **kwargs)
            return None

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
