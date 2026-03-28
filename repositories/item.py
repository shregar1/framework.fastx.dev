"""Item repository — in-memory sample; production uses database/SQLAlchemy as needed."""

from datetime import datetime
from typing import Any

from abstractions.result import Result, failure, success
from models.item import Item
from repositories.abstraction import IRepository


class ItemRepository(IRepository):
    """Repository for :class:`Item` with in-memory storage.

    Inherits :class:`repositories.abstraction.IRepository` directly (no separate
    ``IItemRepository`` abstraction). Replace ``_storage`` with real persistence
    when wired to the database.

    Example:
        repo = ItemRepository()
        result = await repo.create(item)
        if result.is_success:
            print(f"Created: {result.value}")

    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize repository with empty storage."""
        super().__init__(**kwargs)
        self._storage: dict[str, dict[str, Any]] = {}
        self._counter = 0

    def _generate_id(self) -> str:
        """Generate unique identifier."""
        self._counter += 1
        return f"item_{self._counter}"

    def _to_entity(self, data: dict[str, Any]) -> Item:
        """Convert stored data to entity."""
        return Item.from_dict(data)

    def _from_entity(self, entity: Item) -> dict[str, Any]:
        """Convert entity to stored data."""
        return entity.to_dict()

    # CRUD Operations

    async def create(self, entity: Item) -> Result[Item, Any]:
        """Create a new item.

        Args:
            entity: Item entity to create

        Returns:
            Result containing created entity or error

        """
        try:
            if not entity.id:
                entity._id = self._generate_id()

            # Check if already exists
            if entity.id in self._storage:
                return failure("Item with this ID already exists")

            self._storage[entity.id] = self._from_entity(entity)
            return success(entity)
        except Exception as e:
            return failure(f"Failed to create item: {str(e)}")

    async def get_by_id(self, id: str) -> Result[Item | None, Any]:
        """Get item by ID.

        Args:
            id: Item identifier

        Returns:
            Result containing entity or None if not found

        """
        try:
            data = self._storage.get(id)
            if data is None:
                return success(None)
            return success(self._to_entity(data))
        except Exception as e:
            return failure(f"Failed to get item: {str(e)}")

    async def get_all(self) -> Result[list[Item], Any]:
        """Get all items.

        Returns:
            Result containing list of all entities

        """
        try:
            entities = [self._to_entity(data) for data in self._storage.values()]
            return success(entities)
        except Exception as e:
            return failure(f"Failed to get items: {str(e)}")

    async def update(self, entity: Item) -> Result[Item, Any]:
        """Update existing item.

        Args:
            entity: Item entity with updated values

        Returns:
            Result containing updated entity or error

        """
        try:
            if not entity.id or entity.id not in self._storage:
                return failure("Item not found")

            # Update timestamp
            entity._updated_at = datetime.utcnow()
            self._storage[entity.id] = self._from_entity(entity)
            return success(entity)
        except Exception as e:
            return failure(f"Failed to update item: {str(e)}")

    async def delete(self, id: str) -> Result[bool, Any]:
        """Delete item by ID.

        Args:
            id: Item identifier

        Returns:
            Result containing True if deleted, False if not found

        """
        try:
            if id not in self._storage:
                return success(False)

            del self._storage[id]
            return success(True)
        except Exception as e:
            return failure(f"Failed to delete item: {str(e)}")

    # Query Operations

    async def find_by_name(self, name: str) -> Result[list[Item], Any]:
        """Find items by name (partial match).

        Args:
            name: Name to search for

        Returns:
            Result containing matching entities

        """
        try:
            results = []
            name_lower = name.lower()
            for data in self._storage.values():
                if name_lower in data.get("name", "").lower():
                    results.append(self._to_entity(data))
            return success(results)
        except Exception as e:
            return failure(f"Failed to search items: {str(e)}")

    async def find_completed(self) -> Result[list[Item], Any]:
        """Find all completed items.

        Returns:
            Result containing completed entities

        """
        try:
            results = [
                self._to_entity(data)
                for data in self._storage.values()
                if data.get("completed", False)
            ]
            return success(results)
        except Exception as e:
            return failure(f"Failed to get completed items: {str(e)}")

    async def find_pending(self) -> Result[list[Item], Any]:
        """Find all pending (not completed) items.

        Returns:
            Result containing pending entities

        """
        try:
            results = [
                self._to_entity(data)
                for data in self._storage.values()
                if not data.get("completed", False)
            ]
            return success(results)
        except Exception as e:
            return failure(f"Failed to get pending items: {str(e)}")

    # Utility

    async def count(self) -> Result[int, Any]:
        """Get total item count.

        Returns:
            Result containing count

        """
        return success(len(self._storage))

    async def clear(self) -> Result[bool, Any]:
        """Clear all items (useful for testing).

        Returns:
            Result containing True

        """
        self._storage.clear()
        self._counter = 0
        return success(True)
