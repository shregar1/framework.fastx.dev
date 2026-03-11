"""
Product Create Request DTO.

This module defines the request DTO for creating new products.
"""


from pydantic import field_validator

from dtos.base import EnhancedBaseModel
from dtos.requests.abstraction import IRequestDTO


class ProductCreateRequestDTO(IRequestDTO, EnhancedBaseModel):
    """
    Request DTO for creating a new product.

    Attributes:
        reference_number (str): Client-provided request tracking ID.
        name (str): Product name.
        description (str): Optional description.
    """

    name: str
    description: str | None = None

    class Config:
        extra = "forbid"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and sanitize name."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        if len(v) > 255:
            raise ValueError("Name cannot exceed 255 characters")
        return v.strip()
