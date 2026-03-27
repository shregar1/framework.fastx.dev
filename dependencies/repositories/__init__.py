"""Repository-oriented FastAPI dependencies."""

from dependencies.repositories.abstraction import IRepositoryDependency
from dependencies.repositories.example import ExampleRepositoryDependency
from dependencies.repositories.item import ItemRepositoryDependency

__all__ = [
    "IRepositoryDependency",
    "ExampleRepositoryDependency",
    "ItemRepositoryDependency",
]
