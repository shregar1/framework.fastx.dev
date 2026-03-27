"""Example Repository Dependency."""

from fastapi import Request
from abstractions.dependency import IDependency
from repositories.example_repository import ExampleRepository


class ExampleRepositoryDependency(IDependency):
    """Dependency for ExampleRepository."""

    @staticmethod
    def derive(request: Request) -> ExampleRepository:
        """Derive the repository instance."""
        urn = getattr(request.state, "urn", None)
        return ExampleRepository(urn=urn)
