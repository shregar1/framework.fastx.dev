"""Example Request DTOs."""

from pydantic import Field
from dtos.requests.example.abstraction import IRequestExampleDTO


class ExampleCreateRequestDTO(IRequestExampleDTO):
    """Example create request payload."""

    name: str = Field(..., description="Example name")
    description: str | None = Field(None, description="Example description")


class ExampleUpdateRequestDTO(IRequestExampleDTO):
    """Example update request payload."""

    name: str | None = Field(None, description="Updated name")
    description: str | None = Field(None, description="Updated description")
