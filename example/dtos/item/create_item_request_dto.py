"""Create item request DTO."""

from __future__ import annotations

from typing import Self
from uuid import uuid4

from pydantic import Field

from dtos.requests.abstraction import IRequestDTO


class CreateItemRequestDTO(IRequestDTO):
    """DTO for creating a new item."""

    reference_number: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    completed: bool = False

    def validate(self) -> tuple[bool, list[str]]:
        errors: list[str] = []
        if not self.name or not self.name.strip():
            errors.append("Name is required")
        elif len(self.name) > 100:
            errors.append("Name cannot exceed 100 characters")
        if len(self.description) > 500:
            errors.append("Description cannot exceed 500 characters")
        return len(errors) == 0, errors

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            completed=data.get("completed", False),
        )
