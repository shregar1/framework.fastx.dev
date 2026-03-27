"""FetchUser Service."""

from abstractions.service import IService
from dtos.requests.apis.v1.user.fetch import FetchUserRequestDTO
from repositories.user.fetch import FetchUserRepository


class FetchUserService(IService):
    """Represents the FetchUserService class."""

    def __init__(self, repo: FetchUserRepository, **kwargs):
        """Execute __init__ operation.

        Args:
            repo: The repo parameter.
        """
        super().__init__(**kwargs)
        self.repo = repo

    def run(self, request_dto: FetchUserRequestDTO) -> dict:
        """Execute run operation.

        Args:
            request_dto: The request_dto parameter.

        Returns:
            The result of the operation.
        """
        self.logger.info("Executing fetch service")
        return {"item": {"id": "1"}, "message": "Success"}
