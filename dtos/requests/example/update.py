"""Example update request DTO.

One concrete request model per file; see ``dtos/README.md`` and ``docs/guide/new-api-scaffolding.md``.
"""

from pydantic import Field

from dtos.requests.example.abstraction import IRequestExampleDTO


class ExampleUpdateRequestDTO(IRequestExampleDTO):
    """Example update request payload."""

    name: str | None = Field(None, description="Updated name")
    description: str | None = Field(None, description="Updated description")
