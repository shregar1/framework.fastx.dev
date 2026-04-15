"""Example create service."""

from typing import Any

from dtos.requests.example import ExampleCreateRequestDTO
from repositories.example.example_repository import ExampleRepository
from services.example.abstraction import IExampleService


class ExampleCreateService(IExampleService):
    """Single-verb service: create an example record."""

    def __init__(self, example_repo: ExampleRepository, *args: Any, **kwargs: Any):
        """Initialize with repository and forward context to parent."""
        super().__init__(*args, **kwargs)
        self.example_repo = example_repo

    async def run(self, request_dto: ExampleCreateRequestDTO) -> dict:
        """Execute example business logic for creation."""
        self.logger.info(f"Processing example request for: {request_dto.name}")

        new_record = self.example_repo.create_record(
            {"name": request_dto.name, "description": request_dto.description}
        )

        self.logger.info(
            f"Successfully created example record with ID: {new_record['id']}"
        )

        return {"item": new_record, "message": "Example processed successfully"}
