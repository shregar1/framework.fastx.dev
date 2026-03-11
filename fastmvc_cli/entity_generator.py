"""
FastMVC Entity Generator.

This module generates complete CRUD scaffolding for new entities,
including models, repositories, services, controllers, DTOs, and tests.

Example:
    >>> generator = EntityGenerator("Product", project_path)
    >>> generator.generate()

This creates:
    - models/product.py
    - repositories/product.py
    - services/product/
    - controllers/product/
    - dtos/requests/product/
    - dependencies/repositories/product.py
    - dependencies/services/product/
    - tests/unit/*/test_product.py
"""

from pathlib import Path

import click


class EntityGenerator:
    """
    Generator for complete entity CRUD scaffolding.

    Creates all layers needed for a new entity following FastMVC patterns.
    """

    def __init__(
        self,
        entity_name: str,
        project_path: Path,
        with_tests: bool = True,
    ):
        """
        Initialize entity generator.

        Args:
            entity_name: Name of the entity (e.g., "Product", "Order").
            project_path: Path to the FastMVC project.
            with_tests: Whether to generate test files.
        """
        self.entity_name = entity_name
        self.entity_lower = entity_name.lower()
        self.entity_snake = self._to_snake_case(entity_name)
        self.project_path = Path(project_path)
        self.with_tests = with_tests

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to CamelCase."""
        components = name.split('_')
        return ''.join(x.title() for x in components)

    def generate(self):
        """Generate all entity files."""
        click.secho("  ● Generating model...", fg="white")
        self._generate_model()

        click.secho("  ● Generating repository...", fg="white")
        self._generate_repository()

        click.secho("  ● Generating DTOs...", fg="white")
        self._generate_dtos()

        click.secho("  ● Generating service...", fg="white")
        self._generate_service()

        click.secho("  ● Generating controller...", fg="white")
        self._generate_controller()

        click.secho("  ● Generating dependencies...", fg="white")
        self._generate_dependencies()

        if self.with_tests:
            click.secho("  ● Generating tests...", fg="white")
            self._generate_tests()

        click.secho("  ● Updating __init__.py files...", fg="white")
        self._update_init_files()

    def _generate_model(self):
        """Generate SQLAlchemy model."""
        model_content = f'''"""
{self.entity_name} Database Model.

This module defines the SQLAlchemy ORM model for {self.entity_name} entities.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Index
from sqlalchemy.orm import relationship

from models import Base
from constants.db.table import Table


class {self.entity_name}(Base):
    """
    {self.entity_name} database model.

    Represents a {self.entity_lower} entity in the database.

    Attributes:
        id (int): Primary key.
        urn (str): Unique resource name (ULID).
        name (str): {self.entity_name} name.
        description (str): Optional description.
        is_active (bool): Whether the {self.entity_lower} is active.
        is_deleted (bool): Soft delete flag.
        created_by (int): ID of user who created this record.
        created_on (datetime): Creation timestamp.
        updated_by (int): ID of user who last updated this record.
        updated_on (datetime): Last update timestamp.
    """

    __tablename__ = "{self.entity_snake}s"

    id = Column(Integer, primary_key=True, autoincrement=True)
    urn = Column(String(26), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, default=datetime.now, nullable=False)
    updated_by = Column(Integer, nullable=True)
    updated_on = Column(DateTime, nullable=True, onupdate=datetime.now)

    __table_args__ = (
        Index("ix_{self.entity_snake}_name", "name"),
        Index("ix_{self.entity_snake}_active", "is_active", "is_deleted"),
    )

    def __repr__(self) -> str:
        return f"<{self.entity_name}(id={{self.id}}, name={{self.name}})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {{
            "id": self.id,
            "urn": self.urn,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_on": str(self.created_on) if self.created_on else None,
            "updated_on": str(self.updated_on) if self.updated_on else None,
        }}
'''
        model_path = self.project_path / "models" / f"{self.entity_snake}.py"
        model_path.write_text(model_content)

    def _generate_repository(self):
        """Generate repository class."""
        repo_content = f'''"""
{self.entity_name} Repository.

This module provides data access operations for {self.entity_name} entities.
"""

from typing import List, Optional

from sqlalchemy.orm import Session
from loguru import logger

from abstractions.repository import IRepository
from models.{self.entity_snake} import {self.entity_name}


class {self.entity_name}Repository(IRepository):
    """
    Repository for {self.entity_name} database operations.

    Provides CRUD operations and queries for {self.entity_name} entities.

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
        self.logger = logger.bind(repository="{self.entity_name}Repository")

    @property
    def session(self) -> Session:
        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    def create_record(self, record: {self.entity_name}) -> {self.entity_name}:
        """
        Create a new {self.entity_lower} record.

        Args:
            record: {self.entity_name} instance to create.

        Returns:
            Created {self.entity_name} with generated ID.
        """
        self.logger.debug(f"Creating {self.entity_lower}: {{record.name}}")
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        self.logger.info(f"Created {self.entity_lower} with ID: {{record.id}}")
        return record

    def retrieve_record_by_id(self, record_id: int) -> Optional[{self.entity_name}]:
        """
        Retrieve a {self.entity_lower} by ID.

        Args:
            record_id: {self.entity_name} ID.

        Returns:
            {self.entity_name} instance or None if not found.
        """
        self.logger.debug(f"Retrieving {self.entity_lower} by ID: {{record_id}}")
        return (
            self.session.query({self.entity_name})
            .filter({self.entity_name}.id == record_id)
            .filter({self.entity_name}.is_deleted == False)
            .first()
        )

    def retrieve_record_by_urn(self, urn: str) -> Optional[{self.entity_name}]:
        """
        Retrieve a {self.entity_lower} by URN.

        Args:
            urn: {self.entity_name} URN.

        Returns:
            {self.entity_name} instance or None if not found.
        """
        self.logger.debug(f"Retrieving {self.entity_lower} by URN: {{urn}}")
        return (
            self.session.query({self.entity_name})
            .filter({self.entity_name}.urn == urn)
            .filter({self.entity_name}.is_deleted == False)
            .first()
        )

    def retrieve_all_records(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[{self.entity_name}]:
        """
        Retrieve all {self.entity_lower}s with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.
            active_only: Only return active records.

        Returns:
            List of {self.entity_name} instances.
        """
        self.logger.debug(f"Retrieving {self.entity_lower}s: skip={{skip}}, limit={{limit}}")
        query = self.session.query({self.entity_name}).filter({self.entity_name}.is_deleted == False)

        if active_only:
            query = query.filter({self.entity_name}.is_active == True)

        return query.offset(skip).limit(limit).all()

    def update_record(self, record: {self.entity_name}) -> {self.entity_name}:
        """
        Update an existing {self.entity_lower} record.

        Args:
            record: {self.entity_name} instance with updated values.

        Returns:
            Updated {self.entity_name} instance.
        """
        self.logger.debug(f"Updating {self.entity_lower}: {{record.id}}")
        self.session.commit()
        self.session.refresh(record)
        self.logger.info(f"Updated {self.entity_lower}: {{record.id}}")
        return record

    def delete_record(self, record_id: int, deleted_by: int) -> bool:
        """
        Soft delete a {self.entity_lower} record.

        Args:
            record_id: {self.entity_name} ID to delete.
            deleted_by: ID of user performing deletion.

        Returns:
            True if deleted, False if not found.
        """
        self.logger.debug(f"Deleting {self.entity_lower}: {{record_id}}")
        record = self.retrieve_record_by_id(record_id)

        if not record:
            return False

        record.is_deleted = True
        record.updated_by = deleted_by
        self.session.commit()
        self.logger.info(f"Soft deleted {self.entity_lower}: {{record_id}}")
        return True

    def count_records(self, active_only: bool = True) -> int:
        """
        Count total {self.entity_lower} records.

        Args:
            active_only: Only count active records.

        Returns:
            Total count.
        """
        query = self.session.query({self.entity_name}).filter({self.entity_name}.is_deleted == False)

        if active_only:
            query = query.filter({self.entity_name}.is_active == True)

        return query.count()
'''
        repo_path = self.project_path / "repositories" / f"{self.entity_snake}.py"
        repo_path.write_text(repo_content)

    def _generate_dtos(self):
        """Generate request/response DTOs."""
        # Create DTO directory
        dto_dir = self.project_path / "dtos" / "requests" / self.entity_snake
        dto_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_content = f'''"""
{self.entity_name} Request DTOs.

This package contains request DTOs for {self.entity_name} operations.
"""

from dtos.requests.{self.entity_snake}.create import {self.entity_name}CreateRequestDTO
from dtos.requests.{self.entity_snake}.update import {self.entity_name}UpdateRequestDTO

__all__ = ["{self.entity_name}CreateRequestDTO", "{self.entity_name}UpdateRequestDTO"]
'''
        (dto_dir / "__init__.py").write_text(init_content)

        # Create DTO
        create_dto_content = f'''"""
{self.entity_name} Create Request DTO.

This module defines the request DTO for creating new {self.entity_lower}s.
"""

from typing import Optional
from pydantic import field_validator

from dtos.requests.abstraction import IRequestDTO
from dtos.base import EnhancedBaseModel


class {self.entity_name}CreateRequestDTO(IRequestDTO, EnhancedBaseModel):
    """
    Request DTO for creating a new {self.entity_lower}.

    Attributes:
        reference_number (str): Client-provided request tracking ID.
        name (str): {self.entity_name} name.
        description (str): Optional description.
    """

    name: str
    description: Optional[str] = None

    class Config:
        extra = "forbid"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and sanitize name."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        if len(v) > 255:
            raise ValueError("Name cannot exceed 255 characters")
        return v.strip()
'''
        (dto_dir / "create.py").write_text(create_dto_content)

        # Update DTO
        update_dto_content = f'''"""
{self.entity_name} Update Request DTO.

This module defines the request DTO for updating {self.entity_lower}s.
"""

from typing import Optional
from pydantic import field_validator

from dtos.requests.abstraction import IRequestDTO
from dtos.base import EnhancedBaseModel


class {self.entity_name}UpdateRequestDTO(IRequestDTO, EnhancedBaseModel):
    """
    Request DTO for updating a {self.entity_lower}.

    Attributes:
        reference_number (str): Client-provided request tracking ID.
        name (str): Optional new name.
        description (str): Optional new description.
        is_active (bool): Optional active status.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        extra = "forbid"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize name if provided."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Name cannot be empty")
        if len(v) > 255:
            raise ValueError("Name cannot exceed 255 characters")
        return v.strip()
'''
        (dto_dir / "update.py").write_text(update_dto_content)

    def _generate_service(self):
        """Generate service layer."""
        service_dir = self.project_path / "services" / self.entity_snake
        service_dir.mkdir(parents=True, exist_ok=True)

        # __init__.py
        init_content = f'''"""
{self.entity_name} Services Package.

This package contains business logic services for {self.entity_name} operations.
"""

from services.{self.entity_snake}.crud import {self.entity_name}CRUDService

__all__ = ["{self.entity_name}CRUDService"]
'''
        (service_dir / "__init__.py").write_text(init_content)

        # Abstraction
        abstraction_content = f'''"""
{self.entity_name} Service Abstraction.

This module defines the base interface for {self.entity_name} services.
"""

from abstractions.service import IService
from loguru import logger


class I{self.entity_name}Service(IService):
    """
    Abstract base class for {self.entity_name} services.
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
    ):
        """Initialize service with request context."""
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self.logger = logger.bind(service=self.__class__.__name__)

    @property
    def urn(self) -> str:
        return self._urn

    @urn.setter
    def urn(self, value: str):
        self._urn = value
'''
        (service_dir / "abstraction.py").write_text(abstraction_content)

        # CRUD Service
        crud_content = f'''"""
{self.entity_name} CRUD Service.

This module provides CRUD operations for {self.entity_name} entities.
"""

from datetime import datetime
from http import HTTPStatus
from typing import List, Optional

from ulid import ULID

from constants.api_status import APIStatus
from dtos.requests.{self.entity_snake}.create import {self.entity_name}CreateRequestDTO
from dtos.requests.{self.entity_snake}.update import {self.entity_name}UpdateRequestDTO
from dtos.responses.base import BaseResponseDTO
from errors.not_found_error import NotFoundError
from errors.bad_input_error import BadInputError
from models.{self.entity_snake} import {self.entity_name}
from repositories.{self.entity_snake} import {self.entity_name}Repository
from services.{self.entity_snake}.abstraction import I{self.entity_name}Service


class {self.entity_name}CRUDService(I{self.entity_name}Service):
    """
    Service for {self.entity_name} CRUD operations.

    Handles create, read, update, delete operations for {self.entity_lower}s.

    Attributes:
        repository ({self.entity_name}Repository): Data access repository.
        user_id (int): Current user ID.
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
        repository: {self.entity_name}Repository = None,
    ):
        """Initialize service with dependencies."""
        super().__init__(urn, user_urn, api_name)
        self._user_id = user_id
        self._repository = repository

    @property
    def repository(self) -> {self.entity_name}Repository:
        return self._repository

    @repository.setter
    def repository(self, value: {self.entity_name}Repository):
        self._repository = value

    @property
    def user_id(self) -> int:
        return self._user_id

    async def create(self, request_dto: {self.entity_name}CreateRequestDTO) -> BaseResponseDTO:
        """
        Create a new {self.entity_lower}.

        Args:
            request_dto: Creation request data.

        Returns:
            Response with created {self.entity_lower} data.
        """
        self.logger.debug(f"Creating {self.entity_lower}: {{request_dto.name}}")

        record = {self.entity_name}(
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
            responseMessage="{self.entity_name} created successfully.",
            responseKey="success_{self.entity_snake}_created",
            data=record.to_dict(),
        )

    async def get_by_id(self, record_id: int) -> BaseResponseDTO:
        """
        Get a {self.entity_lower} by ID.

        Args:
            record_id: {self.entity_name} ID.

        Returns:
            Response with {self.entity_lower} data.

        Raises:
            NotFoundError: If {self.entity_lower} not found.
        """
        self.logger.debug(f"Getting {self.entity_lower}: {{record_id}}")

        record = self.repository.retrieve_record_by_id(record_id)

        if not record:
            raise NotFoundError(
                responseMessage="{self.entity_name} not found.",
                responseKey="error_{self.entity_snake}_not_found",
                httpStatusCode=HTTPStatus.NOT_FOUND,
            )

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="{self.entity_name} retrieved successfully.",
            responseKey="success_{self.entity_snake}_retrieved",
            data=record.to_dict(),
        )

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> BaseResponseDTO:
        """
        Get all {self.entity_lower}s with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            Response with list of {self.entity_lower}s.
        """
        self.logger.debug(f"Getting all {self.entity_lower}s: skip={{skip}}, limit={{limit}}")

        records = self.repository.retrieve_all_records(skip=skip, limit=limit)
        total = self.repository.count_records()

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="{self.entity_name}s retrieved successfully.",
            responseKey="success_{self.entity_snake}s_retrieved",
            data={{
                "items": [r.to_dict() for r in records],
                "total": total,
                "skip": skip,
                "limit": limit,
            }},
        )

    async def update(
        self,
        record_id: int,
        request_dto: {self.entity_name}UpdateRequestDTO,
    ) -> BaseResponseDTO:
        """
        Update a {self.entity_lower}.

        Args:
            record_id: {self.entity_name} ID.
            request_dto: Update request data.

        Returns:
            Response with updated {self.entity_lower} data.

        Raises:
            NotFoundError: If {self.entity_lower} not found.
        """
        self.logger.debug(f"Updating {self.entity_lower}: {{record_id}}")

        record = self.repository.retrieve_record_by_id(record_id)

        if not record:
            raise NotFoundError(
                responseMessage="{self.entity_name} not found.",
                responseKey="error_{self.entity_snake}_not_found",
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
            responseMessage="{self.entity_name} updated successfully.",
            responseKey="success_{self.entity_snake}_updated",
            data=record.to_dict(),
        )

    async def delete(self, record_id: int) -> BaseResponseDTO:
        """
        Delete a {self.entity_lower} (soft delete).

        Args:
            record_id: {self.entity_name} ID.

        Returns:
            Response confirming deletion.

        Raises:
            NotFoundError: If {self.entity_lower} not found.
        """
        self.logger.debug(f"Deleting {self.entity_lower}: {{record_id}}")

        deleted = self.repository.delete_record(record_id, self._user_id or 1)

        if not deleted:
            raise NotFoundError(
                responseMessage="{self.entity_name} not found.",
                responseKey="error_{self.entity_snake}_not_found",
                httpStatusCode=HTTPStatus.NOT_FOUND,
            )

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="{self.entity_name} deleted successfully.",
            responseKey="success_{self.entity_snake}_deleted",
            data={{}},
        )
'''
        (service_dir / "crud.py").write_text(crud_content)

    def _generate_controller(self):
        """Generate controller/routes."""
        controller_dir = self.project_path / "controllers" / self.entity_snake
        controller_dir.mkdir(parents=True, exist_ok=True)

        # __init__.py with routes
        init_content = f'''"""
{self.entity_name} Controller Package.

This package contains API route handlers for {self.entity_name} operations.
Provides RESTful CRUD endpoints.

Routes:
    POST   /{self.entity_snake}         - Create new {self.entity_lower}
    GET    /{self.entity_snake}         - List all {self.entity_lower}s
    GET    /{self.entity_snake}/{{id}}    - Get {self.entity_lower} by ID
    PUT    /{self.entity_snake}/{{id}}    - Update {self.entity_lower}
    DELETE /{self.entity_snake}/{{id}}    - Delete {self.entity_lower}
"""

from typing import Callable, Optional

from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from constants.api_status import APIStatus
from dependencies.db import DBDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dtos.requests.{self.entity_snake}.create import {self.entity_name}CreateRequestDTO
from dtos.requests.{self.entity_snake}.update import {self.entity_name}UpdateRequestDTO
from errors.not_found_error import NotFoundError
from errors.bad_input_error import BadInputError
from repositories.{self.entity_snake} import {self.entity_name}Repository
from services.{self.entity_snake}.crud import {self.entity_name}CRUDService
from utilities.dictionary import DictionaryUtility

from loguru import logger

try:
    from fastmiddleware.request_context import get_request_id
except ImportError:
    def get_request_id():
        return None

logger.debug("Registering {self.entity_name} routes.")

router = APIRouter(prefix="/{self.entity_snake}", tags=["{self.entity_name}"])


def get_{self.entity_snake}_repository(
    session: Session = Depends(DBDependency.derive),
) -> {self.entity_name}Repository:
    """Dependency to get {self.entity_name} repository."""
    repo = {self.entity_name}Repository()
    repo.session = session
    return repo


def get_{self.entity_snake}_service_factory() -> Callable[..., {self.entity_name}CRUDService]:
    """Factory for creating {self.entity_name} service instances."""
    def factory(
        urn: str,
        user_id: int,
        repository: {self.entity_name}Repository,
    ) -> {self.entity_name}CRUDService:
        service = {self.entity_name}CRUDService()
        service.urn = urn
        service._user_id = user_id
        service.repository = repository
        return service
    return factory


@router.post("", summary="Create {self.entity_name}")
async def create_{self.entity_snake}(
    request: Request,
    request_payload: {self.entity_name}CreateRequestDTO,
    repository: {self.entity_name}Repository = Depends(get_{self.entity_snake}_repository),
    service_factory: Callable = Depends(get_{self.entity_snake}_service_factory),
    dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
) -> JSONResponse:
    """
    Create a new {self.entity_lower}.

    Args:
        request: FastAPI request.
        request_payload: {self.entity_name} creation data.

    Returns:
        JSONResponse with created {self.entity_lower}.
    """
    try:
        urn = get_request_id() or getattr(request.state, "urn", None) or "unknown"
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
            content={{
                "transactionUrn": get_request_id() or getattr(request.state, "urn", None) or "unknown",
                "status": APIStatus.FAILED,
                "responseMessage": e.response_message,
                "responseKey": e.response_key,
                "data": {{}},
            }},
        )
    except Exception as e:
        logger.exception(f"Error creating {self.entity_lower}: {{e}}")
        return JSONResponse(
            status_code=500,
            content={{
                "transactionUrn": get_request_id() or getattr(request.state, "urn", None) or "unknown",
                "status": APIStatus.FAILED,
                "responseMessage": "Internal server error.",
                "responseKey": "error_internal",
                "data": {{}},
            }},
        )


@router.get("", summary="List {self.entity_name}s")
async def list_{self.entity_snake}s(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: {self.entity_name}Repository = Depends(get_{self.entity_snake}_repository),
    service_factory: Callable = Depends(get_{self.entity_snake}_service_factory),
    dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
) -> JSONResponse:
    """
    List all {self.entity_lower}s with pagination.

    Args:
        skip: Records to skip.
        limit: Max records to return.

    Returns:
        JSONResponse with list of {self.entity_lower}s.
    """
    try:
        urn = get_request_id() or getattr(request.state, "urn", None) or "unknown"
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
        logger.exception(f"Error listing {self.entity_lower}s: {{e}}")
        return JSONResponse(
            status_code=500,
            content={{
                "transactionUrn": get_request_id() or getattr(request.state, "urn", None) or "unknown",
                "status": APIStatus.FAILED,
                "responseMessage": "Internal server error.",
                "responseKey": "error_internal",
                "data": {{}},
            }},
        )


@router.get("/{{record_id}}", summary="Get {self.entity_name}")
async def get_{self.entity_snake}(
    request: Request,
    record_id: int,
    repository: {self.entity_name}Repository = Depends(get_{self.entity_snake}_repository),
    service_factory: Callable = Depends(get_{self.entity_snake}_service_factory),
    dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
) -> JSONResponse:
    """
    Get a {self.entity_lower} by ID.

    Args:
        record_id: {self.entity_name} ID.

    Returns:
        JSONResponse with {self.entity_lower} data.
    """
    try:
        urn = get_request_id() or getattr(request.state, "urn", None) or "unknown"
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
            content={{
                "transactionUrn": get_request_id() or getattr(request.state, "urn", None) or "unknown",
                "status": APIStatus.FAILED,
                "responseMessage": e.response_message,
                "responseKey": e.response_key,
                "data": {{}},
            }},
        )
    except Exception as e:
        logger.exception(f"Error getting {self.entity_lower}: {{e}}")
        return JSONResponse(
            status_code=500,
            content={{
                "transactionUrn": get_request_id() or getattr(request.state, "urn", None) or "unknown",
                "status": APIStatus.FAILED,
                "responseMessage": "Internal server error.",
                "responseKey": "error_internal",
                "data": {{}},
            }},
        )


@router.put("/{{record_id}}", summary="Update {self.entity_name}")
async def update_{self.entity_snake}(
    request: Request,
    record_id: int,
    request_payload: {self.entity_name}UpdateRequestDTO,
    repository: {self.entity_name}Repository = Depends(get_{self.entity_snake}_repository),
    service_factory: Callable = Depends(get_{self.entity_snake}_service_factory),
    dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
) -> JSONResponse:
    """
    Update a {self.entity_lower}.

    Args:
        record_id: {self.entity_name} ID.
        request_payload: Update data.

    Returns:
        JSONResponse with updated {self.entity_lower}.
    """
    try:
        urn = get_request_id() or getattr(request.state, "urn", None) or "unknown"
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
            content={{
                "transactionUrn": get_request_id() or getattr(request.state, "urn", None) or "unknown",
                "status": APIStatus.FAILED,
                "responseMessage": e.response_message,
                "responseKey": e.response_key,
                "data": {{}},
            }},
        )
    except Exception as e:
        logger.exception(f"Error updating {self.entity_lower}: {{e}}")
        return JSONResponse(
            status_code=500,
            content={{
                "transactionUrn": get_request_id() or getattr(request.state, "urn", None) or "unknown",
                "status": APIStatus.FAILED,
                "responseMessage": "Internal server error.",
                "responseKey": "error_internal",
                "data": {{}},
            }},
        )


@router.delete("/{{record_id}}", summary="Delete {self.entity_name}")
async def delete_{self.entity_snake}(
    request: Request,
    record_id: int,
    repository: {self.entity_name}Repository = Depends(get_{self.entity_snake}_repository),
    service_factory: Callable = Depends(get_{self.entity_snake}_service_factory),
    dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
) -> JSONResponse:
    """
    Delete a {self.entity_lower} (soft delete).

    Args:
        record_id: {self.entity_name} ID.

    Returns:
        JSONResponse confirming deletion.
    """
    try:
        urn = get_request_id() or getattr(request.state, "urn", None) or "unknown"
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
            content={{
                "transactionUrn": get_request_id() or getattr(request.state, "urn", None) or "unknown",
                "status": APIStatus.FAILED,
                "responseMessage": e.response_message,
                "responseKey": e.response_key,
                "data": {{}},
            }},
        )
    except Exception as e:
        logger.exception(f"Error deleting {self.entity_lower}: {{e}}")
        return JSONResponse(
            status_code=500,
            content={{
                "transactionUrn": get_request_id() or getattr(request.state, "urn", None) or "unknown",
                "status": APIStatus.FAILED,
                "responseMessage": "Internal server error.",
                "responseKey": "error_internal",
                "data": {{}},
            }},
        )


logger.debug("Registered {self.entity_name} routes.")
'''
        (controller_dir / "__init__.py").write_text(init_content)

    def _generate_dependencies(self):
        """Generate dependency injection files."""
        # Repository dependency
        repo_dep_dir = self.project_path / "dependencies" / "repositiories"
        repo_dep_dir.mkdir(parents=True, exist_ok=True)

        repo_dep_content = f'''"""
{self.entity_name} Repository Dependency.

Provides dependency injection for {self.entity_name}Repository.
"""

from sqlalchemy.orm import Session

from abstractions.dependency import IDependency
from repositories.{self.entity_snake} import {self.entity_name}Repository


class {self.entity_name}RepositoryDependency(IDependency):
    """Dependency provider for {self.entity_name}Repository."""

    @staticmethod
    def derive(session: Session) -> {self.entity_name}Repository:
        """
        Create repository instance with session.

        Args:
            session: SQLAlchemy session.

        Returns:
            Configured {self.entity_name}Repository.
        """
        repo = {self.entity_name}Repository()
        repo.session = session
        return repo
'''
        (repo_dep_dir / f"{self.entity_snake}.py").write_text(repo_dep_content)

    def _generate_tests(self):
        """Generate test files."""
        # Model tests
        test_model_dir = self.project_path / "tests" / "unit" / "models"
        test_model_dir.mkdir(parents=True, exist_ok=True)

        model_test_content = f'''"""
Tests for {self.entity_name} model.
"""

import pytest
from datetime import datetime

from models.{self.entity_snake} import {self.entity_name}


class Test{self.entity_name}Model:
    """Test cases for {self.entity_name} model."""

    def test_create_{self.entity_snake}(self):
        """Test {self.entity_name} instance creation."""
        {self.entity_snake} = {self.entity_name}(
            urn="01ABC123DEF456GHI789JKL0",
            name="Test {self.entity_name}",
            description="A test {self.entity_lower}",
            is_active=True,
            is_deleted=False,
            created_by=1,
            created_on=datetime.now(),
        )

        assert {self.entity_snake}.name == "Test {self.entity_name}"
        assert {self.entity_snake}.is_active is True
        assert {self.entity_snake}.is_deleted is False

    def test_{self.entity_snake}_to_dict(self):
        """Test {self.entity_name}.to_dict() method."""
        {self.entity_snake} = {self.entity_name}(
            id=1,
            urn="01ABC123DEF456GHI789JKL0",
            name="Test {self.entity_name}",
            description="Description",
            is_active=True,
            created_on=datetime(2024, 1, 1, 12, 0, 0),
        )

        result = {self.entity_snake}.to_dict()

        assert result["id"] == 1
        assert result["urn"] == "01ABC123DEF456GHI789JKL0"
        assert result["name"] == "Test {self.entity_name}"
        assert result["description"] == "Description"
        assert result["is_active"] is True

    def test_{self.entity_snake}_repr(self):
        """Test {self.entity_name}.__repr__() method."""
        {self.entity_snake} = {self.entity_name}(id=1, name="Test")

        assert "<{self.entity_name}(id=1, name=Test)>" in repr({self.entity_snake})
'''
        (test_model_dir / f"test_{self.entity_snake}.py").write_text(model_test_content)

        # Ensure __init__.py exists
        init_path = test_model_dir / "__init__.py"
        if not init_path.exists():
            init_path.write_text("")

    def _update_init_files(self):
        """Update __init__.py files to include new entity."""
        # Update models/__init__.py
        models_init = self.project_path / "models" / "__init__.py"
        if models_init.exists():
            content = models_init.read_text()
            import_line = f"from models.{self.entity_snake} import {self.entity_name}"
            if import_line not in content:
                content += f"\n{import_line}\n"
                models_init.write_text(content)

