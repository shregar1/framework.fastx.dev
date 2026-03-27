"""Response DTO abstraction module.

Layered response DTOs should inherit from :class:`IResponseDTO` or nested
Is under ``dtos.responses.*.abstraction`` so the chain terminates at
:class:`abstractions.dto.AbstractResponseDTO` via :class:`dtos.responses.I.IResponseDTO`.
"""

from abstractions.dto import AbstractResponseDTO
from dtos.responses.I import IResponseDTO


class IResponseDTO(IResponseDTO, AbstractResponseDTO):
    """Standard API response envelope combining Pydantic and framework contracts."""
