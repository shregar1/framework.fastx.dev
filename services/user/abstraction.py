from pydantic import BaseModel

from abstractions.service import IService
from dtos.responses.base import BaseResponseDTO


class IUserService(IService):
    """
    Abstract base class for user services.
    Provides shared logic for user-related service endpoints.
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
    ) -> None:
        super().__init__(urn, user_urn, api_name, user_id)
        self.logger.debug(
            f"IUserService initialized for "
            f"user_id={user_id}, urn={urn}, api_name={api_name}"
        )

    def run(self, request_dto: BaseModel) -> BaseResponseDTO:
        pass
