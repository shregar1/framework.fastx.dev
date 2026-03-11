"""
User Login Request DTO Module.

This module defines the request payload structure for user login.
It includes comprehensive validation for email and password fields
with security checks.

Endpoint: POST /user/login

Request Body:
    {
        "reference_number": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "password": "SecureP@ss123"
    }
"""

from pydantic import EmailStr, field_validator

from dtos.base import EnhancedBaseModel
from dtos.requests.abstraction import IRequestDTO
from utilities.validation import ValidationUtility


class UserLoginRequestDTO(IRequestDTO, EnhancedBaseModel):
    """
    Request DTO for user login/authentication.

    This DTO validates and sanitizes user login credentials before
    they are processed by the login service. It inherits from both
    IRequestDTO (for reference number) and EnhancedBaseModel (for
    security validation).

    Attributes:
        reference_number (str): Client-provided UUID (from IRequestDTO).
        email (EmailStr): User's email address.
            - Validated for proper email format
            - Normalized (lowercased, trimmed)
        password (str): User's password.
            - Validated for non-empty
            - Validated for password strength requirements

    Validation Rules:
        email:
            - Must be valid email format
            - Automatically normalized (lowercase, trimmed)

        password:
            - Cannot be empty
            - Must meet strength requirements:
                - Minimum 8 characters
                - At least one uppercase letter
                - At least one lowercase letter
                - At least one digit
                - At least one special character

    Example:
        >>> from dtos.requests.user.login import UserLoginRequestDTO
        >>>
        >>> login_request = UserLoginRequestDTO(
        ...     reference_number="550e8400-e29b-41d4-a716-446655440000",
        ...     email="User@Example.COM",  # Will be normalized to user@example.com
        ...     password="SecureP@ss123"
        ... )
        >>> login_request.email  # "user@example.com"

    Security:
        - Inherits string sanitization from EnhancedBaseModel
        - Can run validate_security() for injection detection
        - Password is validated but never logged
    """

    email: EmailStr
    """User's email address (validated and normalized)."""

    password: str
    """User's password (validated for strength, never logged)."""

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password is non-empty and meets strength requirements.

        Args:
            v (str): The password to validate.

        Returns:
            str: The validated password.

        Raises:
            ValueError: If password is empty or doesn't meet strength requirements.
        """
        if not v or not v.strip():
            raise ValueError('Password cannot be empty.')

        validation_result = ValidationUtility.validate_password_strength(v)
        if not validation_result['is_valid']:
            issues = ', '.join(validation_result['issues'])
            message = f"Password validation failed: {issues}"
            raise ValueError(message)

        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """
        Validate and normalize email address.

        Args:
            v (str): The email to validate.

        Returns:
            str: The normalized email (lowercased, trimmed).

        Raises:
            ValueError: If email format is invalid.
        """
        validation_result = ValidationUtility.validate_email_format(v)
        if not validation_result['is_valid']:
            raise ValueError(
                f"Invalid email format: {validation_result['error']}"
            )
        return validation_result['normalized_email']
