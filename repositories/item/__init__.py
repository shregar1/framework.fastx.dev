"""Item data access."""

from repositories.item.abstraction import IItemRepository
from repositories.item.item_repository import ItemRepository

__all__ = ["IItemRepository", "ItemRepository"]
