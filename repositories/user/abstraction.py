"""User-domain repository abstraction."""

from typing import Any, Optional

from repositories.abstraction import IRepository


class IUserRepository(IRepository):
    """Interface for repositories under ``repositories/user``."""

    def __init__(
        self,
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Optional[str] = None,
        session: Any = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the user-domain repository base.

        Args:
            urn: Unique Request Number for tracing. Defaults to None.
            user_urn: User's URN. Defaults to None.
            api_name: API name. Defaults to None.
            user_id: User's database ID. Defaults to None.
            session: Database session when applicable. Defaults to None.
            **kwargs: Forwarded to :class:`IRepository`.

        """
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            session=session,
            **kwargs,
        )
