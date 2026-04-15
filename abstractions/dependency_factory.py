"""Service dependency factory mixin.

Eliminates copy-paste across ``dependencies/services/**/*.py`` files whose
``derive()`` method is nothing more than a closure forwarding
``(urn, user_urn, api_name, user_id, **deps)`` into a service constructor.

Usage::

    from abstractions.dependency_factory import ServiceDependencyFactory
    from services.user.login import UserLoginService

    class UserLoginServiceDependency(ServiceDependencyFactory):
        service_cls = UserLoginService
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, ClassVar, Type

from abstractions.service import IService


class ServiceDependencyFactory:
    """Mixin for service dependency classes.

    Subclass and set ``service_cls``. :meth:`derive` returns a factory that
    forwards ``(urn, user_urn, api_name, user_id, **deps)`` into
    ``service_cls(...)``.
    """

    service_cls: ClassVar[Type[IService]]

    @classmethod
    def derive(cls) -> Callable[..., IService]:
        """Return a factory callable that builds ``cls.service_cls`` instances."""
        service_cls = cls.service_cls

        def factory(
            urn: str | None = None,
            user_urn: str | None = None,
            api_name: str | None = None,
            user_id: Any = None,
            **deps: Any,
        ) -> IService:
            return service_cls(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
                **deps,
            )

        return factory


__all__ = ["ServiceDependencyFactory"]
