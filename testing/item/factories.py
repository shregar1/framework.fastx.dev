"""Item Factory - Generate fake data for testing.

Uses Faker for realistic test data generation.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from faker import Faker  # pyright: ignore[reportMissingImports]

# Try to import faker, provide fallback if not available
fake: Faker | None = None
try:
    from faker import Faker as _Faker  # pyright: ignore[reportMissingImports]

    fake = _Faker()
except ImportError:
    pass

from dtos.requests.item import CreateItemRequestDTO, UpdateItemRequestDTO
from dtos.responses.item.item_response_dto import ItemResponseDTO
from models.item import Item


class ItemFactory:
    """Factory for generating fake Item data.

    Provides methods to create:
    - Item instances
    - Request DTOs
    - Response DTOs
    - Dictionary payloads for API tests

    Usage:
        # Create a single item
        item = ItemFactory.create()

        # Create multiple items
        items = ItemFactory.create_batch(5)

        # Create API payload
        payload = ItemFactory.create_dict(completed=True)

        # Create with custom values
        item = ItemFactory.create(name="Custom Name")
    """

    # Default values
    DEFAULTS = {
        "name": "Test Item",
        "description": "A test item description",
        "completed": False,
    }

    @classmethod
    def _generate_fake_data(cls, **overrides) -> dict[str, Any]:
        """Generate fake data for an item."""
        if fake is not None:
            name = fake.sentence(nb_words=3)[:-1]  # Remove period
            description = fake.paragraph(nb_sentences=2)
        else:
            import uuid

            name = f"Test Item {uuid.uuid4().hex[:8]}"
            description = "Test description"

        data = {
            "id": overrides.get("id")
            or (fake.uuid4() if fake is not None else f"test-{datetime.utcnow().timestamp()}"),
            "name": overrides.get("name", name),
            "description": overrides.get("description", description),
            "completed": overrides.get("completed", cls.DEFAULTS["completed"]),
            "created_at": overrides.get("created_at", datetime.utcnow()),
            "updated_at": overrides.get("updated_at", datetime.utcnow()),
        }

        return data

    @classmethod
    def create(cls, **overrides) -> Item:
        """Create an Item instance.

        Args:
            **overrides: Field values to override defaults

        Returns:
            Item instance

        Examples:
            >>> item = ItemFactory.create()
            >>> item = ItemFactory.create(name="Custom Item", completed=True)

        """
        data = cls._generate_fake_data(**overrides)
        return Item(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            completed=data["completed"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    @classmethod
    def create_batch(cls, count: int, **overrides) -> list[Item]:
        """Create multiple Item instances.

        Args:
            count: Number of items to create
            **overrides: Field values to override defaults

        Returns:
            List of Item instances

        Examples:
            >>> items = ItemFactory.create_batch(5)
            >>> items = ItemFactory.create_batch(3, completed=True)

        """
        return [cls.create(**overrides) for _ in range(count)]

    @classmethod
    def create_dict(cls, **overrides) -> dict[str, Any]:
        """Create a dictionary payload for API requests.

        Args:
            **overrides: Field values to override defaults

        Returns:
            Dictionary suitable for JSON serialization

        Examples:
            >>> payload = ItemFactory.create_dict()
            >>> payload = ItemFactory.create_dict(name="API Test")

        """
        data = cls._generate_fake_data(**overrides)
        return {
            "name": data["name"],
            "description": data["description"],
            "completed": data["completed"],
        }

    @classmethod
    def create_batch_dict(cls, count: int, **overrides) -> list[dict[str, Any]]:
        """Create multiple dictionary payloads.

        Args:
            count: Number of items to create
            **overrides: Field values to override defaults

        Returns:
            List of dictionaries

        """
        return [cls.create_dict(**overrides) for _ in range(count)]

    @classmethod
    def create_create_request(cls, **overrides) -> CreateItemRequestDTO:
        """Create a CreateItemRequest DTO.

        Args:
            **overrides: Field values to override defaults

        Returns:
            CreateItemRequestDTO instance

        """
        data = cls._generate_fake_data(**overrides)
        return CreateItemRequestDTO(
            name=data["name"],
            description=data["description"],
        )

    @classmethod
    def create_update_request(cls, **overrides) -> UpdateItemRequestDTO:
        """Create an UpdateItemRequest DTO.

        Args:
            **overrides: Field values to override defaults

        Returns:
            UpdateItemRequestDTO instance

        """
        data = cls._generate_fake_data(**overrides)
        return UpdateItemRequestDTO(
            name=overrides.get("name", data["name"]),
            description=overrides.get("description", data["description"]),
        )

    @classmethod
    def create_response(cls, **overrides) -> ItemResponseDTO:
        """Create an ItemResponse DTO.

        Args:
            **overrides: Field values to override defaults

        Returns:
            ItemResponseDTO instance

        """
        data = cls._generate_fake_data(**overrides)
        return ItemResponseDTO(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            completed=data["completed"],
            created_at=data["created_at"].isoformat(),
            updated_at=data["updated_at"].isoformat(),
        )

    @classmethod
    def completed(cls, **overrides) -> Item:
        """Create a completed item.

        Convenience method for creating completed items.

        Args:
            **overrides: Field values to override defaults

        Returns:
            Completed Item instance

        """
        return cls.create(completed=True, **overrides)

    @classmethod
    def pending(cls, **overrides) -> Item:
        """Create a pending (not completed) item.

        Convenience method for creating pending items.

        Args:
            **overrides: Field values to override defaults

        Returns:
            Pending Item instance

        """
        return cls.create(completed=False, **overrides)

    @classmethod
    def with_long_name(cls, **overrides) -> Item:
        """Create an item with a long name (boundary testing).

        Args:
            **overrides: Field values to override defaults

        Returns:
            Item with long name

        """
        if fake is not None:
            long_name = " ".join([fake.word() for _ in range(15)])[:100]
        else:
            long_name = "A" * 100
        return cls.create(name=long_name, **overrides)

    @classmethod
    def with_long_description(cls, **overrides) -> Item:
        """Create an item with a long description (boundary testing).

        Args:
            **overrides: Field values to override defaults

        Returns:
            Item with long description

        """
        if fake is not None:
            long_desc = fake.paragraph(nb_sentences=20)[:500]
        else:
            long_desc = "B" * 500
        return cls.create(description=long_desc, **overrides)

    @classmethod
    def invalid_name_empty(cls) -> dict[str, Any]:
        """Create invalid payload with empty name (for negative testing).

        Returns:
            Dictionary with empty name

        """
        return {
            "name": "",
            "description": "Valid description",
        }

    @classmethod
    def invalid_name_too_long(cls) -> dict[str, Any]:
        """Create invalid payload with name exceeding limit.

        Returns:
            Dictionary with name > 100 characters

        """
        return {
            "name": "X" * 101,
            "description": "Valid description",
        }

    @classmethod
    def invalid_description_too_long(cls) -> dict[str, Any]:
        """Create invalid payload with description exceeding limit.

        Returns:
            Dictionary with description > 500 characters

        """
        return {
            "name": "Valid Name",
            "description": "Y" * 501,
        }


# Backwards compatibility alias
Factory = ItemFactory
