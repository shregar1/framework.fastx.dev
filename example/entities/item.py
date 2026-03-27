"""Item Entity - Example domain entity.

Demonstrates FastMVC entity patterns with validation and business logic.
"""

from datetime import datetime
from typing import Any, Self

from abstractions.entity import Entity


class ItemEntity(Entity):
    """Item domain entity representing a todo/task item.

    Attributes:
        id: Unique identifier
        name: Item name
        description: Item description
        completed: Whether the item is completed
        created_at: Creation timestamp
        updated_at: Last update timestamp

    """

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        description: str = "",
        completed: bool = False,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
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
        super().__init__(id=id)
        self._name = name
        self._description = description
        self._completed = completed
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()

    # Properties
    @property
    def name(self) -> str:
        """Get item name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set item name with validation."""
        if not value or len(value.strip()) < 1:
            raise ValueError("Name cannot be empty")
        if len(value) > 100:
            raise ValueError("Name cannot exceed 100 characters")
        self._name = value.strip()
        self._updated_at = datetime.utcnow()

    @property
    def description(self) -> str:
        """Get item description."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Set item description with validation."""
        if len(value) > 500:
            raise ValueError("Description cannot exceed 500 characters")
        self._description = value
        self._updated_at = datetime.utcnow()

    @property
    def completed(self) -> bool:
        """Get completion status."""
        return self._completed

    @completed.setter
    def completed(self, value: bool) -> None:
        """Set completion status."""
        self._completed = value
        self._updated_at = datetime.utcnow()

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at

    # Business logic
    def complete(self) -> Self:
        """Mark item as completed."""
        self.completed = True
        return self

    def uncomplete(self) -> Self:
        """Mark item as not completed."""
        self.completed = False
        return self

    def toggle(self) -> Self:
        """Toggle completion status."""
        self.completed = not self._completed
        return self

    # Serialization
    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "completed": self.completed,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create entity from dictionary."""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            completed=data.get("completed", False),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else None,
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else None,
        )

    def __repr__(self) -> str:
        """Execute __repr__ operation.

        Returns:
            The result of the operation.
        """
        return f"ItemEntity(id={self.id}, name={self.name}, completed={self.completed})"

    def __eq__(self, other: object) -> bool:
        """Execute __eq__ operation.

        Args:
            other: The other parameter.

        Returns:
            The result of the operation.
        """
        if not isinstance(other, ItemEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Execute __hash__ operation.

        Returns:
            The result of the operation.
        """
        return hash(self.id)
