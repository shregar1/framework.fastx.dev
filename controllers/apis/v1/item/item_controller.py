"""Item Controller - Example controller implementation.

Demonstrates FastMVC controller patterns with FastAPI routes.
"""

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from abstractions.controller import IController
from abstractions.result import Result
from dtos.requests.item import CreateItemRequestDTO, UpdateItemRequestDTO
from dtos.responses.item import (
    ItemListResponseDTO,
    ItemResponseDTO,
    ItemStatsResponseDTO,
)
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

    def _handle_result(
        self, result: Result, status_code: int = HTTPStatus.OK
    ) -> JSONResponse:
        """Handle service result and convert to HTTP response.

        Args:
            result: Service operation result
            status_code: HTTP status code for success

        Returns:
            JSONResponse

        """
        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        if result.value is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Resource not found",
            )

        return JSONResponse(
            status_code=status_code,
            content=result.value.to_dict()
            if hasattr(result.value, "to_dict")
            else result.value,
        )

    # CRUD Endpoints

    async def create(self, request: CreateItemRequestDTO) -> JSONResponse:
        """Create a new item.

        Args:
            request: Create item request

        Returns:
            Created item response

        """
        # Validate request
        is_valid, errors = request.validate()
        if not is_valid:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail={"errors": errors},
            )

        # Create item
        result = await self._service.create_item(
            name=request.name,
            description=request.description,
        )

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        # Convert to response DTO
        response = ItemResponseDTO.from_entity(result.value)

        return JSONResponse(
            status_code=HTTPStatus.CREATED,
            content=response.to_dict(),
        )

    async def get_by_id(self, item_id: str) -> JSONResponse:
        """Get item by ID.

        Args:
            item_id: Item identifier

        Returns:
            Item response

        """
        result = await self._service.get_item(item_id)

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        if result.value is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Item with ID '{item_id}' not found",
            )

        response = ItemResponseDTO.from_entity(result.value)
        return JSONResponse(content=response.to_dict())

    async def get_all(self) -> JSONResponse:
        """Get all items.

        Returns:
            List of items

        """
        result = await self._service.get_all_items()

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        response = ItemListResponseDTO.from_entities(result.value)
        return JSONResponse(content=response.to_dict())

    async def update(self, item_id: str, request: UpdateItemRequestDTO) -> JSONResponse:
        """Update an item.

        Args:
            item_id: Item identifier
            request: Update item request

        Returns:
            Updated item response

        """
        # Validate request
        is_valid, errors = request.validate()
        if not is_valid:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail={"errors": errors},
            )

        # Update item
        result = await self._service.update_item(
            item_id=item_id,
            name=request.name,
            description=request.description,
        )

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        response = ItemResponseDTO.from_entity(result.value)
        return JSONResponse(content=response.to_dict())

    async def delete(self, item_id: str) -> JSONResponse:
        """Delete an item.

        Args:
            item_id: Item identifier

        Returns:
            Deletion confirmation

        """
        result = await self._service.delete_item(item_id)

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        if not result.value:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Item with ID '{item_id}' not found",
            )

        return JSONResponse(
            content={"message": f"Item '{item_id}' deleted successfully"},
        )

    # Action Endpoints

    async def complete(self, item_id: str) -> JSONResponse:
        """Mark item as completed.

        Args:
            item_id: Item identifier

        Returns:
            Updated item response

        """
        result = await self._service.complete_item(item_id)

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        response = ItemResponseDTO.from_entity(result.value)
        return JSONResponse(content=response.to_dict())

    async def uncomplete(self, item_id: str) -> JSONResponse:
        """Mark item as not completed.

        Args:
            item_id: Item identifier

        Returns:
            Updated item response

        """
        result = await self._service.uncomplete_item(item_id)

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        response = ItemResponseDTO.from_entity(result.value)
        return JSONResponse(content=response.to_dict())

    async def toggle(self, item_id: str) -> JSONResponse:
        """Toggle item completion status.

        Args:
            item_id: Item identifier

        Returns:
            Updated item response

        """
        result = await self._service.toggle_item(item_id)

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        response = ItemResponseDTO.from_entity(result.value)
        return JSONResponse(content=response.to_dict())

    # Query Endpoints

    async def search(self, query: str = "") -> JSONResponse:
        """Search items by name.

        Args:
            query: Search query string

        Returns:
            List of matching items

        """
        result = await self._service.search_items(query)

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        response = ItemListResponseDTO.from_entities(result.value)
        return JSONResponse(content=response.to_dict())

    async def get_completed(self) -> JSONResponse:
        """Get all completed items.

        Returns:
            List of completed items

        """
        result = await self._service.get_completed_items()

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        response = ItemListResponseDTO.from_entities(result.value)
        return JSONResponse(content=response.to_dict())

    async def get_pending(self) -> JSONResponse:
        """Get all pending items.

        Returns:
            List of pending items

        """
        result = await self._service.get_pending_items()

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        response = ItemListResponseDTO.from_entities(result.value)
        return JSONResponse(content=response.to_dict())

    async def get_statistics(self) -> JSONResponse:
        """Get item statistics.

        Returns:
            Statistics response

        """
        result = await self._service.get_statistics()

        if result.is_failure:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=result.error,
            )

        response = ItemStatsResponseDTO.from_stats(result.value)
        return JSONResponse(content=response.to_dict())


# Route Definitions

_controller = ItemController()


@router.post("", response_model=dict, status_code=HTTPStatus.CREATED)
async def create_item(request: CreateItemRequestDTO) -> JSONResponse:
    """Create a new item."""
    return await _controller.create(request)


@router.get("", response_model=dict)
async def get_all_items() -> JSONResponse:
    """Get all items."""
    return await _controller.get_all()


@router.get("/search", response_model=dict)
async def search_items(query: str = "") -> JSONResponse:
    """Search items by name."""
    return await _controller.search(query)


@router.get("/completed", response_model=dict)
async def get_completed_items() -> JSONResponse:
    """Get all completed items."""
    return await _controller.get_completed()


@router.get("/pending", response_model=dict)
async def get_pending_items() -> JSONResponse:
    """Get all pending items."""
    return await _controller.get_pending()


@router.get("/statistics", response_model=dict)
async def get_item_statistics() -> JSONResponse:
    """Get item statistics."""
    return await _controller.get_statistics()


@router.get("/{item_id}", response_model=dict)
async def get_item(item_id: str) -> JSONResponse:
    """Get item by ID."""
    return await _controller.get_by_id(item_id)


@router.patch("/{item_id}", response_model=dict)
async def update_item(item_id: str, request: UpdateItemRequestDTO) -> JSONResponse:
    """Update an item."""
    return await _controller.update(item_id, request)


@router.delete("/{item_id}", response_model=dict)
async def delete_item(item_id: str) -> JSONResponse:
    """Delete an item."""
    return await _controller.delete(item_id)


@router.post("/{item_id}/complete", response_model=dict)
async def complete_item(item_id: str) -> JSONResponse:
    """Mark item as completed."""
    return await _controller.complete(item_id)


@router.post("/{item_id}/uncomplete", response_model=dict)
async def uncomplete_item(item_id: str) -> JSONResponse:
    """Mark item as not completed."""
    return await _controller.uncomplete(item_id)


@router.post("/{item_id}/toggle", response_model=dict)
async def toggle_item(item_id: str) -> JSONResponse:
    """Toggle item completion status."""
    return await _controller.toggle(item_id)
