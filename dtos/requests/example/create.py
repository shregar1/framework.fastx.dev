"""Example create request DTO.

One concrete request model per file; see ``dtos/README.md`` and ``docs/guide/new-api-scaffolding.md``.
"""

from pydantic import Field

from dtos.requests.example.abstraction import IRequestExampleDTO


class ExampleCreateRequestDTO(IRequestExampleDTO):
    """Example create request payload."""

    name: str = Field(..., description="Example name")
    description: str | None = Field(None, description="Example description")
