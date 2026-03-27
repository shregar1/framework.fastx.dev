"""Abstraction for v1 API controllers."""

from typing import Any

from controllers.apis.abstraction import IAPIController


class IAPIV1Controller(IAPIController):
    """Interface for v1 API controllers."""

    def __init__(
        self,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the v1 API controller base.

        Args:
            urn: Unique Request Number for tracing. Defaults to None.
            user_urn: User's URN. Defaults to None.
            api_name: API name. Defaults to None.
            user_id: User's database ID. Defaults to None.
            **kwargs: Forwarded to :class:`IAPIController`.

        """
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            **kwargs,
        )
