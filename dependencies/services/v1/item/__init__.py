"""v1 item API service dependencies."""

from dependencies.services.v1.item.abstraction import IItemServiceDependency
from dependencies.services.v1.item.item_service_dependency import ItemServiceDependency

__all__ = ["IItemServiceDependency", "ItemServiceDependency"]
