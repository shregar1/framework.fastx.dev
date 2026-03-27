"""Example service dependencies.

Demonstrates FastMVC dependency injection patterns.
"""

from typing import Annotated

from fastapi import Depends

from example.services.item_service import ItemService
from example.repositories.item_repository import ItemRepository


# Singleton instances (in production, use proper DI container)
_item_repository: ItemRepository | None = None
_item_service: ItemService | None = None


def get_item_repository() -> ItemRepository:
    """Get or create item repository singleton.

    Returns:
        ItemRepository instance

    """
    global _item_repository
    if _item_repository is None:
        _item_repository = ItemRepository()
    return _item_repository


def get_item_service() -> ItemService:
    """Get or create item service singleton.

    Returns:
        ItemService instance

    """
    global _item_service
    if _item_service is None:
        repository = get_item_repository()
        _item_service = ItemService(repository)
    return _item_service


# Type alias for dependency injection
ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]


# Reset functions for testing
def reset_repository() -> None:
    """Reset repository singleton (useful for testing)."""
    global _item_repository
    _item_repository = None


def reset_service() -> None:
    """Reset service singleton (useful for testing)."""
    global _item_service
    _item_service = None


def reset_all() -> None:
    """Reset all singletons (useful for testing)."""
    reset_repository()
    reset_service()
