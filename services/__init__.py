"""
Services Package.

This package contains the business logic layer of the FastMVC application.
Services implement domain operations, coordinate between repositories and
external systems, and return structured responses.

Subpackages:
    - user/: User authentication and management services
    - apis/: API feature services (versioned)

Usage:
    >>> from services.user.login import UserLoginService
    >>> from services.user.registration import UserRegistrationService
"""

