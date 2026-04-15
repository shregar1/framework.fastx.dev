"""Example fetch-all service."""

from typing import Any, Dict, List

from repositories.example.example_repository import ExampleRepository
from services.example.abstraction import IExampleService


class ExampleFetchAllService(IExampleService):
    """Single-verb service: fetch all example records."""

    def __init__(self, example_repo: ExampleRepository, *args: Any, **kwargs: Any):
        """Initialize with repository and forward context to parent."""
        super().__init__(*args, **kwargs)
        self.example_repo = example_repo

    async def run(self, request_dto: Any = None) -> List[Dict[str, Any]]:
        """Return all example records."""
        return self.example_repo.list_all()
