"""Module item_service.py."""

from typing import Any

"""
Item Service - Example service implementation.

Demonstrates the Service pattern with business logic.
"""

from typing import Self

from abstractions.service import IService
from abstractions.result import Result, success, failure
from example.entities.item import ItemEntity
from example.repositories.item_repository import ItemRepository


class ItemService(IService):
    """Represents the ItemService class."""

    def run(self, request_dto: Any) -> dict:
        """Execute run operation.

        Args:
            request_dto: The request_dto parameter.

        Returns:
            The result of the operation.
        """
        return {}

    """
    Service for managing items with business logic.
    
    Example:
        service = ItemService(repository)
        result = await service.create_item("Buy milk", "Get from store")
        if result.is_success:
            print(f"Created: {result.value.name}")
    """

    def __init__(self, repository: ItemRepository | None = None) -> None:
        """Initialize service with repository.

        Args:
            repository: Item repository (creates new if None)

        """
        self._repository = repository or ItemRepository()

    # Business Operations

    async def create_item(
        self, name: str, description: str = ""
    ) -> Result[ItemEntity, Any]:
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
            item = ItemEntity(
                name=name.strip(),
                description=description.strip(),
            )

            # Persist
            return await self._repository.create(item)
        except ValueError as e:
            return failure(f"Validation error: {str(e)}")
        except Exception as e:
            return failure(f"Failed to create item: {str(e)}")

    async def get_item(self, item_id: str) -> Result[ItemEntity | None, Any]:
        """Get item by ID.

        Args:
            item_id: Item identifier

        Returns:
            Result containing entity or None

        """
        return await self._repository.get_by_id(item_id)

    async def get_all_items(self) -> Result[list[ItemEntity], Any]:
        """Get all items.

        Returns:
            Result containing all entities

        """
        return await self._repository.get_all()

    async def update_item(
        self,
        item_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> Result[ItemEntity, Any]:
        """Update an item.

        Args:
            item_id: Item identifier
            name: New name (optional)
            description: New description (optional)

        Returns:
            Result containing updated entity

        """
        try:
            # Get existing
            get_result = await self._repository.get_by_id(item_id)
            if get_result.is_failure:
                return get_result

            item = get_result.value
            if item is None:
                return failure("Item not found")

            # Apply updates
            if name is not None:
                item.name = name
            if description is not None:
                item.description = description

            # Persist
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

    async def complete_item(self, item_id: str) -> Result[ItemEntity, Any]:
        """Mark item as completed.

        Args:
            item_id: Item identifier

        Returns:
            Result containing updated entity

        """
        try:
            get_result = await self._repository.get_by_id(item_id)
            if get_result.is_failure:
                return get_result

            item = get_result.value
            if item is None:
                return failure("Item not found")

            item.complete()
            return await self._repository.update(item)
        except Exception as e:
            return failure(f"Failed to complete item: {str(e)}")

    async def uncomplete_item(self, item_id: str) -> Result[ItemEntity, Any]:
        """Mark item as not completed.

        Args:
            item_id: Item identifier

        Returns:
            Result containing updated entity

        """
        try:
            get_result = await self._repository.get_by_id(item_id)
            if get_result.is_failure:
                return get_result

            item = get_result.value
            if item is None:
                return failure("Item not found")

            item.uncomplete()
            return await self._repository.update(item)
        except Exception as e:
            return failure(f"Failed to uncomplete item: {str(e)}")

    async def toggle_item(self, item_id: str) -> Result[ItemEntity, Any]:
        """Toggle item completion status.

        Args:
            item_id: Item identifier

        Returns:
            Result containing updated entity

        """
        try:
            get_result = await self._repository.get_by_id(item_id)
            if get_result.is_failure:
                return get_result

            item = get_result.value
            if item is None:
                return failure("Item not found")

            item.toggle()
            return await self._repository.update(item)
        except Exception as e:
            return failure(f"Failed to toggle item: {str(e)}")

    # Query Operations

    async def search_items(self, query: str) -> Result[list[ItemEntity], Any]:
        """Search items by name.

        Args:
            query: Search query

        Returns:
            Result containing matching entities

        """
        if not query:
            return await self._repository.get_all()
        return await self._repository.find_by_name(query)

    async def get_completed_items(self) -> Result[list[ItemEntity], Any]:
        """Get all completed items.

        Returns:
            Result containing completed entities

        """
        return await self._repository.find_completed()

    async def get_pending_items(self) -> Result[list[ItemEntity], Any]:
        """Get all pending items.

        Returns:
            Result containing pending entities

        """
        return await self._repository.find_pending()

    async def get_statistics(self) -> Result[dict, Any]:
        """Get item statistics.

        Returns:
            Result containing stats dict

        """
        try:
            all_result = await self._repository.get_all()
            if all_result.is_failure:
                return all_result

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
                return pending_result

            pending = pending_result.value
            count = 0
            for item in pending:
                item.complete()
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
