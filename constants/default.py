"""
Default Configuration Constants Module.

This module defines default values for application configuration settings.
These defaults are used as fallbacks when configuration files are missing
or when specific values are not provided.

Usage:
    >>> from constants.default import Default
    >>> token_expiry = config.get("expiry", Default.ACCESS_TOKEN_EXPIRE_MINUTES)
"""

from typing import Any, Final


class Default:
    """
    Default configuration values for the FastMVC application.

    This class contains all default values for application settings including
    authentication, rate limiting, security headers, input validation, and CORS.
    These values are used when configuration files are missing or incomplete.

    Attributes:
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Default JWT token expiry time.
        RATE_LIMIT_MAX_REQUESTS (int): Maximum requests per window.
        RATE_LIMIT_WINDOW_SECONDS (int): Rate limit window duration.
        RATE_LIMIT_REQUESTS_PER_MINUTE (int): Requests allowed per minute.
        RATE_LIMIT_REQUESTS_PER_HOUR (int): Requests allowed per hour.
        RATE_LIMIT_BURST_LIMIT (int): Maximum burst request count.
        SECURITY_CONFIGURATION (dict): Complete security configuration defaults.

    Example:
        >>> from constants.default import Default
        >>>
        >>> # Use default if config value missing
        >>> expiry = user_config.get(
        ...     "jwt_expiry",
        ...     Default.SECURITY_CONFIGURATION["authentication"]["jwt_expiry_minutes"]
        ... )

    Security Configuration Structure:
        - rate_limiting: Request rate limiting settings
        - security_headers: HTTP security header configuration
        - input_validation: Input sanitization and validation rules
        - authentication: JWT and session settings
        - cors: Cross-Origin Resource Sharing settings

    Note:
        These defaults are designed for development. Production deployments
        should use explicit configuration files with stricter values.
    """

    ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 1440
    """Default JWT access token expiry: 24 hours (1440 minutes)."""

    RATE_LIMIT_MAX_REQUESTS: Final[int] = 2
    """Maximum requests per rate limit window."""

    RATE_LIMIT_WINDOW_SECONDS: Final[int] = 60
    """Rate limit window duration in seconds."""

    RATE_LIMIT_REQUESTS_PER_MINUTE: Final[int] = 60
    """Allowed requests per minute per client."""

    RATE_LIMIT_REQUESTS_PER_HOUR: Final[int] = 1000
    """Allowed requests per hour per client."""

    RATE_LIMIT_BURST_LIMIT: Final[int] = 10
    """Maximum burst requests allowed."""

    SECURITY_CONFIGURATION: Final[dict[str, Any]] = {
        "rate_limiting": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "burst_limit": 10,
            "window_size": 60,
            "enable_sliding_window": True,
            "enable_token_bucket": False,
            "enable_fixed_window": False,
            "excluded_paths": ["/health", "/docs", "/openapi.json"],
            "excluded_methods": ["OPTIONS"]
        },
        "security_headers": {
            "enable_hsts": True,
            "enable_csp": True,
            "csp_report_only": False,
            "hsts_max_age": 31536000,
            "hsts_include_subdomains": True,
            "hsts_preload": False,
            "frame_options": "DENY",
            "content_type_options": "nosniff",
            "xss_protection": "1; mode=block",
            "referrer_policy": "strict-origin-when-cross-origin",
            "custom_csp": None,
            "custom_permissions_policy": None
        },
        "input_validation": {
            "max_string_length": 1000,
            "max_password_length": 128,
            "min_password_length": 8,
            "max_email_length": 254,
            "enable_sql_injection_check": True,
            "enable_xss_check": True,
            "enable_path_traversal_check": True,
            "weak_passwords": [
                "password", "123456", "qwerty", "admin", "letmein"
            ]
        },
        "authentication": {
            "jwt_expiry_minutes": 30,
            "refresh_token_expiry_days": 7,
            "max_login_attempts": 5,
            "lockout_duration_minutes": 15,
            "password_history_count": 5,
            "require_strong_password": True,
            "session_timeout_minutes": 60
        },
        "cors": {
            "allowed_origins": ["*"],
            "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allowed_headers": ["*"],
            "allow_credentials": True,
            "max_age": 3600
        }
    }
    """
    Complete security configuration with sensible defaults.

    Sections:
        rate_limiting:
            - requests_per_minute: 60 requests/minute allowed
            - requests_per_hour: 1000 requests/hour allowed
            - burst_limit: 10 concurrent requests max
            - enable_sliding_window: Use sliding window algorithm
            - excluded_paths: Paths exempt from rate limiting

        security_headers:
            - enable_hsts: HTTP Strict Transport Security
            - enable_csp: Content Security Policy
            - hsts_max_age: HSTS duration (1 year default)
            - frame_options: Clickjacking protection

        input_validation:
            - max_string_length: Maximum input string length
            - min_password_length: Minimum password characters
            - enable_sql_injection_check: SQL injection detection
            - enable_xss_check: XSS attack detection

        authentication:
            - jwt_expiry_minutes: Token validity duration
            - max_login_attempts: Before account lockout
            - lockout_duration_minutes: Lockout period

        cors:
            - allowed_origins: Permitted request origins
            - allowed_methods: Permitted HTTP methods
            - allow_credentials: Cookie/auth header support
    """
