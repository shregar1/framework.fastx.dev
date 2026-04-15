"""Example Service Dependency.

Returns a factory callable that, when invoked with request context and a
repository, produces an
:class:`~services.example.create.ExampleCreateService`.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from dependencies.services.v1.example.abstraction import IExampleServiceDependency
from start_utils import logger


class ExampleServiceDependency(IExampleServiceDependency):
    """FastAPI dependency provider for ExampleCreateService."""

    @staticmethod
    def derive() -> Callable:
        """Return a factory for creating ExampleCreateService instances.

        Returns:
            Callable: Factory with signature
                ``factory(urn, user_urn, api_name, user_id, example_repo) -> ExampleCreateService``.
        """
        logger.debug("ExampleServiceDependency factory created")

        def factory(
            urn: str | None = None,
            user_urn: str | None = None,
            api_name: str | None = None,
            user_id: Any = None,
            example_repo: Any = None,
        ) -> Any:
            """Create an ExampleCreateService instance with request context."""
            from services.example.create import ExampleCreateService

            logger.info("Instantiating ExampleCreateService")
            return ExampleCreateService(
                example_repo=example_repo,
                urn=urn,
                user_urn=user_urn,
                api_name=api_name or "example_api",
                user_id=user_id,
            )

        return factory


# Aliases for sibling single-verb services. Each follows the same factory
# shape as ExampleServiceDependency but instantiates a different service.


class ExampleCreateServiceDependency(IExampleServiceDependency):
    """FastAPI dependency provider for ExampleCreateService."""

    @staticmethod
    def derive() -> Callable:
        """Return a factory for ExampleCreateService."""
        def factory(
            urn: str | None = None,
            user_urn: str | None = None,
            api_name: str | None = None,
            user_id: Any = None,
            example_repo: Any = None,
        ) -> Any:
            from services.example.create import ExampleCreateService

            return ExampleCreateService(
                example_repo=example_repo,
                urn=urn,
                user_urn=user_urn,
                api_name=api_name or "example_api",
                user_id=user_id,
            )

        return factory


class ExampleFetchAllServiceDependency(IExampleServiceDependency):
    """FastAPI dependency provider for ExampleFetchAllService."""

    @staticmethod
    def derive() -> Callable:
        """Return a factory for ExampleFetchAllService."""
        def factory(
            urn: str | None = None,
            user_urn: str | None = None,
            api_name: str | None = None,
            user_id: Any = None,
            example_repo: Any = None,
        ) -> Any:
            from services.example.fetch_all import ExampleFetchAllService

            return ExampleFetchAllService(
                example_repo=example_repo,
                urn=urn,
                user_urn=user_urn,
                api_name=api_name or "example_api",
                user_id=user_id,
            )

        return factory


class ExampleFetchServiceDependency(IExampleServiceDependency):
    """FastAPI dependency provider for ExampleFetchService."""

    @staticmethod
    def derive() -> Callable:
        """Return a factory for ExampleFetchService."""
        def factory(
            urn: str | None = None,
            user_urn: str | None = None,
            api_name: str | None = None,
            user_id: Any = None,
            example_repo: Any = None,
        ) -> Any:
            from services.example.fetch import ExampleFetchService

            return ExampleFetchService(
                example_repo=example_repo,
                urn=urn,
                user_urn=user_urn,
                api_name=api_name or "example_api",
                user_id=user_id,
            )

        return factory


class ExampleUpdateServiceDependency(IExampleServiceDependency):
    """FastAPI dependency provider for ExampleUpdateService."""

    @staticmethod
    def derive() -> Callable:
        """Return a factory for ExampleUpdateService."""
        def factory(
            urn: str | None = None,
            user_urn: str | None = None,
            api_name: str | None = None,
            user_id: Any = None,
            example_repo: Any = None,
        ) -> Any:
            from services.example.update import ExampleUpdateService

            return ExampleUpdateService(
                example_repo=example_repo,
                urn=urn,
                user_urn=user_urn,
                api_name=api_name or "example_api",
                user_id=user_id,
            )

        return factory


class ExampleDeleteServiceDependency(IExampleServiceDependency):
    """FastAPI dependency provider for ExampleDeleteService."""

    @staticmethod
    def derive() -> Callable:
        """Return a factory for ExampleDeleteService."""
        def factory(
            urn: str | None = None,
            user_urn: str | None = None,
            api_name: str | None = None,
            user_id: Any = None,
            example_repo: Any = None,
        ) -> Any:
            from services.example.delete import ExampleDeleteService

            return ExampleDeleteService(
                example_repo=example_repo,
                urn=urn,
                user_urn=user_urn,
                api_name=api_name or "example_api",
                user_id=user_id,
            )

        return factory


__all__ = [
    "ExampleServiceDependency",
    "ExampleCreateServiceDependency",
    "ExampleFetchAllServiceDependency",
    "ExampleFetchServiceDependency",
    "ExampleUpdateServiceDependency",
    "ExampleDeleteServiceDependency",
]
