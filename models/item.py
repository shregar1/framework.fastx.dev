"""Item domain model (sample).

Maps to persistence via ``repositories.item.ItemRepository``; keep validation and
serialization here.
"""

from datetime import datetime
from typing import Optional

from abstractions.entity import Entity


class Item(Entity):
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
        id: Optional[str] = None,
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
        self._id = id or ""
        self._name = name
        self._description = description
        self._completed = completed
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        if not self._id:
            import uuid

            self._id = str(uuid.uuid4())

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

    @created_at.setter
    def created_at(self, value: datetime) -> None:
        """Allow I/dataclass compatibility when setting created_at."""
        self._created_at = value

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value: datetime) -> None:
        """Allow I/dataclass compatibility when setting updated_at."""
        self._updated_at = value

    def __repr__(self) -> str:
        """Execute __repr__ operation.

        Returns:
            The result of the operation.
        """
        return f"Item(id={self.id}, name={self.name}, completed={self.completed})"

    def __eq__(self, other: object) -> bool:
        """Execute __eq__ operation.

        Args:
            other: The other parameter.

        Returns:
            The result of the operation.
        """
        if not isinstance(other, Item):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Execute __hash__ operation.

        Returns:
            The result of the operation.
        """
        return hash(self.id)
