"""Example delete service."""

from typing import Any

from repositories.example.example_repository import ExampleRepository
from services.example.abstraction import IExampleService


class ExampleDeleteService(IExampleService):
    """Single-verb service: delete an example record."""

    def __init__(self, example_repo: ExampleRepository, *args: Any, **kwargs: Any):
        """Initialize with repository and forward context to parent."""
        super().__init__(*args, **kwargs)
        self.example_repo = example_repo

    async def run(self, request_dto: Any) -> bool:
        """Delete an example record.

        ``request_dto`` may be a DTO exposing ``example_id`` or the raw ID.
        """
        example_id = getattr(request_dto, "example_id", request_dto)
        item = self.example_repo.retrieve_record_by_id(example_id)
        if not item:
            return False
        return True
