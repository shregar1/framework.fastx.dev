"""Example update service."""

from typing import Any, Dict, Optional

from dtos.requests.example import ExampleUpdateRequestDTO
from repositories.example.example_repository import ExampleRepository
from services.example.abstraction import IExampleService


class ExampleUpdateService(IExampleService):
    """Single-verb service: update an example record."""

    def __init__(self, example_repo: ExampleRepository, *args: Any, **kwargs: Any):
        """Initialize with repository and forward context to parent."""
        super().__init__(*args, **kwargs)
        self.example_repo = example_repo

    async def run(
        self, request_dto: ExampleUpdateRequestDTO
    ) -> Optional[Dict[str, Any]]:
        """Update an example record identified by ``request_dto.example_id``."""
        example_id = getattr(request_dto, "example_id", None)
        item = self.example_repo.retrieve_record_by_id(example_id)
        if not item:
            return None

        if request_dto.name:
            item["name"] = request_dto.name
        if request_dto.description:
            item["description"] = request_dto.description

        return item
