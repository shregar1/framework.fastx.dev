"""Item-domain repository abstraction."""

from typing import Any, Optional

from repositories.abstraction import IRepository


class IItemRepository(IRepository):
    """Interface for repositories under ``repositories/item``."""

    def __init__(
        self,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Optional[str] = None,
        session: Any = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the item-domain repository base."""
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            session=session,
            **kwargs,
        )
