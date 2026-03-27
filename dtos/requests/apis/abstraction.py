"""Request DTO abstraction for ``controllers/apis``-aligned payloads."""

from dtos.requests.abstraction import IRequestDTO


class IRequestAPIDTO(IRequestDTO):
    """Interface for REST API request DTOs under ``dtos/requests/apis``."""
