"""Item Controller - Example controller implementation.

Demonstrates FastMVC controller patterns with FastAPI routes.
"""

from http import HTTPStatus

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from abstractions.controller import IController
from controllers.apis.v1.item import http as item_http
from dtos.requests.item import CreateItemRequestDTO, UpdateItemRequestDTO
from services.item.item_service import ItemService

# Create router
router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
    },
)


class ItemController(IController):
    """Controller for item management endpoints.

    Provides CRUD operations and business actions for items.

    Example:
        # In your main app:
        from controllers.apis.v1.item.item_controller import router
        app.include_router(router)

    """

    def __init__(self, service: ItemService | None = None) -> None:
        """Initialize controller with service.

        Args:
            service: Item service (creates new if None)

        """
        self._service = service or ItemService()

    async def create(
        self, body: CreateItemRequestDTO, http_request: Request | None = None
    ) -> JSONResponse:
        """Create a new item."""
        item_http.raise_unprocessable_if_dto_invalid(body)

        return item_http.respond_created_item(
            await self._service.create_item(
                name=body.name,
                description=body.description,
            ),
            http_request,
            reference_urn=body.reference_urn,
        )

    async def get_by_id(
        self, item_id: str, http_request: Request | None = None
    ) -> JSONResponse:
        """Get item by ID."""
        result = await self._service.get_item(item_id)
        entity = item_http.unwrap_item_or_404(result, item_id=item_id)
        return item_http.json_item(entity, http_request)

    async def get_all(self, http_request: Request | None = None) -> JSONResponse:
        """Get all items."""
        return item_http.respond_item_list(
            await self._service.get_all_items(), http_request
        )

    async def update(
        self,
        item_id: str,
        body: UpdateItemRequestDTO,
        http_request: Request | None = None,
    ) -> JSONResponse:
        """Update an item."""
        item_http.raise_unprocessable_if_dto_invalid(body)

        return item_http.respond_item_with_ref(
            await self._service.update_item(
                item_id=item_id,
                name=body.name,
                description=body.description,
            ),
            http_request,
            reference_urn=body.reference_urn,
        )

    async def delete(
        self, item_id: str, http_request: Request | None = None
    ) -> JSONResponse:
        """Delete an item."""
        result = await self._service.delete_item(item_id)
        item_http.unwrap_deleted_or_404(result, item_id=item_id)
        return item_http.json_delete_message(item_id, http_request)

    async def complete(
        self, item_id: str, http_request: Request | None = None
    ) -> JSONResponse:
        """Mark item as completed."""
        return item_http.respond_item(
            await self._service.complete_item(item_id), http_request
        )

    async def uncomplete(
        self, item_id: str, http_request: Request | None = None
    ) -> JSONResponse:
        """Mark item as not completed."""
        return item_http.respond_item(
            await self._service.uncomplete_item(item_id), http_request
        )

    async def toggle(
        self, item_id: str, http_request: Request | None = None
    ) -> JSONResponse:
        """Toggle item completion status."""
        return item_http.respond_item(
            await self._service.toggle_item(item_id), http_request
        )

    async def search(
        self, query: str = "", http_request: Request | None = None
    ) -> JSONResponse:
        """Search items by name."""
        return item_http.respond_item_list(
            await self._service.search_items(query), http_request
        )

    async def get_completed(self, http_request: Request | None = None) -> JSONResponse:
        """Get all completed items."""
        return item_http.respond_item_list(
            await self._service.get_completed_items(), http_request
        )

    async def get_pending(self, http_request: Request | None = None) -> JSONResponse:
        """Get all pending items."""
        return item_http.respond_item_list(
            await self._service.get_pending_items(), http_request
        )

    async def get_statistics(self, http_request: Request | None = None) -> JSONResponse:
        """Get item statistics."""
        return item_http.respond_item_stats(
            await self._service.get_statistics(), http_request
        )


# Route Definitions

_controller = ItemController()


@router.post("", response_model=dict, status_code=HTTPStatus.CREATED)
async def create_item(
    http_request: Request, body: CreateItemRequestDTO
) -> JSONResponse:
    """Create a new item."""
    return await _controller.create(body, http_request)


@router.get("", response_model=dict)
async def get_all_items(http_request: Request) -> JSONResponse:
    """Get all items."""
    return await _controller.get_all(http_request)


@router.get("/search", response_model=dict)
async def search_items(http_request: Request, query: str = "") -> JSONResponse:
    """Search items by name."""
    return await _controller.search(query, http_request)


@router.get("/completed", response_model=dict)
async def get_completed_items(http_request: Request) -> JSONResponse:
    """Get all completed items."""
    return await _controller.get_completed(http_request)


@router.get("/pending", response_model=dict)
async def get_pending_items(http_request: Request) -> JSONResponse:
    """Get all pending items."""
    return await _controller.get_pending(http_request)


@router.get("/statistics", response_model=dict)
async def get_item_statistics(http_request: Request) -> JSONResponse:
    """Get item statistics."""
    return await _controller.get_statistics(http_request)


@router.get("/{item_id}", response_model=dict)
async def get_item(http_request: Request, item_id: str) -> JSONResponse:
    """Get item by ID."""
    return await _controller.get_by_id(item_id, http_request)


@router.patch("/{item_id}", response_model=dict)
async def update_item(
    http_request: Request, item_id: str, body: UpdateItemRequestDTO
) -> JSONResponse:
    """Update an item."""
    return await _controller.update(item_id, body, http_request)


@router.delete("/{item_id}", response_model=dict)
async def delete_item(http_request: Request, item_id: str) -> JSONResponse:
    """Delete an item."""
    return await _controller.delete(item_id, http_request)


@router.post("/{item_id}/complete", response_model=dict)
async def complete_item(http_request: Request, item_id: str) -> JSONResponse:
    """Mark item as completed."""
    return await _controller.complete(item_id, http_request)


@router.post("/{item_id}/uncomplete", response_model=dict)
async def uncomplete_item(http_request: Request, item_id: str) -> JSONResponse:
    """Mark item as not completed."""
    return await _controller.uncomplete(item_id, http_request)


@router.post("/{item_id}/toggle", response_model=dict)
async def toggle_item(http_request: Request, item_id: str) -> JSONResponse:
    """Toggle item completion status."""
    return await _controller.toggle(item_id, http_request)
