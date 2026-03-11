"""
Product CRUD Service.

This module provides CRUD operations for Product entities.
"""

from datetime import datetime
from http import HTTPStatus

from ulid import ULID

from constants.api_status import APIStatus
from dtos.requests.product.create import ProductCreateRequestDTO
from dtos.requests.product.update import ProductUpdateRequestDTO
from dtos.responses.base import BaseResponseDTO
from errors.not_found_error import NotFoundError
from models.product import Product
from repositories.product import ProductRepository
from services.product.abstraction import IProductService


class ProductCRUDService(IProductService):
    """
    Service for Product CRUD operations.

    Handles create, read, update, delete operations for products.

    Attributes:
        repository (ProductRepository): Data access repository.
        user_id (int): Current user ID.
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
        repository: ProductRepository = None,
    ):
        """Initialize service with dependencies."""
        super().__init__(urn, user_urn, api_name)
        self._user_id = user_id
        self._repository = repository

    @property
    def repository(self) -> ProductRepository:
        return self._repository

    @repository.setter
    def repository(self, value: ProductRepository):
        self._repository = value

    @property
    def user_id(self) -> int:
        return self._user_id

    async def run(self, request_dto) -> dict:
        """
        Execute the service operation.

        This is the main entry point for the service.
        For CRUD services, this delegates to the appropriate method
        based on the request context.

        Args:
            request_dto: The request data transfer object.

        Returns:
            Response dictionary.
        """
        # CRUD service delegates to specific methods
        # This satisfies the abstract method requirement
        if isinstance(request_dto, ProductCreateRequestDTO):
            response = await self.create(request_dto)
            return response.model_dump()
        elif isinstance(request_dto, ProductUpdateRequestDTO):
            # Update requires ID which would need to be passed differently
            raise NotImplementedError("Use update() method directly with record_id")
        else:
            raise NotImplementedError(f"Unknown request type: {type(request_dto)}")

    async def create(self, request_dto: ProductCreateRequestDTO) -> BaseResponseDTO:
        """
        Create a new product.

        Args:
            request_dto: Creation request data.

        Returns:
            Response with created product data.
        """
        self.logger.debug(f"Creating product: {request_dto.name}")

        record = Product(
            urn=str(ULID()),
            name=request_dto.name,
            description=request_dto.description,
            is_active=True,
            is_deleted=False,
            created_by=self._user_id or 1,
            created_on=datetime.now(),
        )

        record = self.repository.create_record(record)

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="Product created successfully.",
            responseKey="success_product_created",
            data=record.to_dict(),
        )

    async def get_by_id(self, record_id: int) -> BaseResponseDTO:
        """
        Get a product by ID.

        Args:
            record_id: Product ID.

        Returns:
            Response with product data.

        Raises:
            NotFoundError: If product not found.
        """
        self.logger.debug(f"Getting product: {record_id}")

        record = self.repository.retrieve_record_by_id(record_id)

        if not record:
            raise NotFoundError(
                responseMessage="Product not found.",
                responseKey="error_product_not_found",
                httpStatusCode=HTTPStatus.NOT_FOUND,
            )

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="Product retrieved successfully.",
            responseKey="success_product_retrieved",
            data=record.to_dict(),
        )

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> BaseResponseDTO:
        """
        Get all products with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            Response with list of products.
        """
        self.logger.debug(f"Getting all products: skip={skip}, limit={limit}")

        records = self.repository.retrieve_all_records(skip=skip, limit=limit)
        total = self.repository.count_records()

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="Products retrieved successfully.",
            responseKey="success_products_retrieved",
            data={
                "items": [r.to_dict() for r in records],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )

    async def update(
        self,
        record_id: int,
        request_dto: ProductUpdateRequestDTO,
    ) -> BaseResponseDTO:
        """
        Update a product.

        Args:
            record_id: Product ID.
            request_dto: Update request data.

        Returns:
            Response with updated product data.

        Raises:
            NotFoundError: If product not found.
        """
        self.logger.debug(f"Updating product: {record_id}")

        record = self.repository.retrieve_record_by_id(record_id)

        if not record:
            raise NotFoundError(
                responseMessage="Product not found.",
                responseKey="error_product_not_found",
                httpStatusCode=HTTPStatus.NOT_FOUND,
            )

        # Update fields if provided
        if request_dto.name is not None:
            record.name = request_dto.name
        if request_dto.description is not None:
            record.description = request_dto.description
        if request_dto.is_active is not None:
            record.is_active = request_dto.is_active

        record.updated_by = self._user_id
        record.updated_on = datetime.now()

        record = self.repository.update_record(record)

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="Product updated successfully.",
            responseKey="success_product_updated",
            data=record.to_dict(),
        )

    async def delete(self, record_id: int) -> BaseResponseDTO:
        """
        Delete a product (soft delete).

        Args:
            record_id: Product ID.

        Returns:
            Response confirming deletion.

        Raises:
            NotFoundError: If product not found.
        """
        self.logger.debug(f"Deleting product: {record_id}")

        deleted = self.repository.delete_record(record_id, self._user_id or 1)

        if not deleted:
            raise NotFoundError(
                responseMessage="Product not found.",
                responseKey="error_product_not_found",
                httpStatusCode=HTTPStatus.NOT_FOUND,
            )

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="Product deleted successfully.",
            responseKey="success_product_deleted",
            data={},
        )
