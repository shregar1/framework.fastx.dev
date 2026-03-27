"""FastMVC Example API - Item Management.

A complete example demonstrating FastMVC patterns:
- Entity with validation
- Repository pattern
- Service layer
- Controller with CRUD endpoints
- DTOs for type safety

Usage:
    from fast_mvc.example import ItemEntity, ItemService, ItemController

    # Or import all example components
    from fast_mvc.example import *
"""

# Entity
from example.entities.item import ItemEntity

# Repository
from example.repositories.item_repository import ItemRepository

# Service
from example.services.item_service import ItemService

# Controller
from example.controllers.item_controller import ItemController, router as item_router

# DTOs
from example.dtos.item import (
    CreateItemRequestDTO,
    UpdateItemRequestDTO,
    ItemResponseDTO,
    ItemListResponseDTO,
    ItemStatsResponseDTO,
)

# Testing utilities (optional import)
try:
    from example.testing import (
        ItemFactory,
        item_client,
        item_db,
        mock_auth,
        mock_user,
        test_item,
        test_items,
    )

    _TESTING_AVAILABLE = True
except ImportError:
    _TESTING_AVAILABLE = False

__all__ = [
    # Entity
    "ItemEntity",
    # Repository
    "ItemRepository",
    # Service
    "ItemService",
    # Controller
    "ItemController",
    "item_router",
    # DTOs
    "CreateItemRequestDTO",
    "UpdateItemRequestDTO",
    "ItemResponseDTO",
    "ItemListResponseDTO",
    "ItemStatsResponseDTO",
]

# Add testing exports if available
if _TESTING_AVAILABLE:
    __all__.extend(
        [
            "ItemFactory",
            "item_client",
            "item_db",
            "mock_auth",
            "mock_user",
            "test_item",
            "test_items",
        ]
    )
