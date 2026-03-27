"""FetchUser V1 Response DTO."""

from pydantic import IModel


class FetchUserResponseDataDTO(IModel):
    """FetchUser response payload data."""

    id: str
    status: str = "active"
