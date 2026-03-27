"""Update item request DTO."""

from __future__ import annotations

from typing import Self
from uuid import uuid4

from pydantic import Field

from dtos.requests.abstraction import IRequestDTO


class UpdateItemRequestDTO(IRequestDTO):
    """DTO for updating an existing item."""

    reference_number: str = Field(default_factory=lambda: str(uuid4()))
    name: str | None = None
    description: str | None = None

    def validate(self) -> tuple[bool, list[str]]:
        errors: list[str] = []
        if self.name is not None:
            if not self.name.strip():
                errors.append("Name cannot be empty")
            elif len(self.name) > 100:
                errors.append("Name cannot exceed 100 characters")
        if self.description is not None and len(self.description) > 500:
            errors.append("Description cannot exceed 500 characters")
        return len(errors) == 0, errors

    def to_dict(self) -> dict:
        result: dict[str, str] = {}
        if self.name is not None:
            result["name"] = self.name
        if self.description is not None:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            name=data.get("name"),
            description=data.get("description"),
        )
