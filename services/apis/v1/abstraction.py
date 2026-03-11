from pydantic import BaseModel

from dtos.responses.base import BaseResponseDTO
from services.apis.abstraction import IAPIService


class IV1APIService(IAPIService):
    """
    Abstract base class for v1 API services.
    Provides shared logic for v1 endpoints.
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
            f"IV1APIService initialized for "
            f"user_id={user_id}, urn={urn}, api_name={api_name}"
        )

    def run(self, request_dto: BaseModel) -> BaseResponseDTO:
        pass
