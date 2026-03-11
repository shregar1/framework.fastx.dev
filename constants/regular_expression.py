"""
Regular Expression Patterns Module.

This module defines compiled regular expressions and pattern strings
for input validation, security checks, and data parsing. These patterns
are used throughout the application for consistent validation.

Usage:
    >>> from constants.regular_expression import RegularExpression
    >>> if RegularExpression.EMAIL_PATTERN.match(email):
    ...     print("Valid email format")
"""

import re
from typing import Final


class RegularExpression:
    """
    Collection of regular expressions for validation and security.

    This class provides pre-compiled regex patterns and pattern strings
    for common validation tasks including email, password, phone number
    validation, and security-related pattern detection.

    Attributes:
        DD_MM_YYYY (str): Pattern for date format DD/MM/YYYY.
        PASSWORD_PATTERN (Pattern): Strong password validation pattern.
        EMAIL_PATTERN (Pattern): Email address validation pattern.
        PHONE_PATTERN (Pattern): International phone number pattern.
        ALPHANUMERIC_PATTERN (Pattern): Alphanumeric with spaces/dashes.
        DANGEROUS_SQL_INJECTION_PATTERNS (list): SQL injection detection patterns.
        DANGEROUS_XSS_PATTERNS (list): XSS attack detection patterns.
        DANGEROUS_PATH_TRAVERSAL_PATTERNS (list): Path traversal detection patterns.

    Example:
        >>> from constants.regular_expression import RegularExpression
        >>>
        >>> # Validate email
        >>> if RegularExpression.EMAIL_PATTERN.match("user@example.com"):
        ...     print("Valid email")
        >>>
        >>> # Check for SQL injection
        >>> def is_safe_input(text: str) -> bool:
        ...     for pattern in RegularExpression.DANGEROUS_SQL_INJECTION_PATTERNS:
        ...         if re.search(pattern, text, re.IGNORECASE):
        ...             return False
        ...     return True

    Security Note:
        The dangerous pattern lists should be used for input sanitization
        and logging, but should not be the only line of defense against
        injection attacks. Always use parameterized queries and proper
        encoding.
    """

    DD_MM_YYYY: Final[str] = r"\b\d{2}/\d{2}/\d{4}\b"
    """
    Date pattern for DD/MM/YYYY format.

    Matches: 01/12/2024, 31/01/2025
    Does not validate actual date validity (e.g., 32/13/2024 would match).
    """

    PASSWORD_PATTERN: Final[re.Pattern] = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    )
    """
    Strong password validation pattern.

    Requirements:
        - At least 8 characters
        - At least one lowercase letter (a-z)
        - At least one uppercase letter (A-Z)
        - At least one digit (0-9)
        - At least one special character (@$!%*?&)

    Example:
        >>> RegularExpression.PASSWORD_PATTERN.match("MyP@ss1")  # None (too short)
        >>> RegularExpression.PASSWORD_PATTERN.match("MyP@ss123")  # Match
    """

    EMAIL_PATTERN: Final[re.Pattern] = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    """
    Email address validation pattern.

    Validates basic email format: local@domain.tld
    Allows: letters, numbers, dots, underscores, percent, plus, hyphen

    Example:
        >>> RegularExpression.EMAIL_PATTERN.match("user@example.com")  # Match
        >>> RegularExpression.EMAIL_PATTERN.match("invalid-email")  # None
    """

    PHONE_PATTERN: Final[re.Pattern] = re.compile(
        r'^\+?1?\d{9,15}$'
    )
    """
    International phone number pattern.

    Matches: 9-15 digits with optional + prefix and country code 1
    Follows E.164 format loosely.

    Example:
        >>> RegularExpression.PHONE_PATTERN.match("+14155552671")  # Match
        >>> RegularExpression.PHONE_PATTERN.match("4155552671")  # Match
    """

    ALPHANUMERIC_PATTERN: Final[re.Pattern] = re.compile(
        r'^[a-zA-Z0-9\s\-_]+$'
    )
    """
    Alphanumeric pattern with spaces, hyphens, and underscores.

    Useful for validating names, titles, slugs, and identifiers
    that should not contain special characters.

    Example:
        >>> RegularExpression.ALPHANUMERIC_PATTERN.match("Hello World")  # Match
        >>> RegularExpression.ALPHANUMERIC_PATTERN.match("test-item_1")  # Match
        >>> RegularExpression.ALPHANUMERIC_PATTERN.match("test@item")  # None
    """

    DANGEROUS_SQL_INJECTION_PATTERNS: Final[list[str]] = [
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|\
            execute)\b)',
        r'(\b(or|and)\b\s+\d+\s*=\s*\d+)',
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|\
            execute)\b.*\b(union|select|insert|update|delete|drop|create|\
            alter|exec|execute)\b)',
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|\
            execute)\b.*\b(union|select|insert|update|delete|drop|create|\
            alter|exec|execute)\b.*\b(union|select|insert|update|delete|\
            drop|create|alter|exec|execute)\b)',
    ]
    """
    SQL injection detection patterns.

    Detects common SQL injection attempts including:
        - SQL keywords (SELECT, INSERT, UPDATE, DELETE, DROP, etc.)
        - Boolean-based injection (OR 1=1, AND 1=1)
        - Stacked queries with multiple SQL commands

    Warning:
        These patterns are for detection/logging only. Always use
        parameterized queries as the primary defense against SQL injection.
    """

    DANGEROUS_XSS_PATTERNS: Final[list[str]] = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
    ]
    """
    Cross-Site Scripting (XSS) detection patterns.

    Detects common XSS attack vectors including:
        - Script tags (<script>...</script>)
        - JavaScript URIs (javascript:)
        - Event handlers (onclick=, onerror=, etc.)
        - Embedded content tags (iframe, object, embed)

    Warning:
        These patterns are for detection/logging only. Always use
        proper output encoding and Content Security Policy headers.
    """

    DANGEROUS_PATH_TRAVERSAL_PATTERNS: Final[list[str]] = [
        r'\.\./',
        r'\.\.\\',
        r'%2e%2e%2f',
        r'%2e%2e%5c',
    ]
    """
    Path traversal attack detection patterns.

    Detects directory traversal attempts including:
        - Unix-style: ../
        - Windows-style: ..\\
        - URL-encoded variants: %2e%2e%2f, %2e%2e%5c

    Warning:
        These patterns are for detection/logging only. Always validate
        and sanitize file paths, and use allowlists for permitted directories.
    """
