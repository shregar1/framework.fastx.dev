"""
User Registration Request DTO Module.

This module defines the request payload structure for new user registration.
It includes comprehensive validation for email and password fields
with security checks.

Endpoint: POST /user/register

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


class UserRegistrationRequestDTO(IRequestDTO, EnhancedBaseModel):
    """
    Request DTO for new user registration.

    This DTO validates and sanitizes user registration data before
    a new account is created. It inherits from both IRequestDTO
    (for reference number) and EnhancedBaseModel (for security validation).

    Attributes:
        reference_number (str): Client-provided UUID (from IRequestDTO).
        email (EmailStr): User's email address for the new account.
            - Validated for proper email format
            - Normalized (lowercased, trimmed)
            - Must be unique (checked by service layer)
        password (str): Password for the new account.
            - Validated for non-empty
            - Validated for password strength requirements

    Validation Rules:
        email:
            - Must be valid email format
            - Automatically normalized (lowercase, trimmed)
            - Uniqueness checked in registration service

        password:
            - Cannot be empty
            - Must meet strength requirements:
                - Minimum 8 characters
                - At least one uppercase letter
                - At least one lowercase letter
                - At least one digit
                - At least one special character

    Example:
        >>> from dtos.requests.user.registration import UserRegistrationRequestDTO
        >>>
        >>> registration = UserRegistrationRequestDTO(
        ...     reference_number="550e8400-e29b-41d4-a716-446655440000",
        ...     email="NewUser@Example.COM",
        ...     password="MySecure@Pass1"
        ... )
        >>> registration.email  # "newuser@example.com"

    Security:
        - Inherits string sanitization from EnhancedBaseModel
        - Can run validate_security() for injection detection
        - Password is hashed before storage (in service layer)
    """

    email: EmailStr
    """Email address for the new account (validated and normalized)."""

    password: str
    """Password for the new account (validated, will be hashed)."""

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
