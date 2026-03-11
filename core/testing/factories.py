"""
Factory Pattern for Test Data.

Provides a flexible factory pattern for generating test data.
"""

import random
import string
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar

T = TypeVar("T")


class FactoryField:
    """
    Factory field definition.

    Defines how a field value is generated.
    """

    def __init__(
        self,
        generator: Optional[Callable[[], Any]] = None,
        default: Any = None,
        sequence: bool = False,
        lazy: bool = False,
    ):
        """
        Initialize factory field.

        Args:
            generator: Function to generate value.
            default: Default value.
            sequence: Use sequence counter.
            lazy: Generate value lazily.
        """
        self._generator = generator
        self._default = default
        self._sequence = sequence
        self._lazy = lazy
        self._counter = 0

    def generate(self, context: Optional[Dict[str, Any]] = None) -> Any:
        """Generate field value."""
        if self._sequence:
            self._counter += 1
            return self._counter

        if self._generator:
            return self._generator()

        return self._default


class FakerGenerators:
    """Built-in fake data generators."""

    @staticmethod
    def email() -> str:
        """Generate random email."""
        username = "".join(random.choices(string.ascii_lowercase, k=8))
        domain = random.choice(["example.com", "test.com", "demo.org"])
        return f"{username}@{domain}"

    @staticmethod
    def name() -> str:
        """Generate random name."""
        first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    @staticmethod
    def first_name() -> str:
        """Generate random first name."""
        names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank"]
        return random.choice(names)

    @staticmethod
    def last_name() -> str:
        """Generate random last name."""
        names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
        return random.choice(names)

    @staticmethod
    def uuid() -> str:
        """Generate UUID."""
        return str(uuid.uuid4())

    @staticmethod
    def phone() -> str:
        """Generate random phone number."""
        return f"+1{random.randint(2000000000, 9999999999)}"

    @staticmethod
    def street_address() -> str:
        """Generate random street address."""
        number = random.randint(1, 9999)
        streets = ["Main St", "Oak Ave", "Park Blvd", "First St", "Elm Dr"]
        return f"{number} {random.choice(streets)}"

    @staticmethod
    def city() -> str:
        """Generate random city."""
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Seattle"]
        return random.choice(cities)

    @staticmethod
    def country() -> str:
        """Generate random country."""
        countries = ["USA", "Canada", "UK", "Germany", "France", "Japan", "Australia"]
        return random.choice(countries)

    @staticmethod
    def text(length: int = 100) -> str:
        """Generate random text."""
        words = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing"]
        text = " ".join(random.choices(words, k=length // 6))
        return text[:length]

    @staticmethod
    def boolean() -> bool:
        """Generate random boolean."""
        return random.choice([True, False])

    @staticmethod
    def integer(min_val: int = 0, max_val: int = 1000) -> int:
        """Generate random integer."""
        return random.randint(min_val, max_val)

    @staticmethod
    def decimal(min_val: float = 0.0, max_val: float = 1000.0, decimals: int = 2) -> float:
        """Generate random decimal."""
        return round(random.uniform(min_val, max_val), decimals)

    @staticmethod
    def date(start_year: int = 2020, end_year: int = 2025) -> datetime:
        """Generate random date."""
        start = datetime(start_year, 1, 1)
        end = datetime(end_year, 12, 31)
        delta = end - start
        random_days = random.randint(0, delta.days)
        return start + timedelta(days=random_days)

    @staticmethod
    def past_date(days: int = 365) -> datetime:
        """Generate random past date."""
        return datetime.utcnow() - timedelta(days=random.randint(1, days))

    @staticmethod
    def future_date(days: int = 365) -> datetime:
        """Generate random future date."""
        return datetime.utcnow() + timedelta(days=random.randint(1, days))


class Factory(Generic[T]):
    """
    Factory base class for generating test data.

    Usage:
        class UserFactory(Factory[User]):
            model = User

            email = Factory.faker("email")
            name = Factory.faker("name")
            is_active = True  # Static value

        # Create one
        user = await UserFactory.create()

        # Create many
        users = await UserFactory.create_batch(10)

        # With overrides
        admin = await UserFactory.create(is_admin=True)
    """

    model: Type[T]
    _sequence: int = 0
    _fields: Dict[str, Any] = {}

    @classmethod
    def faker(cls, name: str, **kwargs: Any) -> FactoryField:
        """
        Create a faker field.

        Args:
            name: Name of faker generator (email, name, uuid, etc.).
            **kwargs: Additional arguments for generator.

        Returns:
            FactoryField with faker generator.
        """
        generator = getattr(FakerGenerators, name, None)
        if generator is None:
            raise ValueError(f"Unknown faker: {name}")

        if kwargs:
            return FactoryField(generator=lambda: generator(**kwargs))
        return FactoryField(generator=generator)

    @classmethod
    def sequence(cls) -> FactoryField:
        """Create a sequence field."""
        return FactoryField(sequence=True)

    @classmethod
    def lazy(cls, func: Callable[[], Any]) -> FactoryField:
        """Create a lazy field."""
        return FactoryField(generator=func, lazy=True)

    @classmethod
    def _get_field_value(cls, name: str, field: Any, overrides: Dict[str, Any]) -> Any:
        """Get value for a field."""
        if name in overrides:
            return overrides[name]

        if isinstance(field, FactoryField):
            return field.generate()

        if callable(field):
            return field()

        return field

    @classmethod
    def _build_kwargs(cls, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build kwargs for model creation."""
        overrides = overrides or {}
        kwargs = {}

        # Get all class attributes that aren't special
        for name in dir(cls):
            if name.startswith("_") or name in ("model", "create", "create_batch", "build", "build_batch"):
                continue

            attr = getattr(cls, name)
            if not callable(attr) or isinstance(attr, FactoryField):
                kwargs[name] = cls._get_field_value(name, attr, overrides)

        # Add any extra overrides
        kwargs.update(overrides)

        return kwargs

    @classmethod
    async def create(cls, **overrides: Any) -> T:
        """
        Create and persist an instance.

        Override this in subclasses to add persistence logic.
        """
        return cls.build(**overrides)

    @classmethod
    async def create_batch(cls, count: int, **overrides: Any) -> List[T]:
        """Create multiple instances."""
        return [await cls.create(**overrides) for _ in range(count)]

    @classmethod
    def build(cls, **overrides: Any) -> T:
        """Build an instance without persisting."""
        kwargs = cls._build_kwargs(overrides)

        if hasattr(cls, "model") and cls.model:
            return cls.model(**kwargs)

        # Return as dict if no model specified
        return kwargs  # type: ignore

    @classmethod
    def build_batch(cls, count: int, **overrides: Any) -> List[T]:
        """Build multiple instances without persisting."""
        return [cls.build(**overrides) for _ in range(count)]


# Convenience alias
define = Factory


class RelatedFactory:
    """
    Factory for related objects.

    Usage:
        class OrderFactory(Factory[Order]):
            user = RelatedFactory(UserFactory)
    """

    def __init__(
        self,
        factory: Type[Factory],
        size: int = 1,
        **kwargs: Any,
    ):
        self._factory = factory
        self._size = size
        self._kwargs = kwargs

    async def generate(self) -> Any:
        """Generate related object(s)."""
        if self._size == 1:
            return await self._factory.create(**self._kwargs)
        return await self._factory.create_batch(self._size, **self._kwargs)
