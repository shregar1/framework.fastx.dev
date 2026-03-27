"""Example Service."""

from typing import Dict, List, Optional, Any
from abstractions.service import IService
from dtos.requests.example.example_request import (
    ExampleCreateRequestDTO,
    ExampleUpdateRequestDTO,
)
from repositories.example_repository import ExampleRepository


class ExampleService(IService):
    """Example business logic service.
    Orchestrates between repository and controllers.
    """

    def __init__(self, example_repo: ExampleRepository, **kwargs):
        """Execute __init__ operation.

        Args:
            example_repo: The example_repo parameter.
        """
        super().__init__(**kwargs)
        self.example_repo = example_repo

    def run(self, request_dto: ExampleCreateRequestDTO) -> dict:
        """Execute example business logic for creation."""
        self.logger.info(f"Processing example request for: {request_dto.name}")

        # Call repository
        new_record = self.example_repo.create_record(
            {"name": request_dto.name, "description": request_dto.description}
        )

        self.logger.info(
            f"Successfully created example record with ID: {new_record['id']}"
        )

        return {"item": new_record, "message": "Example processed successfully"}

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all examples."""
        return self.example_repo.list_all()

    def get_by_id(self, example_id: str) -> Optional[Dict[str, Any]]:
        """Get example by ID."""
        return self.example_repo.retrieve_record_by_id(example_id)

    def update(
        self, example_id: str, request_dto: ExampleUpdateRequestDTO
    ) -> Optional[Dict[str, Any]]:
        """Update example."""
        item = self.example_repo.retrieve_record_by_id(example_id)
        if not item:
            return None

        if request_dto.name:
            item["name"] = request_dto.name
        if request_dto.description:
            item["description"] = request_dto.description

        return item

    def delete(self, example_id: str) -> bool:
        """Delete example."""
        item = self.example_repo.retrieve_record_by_id(example_id)
        if not item:
            return False
        # In actual repo we would remove it from list
        return True
