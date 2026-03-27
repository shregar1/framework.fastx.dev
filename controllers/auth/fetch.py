"""FetchUser Core Controller."""

from controllers.auth.abstraction import IAuthController
from services.user.fetch import FetchUserService
from dtos.requests.apis.v1.user.fetch import FetchUserRequestDTO
from dtos.responses.I import IResponseDTO
from constants.api_status import APIStatus


class FetchUserController(IAuthController):
    """Represents the FetchUserController class."""

    async def handle(self, urn, payload, api_name) -> IResponseDTO:
        """Execute handle operation.

        Args:
            urn: The urn parameter.
            payload: The payload parameter.
            api_name: The api_name parameter.

        Returns:
            The result of the operation.
        """
        await self.validate_request(urn=urn, request_payload=payload, api_name=api_name)
        return IResponseDTO(status=APIStatus.SUCCESS, responseMessage="Flow check")
