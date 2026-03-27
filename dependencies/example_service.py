"""Example Service Dependency."""

from typing import Callable
from fastapi import Request, Depends
from abstractions.dependency import IDependency
from services.example_service import ExampleService
from dependencies.example_repository import ExampleRepositoryDependency
from repositories.example_repository import ExampleRepository


class ExampleServiceDependency(IDependency):
    """Dependency for ExampleService."""

    @staticmethod
    def derive(
        request: Request,
        repository: ExampleRepository = Depends(ExampleRepositoryDependency.derive),
    ) -> ExampleService:
        """Derive the service instance."""
        urn = getattr(request.state, "urn", None)
        user_urn = getattr(request.state, "user_urn", None)
        user_id = getattr(request.state, "user_id", None)

        return ExampleService(
            example_repo=repository,
            urn=urn,
            user_urn=user_urn,
            user_id=user_id,
            api_name="example_api",
        )
