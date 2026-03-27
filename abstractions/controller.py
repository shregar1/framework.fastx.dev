"""Controller Abstraction Module.

This module defines the I controller interface that all API controllers
must inherit from. Controllers handle HTTP request validation, orchestrate
service calls, and format responses.

Example:
    >>> class UserLoginController(IController):
    ...     async def validate_request(self, urn, user_urn, request_payload, ...):
    ...         await super().validate_request(...)
    ...         # Custom validation logic

"""

from abc import ABC
from typing import Any

from core.utils.context import ContextMixin


class IController(ABC, ContextMixin):
    """Abstract I class for all API controllers.

    The IController provides a standardized interface for handling HTTP requests
    in the FastMVC framework. It includes request context tracking (URN, user info),
    structured logging, and request validation hooks.

    Attributes:
        urn (str): Unique Request Number - a unique identifier for each request,
            used for distributed tracing and log correlation.
        user_urn (str): User's unique resource name for identifying the requester.
        api_name (str): Name of the API endpoint being called.
        user_id (str): DataI identifier of the authenticated user.
        logger: Structured logger instance bound with request context.

    Example:
        >>> class MyController(IController):
        ...     def __init__(self, urn: str, user_urn: str):
        ...         super().__init__(urn=urn, user_urn=user_urn)
        ...
        ...     async def validate_request(self, ...):
        ...         await super().validate_request(...)
        ...         # Add custom validation

    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the controller with request context.

        Args:
            urn (str, optional): Unique Request Number for tracing. Defaults to None.
            user_urn (str, optional): User's unique resource name. Defaults to None.
            api_name (str, optional): Name of the API endpoint. Defaults to None.
            user_id (str, optional): DataI ID of the user. Defaults to None.
            **kwargs: Additional arguments for parent classes.

        """
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            **kwargs,
        )

    async def validate_request(
        self,
        urn: str,
        user_urn: str,
        request_payload: dict,
        request_headers: dict,
        api_name: str,
        user_id: str,
    ) -> None:
        """Validate and process incoming HTTP request.

        This method should be called at the start of each controller action
        to set up the request context and perform validation. Subclasses
        should call super().validate_request() and add custom validation.

        Args:
            urn (str): Unique Request Number for this request.
            user_urn (str): User's unique resource name.
            request_payload (dict): Parsed request body/payload.
            request_headers (dict): HTTP request headers.
            api_name (str): Name of the API endpoint.
            user_id (str): DataI ID of the authenticated user.

        Returns:
            None

        Raises:
            BadInputError: If validation fails (in subclass implementations).

        Example:
            >>> async def validate_request(self, ...):
            ...     await super().validate_request(...)
            ...     if not request_payload.get('email'):
            ...         raise BadInputError("Email is required")

        """
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name
        self.user_id = user_id
        return
