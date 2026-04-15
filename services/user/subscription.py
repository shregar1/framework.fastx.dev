"""User Subscription Service."""

from __future__ import annotations

from typing import Any

from constants.api_status import APIStatus
from dtos.responses.base import BaseResponseDTO
from services.user.abstraction import IUserService


class UserSubscriptionService(IUserService):
    """Returns the current user's active subscription."""

    def __init__(
        self,
        subscription_repository: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.subscription_repository = subscription_repository

    async def run(self, request_dto: Any = None) -> BaseResponseDTO:
        """Alias for :meth:`get_current`."""
        return await self.get_current()

    async def get_current(self) -> BaseResponseDTO:
        """Get the current user's active subscription."""
        subscription = None
        if self.subscription_repository and self.user_id:
            try:
                subscription = self.subscription_repository.get_active_for_user(
                    user_id=self.user_id
                )
            except Exception:
                pass

        if subscription is None:
            return BaseResponseDTO(
                transactionUrn=self.urn or "",
                status=APIStatus.SUCCESS,
                responseMessage="No active subscription.",
                responseKey="success_no_subscription",
                data={"subscription": None},
            )

        sub_data = {
            "id": getattr(subscription, "id", None),
            "urn": getattr(subscription, "urn", None),
            "user_id": getattr(subscription, "user_id", None),
            "organization_id": getattr(subscription, "organization_id", None),
            "plan_code": getattr(subscription, "plan_code", None),
            "status": getattr(subscription, "status", None),
            "start_date": (
                subscription.start_date.isoformat()
                if getattr(subscription, "start_date", None)
                else None
            ),
            "end_date": (
                subscription.end_date.isoformat()
                if getattr(subscription, "end_date", None)
                else None
            ),
            "grace_period_ends_at": (
                subscription.grace_period_ends_at.isoformat()
                if getattr(subscription, "grace_period_ends_at", None)
                else None
            ),
            "is_deleted": getattr(subscription, "is_deleted", None),
            "created_at": (
                subscription.created_at.isoformat()
                if getattr(subscription, "created_at", None)
                else None
            ),
            "updated_at": (
                subscription.updated_at.isoformat()
                if getattr(subscription, "updated_at", None)
                else None
            ),
        }

        return BaseResponseDTO(
            transactionUrn=self.urn or "",
            status=APIStatus.SUCCESS,
            responseMessage="Subscription retrieved.",
            responseKey="success_get_subscription",
            data={"subscription": sub_data},
        )


__all__ = ["UserSubscriptionService"]
