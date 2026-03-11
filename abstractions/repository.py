"""
Repository Abstraction Module.

This module defines the base repository interface implementing the
Repository design pattern. Repositories abstract database operations,
providing a clean interface for data access with built-in caching.

Example:
    >>> class UserRepository(IRepository):
    ...     def __init__(self, session, **kwargs):
    ...         super().__init__(model=UserModel, **kwargs)
    ...         self.session = session
    ...
    ...     def find_by_email(self, email: str) -> UserModel:
    ...         return self.retrieve_record_by_filter(
    ...             filters={"email": email}
    ...         )
"""

from abc import ABC
from datetime import datetime
from operator import attrgetter
from typing import Any

from cachetools import LRUCache, cachedmethod
from loguru import logger
from sqlalchemy import and_, or_
from sqlalchemy.ext.declarative import DeclarativeMeta

from constants.filter_operator import FilterOperator


class IRepository(ABC):
    """
    Abstract base class for database repository pattern implementation.

    The IRepository class provides a standardized interface for data access
    operations in the FastMVC framework. It includes built-in support for:
        - CRUD operations (Create, Read, Update, Delete)
        - Flexible filtering with multiple operators
        - Query result caching with LRU cache
        - Execution time logging for performance monitoring
        - Soft delete support via is_deleted flag

    Attributes:
        urn (str): Unique Request Number for tracing.
        user_urn (str): User's unique resource name.
        api_name (str): Name of the API endpoint.
        user_id (str): Database identifier of the user.
        model (DeclarativeMeta): SQLAlchemy model class for this repository.
        cache (LRUCache): Cache instance for query result caching.
        logger: Structured logger bound with request context.

    Note:
        Subclasses must provide a `session` attribute (SQLAlchemy session)
        for database operations to work.

    Example:
        >>> class ProductRepository(IRepository):
        ...     def __init__(self, session, cache_size: int = 100):
        ...         super().__init__(
        ...             model=ProductModel,
        ...             cache=LRUCache(maxsize=cache_size)
        ...         )
        ...         self.session = session
        ...
        ...     def find_active_by_category(self, category: str):
        ...         return self.retrieve_records_by_filter(
        ...             filters={"category": category, "is_active": True},
        ...             order_by="name"
        ...         )
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
        model: DeclarativeMeta = None,
        cache: LRUCache = None,
    ) -> None:
        """
        Initialize the repository with model and optional caching.

        Args:
            urn (str, optional): Unique Request Number for tracing. Defaults to None.
            user_urn (str, optional): User's unique resource name. Defaults to None.
            api_name (str, optional): Name of the API endpoint. Defaults to None.
            user_id (str, optional): Database ID of the user. Defaults to None.
            model (DeclarativeMeta, optional): SQLAlchemy model class. Defaults to None.
            cache (LRUCache, optional): Cache instance for results. Defaults to None.
        """
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._logger = logger.bind(
            urn=self._urn,
            user_urn=self._user_urn,
            api_name=self._api_name,
            user_id=self._user_id,
        )
        self._model = model
        self._cache = cache

    @property
    def urn(self) -> str:
        """str: Get the Unique Request Number."""
        return self._urn

    @urn.setter
    def urn(self, value: str) -> None:
        """Set the Unique Request Number."""
        self._urn = value

    @property
    def user_urn(self) -> str:
        """str: Get the user's unique resource name."""
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value: str) -> None:
        """Set the user's unique resource name."""
        self._user_urn = value

    @property
    def api_name(self) -> str:
        """str: Get the API endpoint name."""
        return self._api_name

    @api_name.setter
    def api_name(self, value: str) -> None:
        """Set the API endpoint name."""
        self._api_name = value

    @property
    def logger(self):
        """loguru.Logger: Get the structured logger instance."""
        return self._logger

    @logger.setter
    def logger(self, value) -> None:
        """Set the structured logger instance."""
        self._logger = value

    @property
    def user_id(self) -> str:
        """str: Get the user's database identifier."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        """Set the user's database identifier."""
        self._user_id = value

    @property
    def model(self) -> DeclarativeMeta:
        """DeclarativeMeta: Get the SQLAlchemy model class."""
        return self._model

    @model.setter
    def model(self, value: DeclarativeMeta) -> None:
        """Set the SQLAlchemy model class."""
        self._model = value

    @property
    def cache(self) -> LRUCache:
        """LRUCache: Get the cache instance."""
        return self._cache

    @cache.setter
    def cache(self, value: LRUCache) -> None:
        """Set the cache instance."""
        self._cache = value

    def _build_filter_condition(
        self,
        field: str,
        operator: str,
        value: Any,
    ):
        """
        Build a SQLAlchemy filter condition from field, operator, and value.

        Args:
            field: Model attribute name.
            operator: Filter operator (from FilterOperator).
            value: Value to filter by.

        Returns:
            SQLAlchemy filter condition.

        Raises:
            AttributeError: If field doesn't exist on model.
            ValueError: If operator is not supported.
        """
        column = getattr(self.model, field)

        operator_map = {
            FilterOperator.EQ: lambda c, v: c == v,
            FilterOperator.NE: lambda c, v: c != v,
            FilterOperator.LT: lambda c, v: c < v,
            FilterOperator.LE: lambda c, v: c <= v,
            FilterOperator.GT: lambda c, v: c > v,
            FilterOperator.GE: lambda c, v: c >= v,
            FilterOperator.IN: lambda c, v: c.in_(v),
            FilterOperator.NOT_IN: lambda c, v: ~c.in_(v),
            FilterOperator.LIKE: lambda c, v: c.like(v),
            FilterOperator.ILIKE: lambda c, v: c.ilike(v),
            FilterOperator.IS_NULL: lambda c, v: c.is_(None),
            FilterOperator.IS_NOT_NULL: lambda c, v: c.isnot(None),
            FilterOperator.BETWEEN: lambda c, v: c.between(v[0], v[1]),
        }

        if operator not in operator_map:
            raise ValueError(f"Unsupported operator: {operator}")

        return operator_map[operator](column, value)

    def _build_query_filters(
        self,
        filters: dict[str, Any] | list[tuple],
        use_or: bool = False,
    ) -> list:
        """
        Build a list of SQLAlchemy filter conditions from filters specification.

        Supports two filter formats:
        1. Simple dict: {"field": value} - uses equality operator
        2. List of tuples: [("field", "operator", value)] - custom operators

        Args:
            filters: Filter specification (dict or list of tuples).
            use_or: If True, combine filters with OR instead of AND.

        Returns:
            List of SQLAlchemy filter conditions.

        Example:
            >>> # Simple equality filters
            >>> filters = {"status": "active", "is_deleted": False}
            >>>
            >>> # Advanced filters with operators
            >>> filters = [
            ...     ("age", FilterOperator.GTE, 18),
            ...     ("status", FilterOperator.IN, ["active", "pending"]),
            ...     ("name", FilterOperator.LIKE, "%john%"),
            ... ]
        """
        conditions = []

        if isinstance(filters, dict):
            # Simple dict format: {"field": value} uses equality
            for field, value in filters.items():
                conditions.append(
                    self._build_filter_condition(field, FilterOperator.EQ, value)
                )
        elif isinstance(filters, list):
            # List of tuples format: [("field", "operator", value)]
            for filter_spec in filters:
                if len(filter_spec) == 2:
                    # ("field", value) - use equality
                    field, value = filter_spec
                    operator = FilterOperator.EQ
                elif len(filter_spec) == 3:
                    # ("field", "operator", value)
                    field, operator, value = filter_spec
                else:
                    raise ValueError(f"Invalid filter specification: {filter_spec}")

                conditions.append(
                    self._build_filter_condition(field, operator, value)
                )

        return conditions

    def retrieve_record_by_filter(
        self,
        filters: dict[str, Any] | list[tuple] = None,
        use_or: bool = False,
        order_by: str | list[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
    ) -> DeclarativeMeta | None:
        """
        Retrieve a single record matching the filter criteria.

        This is the core flexible filtering method that can be used
        to build any kind of query. It supports simple equality filters
        via dict, or complex filters with operators via list of tuples.

        Args:
            filters: Filter criteria. Can be:
                - Dict[str, Any]: Simple equality filters {"field": value}
                - List[tuple]: Advanced filters [("field", "operator", value)]
            use_or: If True, combine filters with OR. Default is AND.
            order_by: Field(s) to order by before selecting first.
            order_desc: If True, order descending. Default ascending.
            include_deleted: If True, include soft-deleted records.

        Returns:
            The first matching record, or None if not found.

        Example:
            >>> # Simple filter
            >>> user = repo.retrieve_record_by_filter({"email": "user@example.com"})
            >>>
            >>> # Multiple conditions (AND)
            >>> product = repo.retrieve_record_by_filter({
            ...     "category": "electronics",
            ...     "is_active": True
            ... })
            >>>
            >>> # Advanced filter with operators
            >>> order = repo.retrieve_record_by_filter([
            ...     ("user_id", FilterOperator.EQ, user_id),
            ...     ("total", FilterOperator.GTE, 100),
            ...     ("status", FilterOperator.IN, ["pending", "processing"]),
            ... ], order_by="created_at", order_desc=True)
            >>>
            >>> # OR conditions
            >>> record = repo.retrieve_record_by_filter([
            ...     ("email", FilterOperator.EQ, email),
            ...     ("phone", FilterOperator.EQ, phone),
            ... ], use_or=True)
        """
        start_time = datetime.now()

        query = self.session.query(self.model)

        # Apply soft-delete filter unless explicitly including deleted
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(not self.model.is_deleted)

        # Apply custom filters
        if filters:
            conditions = self._build_query_filters(filters, use_or)
            if conditions:
                if use_or:
                    query = query.filter(or_(*conditions))
                else:
                    query = query.filter(and_(*conditions))

        # Apply ordering
        if order_by:
            if isinstance(order_by, str):
                order_by = [order_by]
            for field in order_by:
                column = getattr(self.model, field)
                query = query.order_by(column.desc() if order_desc else column.asc())

        record = query.first()

        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.debug(
            f"retrieve_record_by_filter executed in {execution_time}",
            filters=str(filters),
            found=record is not None,
        )

        return record

    def retrieve_records_by_filter(
        self,
        filters: dict[str, Any] | list[tuple] = None,
        use_or: bool = False,
        order_by: str | list[str] = None,
        order_desc: bool = False,
        limit: int = None,
        offset: int = None,
        include_deleted: bool = False,
    ) -> list[DeclarativeMeta]:
        """
        Retrieve multiple records matching the filter criteria.

        Similar to retrieve_record_by_filter but returns all matching
        records with optional pagination support.

        Args:
            filters: Filter criteria (dict or list of tuples).
            use_or: If True, combine filters with OR. Default is AND.
            order_by: Field(s) to order results by.
            order_desc: If True, order descending. Default ascending.
            limit: Maximum number of records to return.
            offset: Number of records to skip (for pagination).
            include_deleted: If True, include soft-deleted records.

        Returns:
            List of matching records (empty list if none found).

        Example:
            >>> # Get all active products in a category
            >>> products = repo.retrieve_records_by_filter(
            ...     filters={"category": "electronics", "is_active": True},
            ...     order_by="price",
            ...     limit=20,
            ...     offset=0
            ... )
            >>>
            >>> # Complex query with multiple operators
            >>> orders = repo.retrieve_records_by_filter(
            ...     filters=[
            ...         ("created_at", FilterOperator.GTE, start_date),
            ...         ("created_at", FilterOperator.LTE, end_date),
            ...         ("status", FilterOperator.NOT_IN, ["cancelled", "refunded"]),
            ...     ],
            ...     order_by="created_at",
            ...     order_desc=True,
            ...     limit=100
            ... )
        """
        start_time = datetime.now()

        query = self.session.query(self.model)

        # Apply soft-delete filter unless explicitly including deleted
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(not self.model.is_deleted)

        # Apply custom filters
        if filters:
            conditions = self._build_query_filters(filters, use_or)
            if conditions:
                if use_or:
                    query = query.filter(or_(*conditions))
                else:
                    query = query.filter(and_(*conditions))

        # Apply ordering
        if order_by:
            if isinstance(order_by, str):
                order_by = [order_by]
            for field in order_by:
                column = getattr(self.model, field)
                query = query.order_by(column.desc() if order_desc else column.asc())

        # Apply pagination
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        records = query.all()

        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.debug(
            f"retrieve_records_by_filter executed in {execution_time}",
            filters=str(filters),
            count=len(records),
        )

        return records

    def count_by_filter(
        self,
        filters: dict[str, Any] | list[tuple] = None,
        use_or: bool = False,
        include_deleted: bool = False,
    ) -> int:
        """
        Count records matching the filter criteria.

        Args:
            filters: Filter criteria (dict or list of tuples).
            use_or: If True, combine filters with OR. Default is AND.
            include_deleted: If True, include soft-deleted records.

        Returns:
            Number of matching records.

        Example:
            >>> active_count = repo.count_by_filter({"is_active": True})
            >>> recent_orders = repo.count_by_filter([
            ...     ("created_at", FilterOperator.GTE, last_week),
            ... ])
        """
        start_time = datetime.now()

        query = self.session.query(self.model)

        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(not self.model.is_deleted)

        if filters:
            conditions = self._build_query_filters(filters, use_or)
            if conditions:
                if use_or:
                    query = query.filter(or_(*conditions))
                else:
                    query = query.filter(and_(*conditions))

        count = query.count()

        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.debug(
            f"count_by_filter executed in {execution_time}",
            filters=str(filters),
            count=count,
        )

        return count

    def exists_by_filter(
        self,
        filters: dict[str, Any] | list[tuple] = None,
        use_or: bool = False,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check if any record exists matching the filter criteria.

        More efficient than count_by_filter when you just need to
        know if a record exists.

        Args:
            filters: Filter criteria (dict or list of tuples).
            use_or: If True, combine filters with OR. Default is AND.
            include_deleted: If True, include soft-deleted records.

        Returns:
            True if at least one record matches, False otherwise.

        Example:
            >>> if repo.exists_by_filter({"email": email}):
            ...     raise ValueError("Email already registered")
        """
        record = self.retrieve_record_by_filter(
            filters=filters,
            use_or=use_or,
            include_deleted=include_deleted,
        )
        return record is not None

    def create_record(
        self,
        record: DeclarativeMeta,
    ) -> DeclarativeMeta:
        """
        Create a new record in the database.

        Adds the record to the session and commits the transaction.
        Logs the execution time for performance monitoring.

        Args:
            record (DeclarativeMeta): The model instance to persist.

        Returns:
            DeclarativeMeta: The persisted record with generated ID.

        Raises:
            SQLAlchemyError: If database operation fails.

        Example:
            >>> user = UserModel(email="user@example.com", name="John")
            >>> created_user = repository.create_record(user)
            >>> print(created_user.id)  # Auto-generated ID
        """
        start_time = datetime.now()
        self.session.add(record)
        self.session.commit()

        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"create_record executed in {execution_time}")

        return record

    @cachedmethod(attrgetter('_cache'))
    def retrieve_record_by_id(
        self,
        id: str,
        is_deleted: bool = False
    ) -> DeclarativeMeta | None:
        """
        Retrieve a record by its primary key ID.

        Results are cached using LRU cache for improved performance
        on repeated queries. Uses retrieve_record_by_filter internally.

        Args:
            id (str): The primary key ID of the record.
            is_deleted (bool, optional): Filter by soft-delete status.
                Defaults to False (only active records).

        Returns:
            Optional[DeclarativeMeta]: The found record or None if not found.

        Example:
            >>> user = repository.retrieve_record_by_id("user-123")
            >>> if user:
            ...     print(user.email)
        """
        return self.retrieve_record_by_filter(
            filters={"id": id},
            include_deleted=is_deleted,
        )

    @cachedmethod(attrgetter('_cache'))
    def retrieve_record_by_urn(
        self,
        urn: str,
        is_deleted: bool = False,
    ) -> DeclarativeMeta | None:
        """
        Retrieve a record by its Unique Resource Name (URN).

        Results are cached using LRU cache for improved performance
        on repeated queries. Uses retrieve_record_by_filter internally.

        Args:
            urn (str): The unique resource name of the record.
            is_deleted (bool, optional): Filter by soft-delete status.
                Defaults to False (only active records).

        Returns:
            Optional[DeclarativeMeta]: The found record or None if not found.

        Example:
            >>> user = repository.retrieve_record_by_urn("urn:user:abc123")
            >>> if user:
            ...     print(user.name)
        """
        return self.retrieve_record_by_filter(
            filters={"urn": urn},
            include_deleted=is_deleted,
        )

    def update_record(
        self,
        id: str,
        new_data: dict[str, Any],
    ) -> DeclarativeMeta:
        """
        Update an existing record with new data.

        Finds the record by ID and updates the specified attributes.
        Commits the transaction and logs execution time.

        Args:
            id (str): The primary key ID of the record to update.
            new_data (dict): Dictionary of attribute names to new values.

        Returns:
            DeclarativeMeta: The updated record.

        Raises:
            ValueError: If no record with the given ID exists.
            SQLAlchemyError: If database operation fails.

        Example:
            >>> updated_user = repository.update_record(
            ...     id="user-123",
            ...     new_data={"name": "Jane Doe", "email": "jane@example.com"}
            ... )
        """
        start_time = datetime.now()
        record = self.retrieve_record_by_filter(
            filters={"id": id},
            include_deleted=True,  # Allow updating soft-deleted records
        )

        if not record:
            raise ValueError(f"{self.model.__name__} with id {id} not found")

        for attr, value in new_data.items():
            setattr(record, attr, value)

        self.session.commit()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"update_record executed in {execution_time}")

        return record

    def update_record_by_filter(
        self,
        filters: dict[str, Any] | list[tuple],
        new_data: dict[str, Any],
        use_or: bool = False,
    ) -> DeclarativeMeta | None:
        """
        Update a record matching the filter criteria.

        Finds the first record matching the filters and updates it.

        Args:
            filters: Filter criteria to find the record.
            new_data: Dictionary of attribute names to new values.
            use_or: If True, combine filters with OR.

        Returns:
            The updated record, or None if not found.

        Example:
            >>> repo.update_record_by_filter(
            ...     filters={"email": "old@example.com"},
            ...     new_data={"email": "new@example.com", "updated_at": datetime.now()}
            ... )
        """
        start_time = datetime.now()
        record = self.retrieve_record_by_filter(
            filters=filters,
            use_or=use_or,
            include_deleted=True,
        )

        if not record:
            return None

        for attr, value in new_data.items():
            setattr(record, attr, value)

        self.session.commit()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"update_record_by_filter executed in {execution_time}")

        return record

    def delete_record_by_filter(
        self,
        filters: dict[str, Any] | list[tuple],
        use_or: bool = False,
        hard_delete: bool = False,
        deleted_by: Any = None,
    ) -> bool:
        """
        Delete a record matching the filter criteria.

        By default performs a soft delete (sets is_deleted=True).
        Use hard_delete=True for permanent deletion.

        Args:
            filters: Filter criteria to find the record.
            use_or: If True, combine filters with OR.
            hard_delete: If True, permanently delete the record.
            deleted_by: User ID performing the deletion (for audit).

        Returns:
            True if a record was deleted, False if not found.

        Example:
            >>> # Soft delete
            >>> repo.delete_record_by_filter(
            ...     filters={"id": record_id},
            ...     deleted_by=current_user.id
            ... )
            >>>
            >>> # Hard delete
            >>> repo.delete_record_by_filter(
            ...     filters={"status": "expired"},
            ...     hard_delete=True
            ... )
        """
        start_time = datetime.now()
        record = self.retrieve_record_by_filter(
            filters=filters,
            use_or=use_or,
            include_deleted=False,
        )

        if not record:
            return False

        if hard_delete:
            self.session.delete(record)
        else:
            record.is_deleted = True
            if deleted_by is not None and hasattr(record, 'updated_by'):
                record.updated_by = deleted_by
            if hasattr(record, 'updated_on'):
                record.updated_on = datetime.now()

        self.session.commit()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(
            f"delete_record_by_filter executed in {execution_time}",
            hard_delete=hard_delete,
        )

        return True
