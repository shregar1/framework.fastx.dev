"""Create item request DTO.

Leaf module under ``dtos/requests/item/`` — filename is ``create.py`` (context from parent folders).
"""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from pydantic import Field, field_validator

from dtos.requests.item.abstraction import IRequestItemDTO


class CreateItemRequestDTO(IRequestItemDTO):
    """DTO for creating a new item."""

    reference_urn: str = Field(default_factory=lambda: str(uuid4()))
    name: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str, Field(default="", max_length=500)] = ""
    completed: bool = False

    @field_validator("name")
    @classmethod
    def _strip_and_require_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name is required")
        return v
