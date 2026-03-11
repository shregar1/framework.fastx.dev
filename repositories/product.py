"""
Product Repository.

This module provides data access operations for Product entities.
"""


from loguru import logger
from sqlalchemy.orm import Session

from abstractions.repository import IRepository
from models.product import Product


class ProductRepository(IRepository):
    """
    Repository for Product database operations.

    Provides CRUD operations and queries for Product entities.

    Attributes:
        session (Session): SQLAlchemy database session.
    """

    def __init__(self, session: Session = None):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy session instance.
        """
        self._session = session
        self.logger = logger.bind(repository="ProductRepository")

    @property
    def session(self) -> Session:
        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    def create_record(self, record: Product) -> Product:
        """
        Create a new product record.

        Args:
            record: Product instance to create.

        Returns:
            Created Product with generated ID.
        """
        self.logger.debug(f"Creating product: {record.name}")
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        self.logger.info(f"Created product with ID: {record.id}")
        return record

    def retrieve_record_by_id(self, record_id: int) -> Product | None:
        """
        Retrieve a product by ID.

        Args:
            record_id: Product ID.

        Returns:
            Product instance or None if not found.
        """
        self.logger.debug(f"Retrieving product by ID: {record_id}")
        return (
            self.session.query(Product)
            .filter(Product.id == record_id)
            .filter(not Product.is_deleted)
            .first()
        )

    def retrieve_record_by_urn(self, urn: str) -> Product | None:
        """
        Retrieve a product by URN.

        Args:
            urn: Product URN.

        Returns:
            Product instance or None if not found.
        """
        self.logger.debug(f"Retrieving product by URN: {urn}")
        return (
            self.session.query(Product)
            .filter(Product.urn == urn)
            .filter(not Product.is_deleted)
            .first()
        )

    def retrieve_all_records(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> list[Product]:
        """
        Retrieve all products with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.
            active_only: Only return active records.

        Returns:
            List of Product instances.
        """
        self.logger.debug(f"Retrieving products: skip={skip}, limit={limit}")
        query = self.session.query(Product).filter(not Product.is_deleted)

        if active_only:
            query = query.filter(Product.is_active)

        return query.offset(skip).limit(limit).all()

    def update_record(self, record: Product) -> Product:
        """
        Update an existing product record.

        Args:
            record: Product instance with updated values.

        Returns:
            Updated Product instance.
        """
        self.logger.debug(f"Updating product: {record.id}")
        self.session.commit()
        self.session.refresh(record)
        self.logger.info(f"Updated product: {record.id}")
        return record

    def delete_record(self, record_id: int, deleted_by: int) -> bool:
        """
        Soft delete a product record.

        Args:
            record_id: Product ID to delete.
            deleted_by: ID of user performing deletion.

        Returns:
            True if deleted, False if not found.
        """
        self.logger.debug(f"Deleting product: {record_id}")
        record = self.retrieve_record_by_id(record_id)

        if not record:
            return False

        record.is_deleted = True
        record.updated_by = deleted_by
        self.session.commit()
        self.logger.info(f"Soft deleted product: {record_id}")
        return True

    def count_records(self, active_only: bool = True) -> int:
        """
        Count total product records.

        Args:
            active_only: Only count active records.

        Returns:
            Total count.
        """
        query = self.session.query(Product).filter(not Product.is_deleted)

        if active_only:
            query = query.filter(Product.is_active)

        return query.count()
