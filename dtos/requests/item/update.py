"""Update item request DTO.

Leaf module under ``dtos/requests/item/`` — filename is ``update.py`` (context from parent folders).
"""

from __future__ import annotations

from typing import Annotated, Optional
from uuid import uuid4

from pydantic import Field, field_validator

from dtos.requests.item.abstraction import IRequestItemDTO


class UpdateItemRequestDTO(IRequestItemDTO):
    """DTO for updating an existing item."""

    reference_urn: str = Field(default_factory=lambda: str(uuid4()))
    name: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    description: Annotated[Optional[str], Field(default=None, max_length=500)] = None

    @field_validator("name")
    @classmethod
    def _non_empty_name_if_set(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v
