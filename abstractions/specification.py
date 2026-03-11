"""
Specification Pattern.

Encapsulates business rules as reusable, composable query specifications.

Implements:
- Composite specifications (AND, OR, NOT)
- Type-safe query building
- Repository integration

SOLID Principles:
- Single Responsibility: Each spec encapsulates one rule
- Open/Closed: New specs without modifying existing ones
- Liskov Substitution: All specs are interchangeable
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generic, List, Optional, TypeVar

T = TypeVar("T")


class ISpecification(ABC, Generic[T]):
    """
    Abstract Specification interface.

    Encapsulates a business rule that can be evaluated against an entity.

    Usage:
        class ActiveUserSpec(ISpecification[User]):
            def is_satisfied_by(self, user: User) -> bool:
                return user.is_active

        class PremiumUserSpec(ISpecification[User]):
            def is_satisfied_by(self, user: User) -> bool:
                return user.subscription == "premium"

        # Compose specifications
        active_premium = ActiveUserSpec() & PremiumUserSpec()
    """

    @abstractmethod
    def is_satisfied_by(self, entity: T) -> bool:
        """
        Check if entity satisfies this specification.

        Args:
            entity: Entity to check.

        Returns:
            True if entity satisfies specification.
        """
        pass

    def __and__(self, other: "ISpecification[T]") -> "AndSpecification[T]":
        """Combine with AND logic."""
        return AndSpecification(self, other)

    def __or__(self, other: "ISpecification[T]") -> "OrSpecification[T]":
        """Combine with OR logic."""
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification[T]":
        """Negate specification."""
        return NotSpecification(self)


class AndSpecification(ISpecification[T]):
    """Composite AND specification."""

    def __init__(self, left: ISpecification[T], right: ISpecification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, entity: T) -> bool:
        return self._left.is_satisfied_by(entity) and self._right.is_satisfied_by(entity)


class OrSpecification(ISpecification[T]):
    """Composite OR specification."""

    def __init__(self, left: ISpecification[T], right: ISpecification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, entity: T) -> bool:
        return self._left.is_satisfied_by(entity) or self._right.is_satisfied_by(entity)


class NotSpecification(ISpecification[T]):
    """Negated specification."""

    def __init__(self, spec: ISpecification[T]):
        self._spec = spec

    def is_satisfied_by(self, entity: T) -> bool:
        return not self._spec.is_satisfied_by(entity)


class LambdaSpecification(ISpecification[T]):
    """
    Specification from a lambda function.

    Usage:
        is_adult = LambdaSpecification(lambda user: user.age >= 18)
    """

    def __init__(self, predicate: Callable[[T], bool]):
        self._predicate = predicate

    def is_satisfied_by(self, entity: T) -> bool:
        return self._predicate(entity)


@dataclass
class QuerySpecification(Generic[T]):
    """
    Query specification for database queries.

    Translates business rules to database query conditions.

    Usage:
        spec = QuerySpecification[User]()
        spec.add_filter("is_active", "eq", True)
        spec.add_filter("age", "gte", 18)
        spec.order_by("created_at", descending=True)
        spec.paginate(page=1, page_size=20)
    """

    filters: List[tuple] = None
    ordering: List[tuple] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    includes: List[str] = None

    def __post_init__(self):
        self.filters = self.filters or []
        self.ordering = self.ordering or []
        self.includes = self.includes or []

    def add_filter(
        self,
        field: str,
        operator: str,
        value: Any,
    ) -> "QuerySpecification[T]":
        """
        Add a filter condition.

        Args:
            field: Field name to filter on.
            operator: Comparison operator (eq, ne, gt, gte, lt, lte, like, in).
            value: Value to compare against.

        Returns:
            Self for chaining.
        """
        self.filters.append((field, operator, value))
        return self

    def where(self, field: str) -> "FilterBuilder[T]":
        """Start building a filter for a field."""
        return FilterBuilder(self, field)

    def order_by(self, field: str, descending: bool = False) -> "QuerySpecification[T]":
        """Add ordering."""
        self.ordering.append((field, descending))
        return self

    def paginate(self, page: int, page_size: int = 20) -> "QuerySpecification[T]":
        """Add pagination."""
        self.page = page
        self.page_size = page_size
        return self

    def include(self, *relations: str) -> "QuerySpecification[T]":
        """Include related entities."""
        self.includes.extend(relations)
        return self

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "filters": self.filters,
            "ordering": self.ordering,
            "page": self.page,
            "page_size": self.page_size,
            "includes": self.includes,
        }


class FilterBuilder(Generic[T]):
    """Fluent filter builder."""

    def __init__(self, spec: QuerySpecification[T], field: str):
        self._spec = spec
        self._field = field

    def eq(self, value: Any) -> QuerySpecification[T]:
        """Equal to."""
        return self._spec.add_filter(self._field, "eq", value)

    def ne(self, value: Any) -> QuerySpecification[T]:
        """Not equal to."""
        return self._spec.add_filter(self._field, "ne", value)

    def gt(self, value: Any) -> QuerySpecification[T]:
        """Greater than."""
        return self._spec.add_filter(self._field, "gt", value)

    def gte(self, value: Any) -> QuerySpecification[T]:
        """Greater than or equal."""
        return self._spec.add_filter(self._field, "gte", value)

    def lt(self, value: Any) -> QuerySpecification[T]:
        """Less than."""
        return self._spec.add_filter(self._field, "lt", value)

    def lte(self, value: Any) -> QuerySpecification[T]:
        """Less than or equal."""
        return self._spec.add_filter(self._field, "lte", value)

    def like(self, value: str) -> QuerySpecification[T]:
        """SQL LIKE pattern."""
        return self._spec.add_filter(self._field, "like", value)

    def ilike(self, value: str) -> QuerySpecification[T]:
        """Case-insensitive LIKE."""
        return self._spec.add_filter(self._field, "ilike", value)

    def in_(self, values: List[Any]) -> QuerySpecification[T]:
        """In list of values."""
        return self._spec.add_filter(self._field, "in", values)

    def not_in(self, values: List[Any]) -> QuerySpecification[T]:
        """Not in list of values."""
        return self._spec.add_filter(self._field, "not_in", values)

    def is_null(self) -> QuerySpecification[T]:
        """Is NULL."""
        return self._spec.add_filter(self._field, "is_null", True)

    def is_not_null(self) -> QuerySpecification[T]:
        """Is not NULL."""
        return self._spec.add_filter(self._field, "is_null", False)

    def between(self, low: Any, high: Any) -> QuerySpecification[T]:
        """Between two values."""
        return self._spec.add_filter(self._field, "between", (low, high))
