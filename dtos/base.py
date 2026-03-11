"""
Enhanced Base Model Module.

This module provides an enhanced Pydantic BaseModel with additional
security validation, input sanitization, and configuration options.
All request DTOs should inherit from EnhancedBaseModel for consistent
security validation.

Usage:
    >>> from dtos.base import EnhancedBaseModel
    >>>
    >>> class MyRequestDTO(EnhancedBaseModel):
    ...     name: str
    ...     email: str
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, validator

from start_utils import logger
from utilities.validation import SecurityValidators, ValidationUtility


class EnhancedBaseModel(BaseModel):
    """
    Enhanced Pydantic BaseModel with security features.

    This base model extends Pydantic's BaseModel to provide:
        - Automatic string sanitization on all inputs
        - Security validation (SQL injection, XSS, path traversal)
        - Strict field validation (rejects extra fields)
        - Custom JSON encoders for datetime

    All request DTOs that handle user input should inherit from this
    class to ensure consistent security measures.

    Configuration:
        - extra = "forbid": Reject fields not defined in the model
        - validate_assignment = True: Validate on attribute assignment
        - use_enum_values = True: Use enum values in serialization
        - json_encoders: Custom datetime ISO format encoding

    Example:
        >>> class UserInputDTO(EnhancedBaseModel):
        ...     username: str
        ...     bio: str
        ...
        >>> # Input is automatically sanitized
        >>> dto = UserInputDTO(username="  john  ", bio="Hello <script>alert(1)</script>")
        >>> dto.username  # "john" (trimmed)
        >>>
        >>> # Security validation
        >>> result = dto.validate_security()
        >>> if not result['is_valid']:
        ...     print(result['issues'])  # ["Potential XSS in field 'bio'"]

    Security Features:
        - SQL injection pattern detection
        - XSS attack pattern detection
        - Path traversal attempt detection
        - String sanitization (trimming, normalization)
    """

    class Config:
        """Pydantic model configuration."""

        extra = "forbid"
        """Reject any fields not explicitly defined in the model."""

        validate_assignment = True
        """Re-validate the model when attributes are assigned."""

        use_enum_values = True
        """Use enum values instead of enum instances in serialization."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        """Custom JSON encoders for specific types."""

    @validator('*', pre=True)
    def sanitize_strings(cls, v):
        """
        Sanitize all string inputs before validation.

        This pre-validator runs on every field before other validators.
        It sanitizes strings by trimming whitespace and applying
        security-safe transformations.

        Args:
            v: The field value to sanitize.

        Returns:
            The sanitized value (strings are cleaned, others pass through).
        """
        logger.debug("Sanitizing all string inputs in EnhancedBaseModel")
        if isinstance(v, str):
            return ValidationUtility.sanitize_string(v)
        return v

    def validate_security(self) -> dict[str, Any]:
        """
        Perform comprehensive security validation on all string fields.

        Checks all string fields for potential security threats including
        SQL injection, XSS attacks, and path traversal attempts.

        Returns:
            dict: Validation result with:
                - is_valid (bool): True if no security issues found
                - issues (list): List of security issue descriptions

        Example:
            >>> dto = MyDTO(user_input="SELECT * FROM users")
            >>> result = dto.validate_security()
            >>> if not result['is_valid']:
            ...     for issue in result['issues']:
            ...         logger.warning(issue)
            ...     raise SecurityError("Malicious input detected")
        """
        logger.debug("Performing security validation on EnhancedBaseModel")
        issues = []

        for field_name, field_value in self.dict().items():
            if isinstance(field_value, str):
                if not SecurityValidators.validate_sql_injection_prevention(
                    field_value,
                ):
                    issues.append(
                        f"Potential SQL injection in field '{field_name}'"
                    )

                if not SecurityValidators.validate_xss_prevention(field_value):
                    issues.append(f"Potential XSS in field '{field_name}'")

                if not SecurityValidators.validate_path_traversal_prevention(
                    field_value,
                ):
                    issues.append(
                        f"Potential path traversal in field '{field_name}'"
                    )

        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }
