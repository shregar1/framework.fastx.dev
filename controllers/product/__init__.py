"""
Product Controller Package.

This package contains API route handlers for Product operations.
Provides RESTful CRUD endpoints.

Routes:
    POST   /product         - Create new product
    GET    /product         - List all products
    GET    /product/{id}    - Get product by ID
    PUT    /product/{id}    - Update product
    DELETE /product/{id}    - Delete product
"""

from collections.abc import Callable
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.orm import Session

from constants.api_status import APIStatus
from dependencies.db import DBDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dtos.requests.product.create import ProductCreateRequestDTO
from dtos.requests.product.update import ProductUpdateRequestDTO
from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from repositories.product import ProductRepository
from services.product.crud import ProductCRUDService
from utilities.dictionary import DictionaryUtility

logger.debug("Registering Product routes.")

router = APIRouter(prefix="/product", tags=["Product"])


def get_product_repository(
    session: Session = Depends(DBDependency.derive),
) -> ProductRepository:
    """Dependency to get Product repository."""
    repo = ProductRepository()
    repo.session = session
    return repo


def get_product_service_factory() -> Callable[..., ProductCRUDService]:
    """Factory for creating Product service instances."""
    def factory(
        urn: str,
        user_id: int,
        repository: ProductRepository,
    ) -> ProductCRUDService:
        service = ProductCRUDService()
        service.urn = urn
        service._user_id = user_id
        service.repository = repository
        return service
    return factory


@router.post("", summary="Create Product")
async def create_product(
    request: Request,
    request_payload: ProductCreateRequestDTO,
    repository: ProductRepository = Depends(get_product_repository),
    service_factory: Callable = Depends(get_product_service_factory),
    dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
) -> JSONResponse:
    """
    Create a new product.

    Args:
        request: FastAPI request.
        request_payload: Product creation data.

    Returns:
        JSONResponse with created product.
    """
    try:
        urn = getattr(request.state, "urn", "unknown")
        user_id = getattr(request.state, "user_id", 1)

        service = service_factory(
            urn=urn,
            user_id=user_id,
            repository=repository,
        )

        response = await service.create(request_payload)

        return JSONResponse(
            status_code=200,
            content=dictionary_utility.convert_dict_keys_to_camel_case(
                response.model_dump()
            ),
        )
    except BadInputError as e:
        return JSONResponse(
            status_code=e.http_status_code,
            content={
                "transactionUrn": getattr(request.state, "urn", "unknown"),
                "status": APIStatus.FAILED,
                "responseMessage": e.response_message,
                "responseKey": e.response_key,
                "data": {},
            },
        )
    except Exception as e:
        logger.exception(f"Error creating product: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "transactionUrn": getattr(request.state, "urn", "unknown"),
                "status": APIStatus.FAILED,
                "responseMessage": "Internal server error.",
                "responseKey": "error_internal",
                "data": {},
            },
        )


@router.get("", summary="List Products")
async def list_products(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: ProductRepository = Depends(get_product_repository),
    service_factory: Callable = Depends(get_product_service_factory),
    dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
) -> JSONResponse:
    """
    List all products with pagination.

    Args:
        skip: Records to skip.
        limit: Max records to return.

    Returns:
        JSONResponse with list of products.
    """
    try:
        urn = getattr(request.state, "urn", "unknown")
        user_id = getattr(request.state, "user_id", 1)

        service = service_factory(
            urn=urn,
            user_id=user_id,
            repository=repository,
        )

        response = await service.get_all(skip=skip, limit=limit)

        return JSONResponse(
            status_code=200,
            content=dictionary_utility.convert_dict_keys_to_camel_case(
                response.model_dump()
            ),
        )
    except Exception as e:
        logger.exception(f"Error listing products: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "transactionUrn": getattr(request.state, "urn", "unknown"),
                "status": APIStatus.FAILED,
                "responseMessage": "Internal server error.",
                "responseKey": "error_internal",
                "data": {},
            },
        )


@router.get("/{record_id}", summary="Get Product")
async def get_product(
    request: Request,
    record_id: int,
    repository: ProductRepository = Depends(get_product_repository),
    service_factory: Callable = Depends(get_product_service_factory),
    dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
) -> JSONResponse:
    """
    Get a product by ID.

    Args:
        record_id: Product ID.

    Returns:
        JSONResponse with product data.
    """
    try:
        urn = getattr(request.state, "urn", "unknown")
        user_id = getattr(request.state, "user_id", 1)

        service = service_factory(
            urn=urn,
            user_id=user_id,
            repository=repository,
        )

        response = await service.get_by_id(record_id)

        return JSONResponse(
            status_code=200,
            content=dictionary_utility.convert_dict_keys_to_camel_case(
                response.model_dump()
            ),
        )
    except NotFoundError as e:
        return JSONResponse(
            status_code=e.http_status_code,
            content={
                "transactionUrn": getattr(request.state, "urn", "unknown"),
                "status": APIStatus.FAILED,
                "responseMessage": e.response_message,
                "responseKey": e.response_key,
                "data": {},
            },
        )
    except Exception as e:
        logger.exception(f"Error getting product: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "transactionUrn": getattr(request.state, "urn", "unknown"),
                "status": APIStatus.FAILED,
                "responseMessage": "Internal server error.",
                "responseKey": "error_internal",
                "data": {},
            },
        )


@router.put("/{record_id}", summary="Update Product")
async def update_product(
    request: Request,
    record_id: int,
    request_payload: ProductUpdateRequestDTO,
    repository: ProductRepository = Depends(get_product_repository),
    service_factory: Callable = Depends(get_product_service_factory),
    dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
) -> JSONResponse:
    """
    Update a product.

    Args:
        record_id: Product ID.
        request_payload: Update data.

    Returns:
        JSONResponse with updated product.
    """
    try:
        urn = getattr(request.state, "urn", "unknown")
        user_id = getattr(request.state, "user_id", 1)

        service = service_factory(
            urn=urn,
            user_id=user_id,
            repository=repository,
        )

        response = await service.update(record_id, request_payload)

        return JSONResponse(
            status_code=200,
            content=dictionary_utility.convert_dict_keys_to_camel_case(
                response.model_dump()
            ),
        )
    except NotFoundError as e:
        return JSONResponse(
            status_code=e.http_status_code,
            content={
                "transactionUrn": getattr(request.state, "urn", "unknown"),
                "status": APIStatus.FAILED,
                "responseMessage": e.response_message,
                "responseKey": e.response_key,
                "data": {},
            },
        )
    except Exception as e:
        logger.exception(f"Error updating product: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "transactionUrn": getattr(request.state, "urn", "unknown"),
                "status": APIStatus.FAILED,
                "responseMessage": "Internal server error.",
                "responseKey": "error_internal",
                "data": {},
            },
        )


@router.delete("/{record_id}", summary="Delete Product")
async def delete_product(
    request: Request,
    record_id: int,
    repository: ProductRepository = Depends(get_product_repository),
    service_factory: Callable = Depends(get_product_service_factory),
    dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
) -> JSONResponse:
    """
    Delete a product (soft delete).

    Args:
        record_id: Product ID.

    Returns:
        JSONResponse confirming deletion.
    """
    try:
        urn = getattr(request.state, "urn", "unknown")
        user_id = getattr(request.state, "user_id", 1)

        service = service_factory(
            urn=urn,
            user_id=user_id,
            repository=repository,
        )

        response = await service.delete(record_id)

        return JSONResponse(
            status_code=200,
            content=dictionary_utility.convert_dict_keys_to_camel_case(
                response.model_dump()
            ),
        )
    except NotFoundError as e:
        return JSONResponse(
            status_code=e.http_status_code,
            content={
                "transactionUrn": getattr(request.state, "urn", "unknown"),
                "status": APIStatus.FAILED,
                "responseMessage": e.response_message,
                "responseKey": e.response_key,
                "data": {},
            },
        )
    except Exception as e:
        logger.exception(f"Error deleting product: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "transactionUrn": getattr(request.state, "urn", "unknown"),
                "status": APIStatus.FAILED,
                "responseMessage": "Internal server error.",
                "responseKey": "error_internal",
                "data": {},
            },
        )


logger.debug("Registered Product routes.")
