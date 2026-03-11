"""
User Controller Abstraction Module.

This module defines the base abstraction for all user-related controllers.
It extends the core IController interface with user-specific initialization.

Example:
    >>> class MyUserController(IUserController):
    ...     async def post(self, request: Request):
    ...         # Handle user operation
    ...         pass
"""

from abstractions.controller import IController
from start_utils import logger


class IUserController(IController):
    """
    Base abstraction for all user controllers.

    This class extends IController to provide user-specific functionality.
    All controllers handling /user/* routes should inherit from this class.

    Features:
        - Automatic debug logging on initialization
        - Request context propagation (URN, user info)
        - Structured logging with user context

    Attributes:
        Inherits all attributes from IController:
            - urn (str): Unique Request Number
            - user_urn (str): User's unique resource name
            - api_name (str): Name of the API endpoint
            - user_id (int): Database ID of the user
            - logger: Structured logger instance

    Example:
        >>> class PasswordResetController(IUserController):
        ...     def __init__(self, urn: str = None):
        ...         super().__init__(urn=urn, api_name="PASSWORD_RESET")
        ...
        ...     async def post(self, request: Request) -> JSONResponse:
        ...         self.logger.info("Processing password reset")
        ...         # Implementation
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
    ) -> None:
        """
        Initialize the user controller.

        Args:
            urn (str, optional): Unique Request Number. Defaults to None.
            user_urn (str, optional): User's unique resource name. Defaults to None.
            api_name (str, optional): Name of the API endpoint. Defaults to None.
            user_id (int, optional): Database ID of the user. Defaults to None.
        """
        logger.debug("Initializing IUserController")
        super().__init__(urn, user_urn, api_name, user_id)
