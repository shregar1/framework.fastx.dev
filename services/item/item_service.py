"""Item application service."""

from __future__ import annotations

from typing import Any, Optional, cast

from abstractions.result import Result, failure, success
from models.item import Item
from repositories.item import ItemRepository
from services.item.abstraction import IItemService


class ItemService(IItemService):
    """Application service for item operations."""

    def __init__(self, repository: ItemRepository | None = None, *args: Any, **kwargs: Any) -> None:
        """Initialize service with repository.

        Args:
            repository: Item repository (creates new if None)
            *args: Additional positional arguments for parent class.
            **kwargs: Additional keyword arguments for parent class.

        """
        super().__init__(*args, **kwargs)
        self._repository = repository or ItemRepository()

    async def _require_item(self, item_id: str) -> Result[Item, Any]:
        """Load item by id or return failure (not found / repository error)."""
        get_result = await self._repository.get_by_id(item_id)
        if get_result.is_failure:
            return cast(Result[Item, Any], failure(get_result.error))
        if get_result.value is None:
            return failure("Item not found")
        return success(get_result.value)

    def run(self, request_dto: Any) -> dict:
        """Framework hook; item flows use explicit methods (create_item, …)."""
        return {}

    # Business Operations

    async def create_item(
        self, name: str, description: str = ""
    ) -> Result[Item, Any]:
        """Create a new item.

        Args:
            name: Item name
            description: Item description

        Returns:
            Result containing created entity

        """
        try:
            # Business validation
            if not name or not name.strip():
                return failure("Item name is required")

            # Create entity
            item = Item(
                name=name.strip(),
                description=description.strip(),
            )

            # Persist
            return await self._repository.create(item)
        except ValueError as e:
            return failure(f"Validation error: {str(e)}")
        except Exception as e:
            return failure(f"Failed to create item: {str(e)}")

    async def create(self, entity: Item) -> Item:
        """Compatibility wrapper used by tests/legacy service callers."""
        result = await self._repository.create(entity)
        if result.is_failure:
            raise ValueError(str(result.error))
        return cast(Item, result.value)

    async def get_item(self, item_id: str) -> Result[Item | None, Any]:
        """Get item by ID.

        Args:
            item_id: Item identifier

        Returns:
            Result containing entity or None

        """
        return await self._repository.get_by_id(item_id)

    async def get_by_id(self, item_id: str) -> Item | None:
        """Compatibility wrapper used by tests/legacy service callers."""
        result = await self._repository.get_by_id(item_id)
        if result.is_failure:
            return None
        return cast(Item | None, result.value)

    async def get_all_items(self) -> Result[list[Item], Any]:
        """Get all items.

        Returns:
            Result containing all entities

        """
        return await self._repository.get_all()

    async def update_item(
        self,
        item_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Result[Item, Any]:
        """Update an item.

        Args:
            item_id: Item identifier
            name: New name (optional)
            description: New description (optional)

        Returns:
            Result containing updated entity

        """
        try:
            req = await self._require_item(item_id)
            if req.is_failure:
                return req
            item = req.value

            if name is not None:
                item.name = name
            if description is not None:
                item.description = description

            return await self._repository.update(item)
        except ValueError as e:
            return failure(f"Validation error: {str(e)}")
        except Exception as e:
            return failure(f"Failed to update item: {str(e)}")

    async def delete_item(self, item_id: str) -> Result[bool, Any]:
        """Delete an item.

        Args:
            item_id: Item identifier

        Returns:
            Result containing True if deleted

        """
        return await self._repository.delete(item_id)

    async def complete_item(self, item_id: str) -> Result[Item, Any]:
        """Mark item as completed.

        Args:
            item_id: Item identifier

        Returns:
            Result containing updated entity

        """
        try:
            req = await self._require_item(item_id)
            if req.is_failure:
                return req
            item = req.value
            item.completed = True
            return await self._repository.update(item)
        except Exception as e:
            return failure(f"Failed to complete item: {str(e)}")

    async def uncomplete_item(self, item_id: str) -> Result[Item, Any]:
        """Mark item as not completed.

        Args:
            item_id: Item identifier

        Returns:
            Result containing updated entity

        """
        try:
            req = await self._require_item(item_id)
            if req.is_failure:
                return req
            item = req.value
            item.completed = False
            return await self._repository.update(item)
        except Exception as e:
            return failure(f"Failed to uncomplete item: {str(e)}")

    async def toggle_item(self, item_id: str) -> Result[Item, Any]:
        """Toggle item completion status.

        Args:
            item_id: Item identifier

        Returns:
            Result containing updated entity

        """
        try:
            req = await self._require_item(item_id)
            if req.is_failure:
                return req
            item = req.value
            item.completed = not item.completed
            return await self._repository.update(item)
        except Exception as e:
            return failure(f"Failed to toggle item: {str(e)}")

    # Query Operations

    async def search_items(self, query: str) -> Result[list[Item], Any]:
        """Search items by name.

        Args:
            query: Search query

        Returns:
            Result containing matching entities

        """
        if not query:
            return await self._repository.get_all()
        return await self._repository.find_by_name(query)

    async def get_completed_items(self) -> Result[list[Item], Any]:
        """Get all completed items.

        Returns:
            Result containing completed entities

        """
        return await self._repository.find_completed()

    async def get_pending_items(self) -> Result[list[Item], Any]:
        """Get all pending items.

        Returns:
            Result containing pending entities

        """
        return await self._repository.find_pending()

    async def get_statistics(self) -> Result[dict[str, Any], Any]:
        """Get item statistics.

        Returns:
            Result containing stats dict

        """
        try:
            all_result = await self._repository.get_all()
            if all_result.is_failure:
                return cast(
                    Result[dict[str, Any], Any],
                    failure(all_result.error),
                )

            items = all_result.value
            completed = sum(1 for item in items if item.completed)
            pending = len(items) - completed

            return success(
                {
                    "total": len(items),
                    "completed": completed,
                    "pending": pending,
                    "completion_rate": completed / len(items) if items else 0,
                }
            )
        except Exception as e:
            return failure(f"Failed to get statistics: {str(e)}")

    # Bulk Operations

    async def complete_all(self) -> Result[int, Any]:
        """Mark all pending items as completed.

        Returns:
            Result containing count of updated items

        """
        try:
            pending_result = await self._repository.find_pending()
            if pending_result.is_failure:
                return cast(
                    Result[int, Any],
                    failure(pending_result.error),
                )

            pending = pending_result.value
            count = 0
            for item in pending:
                item.completed = True
                update_result = await self._repository.update(item)
                if update_result.is_success:
                    count += 1

            return success(count)
        except Exception as e:
            return failure(f"Failed to complete all items: {str(e)}")

    async def clear_all(self) -> Result[bool, Any]:
        """Delete all items (useful for testing).

        Returns:
            Result containing True

        """
        return await self._repository.clear()
