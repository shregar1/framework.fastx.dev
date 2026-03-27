"""FastAPI dependency for :class:`repositories.item.item_repository.ItemRepository`."""

from fastapi import Request

from dependencies.repositories.abstraction import IRepositoryDependency
from repositories.item.item_repository import ItemRepository


class ItemRepositoryDependency(IRepositoryDependency):
    """Derives an :class:`ItemRepository` for the current request."""

    @staticmethod
    def derive(request: Request) -> ItemRepository:
        """Build an in-memory item repository (URN available on ``request.state`` for tracing)."""
        _ = request  # reserved for session-scoped repos
        return ItemRepository()
