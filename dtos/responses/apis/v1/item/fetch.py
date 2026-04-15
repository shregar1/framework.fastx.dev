"""Item V1 Response DTO.

Serialization DTO for :class:`models.item.Item`. ORM / domain models only
carry schema; converting a domain entity to a JSON-ready payload is the
response DTO's job.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from models.item import Item


class ItemResponseDTO(BaseModel):
    """Item response payload (flat JSON body for sample CRUD)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: Item) -> "ItemResponseDTO":
        """Build a response DTO from a domain :class:`Item` entity."""
        return cls(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            completed=entity.completed,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_payload(self) -> dict[str, Any]:
        """Return a JSON-serializable dict (ISO-formatted timestamps)."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
