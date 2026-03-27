"""FastAPI dependency for :class:`services.item.item_service.ItemService`."""

from fastapi import Depends, Request

from dependencies.repositories.item.item_repository_dependency import (
    ItemRepositoryDependency,
)
from dependencies.services.v1.item.abstraction import IItemServiceDependency
from repositories.item.item_repository import ItemRepository
from services.item.item_service import ItemService


class ItemServiceDependency(IItemServiceDependency):
    """Derives an :class:`ItemService` from the current request and repository."""

    @staticmethod
    def derive(
        request: Request,
        repository: ItemRepository = Depends(ItemRepositoryDependency.derive),
    ) -> ItemService:
        """Build a service instance with optional request context."""
        _ = request
        return ItemService(repository=repository)
