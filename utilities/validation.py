"""
Utility classes for input validation, security checks
"""
import re
import uuid
from datetime import datetime
from typing import Any

from email_validator import EmailNotValidError, validate_email

from abstractions.utility import IUtility
from constants.regular_expression import RegularExpression
from start_utils import logger


class ValidationUtility(IUtility):
    """
    Utility class for comprehensive input validation beyond Pydantic.
    """

    @staticmethod
    def validate_password_strength(password: str) -> dict[str, Any]:
        """
        Validate password strength with detailed feedback.

        Returns:
            Dict with 'is_valid' boolean and 'issues' list
        """
        logger.debug("Validating password strength")
        issues = []

        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")

        if not re.search(r'[a-z]', password):
            issues.append(
                "Password must contain at least one lowercase letter"
            )

        if not re.search(r'[A-Z]', password):
            issues.append(
                "Password must contain at least one uppercase letter"
            )

        if not re.search(r'\d', password):
            issues.append("Password must contain at least one digit")

        if not re.search(r'[@$!%*?&]', password):
            issues.append(
                "Password must contain at least one special character "
                "(@$!%*?&)"
            )

        if re.search(r'(.)\1{2,}', password):
            issues.append(
                "Password cannot contain more than 2 consecutive identical "
                "characters"
            )

        weak_passwords = [
            "password",
            "123456",
            "qwerty",
            "admin",
            "letmein",
        ]
        if password.lower() in weak_passwords:
            issues.append(
                "Password is too common, please choose a stronger password"
            )

        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }

    @staticmethod
    def validate_email_format(email: str) -> dict[str, Any]:
        """
        Validate email format using email-validator library.
        """
        logger.debug("Validating email format")
        try:
            valid = validate_email(email)
            return {
                'is_valid': True,
                'normalized_email': valid.email
            }
        except EmailNotValidError as e:
            return {
                'is_valid': False,
                'error': str(e)
            }

    @staticmethod
    def validate_uuid_format(uuid_string: str) -> bool:
        """
        Validate UUID format.
        """
        logger.debug("Validating UUID format")
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_date_range(
        start_date: datetime,
        end_date: datetime,
        max_days: int = 365,
    ) -> dict[str, Any]:
        """
        Validate date range with maximum allowed span.
        """
        logger.debug("Validating date range")
        if start_date >= end_date:
            return {
                'is_valid': False,
                'error': 'Start date must be before end date'
            }

        date_diff = end_date - start_date
        if date_diff.days > max_days:
            return {
                'is_valid': False,
                'error': f'Date range cannot exceed {max_days} days'
            }

        return {'is_valid': True}

    @staticmethod
    def sanitize_string(input_string: str, max_length: int = 1000) -> str:
        """
        Sanitize string input by removing potentially dangerous characters.

        Args:
            input_string (str): The string to sanitize.
            max_length (int): The maximum length of the sanitized string.

        Returns:
            str: The sanitized string.
        """
        logger.debug("Sanitizing string input")
        if not input_string:
            return ""

        sanitized = ''.join(char for char in input_string if ord(char) >= 32)

        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()

    @staticmethod
    def validate_numeric_range(
        value: int | float,
        min_val: int | float,
        max_val: int | float,
    ) -> bool:
        """
        Validate numeric value is within specified range.
        """
        logger.debug("Validating numeric range")
        return min_val <= value <= max_val

    @staticmethod
    def validate_string_length(
        value: str,
        min_length: int = 1,
        max_length: int = 1000,
    ) -> bool:
        """
        Validate string length is within specified range.
        """
        logger.debug("Validating string length")
        return min_length <= len(value) <= max_length


class SecurityValidators:
    """
    Security-focused validators for request data.
    """

    @staticmethod
    def validate_sql_injection_prevention(value: str) -> bool:
        """
        Basic SQL injection prevention check.
        """
        logger.debug("Validating SQL injection prevention")
        if not value:
            return True

        value_lower = value.lower()
        for pattern in RegularExpression.DANGEROUS_SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower):
                return False
        return True

    @staticmethod
    def validate_xss_prevention(value: str) -> bool:
        """
        Basic XSS prevention check.
        """
        logger.debug("Validating XSS prevention")
        if not value:
            return True

        value_lower = value.lower()
        for pattern in RegularExpression.DANGEROUS_XSS_PATTERNS:
            if re.search(pattern, value_lower):
                return False
        return True

    @staticmethod
    def validate_path_traversal_prevention(value: str) -> bool:
        """
        Prevent path traversal attacks.
        """
        logger.debug("Validating path traversal prevention")
        if not value:
            return True

        for pattern in RegularExpression.DANGEROUS_PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return False
        return True
