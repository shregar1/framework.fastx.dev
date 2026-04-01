"""Create-example API controller (v1)."""

from fastapi import Request

from constants.api_status import APIStatus
from controllers.apis.v1.example.abstraction import IExampleAPIController
from dependencies.repositories.example.example_repository_dependency import (
    ExampleRepositoryDependency,
)
from dependencies.services.v1.example.example_service_dependency import (
    ExampleServiceDependency,
)
from dtos.requests.example.create import ExampleCreateRequestDTO
from dtos.responses.abstraction import IResponseDTO
from dtos.responses.example.example_response import ExampleResponseDataDTO


class ExampleCreateController(IExampleAPIController):
    """Handles POST create example — DTO → service → response."""

    async def handle_create_example(
        self,
        request: Request,
        urn: str,
        user_urn: str,
        payload: dict,
        headers: dict,
        api_name: str,
        user_id: str,
    ) -> IResponseDTO:
        """Handle a POST request to create an example item."""
        await self.validate_request(
            urn=urn,
            user_urn=user_urn,
            request_payload=payload,
            request_headers=headers,
            api_name=api_name,
            user_id=user_id,
        )

        self.logger.info("Handling create example request")

        request_dto = ExampleCreateRequestDTO(**payload)

        repository = ExampleRepositoryDependency.derive(request)
        service = ExampleServiceDependency.derive(request, repository=repository)

        result = service.run(request_dto)

        response_data = ExampleResponseDataDTO(**result["item"])

        return IResponseDTO(
            transactionUrn=urn,
            status=APIStatus.SUCCESS,
            responseMessage=result["message"],
            responseKey="success_example_created",
            data=response_data.model_dump(),
            reference_urn=request_dto.reference_urn,
        )
