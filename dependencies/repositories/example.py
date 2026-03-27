"""FastAPI dependency for :class:`repositories.example.example_repository.ExampleRepository`."""

from fastapi import Request

from dependencies.repositories.abstraction import IRepositoryDependency
from repositories.example import ExampleRepository


class ExampleRepositoryDependency(IRepositoryDependency):
    """Derives an :class:`ExampleRepository` from the current request."""

    @staticmethod
    def derive(request: Request) -> ExampleRepository:
        """Build a repository instance with URN from request state."""
        urn = getattr(request.state, "urn", None)
        return ExampleRepository(urn=urn)
