"""
API Controller Abstraction Module.

This module defines the base abstraction for all API controllers.
It extends the core IController interface with API-specific
initialization and logging.

Example:
    >>> class MyAPIController(IAPIController):
    ...     async def get(self, request: Request):
    ...         # Handle GET request
    ...         pass
"""

from abstractions.controller import IController
from start_utils import logger


class IAPIController(IController):
    """
    Base abstraction for all API controllers.

    This class extends IController to provide API-specific functionality.
    All controllers handling /api/* routes should inherit from this class.

    Features:
        - Automatic debug logging on initialization
        - Request context propagation (URN, user info)
        - Structured logging with API context

    Attributes:
        Inherits all attributes from IController:
            - urn (str): Unique Request Number
            - user_urn (str): User's unique resource name
            - api_name (str): Name of the API endpoint
            - user_id (int): Database ID of the user
            - logger: Structured logger instance

    Example:
        >>> class ProductController(IAPIController):
        ...     def __init__(self, urn: str = None):
        ...         super().__init__(urn=urn, api_name="PRODUCT_LIST")
        ...
        ...     async def get(self, request: Request) -> JSONResponse:
        ...         self.logger.info("Fetching products")
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
        Initialize the API controller.

        Args:
            urn (str, optional): Unique Request Number. Defaults to None.
            user_urn (str, optional): User's unique resource name. Defaults to None.
            api_name (str, optional): Name of the API endpoint. Defaults to None.
            user_id (int, optional): Database ID of the user. Defaults to None.
        """
        logger.debug("Initializing IAPIController")
        super().__init__(urn, user_urn, api_name, user_id)
