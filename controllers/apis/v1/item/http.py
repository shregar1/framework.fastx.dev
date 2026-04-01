"""Shared FastAPI/JSON helpers for the Item API (DRY response and error handling)."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any, TypeVar

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from abstractions.result import Result
from constants.http_header import HttpHeader
from dtos.responses.item import (
    ItemListResponseDTO,
    ItemResponseDTO,
    ItemStatsResponseDTO,
)
from models.item import Item

_TVal = TypeVar("_TVal")


def item_ref_headers(
    *,
    body_reference: str | None,
    http_request: Request | None,
) -> dict[str, str]:
    """Prefer body ``reference_urn``; else echo ``x-reference-urn`` from the request."""
    ref = body_reference
    if ref is None and http_request is not None:
        ref = http_request.headers.get(HttpHeader.X_REFERENCE_URN)
    return HttpHeader().get_reference_urn_header(reference_urn=ref)


def raise_bad_request_if_failure(result: Result[Any, Any]) -> None:
    if result.is_failure:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=result.error,
        )


def _success_payload(result: Result[_TVal, Any]) -> _TVal:
    """Narrow a successful ``Result`` to its value (400 if failure)."""
    raise_bad_request_if_failure(result)
    assert result.value is not None
    return result.value


def raise_unprocessable_if_dto_invalid(dto: Any) -> None:
    is_valid, errors = dto.validate()
    if not is_valid:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail={"errors": errors},
        )


def json_item(
    entity: Item,
    http_request: Request | None,
    *,
    reference_urn: str | None = None,
    status_code: int = HTTPStatus.OK,
) -> JSONResponse:
    dto = ItemResponseDTO.from_entity(entity, reference_urn=reference_urn)
    return JSONResponse(
        status_code=status_code,
        content=dto.to_dict(),
        headers=item_ref_headers(
            body_reference=reference_urn, http_request=http_request
        ),
    )


def json_item_list(entities: list[Item], http_request: Request | None) -> JSONResponse:
    return JSONResponse(
        content=ItemListResponseDTO.from_entities(entities).to_dict(),
        headers=item_ref_headers(body_reference=None, http_request=http_request),
    )


def json_item_stats(
    stats: dict[str, Any], http_request: Request | None
) -> JSONResponse:
    return JSONResponse(
        content=ItemStatsResponseDTO.from_stats(stats).to_dict(),
        headers=item_ref_headers(body_reference=None, http_request=http_request),
    )


def respond_item_list(
    result: Result[list[Item], Any], http_request: Request | None
) -> JSONResponse:
    """Raise on failure, then JSON-wrap a list of items."""
    return json_item_list(_success_payload(result), http_request)


def respond_item_stats(
    result: Result[dict[str, Any], Any], http_request: Request | None
) -> JSONResponse:
    """Raise on failure, then JSON-wrap statistics."""
    return json_item_stats(_success_payload(result), http_request)


def respond_item(
    result: Result[Item, Any], http_request: Request | None
) -> JSONResponse:
    """Raise on failure, then JSON-wrap one item (no reference urn)."""
    return json_item(_success_payload(result), http_request)


def respond_item_with_ref(
    result: Result[Item, Any],
    http_request: Request | None,
    *,
    reference_urn: str | None,
) -> JSONResponse:
    """Raise on failure, then JSON-wrap one item with optional ``reference_urn`` echo."""
    return json_item(
        _success_payload(result), http_request, reference_urn=reference_urn
    )


def respond_created_item(
    result: Result[Item, Any],
    http_request: Request | None,
    *,
    reference_urn: str | None,
) -> JSONResponse:
    """Like :func:`respond_item_with_ref` but with HTTP 201 Created."""
    return json_item(
        _success_payload(result),
        http_request,
        reference_urn=reference_urn,
        status_code=HTTPStatus.CREATED,
    )


def unwrap_item_or_404(result: Result[Item | None, Any], *, item_id: str) -> Item:
    """Map service ``Result[Item | None]`` to entity or raise HTTP errors."""
    raise_bad_request_if_failure(result)
    if result.value is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Item with ID '{item_id}' not found",
        )
    return result.value


def unwrap_deleted_or_404(result: Result[bool, Any], *, item_id: str) -> None:
    raise_bad_request_if_failure(result)
    if not result.value:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Item with ID '{item_id}' not found",
        )


def json_delete_message(item_id: str, http_request: Request | None) -> JSONResponse:
    return JSONResponse(
        content={"message": f"Item '{item_id}' deleted successfully"},
        headers=item_ref_headers(
            body_reference=None,
            http_request=http_request,
        ),
    )
