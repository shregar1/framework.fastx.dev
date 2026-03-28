"""Environment Configuration Validator.

Validates .env configuration on startup to catch misconfigurations early.
Fail fast principle - crashes on invalid config rather than running with bad settings.

Usage:
    from config.validator import ConfigValidator
    validator = ConfigValidator()
    validator.validate()  # Raises ConfigValidationError on invalid config
"""

import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    def __init__(self, errors: list[str]):
        """Execute __init__ operation.

        Args:
            errors: The errors parameter.
        """
        self.errors = errors
        message = "Configuration validation failed:\n" + "\n".join(
            f"  • {e}" for e in errors
        )
        super().__init__(message)


@dataclass
class ValidationRule:
    """A validation rule for a configuration key."""

    key: str
    required: bool = True
    validator: Optional[Callable[[str], tuple[bool, str]]] = None
    default: Any = None
    secret: bool = False  # If True, value won't be printed in error messages


class ConfigValidator:
    """Validates application configuration from environment variables.

    Example:
        validator = ConfigValidator()
        validator.add_rule("DATABASE_URL", required=True, validator=validate_dataI_url)
        validator.add_rule("JWT_SECRET", required=True, validator=validate_jwt_secret)
        validator.validate()

    """

    # Standard validation patterns
    DATABASE_URL_PATTERN = re.compile(
        r"^(postgresql|postgres|mysql|sqlite|redis)://[^:]+:[^@]*@[^/]+/\w+$"
    )

    JWT_SECRET_MIN_LENGTH = 32

    def __init__(self):
        """Execute __init__ operation."""
        self.rules: list[ValidationRule] = []
        self._add_default_rules()

    def _add_default_rules(self):
        """Add default validation rules for common FastMVC settings."""
        # DataI
        self.add_rule(
            "DATABASE_URL",
            required=False,
            validator=self.validate_dataI_url,
            default="sqlite:///./app.db",
        )

        # JWT
        self.add_rule(
            "JWT_SECRET_KEY", required=True, validator=self.validate_jwt_secret
        )
        self.add_rule(
            "JWT_ALGORITHM",
            required=False,
            validator=self.validate_jwt_algorithm,
            default="HS256",
        )

        # Redis (optional but common)
        self.add_rule("REDIS_URL", required=False, validator=self.validate_redis_url)

        # Application
        self.add_rule(
            "APP_ENV",
            required=False,
            validator=self.validate_app_env,
            default="development",
        )
        self.add_rule("DEBUG", required=False, default="false")

        # Server
        self.add_rule("HOST", required=False, default="0.0.0.0")
        self.add_rule(
            "PORT", required=False, validator=self.validate_port, default="8000"
        )

        # Security
        self.add_rule("ALLOWED_HOSTS", required=False, default="*")
        self.add_rule(
            "CORS_ORIGINS",
            required=False,
            default="http://localhost:3000,http://localhost:8080",
        )

    def add_rule(
        self,
        key: str,
        required: bool = True,
        validator: Optional[Callable[[str], tuple[bool, str]]] = None,
        default: Any = None,
        secret: bool = False,
    ):
        """Add a validation rule."""
        self.rules.append(
            ValidationRule(
                key=key,
                required=required,
                validator=validator,
                default=default,
                secret=secret,
            )
        )

    def validate(self, raise_on_error: bool = True) -> tuple[bool, list[str]]:
        """Validate all configured rules.

        Args:
            raise_on_error: If True, raises ConfigValidationError on failure

        Returns:
            Tuple of (is_valid, error_messages)

        """
        errors = []
        warnings = []

        for rule in self.rules:
            value = os.getenv(rule.key, rule.default)

            # Check required
            if rule.required and not value:
                errors.append(f"{rule.key}: Required but not set")
                continue

            # Skip validation if not set and not required
            if not value:
                continue

            # Run custom validator
            if rule.validator:
                is_valid, message = rule.validator(value)
                if not is_valid:
                    if rule.secret:
                        errors.append(f"{rule.key}: {message}")
                    else:
                        errors.append(f"{rule.key}: {message} (got: {value[:20]}...)")

        # Print warnings
        for warning in warnings:
            print(f"⚠️  Config Warning: {warning}")

        is_valid = len(errors) == 0

        if not is_valid and raise_on_error:
            raise ConfigValidationError(errors)

        return is_valid, errors

    # Built-in validators

    @classmethod
    def validate_dataI_url(cls, value: str) -> tuple[bool, str]:
        """Validate database URL format."""
        if not value:
            return True, ""  # Optional

        # SQLite is always valid
        if value.startswith("sqlite://"):
            return True, ""

        # Check other database URLs
        if not cls.DATABASE_URL_PATTERN.match(value):
            return (
                False,
                "Invalid database URL format. Expected: postgresql://user:pass@host/db",
            )

        # Check for default/insecure passwords
        if ":password@" in value.lower() or ":admin@" in value.lower():
            return False, "DataI URL contains default/insecure password"

        return True, ""

    @classmethod
    def validate_jwt_secret(cls, value: str) -> tuple[bool, str]:
        """Validate JWT secret strength."""
        if not value:
            return False, "JWT secret cannot be empty"

        if len(value) < cls.JWT_SECRET_MIN_LENGTH:
            return (
                False,
                f"JWT secret too short. Minimum {cls.JWT_SECRET_MIN_LENGTH} characters (got {len(value)})",
            )

        # Check for common weak secrets
        weak_secrets = [
            "secret",
            "password",
            "123456",
            "jwt",
            "token",
            "your-secret-key",
            "change-me",
            "default",
            "test",
        ]

        if value.lower() in weak_secrets:
            return False, "JWT secret is too common/weak"

        # Check entropy (should have mix of characters)
        has_upper = any(c.isupper() for c in value)
        has_lower = any(c.islower() for c in value)
        has_digit = any(c.isdigit() for c in value)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in value)

        complexity_score = sum([has_upper, has_lower, has_digit, has_special])
        if complexity_score < 2:
            return (
                False,
                f"JWT secret lacks complexity. Use mix of upper, lower, digits, and special characters",
            )

        return True, ""

    @classmethod
    def validate_jwt_algorithm(cls, value: str) -> tuple[bool, str]:
        """Validate JWT algorithm."""
        valid_algorithms = [
            "HS256",
            "HS384",
            "HS512",
            "RS256",
            "RS384",
            "RS512",
            "ES256",
            "ES384",
            "ES512",
        ]

        if value not in valid_algorithms:
            return (
                False,
                f"Invalid algorithm. Must be one of: {', '.join(valid_algorithms)}",
            )

        # Warn about weak algorithms
        if value in ["HS256"]:
            # HS256 is fine for most cases, but we could warn in high-security contexts
            pass

        return True, ""

    @classmethod
    def validate_redis_url(cls, value: str) -> tuple[bool, str]:
        """Validate Redis URL format."""
        if not value:
            return True, ""  # Optional

        if not value.startswith(("redis://", "rediss://")):
            return False, "Invalid Redis URL. Must start with redis:// or rediss://"

        return True, ""

    @classmethod
    def validate_app_env(cls, value: str) -> tuple[bool, str]:
        """Validate application environment."""
        valid_envs = [
            "development",
            "dev",
            "staging",
            "stage",
            "production",
            "prod",
            "test",
            "testing",
        ]

        if value.lower() not in valid_envs:
            return (
                False,
                f"Invalid environment. Must be one of: {', '.join(valid_envs)}",
            )

        return True, ""

    @classmethod
    def validate_port(cls, value: str) -> tuple[bool, str]:
        """Validate port number."""
        try:
            port = int(value)
            if port < 1 or port > 65535:
                return False, f"Port must be between 1-65535 (got {port})"
        except ValueError:
            return False, f"Port must be a number (got {value})"

        return True, ""

    @classmethod
    def validate_email(cls, value: str) -> tuple[bool, str]:
        """Validate email format."""
        pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        if not pattern.match(value):
            return False, "Invalid email format"

        return True, ""

    @classmethod
    def validate_url(cls, value: str) -> tuple[bool, str]:
        """Validate URL format."""
        pattern = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)

        if not pattern.match(value):
            return False, "Invalid URL format. Must start with http:// or https://"

        return True, ""


def validate_config_or_exit():
    """Validate configuration and exit on failure.
    Use this in application startup.
    """
    validator = ConfigValidator()

    try:
        validator.validate(raise_on_error=True)
        print("✅ Configuration validated successfully")
    except ConfigValidationError as e:
        print("\n❌ Configuration Error:\n")
        print(str(e))
        print(
            "\nPlease check your .env file and ensure all required variables are set correctly."
        )
        sys.exit(1)


# Convenience function for quick validation
def quick_validate():
    """Quick validation that raises on error."""
    validator = ConfigValidator()
    validator.validate(raise_on_error=True)
