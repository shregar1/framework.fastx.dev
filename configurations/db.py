"""
Database Configuration Module.

This module provides a singleton configuration manager for database settings.
Configuration is loaded from a JSON file and exposed via a Pydantic DTO.

Usage:
    >>> config = DBConfiguration()
    >>> db_dto = config.get_config()
    >>> engine = create_engine(db_dto.connection_string)
"""

import json
from typing import Optional

from dtos.configurations.db import DBConfigurationDTO
from start_utils import logger


class DBConfiguration:
    """
    Singleton configuration manager for database connection settings.

    This class implements the Singleton pattern to ensure only one instance
    of the database configuration exists throughout the application lifecycle.
    Configuration is loaded from `config/db/config.json`.

    Attributes:
        config (dict): Raw configuration dictionary loaded from JSON.

    Example:
        >>> # First call creates the instance and loads config
        >>> db_config = DBConfiguration()
        >>> dto = db_config.get_config()
        >>>
        >>> # Create SQLAlchemy engine
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine(dto.connection_string)

    Configuration File Format (config/db/config.json):
        ```json
        {
            "user_name": "postgres",
            "password": "secret",
            "host": "localhost",
            "port": 5432,
            "database": "fastmvc_db",
            "connection_string": "postgresql://postgres:secret@localhost:5432/fastmvc_db"
        }
        ```

    Note:
        The connection_string can be provided directly or constructed from
        individual components (user_name, password, host, port, database).
    """

    _instance: Optional['DBConfiguration'] = None

    def __new__(cls) -> 'DBConfiguration':
        """
        Create or return the singleton instance.

        Returns:
            DBConfiguration: The singleton configuration instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = {}
            cls._instance.load_config()
        return cls._instance

    def load_config(self) -> None:
        """
        Load database configuration from JSON file.

        Reads the configuration from `config/db/config.json` and stores
        it in the `config` attribute. Logs debug messages for success or
        failure conditions.

        Raises:
            No exceptions are raised; errors are logged and handled gracefully.

        Note:
            - FileNotFoundError: Logged if config file doesn't exist
            - JSONDecodeError: Logged if config file contains invalid JSON
        """
        try:
            with open("config/db/config.json") as file:
                self.config = json.load(file)
            logger.debug("DB config loaded successfully.")

        except FileNotFoundError:
            logger.debug("DB config file not found.")

        except json.JSONDecodeError:
            logger.debug("Error decoding DB config file.")

    def get_config(self) -> DBConfigurationDTO:
        """
        Get database configuration as a validated DTO.

        Returns:
            DBConfigurationDTO: Pydantic model containing:
                - user_name (str): Database username
                - password (str): Database password
                - host (str): Database server hostname
                - port (int): Database server port
                - database (str): Database name
                - connection_string (str): Full connection URI

        Example:
            >>> config = DBConfiguration().get_config()
            >>> print(f"Connecting to {config.host}:{config.port}/{config.database}")
        """
        return DBConfigurationDTO(
            user_name=self.config.get("user_name"),
            password=self.config.get("password"),
            host=self.config.get("host"),
            port=self.config.get("port"),
            database=self.config.get("database"),
            connection_string=self.config.get("connection_string"),
        )
