"""MFA Service Dependency."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from services.mfa import MFAService
from start_utils import logger


class MFAServiceDependency:
    """FastAPI dependency provider for MFAService."""

    @classmethod
    def derive(cls) -> Callable:
        """Return a factory for creating MFAService instances."""
        logger.debug("MFAServiceDependency factory created")

        def factory(
            urn: str | None = None,
            user_urn: str | None = None,
            api_name: str | None = None,
            user_id: Any = None,
        ) -> MFAService:
            return MFAService(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=int(user_id) if user_id else None,
            )

        return factory


__all__ = ["MFAServiceDependency"]
