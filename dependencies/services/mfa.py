"""MFA Utility Dependency."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from utilities.mfa import MFAUtility
from start_utils import logger


class MFAUtilityDependency:
    """FastAPI dependency provider for MFAUtility."""

    @classmethod
    def derive(cls) -> Callable:
        """Return a factory for creating MFAUtility instances."""
        logger.debug("MFAUtilityDependency factory created")

        def factory(
            urn: str | None = None,
            user_urn: str | None = None,
            api_name: str | None = None,
            user_id: Any = None,
        ) -> MFAUtility:
            return MFAUtility(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=int(user_id) if user_id else None,
            )

        return factory


# Backwards compatibility alias
MFAServiceDependency = MFAUtilityDependency

__all__ = ["MFAUtilityDependency", "MFAServiceDependency"]
