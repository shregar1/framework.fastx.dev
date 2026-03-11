"""
Security Configuration Module.

This module provides a configuration manager for security-related settings
including authentication, input validation, and HTTP security headers.
Supports JSON file configuration with environment variable overrides.

Usage:
    >>> config = SecurityConfiguration()
    >>> security_dto = config.get_config()
    >>> jwt_expiry = security_dto.authentication.jwt_expiry_minutes
"""

import json
import os
from pathlib import Path
from typing import Any

from constants.default import Default
from dtos.configurations.security import SecurityConfigurationDTO
from start_utils import logger


class SecurityConfiguration:
    """
    Configuration manager for security-related settings.

    This class loads security configuration from a JSON file and supports
    runtime overrides via environment variables. Unlike the singleton
    pattern used by other configuration classes, this allows for multiple
    instances with different config paths.

    Features:
        - JSON file-based configuration
        - Environment variable overrides
        - Default fallback values
        - Configuration hot-reload support

    Attributes:
        config_path (str): Path to the security configuration JSON file.

    Example:
        >>> # Load default configuration
        >>> security = SecurityConfiguration()
        >>> config = security.get_config()
        >>>
        >>> # Access nested settings
        >>> max_attempts = config.authentication.max_login_attempts
        >>> jwt_expiry = config.authentication.jwt_expiry_minutes

    Configuration File Format (config/security/config.json):
        ```json
        {
            "security_headers": {
                "hsts_max_age": 31536000,
                "hsts_include_subdomains": true,
                "enable_csp": true,
                "enable_hsts": true
            },
            "input_validation": {
                "max_string_length": 1000,
                "min_password_length": 8
            },
            "authentication": {
                "jwt_expiry_minutes": 60,
                "max_login_attempts": 5
            }
        }
        ```

    Environment Variable Overrides:
        - SECURITY_HSTS_MAX_AGE
        - SECURITY_HSTS_INCLUDE_SUBDOMAINS
        - SECURITY_ENABLE_CSP
        - SECURITY_ENABLE_HSTS
        - SECURITY_MAX_STRING_LENGTH
        - SECURITY_MIN_PASSWORD_LENGTH
        - SECURITY_JWT_EXPIRY_MINUTES
        - SECURITY_MAX_LOGIN_ATTEMPTS
    """

    def __init__(self, config_path: str | None = None) -> None:
        """
        Initialize the SecurityConfiguration.

        Args:
            config_path (str, optional): Path to the security config file.
                Defaults to "config/security/config.json".
        """
        self.config_path = config_path or "config/security/config.json"
        self._config: SecurityConfigurationDTO | None = None

    def get_config(self) -> SecurityConfigurationDTO:
        """
        Get security configuration as a validated DTO.

        Loads configuration on first access and caches the result.
        Subsequent calls return the cached configuration.

        Returns:
            SecurityConfigurationDTO: Pydantic model containing nested
                configuration for security_headers, input_validation,
                and authentication settings.

        Example:
            >>> config = SecurityConfiguration().get_config()
            >>> if config.security_headers.enable_hsts:
            ...     print("HSTS is enabled")
        """
        if self._config is None:
            self._load_config()
        return self._config

    def _load_config(self) -> None:
        """
        Load configuration from JSON file with environment overrides.

        Attempts to load from the configured file path. If the file doesn't
        exist or contains invalid JSON, falls back to default configuration.
        After loading, applies any environment variable overrides.

        Note:
            Errors are logged but not raised; defaults are used as fallback.
        """
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                logger.debug(
                    "Security config file not found. Using default config."
                )
                self._config = self._get_default_config()
                return
            with open(config_file) as f:
                config_data = json.load(f)
            config_data = self._override_with_env_vars(config_data)
            self._config = SecurityConfigurationDTO(**config_data)
            logger.debug("Security config loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading security config: {e}")
            self._config = self._get_default_config()

    def _override_with_env_vars(
        self,
        config_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Apply environment variable overrides to configuration.

        Checks for specific environment variables and overrides the
        corresponding configuration values. Handles type conversion
        for boolean, integer, and float values.

        Args:
            config_data (dict): The configuration dictionary to modify.

        Returns:
            dict: Modified configuration with environment overrides applied.

        Environment Variables:
            - SECURITY_HSTS_MAX_AGE: Override HSTS max-age (int)
            - SECURITY_HSTS_INCLUDE_SUBDOMAINS: Include subdomains (bool)
            - SECURITY_ENABLE_CSP: Enable CSP header (bool)
            - SECURITY_ENABLE_HSTS: Enable HSTS header (bool)
            - SECURITY_MAX_STRING_LENGTH: Max input length (int)
            - SECURITY_MIN_PASSWORD_LENGTH: Min password length (int)
            - SECURITY_JWT_EXPIRY_MINUTES: JWT token expiry (int)
            - SECURITY_MAX_LOGIN_ATTEMPTS: Max failed logins (int)
        """
        env_mappings = {
            "SECURITY_HSTS_MAX_AGE": ("security_headers", "hsts_max_age"),
            "SECURITY_HSTS_INCLUDE_SUBDOMAINS": (
                "security_headers", "hsts_include_subdomains"
            ),
            "SECURITY_ENABLE_CSP": ("security_headers", "enable_csp"),
            "SECURITY_ENABLE_HSTS": ("security_headers", "enable_hsts"),
            "SECURITY_MAX_STRING_LENGTH": (
                "input_validation", "max_string_length"
            ),
            "SECURITY_MIN_PASSWORD_LENGTH": (
                "input_validation", "min_password_length"
            ),
            "SECURITY_JWT_EXPIRY_MINUTES": (
                "authentication", "jwt_expiry_minutes"
            ),
            "SECURITY_MAX_LOGIN_ATTEMPTS": (
                "authentication", "max_login_attempts"),
        }
        for env_var, (section, key) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string to appropriate type
                if isinstance(config_data[section][key], bool):
                    config_data[section][key] = (
                        env_value.lower() in ('true', '1', 'yes')
                    )
                elif isinstance(config_data[section][key], int):
                    config_data[section][key] = int(env_value)
                elif isinstance(config_data[section][key], float):
                    config_data[section][key] = float(env_value)
                else:
                    config_data[section][key] = env_value
        return config_data

    def _get_default_config(self) -> SecurityConfigurationDTO:
        """
        Get default security configuration.

        Returns:
            SecurityConfigurationDTO: Configuration with default values
                as defined in constants.default.Default.SECURITY_CONFIGURATION.
        """
        default_config = Default.SECURITY_CONFIGURATION
        return SecurityConfigurationDTO(**default_config)

    def reload_config(self) -> SecurityConfigurationDTO:
        """
        Reload configuration from file.

        Clears the cached configuration and reloads from the file.
        Useful for picking up configuration changes without restarting.

        Returns:
            SecurityConfigurationDTO: Freshly loaded configuration.

        Example:
            >>> security = SecurityConfiguration()
            >>> # After modifying config file...
            >>> new_config = security.reload_config()
        """
        logger.debug("Reloading security configuration from file.")
        self._config = None
        return self.get_config()
