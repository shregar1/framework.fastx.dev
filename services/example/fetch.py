"""Example fetch-by-id service."""

from typing import Any, Dict, Optional

from repositories.example.example_repository import ExampleRepository
from services.example.abstraction import IExampleService


class ExampleFetchService(IExampleService):
    """Single-verb service: fetch one example record by ID."""

    def __init__(self, example_repo: ExampleRepository, *args: Any, **kwargs: Any):
        """Initialize with repository and forward context to parent."""
        super().__init__(*args, **kwargs)
        self.example_repo = example_repo

    async def run(self, request_dto: Any) -> Optional[Dict[str, Any]]:
        """Return a single example record by ID.

        ``request_dto`` may be a DTO exposing ``example_id`` or the raw ID.
        """
        example_id = getattr(request_dto, "example_id", request_dto)
        return self.example_repo.retrieve_record_by_id(example_id)
