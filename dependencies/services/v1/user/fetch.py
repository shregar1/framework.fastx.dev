"""FetchUser Dependencies."""

from fastapi import Request
from abstractions.dependency import IDependency
from services.user.fetch import FetchUserService
from repositories.user.fetch import FetchUserRepository


class FetchUserServiceDependency(IDependency):
    """Represents the FetchUserServiceDependency class."""

    @staticmethod
    def derive(request: Request) -> FetchUserService:
        """Execute derive operation.

        Args:
            request: The request parameter.

        Returns:
            The result of the operation.
        """
        repo = FetchUserRepository(urn=getattr(request.state, "urn", None))
        return FetchUserService(repo=repo, urn=getattr(request.state, "urn", None))
