"""FetchUser V1 Response DTO."""

from pydantic import BaseModel


class FetchUserResponseDataDTO(BaseModel):
    """FetchUser response payload data."""

    id: str
    status: str = "active"
