"""Example Controller."""

from typing import Any
from abstractions.controller import IController
from dtos.requests.example.example_request import ExampleCreateRequestDTO
from dtos.responses.example.example_response import ExampleResponseDataDTO
from dtos.responses.base import BaseResponseDTO
from constants.api_status import APIStatus
from services.example_service import ExampleService
from repositories.example_repository import ExampleRepository


class ExampleController(IController):
    """Example class-based controller.
    Demonstrates the full FastMVC flow from DTO to Service to Repository.
    """

    async def handle_create_example(
        self,
        urn: str,
        user_urn: str,
        payload: dict,
        headers: dict,
        api_name: str,
        user_id: str,
    ) -> BaseResponseDTO:
        """Handle a POST request to create an example item."""
        # 1. Initialize Context & Validate Request Structure
        await self.validate_request(
            urn=urn,
            user_urn=user_urn,
            request_payload=payload,
            request_headers=headers,
            api_name=api_name,
            user_id=user_id,
        )

        self.logger.info("Handling create example request")

        # 2. Parse payload into Request DTO
        # Note: In a real app, middleware or a factory might do this.
        request_dto = ExampleCreateRequestDTO(**payload)

        # 3. Setup Dependencies
        # Note: Typically handled by a Dependency Provider / IoC Container
        repo = ExampleRepository(urn=urn, logger=self.logger)
        service = ExampleService(
            example_repo=repo,
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            logger=self.logger,
        )

        # 4. Execute Service Logic
        result = service.run(request_dto)

        # 5. Prepare Response Data DTO
        response_data = ExampleResponseDataDTO(**result["item"])

        # 6. Return Standard BaseResponseDTO
        return BaseResponseDTO(
            transactionUrn=urn,
            status=APIStatus.SUCCESS,
            responseMessage=result["message"],
            responseKey="success_example_created",
            data=response_data.model_dump(),
        )
