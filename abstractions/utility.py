"""
Utility Abstraction Module.

This module defines the base utility interface for reusable helper
components. Utilities provide cross-cutting functionality like
data transformation, validation, and external integrations.

Example:
    >>> class JWTUtility(IUtility):
    ...     def __init__(self, secret_key: str, **kwargs):
    ...         super().__init__(**kwargs)
    ...         self.secret_key = secret_key
    ...
    ...     def generate_token(self, payload: dict) -> str:
    ...         return jwt.encode(payload, self.secret_key)
"""

from abc import ABC

from loguru import logger


class IUtility(ABC):
    """
    Abstract base class for utility/helper components.

    The IUtility class provides a standardized interface for creating
    reusable utility components in the FastMVC framework. Utilities
    encapsulate common functionality used across multiple services.

    Common use cases:
        - Data transformation and formatting
        - Validation helpers
        - Encryption/decryption utilities
        - External API wrappers
        - File handling utilities

    Attributes:
        urn (str): Unique Request Number for tracing.
        user_urn (str): User's unique resource name.
        api_name (str): Name of the API endpoint.
        user_id (str): Database identifier of the user.
        logger: Structured logger bound with utility context.

    Example:
        >>> class EmailUtility(IUtility):
        ...     def __init__(self, smtp_config: dict, **kwargs):
        ...         super().__init__(**kwargs)
        ...         self.smtp_config = smtp_config
        ...
        ...     def send_email(self, to: str, subject: str, body: str) -> bool:
        ...         # Email sending logic
        ...         self.logger.info(f"Sending email to {to}")
        ...         return True
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ) -> None:
        """
        Initialize the utility with request context.

        Args:
            urn (str, optional): Unique Request Number for tracing. Defaults to None.
            user_urn (str, optional): User's unique resource name. Defaults to None.
            api_name (str, optional): Name of the API endpoint. Defaults to None.
            user_id (str, optional): Database ID of the user. Defaults to None.
        """
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._logger = logger.bind(
            urn=self._urn,
            user_urn=self._user_urn,
            api_name=self._api_name,
            user_id=self._user_id,
        )

    @property
    def urn(self) -> str:
        """str: Get the Unique Request Number."""
        return self._urn

    @urn.setter
    def urn(self, value: str) -> None:
        """Set the Unique Request Number."""
        self._urn = value

    @property
    def user_urn(self) -> str:
        """str: Get the user's unique resource name."""
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value: str) -> None:
        """Set the user's unique resource name."""
        self._user_urn = value

    @property
    def api_name(self) -> str:
        """str: Get the API endpoint name."""
        return self._api_name

    @api_name.setter
    def api_name(self, value: str) -> None:
        """Set the API endpoint name."""
        self._api_name = value

    @property
    def logger(self):
        """loguru.Logger: Get the structured logger instance."""
        return self._logger

    @logger.setter
    def logger(self, value) -> None:
        """Set the structured logger instance."""
        self._logger = value

    @property
    def user_id(self) -> str:
        """str: Get the user's database identifier."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        """Set the user's database identifier."""
        self._user_id = value
