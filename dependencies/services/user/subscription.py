"""User Subscription Service Dependency."""

from __future__ import annotations

from abstractions.dependency_factory import ServiceDependencyFactory
from services.user.subscription import UserSubscriptionService


class UserSubscriptionServiceDependency(ServiceDependencyFactory):
    """FastAPI dependency provider for UserSubscriptionService."""

    service_cls = UserSubscriptionService


__all__ = ["UserSubscriptionServiceDependency"]
