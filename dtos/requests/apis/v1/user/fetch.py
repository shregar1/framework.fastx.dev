"""FetchUser V1 Request DTO."""

from pydantic import Field
from dtos.requests.abstraction import IRequestDTO


class FetchUserRequestDTO(IRequestDTO):
    """FetchUser request payload."""

    name: str = Field(..., description="Name")
    description: str | None = Field(None, description="Description")
