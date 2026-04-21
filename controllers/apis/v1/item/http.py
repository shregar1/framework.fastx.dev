"""HTTP response helpers for the sample Item API."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from constants.response_keys import ResponseKey
from fast_platform.errors import NotFoundError
from fastapi import Request
from fastapi.responses import JSONResponse

from abstractions.result import Result
from dtos.requests.item import CreateItemRequestDTO, UpdateItemRequestDTO
from dtos.responses.apis.v1.item import ItemResponseDTO
from models.item import Item


class ItemHttpResponseBuilder:
    """Build JSON responses for item routes (flat JSON bodies for sample CRUD)."""

    @staticmethod
    def _item_payload(entity: Item) -> dict[str, Any]:
        """Serialize a domain :class:`Item` via the response DTO."""
        return ItemResponseDTO.from_entity(entity).to_payload()

    @staticmethod
    def raise_unprocessable_if_dto_invalid(
        body: CreateItemRequestDTO | UpdateItemRequestDTO,
    ) -> None:
        # Pydantic field/model validators run at instantiation; nothing to do here.
        del body

    @staticmethod
    def respond_created_item(
        result: Result[Item, Any],
        http_request: Request | None,
        *,
        reference_urn: str = "",
    ) -> JSONResponse:
        del http_request  # sample API does not attach correlation headers
        if result.is_failure:
            return JSONResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content={"detail": str(result.error)},
            )
        item = result.value
        payload: dict[str, Any] = ItemHttpResponseBuilder._item_payload(item)
        if reference_urn:
            payload["reference_urn"] = reference_urn
        return JSONResponse(status_code=HTTPStatus.CREATED, content=payload)

    @staticmethod
    def unwrap_item_or_404(
        result: Result[Item | None, Any],
        *,
        item_id: str,
    ) -> Item:
        if result.is_failure:
            raise NotFoundError(
                responseMessage=str(result.error),
                responseKey=ResponseKey.ERROR_ITEM_NOT_FOUND,
            )
        if result.value is None:
            raise NotFoundError(
                responseMessage=f"Item not found: {item_id}",
                responseKey=ResponseKey.ERROR_ITEM_NOT_FOUND,
            )
        return result.value

    @staticmethod
    def json_item(entity: Item, http_request: Request | None) -> JSONResponse:
        del http_request
        return JSONResponse(content=ItemHttpResponseBuilder._item_payload(entity))

    @staticmethod
    def respond_item_list(
        result: Result[list[Item], Any],
        http_request: Request | None,
    ) -> JSONResponse:
        del http_request
        if result.is_failure:
            return JSONResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content={"detail": str(result.error)},
            )
        items = result.value
        return JSONResponse(content=[ItemHttpResponseBuilder._item_payload(i) for i in items])

    @staticmethod
    def respond_item_with_ref(
        result: Result[Item, Any],
        http_request: Request | None,
        *,
        reference_urn: str = "",
    ) -> JSONResponse:
        del http_request
        if result.is_failure:
            return JSONResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content={"detail": str(result.error)},
            )
        item = result.value
        payload = ItemHttpResponseBuilder._item_payload(item)
        if reference_urn:
            payload["reference_urn"] = reference_urn
        return JSONResponse(content=payload)

    @staticmethod
    def unwrap_deleted_or_404(
        result: Result[bool, Any],
        *,
        item_id: str,
    ) -> None:
        if result.is_failure:
            raise NotFoundError(
                responseMessage=str(result.error),
                responseKey=ResponseKey.ERROR_ITEM_NOT_FOUND,
            )
        if not result.value:
            raise NotFoundError(
                responseMessage=f"Item not found: {item_id}",
                responseKey=ResponseKey.ERROR_ITEM_NOT_FOUND,
            )

    @staticmethod
    def json_delete_message(item_id: str, http_request: Request | None) -> JSONResponse:
        del http_request
        return JSONResponse(
            content={"deleted": True, "id": item_id},
        )

    @staticmethod
    def respond_item(
        result: Result[Item, Any],
        http_request: Request | None,
    ) -> JSONResponse:
        del http_request
        if result.is_failure:
            return JSONResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content={"detail": str(result.error)},
            )
        return JSONResponse(content=ItemHttpResponseBuilder._item_payload(result.value))

    @staticmethod
    def respond_item_stats(
        result: Result[dict[str, Any], Any],
        http_request: Request | None,
    ) -> JSONResponse:
        del http_request
        if result.is_failure:
            return JSONResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content={"detail": str(result.error)},
            )
        return JSONResponse(content=result.value)
