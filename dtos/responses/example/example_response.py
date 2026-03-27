"""Example Response Data DTO."""

from pydantic import BaseModel


class ExampleResponseDataDTO(BaseModel):
    """Example response payload data."""

    id: str
    name: str
    description: str | None = None
    status: str = "active"
