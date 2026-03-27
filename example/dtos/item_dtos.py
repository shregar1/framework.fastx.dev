"""Item DTOs - Example Data Transfer Objects.

Demonstrates FastMVC DTO patterns for requests and responses.
"""

from typing import Self
from datetime import datetime

from dtos.requests.abstraction import IRequestDTO
from dtos.responses.base import BaseResponseDTO


class CreateItemRequest(IRequestDTO):
    """DTO for creating a new item.

    Attributes:
        name: Item name (required, 1-100 chars)
        description: Item description (optional, max 500 chars)

    """

    def __init__(self, name: str, description: str = "") -> None:
        """Execute __init__ operation.

        Args:
            name: The name parameter.
            description: The description parameter.
        """
        self.name = name
        self.description = description

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the request data.

        Returns:
            Tuple of (is_valid, error_messages)

        """
        errors = []

        # Name validation
        if not self.name or not self.name.strip():
            errors.append("Name is required")
        elif len(self.name) > 100:
            errors.append("Name cannot exceed 100 characters")

        # Description validation
        if len(self.description) > 500:
            errors.append("Description cannot exceed 500 characters")

        return len(errors) == 0, errors

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
        )


class UpdateItemRequest(IRequestDTO):
    """DTO for updating an existing item.

    Attributes:
        name: New item name (optional)
        description: New description (optional)

    """

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            name: The name parameter.
            description: The description parameter.
        """
        self.name = name
        self.description = description

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the request data.

        Returns:
            Tuple of (is_valid, error_messages)

        """
        errors = []

        # Name validation (if provided)
        if self.name is not None:
            if not self.name.strip():
                errors.append("Name cannot be empty")
            elif len(self.name) > 100:
                errors.append("Name cannot exceed 100 characters")

        # Description validation (if provided)
        if self.description is not None and len(self.description) > 500:
            errors.append("Description cannot exceed 500 characters")

        return len(errors) == 0, errors

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {}
        if self.name is not None:
            result["name"] = self.name
        if self.description is not None:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create from dictionary."""
        return cls(
            name=data.get("name"),
            description=data.get("description"),
        )


class ItemResponse(BaseResponseDTO):
    """DTO for item responses.

    Attributes:
        id: Item identifier
        name: Item name
        description: Item description
        completed: Completion status
        created_at: Creation timestamp ISO format
        updated_at: Update timestamp ISO format

    """

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        completed: bool,
        created_at: str,
        updated_at: str,
    ) -> None:
        """Execute __init__ operation.

        Args:
            id: The id parameter.
            name: The name parameter.
            description: The description parameter.
            completed: The completed parameter.
            created_at: The created_at parameter.
            updated_at: The updated_at parameter.
        """
        self.id = id
        self.name = name
        self.description = description
        self.completed = completed
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_entity(cls, entity) -> Self:
        """Create response DTO from ItemEntity.

        Args:
            entity: ItemEntity instance

        Returns:
            ItemResponse DTO

        """
        return cls(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            completed=entity.completed,
            created_at=entity.created_at.isoformat(),
            updated_at=entity.updated_at.isoformat(),
        )


class ItemListResponse(BaseResponseDTO):
    """DTO for list of items response.

    Attributes:
        items: List of item responses
        total: Total count
        completed_count: Number of completed items
        pending_count: Number of pending items

    """

    def __init__(
        self,
        items: list[ItemResponse],
        total: int = 0,
        completed_count: int = 0,
        pending_count: int = 0,
    ) -> None:
        """Execute __init__ operation.

        Args:
            items: The items parameter.
            total: The total parameter.
            completed_count: The completed_count parameter.
            pending_count: The pending_count parameter.
        """
        self.items = items
        self.total = total or len(items)
        self.completed_count = completed_count
        self.pending_count = pending_count

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "items": [item.to_dict() for item in self.items],
            "total": self.total,
            "completed_count": self.completed_count,
            "pending_count": self.pending_count,
        }

    @classmethod
    def from_entities(cls, entities: list) -> Self:
        """Create response from list of ItemEntity.

        Args:
            entities: List of ItemEntity instances

        Returns:
            ItemListResponse DTO

        """
        items = [ItemResponse.from_entity(e) for e in entities]
        completed = sum(1 for e in entities if e.completed)

        return cls(
            items=items,
            total=len(items),
            completed_count=completed,
            pending_count=len(items) - completed,
        )


class ItemStatsResponse(BaseResponseDTO):
    """DTO for item statistics response.

    Attributes:
        total: Total number of items
        completed: Number of completed items
        pending: Number of pending items
        completion_rate: Percentage of completed items (0-1)

    """

    def __init__(
        self,
        total: int,
        completed: int,
        pending: int,
        completion_rate: float,
    ) -> None:
        """Execute __init__ operation.

        Args:
            total: The total parameter.
            completed: The completed parameter.
            pending: The pending parameter.
            completion_rate: The completion_rate parameter.
        """
        self.total = total
        self.completed = completed
        self.pending = pending
        self.completion_rate = completion_rate

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total": self.total,
            "completed": self.completed,
            "pending": self.pending,
            "completion_rate": round(self.completion_rate, 2),
        }

    @classmethod
    def from_stats(cls, stats: dict) -> Self:
        """Create response from stats dict.

        Args:
            stats: Dictionary with total, completed, pending, completion_rate

        Returns:
            ItemStatsResponse DTO

        """
        return cls(
            total=stats.get("total", 0),
            completed=stats.get("completed", 0),
            pending=stats.get("pending", 0),
            completion_rate=stats.get("completion_rate", 0.0),
        )
