"""Example Response Data DTO."""

from pydantic import IModel


class ExampleResponseDataDTO(IModel):
    """Example response payload data."""

    id: str
    name: str
    description: str | None = None
    status: str = "active"
