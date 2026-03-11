"""
Product Service Abstraction.

This module defines the base interface for Product services.
"""

from loguru import logger

from abstractions.service import IService


class IProductService(IService):
    """
    Abstract base class for Product services.
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
    ):
        """Initialize service with request context."""
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self.logger = logger.bind(service=self.__class__.__name__)

    @property
    def urn(self) -> str:
        return self._urn

    @urn.setter
    def urn(self, value: str):
        self._urn = value
