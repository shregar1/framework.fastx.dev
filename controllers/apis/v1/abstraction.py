"""
API Version 1 Controller Abstraction Module.

This module defines the base abstraction for all v1 API controllers.
It extends IAPIController with v1-specific initialization and logging.

Example:
    >>> class MyV1Controller(IV1APIController):
    ...     async def get(self, request: Request):
    ...         # Handle GET request for v1 API
    ...         pass
"""

from controllers.apis.abstraction import IAPIController
from start_utils import logger


class IV1APIController(IAPIController):
    """
    Base abstraction for all API v1 controllers.

    This class extends IAPIController to provide v1-specific functionality.
    All controllers handling /api/v1/* routes should inherit from this class.

    This abstraction layer allows for version-specific behavior, such as:
        - v1-specific request/response formats
        - Version-specific middleware or validation
        - Deprecation handling for v1 endpoints

    Attributes:
        Inherits all attributes from IAPIController and IController:
            - urn (str): Unique Request Number
            - user_urn (str): User's unique resource name
            - api_name (str): Name of the API endpoint
            - user_id (int): Database ID of the user
            - logger: Structured logger instance

    Example:
        >>> class OrderController(IV1APIController):
        ...     def __init__(self, urn: str = None):
        ...         super().__init__(urn=urn, api_name="ORDER_CREATE")
        ...
        ...     async def post(self, request: Request) -> JSONResponse:
        ...         self.logger.info("Creating order")
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
        Initialize the v1 API controller.

        Args:
            urn (str, optional): Unique Request Number. Defaults to None.
            user_urn (str, optional): User's unique resource name. Defaults to None.
            api_name (str, optional): Name of the API endpoint. Defaults to None.
            user_id (int, optional): Database ID of the user. Defaults to None.
        """
        logger.debug("Initializing IV1APIController")
        super().__init__(urn, user_urn, api_name, user_id)
