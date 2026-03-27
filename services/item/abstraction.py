"""Item-domain service abstraction."""

from typing import Any, Optional

from services.abstraction import IService


class IItemService(IService):
    """Interface for services under ``services/item``."""

    def __init__(
        self,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the item-domain service base."""
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            **kwargs,
        )
