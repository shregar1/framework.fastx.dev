"""
Value Object Pattern.

Immutable objects that are defined by their attributes,
not by an identity. Used for domain modeling.

Implements:
- Immutable value objects
- Equality by value
- Common value objects (Email, Money, etc.)

SOLID Principles:
- Single Responsibility: Encapsulates a domain concept
- Liskov Substitution: Value objects are interchangeable if equal
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Generic, Optional, TypeVar
import re


T = TypeVar("T")


class ValueObject(ABC, Generic[T]):
    """
    Abstract base class for value objects.

    Value objects are immutable and compared by value, not identity.

    Usage:
        @dataclass(frozen=True)
        class Email(ValueObject[str]):
            value: str

            def __post_init__(self):
                if not self._is_valid_email(self.value):
                    raise ValueError(f"Invalid email: {self.value}")

            @staticmethod
            def _is_valid_email(email: str) -> bool:
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                return bool(re.match(pattern, email))
    """

    @property
    @abstractmethod
    def value(self) -> T:
        """Get the underlying value."""
        pass

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class Email:
    """
    Email value object with validation.

    Usage:
        email = Email("user@example.com")
        print(email.local_part)  # user
        print(email.domain)  # example.com
    """

    address: str

    def __post_init__(self):
        if not self._is_valid():
            raise ValueError(f"Invalid email address: {self.address}")

    def _is_valid(self) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, self.address))

    @property
    def local_part(self) -> str:
        """Get the local part (before @)."""
        return self.address.split("@")[0]

    @property
    def domain(self) -> str:
        """Get the domain part (after @)."""
        return self.address.split("@")[1]

    def __str__(self) -> str:
        return self.address


@dataclass(frozen=True)
class Money:
    """
    Money value object with currency support.

    Usage:
        price = Money(Decimal("99.99"), "USD")
        tax = price * Decimal("0.1")
        total = price + tax
    """

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        # Ensure amount is Decimal
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

    def __add__(self, other: "Money") -> "Money":
        if other.currency != self.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if other.currency != self.currency:
            raise ValueError(f"Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> "Money":
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __truediv__(self, divisor: Decimal) -> "Money":
        return Money(self.amount / Decimal(str(divisor)), self.currency)

    def round(self, places: int = 2) -> "Money":
        """Round to specified decimal places."""
        return Money(round(self.amount, places), self.currency)

    @property
    def is_positive(self) -> bool:
        return self.amount > 0

    @property
    def is_negative(self) -> bool:
        return self.amount < 0

    @property
    def is_zero(self) -> bool:
        return self.amount == 0

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"


@dataclass(frozen=True)
class PhoneNumber:
    """
    Phone number value object.

    Usage:
        phone = PhoneNumber("+1", "555", "1234567")
        print(str(phone))  # +1 (555) 123-4567
    """

    country_code: str
    area_code: str
    number: str

    def __post_init__(self):
        # Validate
        if not self.country_code.startswith("+"):
            object.__setattr__(self, "country_code", f"+{self.country_code}")
        if not self._is_valid():
            raise ValueError(f"Invalid phone number")

    def _is_valid(self) -> bool:
        return (
            len(self.area_code) >= 2
            and len(self.number) >= 6
            and self.area_code.isdigit()
            and self.number.isdigit()
        )

    @property
    def formatted(self) -> str:
        """Get formatted phone number."""
        return f"{self.country_code} ({self.area_code}) {self.number[:3]}-{self.number[3:]}"

    def __str__(self) -> str:
        return self.formatted


@dataclass(frozen=True)
class Address:
    """
    Address value object.

    Usage:
        address = Address(
            street="123 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
            country="USA"
        )
    """

    street: str
    city: str
    state: str
    postal_code: str
    country: str
    street2: Optional[str] = None

    @property
    def full_address(self) -> str:
        """Get full formatted address."""
        parts = [self.street]
        if self.street2:
            parts.append(self.street2)
        parts.append(f"{self.city}, {self.state} {self.postal_code}")
        parts.append(self.country)
        return "\n".join(parts)

    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}"


@dataclass(frozen=True)
class DateRange:
    """
    Date range value object.

    Usage:
        range = DateRange(start=date(2024, 1, 1), end=date(2024, 12, 31))
        if date.today() in range:
            print("Within range")
    """

    from datetime import date as date_type

    start: date_type
    end: date_type

    def __post_init__(self):
        if self.start > self.end:
            raise ValueError("Start date must be before end date")

    def __contains__(self, date: date_type) -> bool:
        return self.start <= date <= self.end

    @property
    def days(self) -> int:
        """Get number of days in range."""
        return (self.end - self.start).days

    def overlaps(self, other: "DateRange") -> bool:
        """Check if ranges overlap."""
        return self.start <= other.end and self.end >= other.start


@dataclass(frozen=True)
class Percentage:
    """
    Percentage value object.

    Usage:
        discount = Percentage(15)  # 15%
        price = Decimal("100")
        discounted = price * (1 - discount.as_decimal)
    """

    value: float

    def __post_init__(self):
        if not 0 <= self.value <= 100:
            raise ValueError(f"Percentage must be between 0 and 100: {self.value}")

    @property
    def as_decimal(self) -> Decimal:
        """Get as decimal (0.15 for 15%)."""
        return Decimal(str(self.value)) / 100

    @property
    def as_multiplier(self) -> Decimal:
        """Get as multiplier (1.15 for 15% increase)."""
        return Decimal("1") + self.as_decimal

    def of(self, amount: Decimal) -> Decimal:
        """Calculate percentage of amount."""
        return amount * self.as_decimal

    def __str__(self) -> str:
        return f"{self.value}%"


@dataclass(frozen=True)
class Slug:
    """
    URL-safe slug value object.

    Usage:
        slug = Slug.from_text("Hello World!")
        print(slug.value)  # hello-world
    """

    value: str

    @classmethod
    def from_text(cls, text: str) -> "Slug":
        """Create slug from text."""
        # Convert to lowercase, replace spaces with hyphens
        slug = text.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)  # Remove special chars
        slug = re.sub(r"[-\s]+", "-", slug)  # Replace spaces/multiple hyphens
        slug = slug.strip("-")
        return cls(slug)

    def __str__(self) -> str:
        return self.value
