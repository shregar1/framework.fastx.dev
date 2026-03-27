"""FetchUser Core Controller."""

from abstractions.controller import IController
from services.user.fetch import FetchUserService
from dtos.requests.apis.v1.user.fetch import FetchUserRequestDTO
from dtos.responses.base import BaseResponseDTO
from constants.api_status import APIStatus


class FetchUserController(IController):
    """Represents the FetchUserController class."""

    async def handle(self, urn, payload, api_name) -> BaseResponseDTO:
        """Execute handle operation.

        Args:
            urn: The urn parameter.
            payload: The payload parameter.
            api_name: The api_name parameter.

        Returns:
            The result of the operation.
        """
        await self.validate_request(urn=urn, request_payload=payload, api_name=api_name)
        return BaseResponseDTO(status=APIStatus.SUCCESS, responseMessage="Flow check")
