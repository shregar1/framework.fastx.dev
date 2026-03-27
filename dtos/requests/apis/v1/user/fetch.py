"""FetchUser V1 Request DTO."""

from pydantic import Field
from dtos.requests.apis.v1.user.abstraction import IRequestUserV1DTO


class FetchUserRequestDTO(IRequestUserV1DTO):
    """FetchUser request payload."""

    name: str = Field(..., description="Name")
    description: str | None = Field(None, description="Description")
