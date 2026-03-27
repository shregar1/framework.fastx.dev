"""FastMVC - Minimal Core Framework.

A production-grade MVC framework for FastAPI with clean architecture,
dependency injection, and modular service integration.

Basic Usage:
    from fast_mvc import FastMVCApp, Controller, Service, Repository

    app = FastMVCApp()
    app.run()

Example API (Included):
    # The example module demonstrates FastMVC patterns with a complete Item API:

    from fast_mvc import item_router  # FastAPI router

    # Add to your app:
    app.include_router(item_router)

    # Or use components directly:
    from fast_mvc import ItemEntity, ItemService, ItemRepository

    service = ItemService()
    result = await service.create_item("Buy milk", "Get from store")

    # Available example endpoints:
    # POST   /items              - Create item
    # GET    /items              - List all items
    # GET    /items/{id}         - Get item by ID
    # PATCH  /items/{id}         - Update item
    # DELETE /items/{id}         - Delete item
    # POST   /items/{id}/complete   - Mark completed
    # POST   /items/{id}/uncomplete - Mark pending
    # POST   /items/{id}/toggle     - Toggle status
    # GET    /items/search       - Search items
    # GET    /items/completed    - List completed
    # GET    /items/pending      - List pending
    # GET    /items/statistics   - Get stats

With Optional Services:
    # Install: pip install pyfastmvc[platform]
    from fast_platform.notifications import EmailClient
    from fast_platform.storage import S3Client

Modules:
    - abstractions: I interfaces (Controller, Service, Repository, etc.)
    - dtos: Data Transfer Objects and validation
    - dependencies: DI container and utilities
    - example: Complete working example (Item API)

Optional Integrations (via fast-platform):
    - notifications: Email, SMS, Chat, Push notifications
    - storage: S3, GCS, Azure Blob
    - messaging: SQS, Pub/Sub, Service Bus
    - payments: Stripe integration
    - observability: Monitoring, tracing, logging
    - llm: AI/LLM integrations
    - search: Full-text search
    - resilience: Circuit breakers, retries
"""

# Core abstractions
from abstractions.controller import IController
from abstractions.service import IService
from abstractions.repository import IRepository
from abstractions.entity import Entity, IEntity, AggregateRoot, IAggregateRoot
from abstractions.unit_of_work import IUnitOfWork, IUnitOfWork
from abstractions.result import Result, Success, Failure, success, failure

# DTOs
from dtos.responses.I import IResponseDTO
from dtos.requests.abstraction import IRequestDTO

# Application factory
from app import app as FastMVCApp

# Example API (optional - demonstrates framework usage)
try:
    from example import (
        ItemEntity,
        ItemRepository,
        ItemService,
        ItemController,
        item_router,
        CreateItemRequestDTO,
        UpdateItemRequestDTO,
        ItemResponseDTO,
        ItemListResponseDTO,
        ItemStatsResponseDTO,
    )

    _EXAMPLE_AVAILABLE = True
except ImportError:
    _EXAMPLE_AVAILABLE = False

__version__ = "1.5.0"

__all__ = [
    # Version
    "__version__",
    # Core abstractions
    "IController",
    "IService",
    "IRepository",
    "Entity",
    "IEntity",
    "AggregateRoot",
    "IAggregateRoot",
    "IUnitOfWork",
    "IUnitOfWork",
    # Result pattern
    "Result",
    "Success",
    "Failure",
    "success",
    "failure",
    # DTOs
    "IResponseDTO",
    "IRequestDTO",
    # App
    "FastMVCApp",
]

# Add example exports if available
if _EXAMPLE_AVAILABLE:
    __all__.extend(
        [
            # Example Entity
            "ItemEntity",
            # Example Repository
            "ItemRepository",
            # Example Service
            "ItemService",
            # Example Controller
            "ItemController",
            "item_router",
            # Example DTOs
            "CreateItemRequestDTO",
            "UpdateItemRequestDTO",
            "ItemResponseDTO",
            "ItemListResponseDTO",
            "ItemStatsResponseDTO",
        ]
    )
