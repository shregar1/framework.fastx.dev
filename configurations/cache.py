"""
Cache Configuration Module.

This module provides a singleton configuration manager for Redis cache settings.
Configuration is loaded from a JSON file and exposed via a Pydantic DTO.

Usage:
    >>> config = CacheConfiguration()
    >>> cache_dto = config.get_config()
    >>> print(cache_dto.host, cache_dto.port)
"""

import json
from typing import Optional

from dtos.configurations.cache import CacheConfigurationDTO
from start_utils import logger


class CacheConfiguration:
    """
    Singleton configuration manager for Redis cache settings.

    This class implements the Singleton pattern to ensure only one instance
    of the cache configuration exists throughout the application lifecycle.
    Configuration is loaded from `config/cache/config.json`.

    Attributes:
        config (dict): Raw configuration dictionary loaded from JSON.

    Example:
        >>> # First call creates the instance and loads config
        >>> cache_config = CacheConfiguration()
        >>> dto = cache_config.get_config()
        >>>
        >>> # Subsequent calls return the same instance
        >>> same_config = CacheConfiguration()
        >>> assert cache_config is same_config  # True

    Configuration File Format (config/cache/config.json):
        ```json
        {
            "host": "localhost",
            "port": 6379,
            "password": "your-redis-password"
        }
        ```
    """

    _instance: Optional['CacheConfiguration'] = None

    def __new__(cls) -> 'CacheConfiguration':
        """
        Create or return the singleton instance.

        Returns:
            CacheConfiguration: The singleton configuration instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = {}
            cls._instance.load_config()
        return cls._instance

    def load_config(self) -> None:
        """
        Load cache configuration from JSON file.

        Reads the configuration from `config/cache/config.json` and stores
        it in the `config` attribute. Logs debug messages for success or
        failure conditions.

        Raises:
            No exceptions are raised; errors are logged and handled gracefully.

        Note:
            - FileNotFoundError: Logged if config file doesn't exist
            - JSONDecodeError: Logged if config file contains invalid JSON
        """
        try:
            with open("config/cache/config.json") as file:
                self.config = json.load(file)
            logger.debug("Cache config loaded successfully.")

        except FileNotFoundError:
            logger.debug("Cache config file not found.")

        except json.JSONDecodeError:
            logger.debug("Error decoding cache config file.")

    def get_config(self) -> CacheConfigurationDTO:
        """
        Get cache configuration as a validated DTO.

        Returns:
            CacheConfigurationDTO: Pydantic model containing:
                - host (str): Redis server hostname
                - port (int): Redis server port
                - password (str): Redis authentication password

        Example:
            >>> config = CacheConfiguration().get_config()
            >>> redis_client = Redis(
            ...     host=config.host,
            ...     port=config.port,
            ...     password=config.password
            ... )
        """
        return CacheConfigurationDTO(
            host=self.config.get("host", {}),
            port=self.config.get("port", {}),
            password=self.config.get("password", {}),
        )
