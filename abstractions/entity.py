"""
Entity and Aggregate Root Patterns.

Entities have identity that persists across time and states.
Aggregate Roots are clusters of domain objects with a root entity.

Implements:
- Entity base class with identity
- Aggregate root with domain events
- Entity comparison by identity

SOLID Principles:
- Single Responsibility: Entities manage their own state
- Open/Closed: Extend entities without modification
- Liskov Substitution: Entities are polymorphic
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
import uuid


TId = TypeVar("TId")


class IEntity(ABC, Generic[TId]):
    """
    Abstract entity interface.

    Entities are objects with a distinct identity that runs
    through time and different states.

    Usage:
        class User(IEntity[str]):
            def __init__(self, user_id: str, email: str):
                self._id = user_id
                self.email = email

            @property
            def id(self) -> str:
                return self._id
    """

    @property
    @abstractmethod
    def id(self) -> TId:
        """Get the entity's unique identifier."""
        pass

    def __eq__(self, other: Any) -> bool:
        """Entities are equal if they have the same ID."""
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID for use in sets/dicts."""
        return hash(self.id)


@dataclass
class Entity(IEntity[str]):
    """
    Base entity with string ID.

    Usage:
        @dataclass
        class User(Entity):
            email: str
            name: str

            def change_email(self, new_email: str):
                self.email = new_email
                self.updated_at = datetime.utcnow()
    """

    _id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def id(self) -> str:
        return self._id

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class IAggregateRoot(IEntity[TId]):
    """
    Aggregate Root interface.

    An aggregate is a cluster of domain objects that can be
    treated as a single unit. The root is the only member that
    outside objects can reference.

    Aggregates:
    - Encapsulate related entities and value objects
    - Enforce invariants across the entire aggregate
    - Are the unit of persistence (loaded/saved together)
    - Raise domain events for cross-aggregate communication
    """

    @abstractmethod
    def get_uncommitted_events(self) -> List[Any]:
        """Get domain events that haven't been dispatched."""
        pass

    @abstractmethod
    def clear_events(self) -> None:
        """Clear uncommitted events after dispatching."""
        pass


@dataclass
class AggregateRoot(Entity, IAggregateRoot[str]):
    """
    Base aggregate root implementation.

    Usage:
        @dataclass
        class Order(AggregateRoot):
            customer_id: str
            items: List[OrderItem] = field(default_factory=list)
            status: str = "pending"

            def place(self):
                if not self.items:
                    raise ValueError("Cannot place empty order")
                self.status = "placed"
                self._raise_event(OrderPlacedEvent(
                    order_id=self.id,
                    customer_id=self.customer_id
                ))

            def add_item(self, product_id: str, quantity: int):
                item = OrderItem(product_id=product_id, quantity=quantity)
                self.items.append(item)
                self.touch()
    """

    _events: List[Any] = field(default_factory=list, repr=False)
    _version: int = field(default=0, repr=False)

    def get_uncommitted_events(self) -> List[Any]:
        return self._events.copy()

    def clear_events(self) -> None:
        self._events.clear()

    def _raise_event(self, event: Any) -> None:
        """
        Raise a domain event.

        Events are collected and dispatched after persistence.
        """
        self._events.append(event)

    @property
    def version(self) -> int:
        """Get aggregate version for optimistic locking."""
        return self._version

    def increment_version(self) -> None:
        """Increment version after save."""
        self._version += 1


class EntityFactory(Generic[TId]):
    """
    Factory for creating entities.

    Usage:
        factory = EntityFactory(User)
        user = factory.create(email="user@example.com", name="John")
    """

    def __init__(self, entity_class: type):
        self._entity_class = entity_class

    def create(self, **kwargs) -> Any:
        """Create a new entity instance."""
        return self._entity_class(**kwargs)

    def reconstitute(self, id: TId, **kwargs) -> Any:
        """Reconstitute an entity from persistence."""
        return self._entity_class(_id=id, **kwargs)


@dataclass
class DomainEvent:
    """
    Base class for domain events.

    Usage:
        @dataclass
        class UserCreated(DomainEvent):
            user_id: str
            email: str

        @dataclass
        class OrderPlaced(DomainEvent):
            order_id: str
            customer_id: str
            total_amount: float
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    aggregate_id: Optional[str] = None
    aggregate_type: Optional[str] = None

    @property
    def event_type(self) -> str:
        """Get the event type name."""
        return self.__class__.__name__


class SoftDeletableEntity(Entity):
    """
    Entity that supports soft deletion.

    Usage:
        @dataclass
        class Product(SoftDeletableEntity):
            name: str
            price: float

        product.delete()  # Soft delete
        product.restore()  # Restore
    """

    deleted_at: Optional[datetime] = field(default=None)

    @property
    def is_deleted(self) -> bool:
        """Check if entity is soft-deleted."""
        return self.deleted_at is not None

    def delete(self) -> None:
        """Soft delete the entity."""
        self.deleted_at = datetime.utcnow()
        self.touch()

    def restore(self) -> None:
        """Restore a soft-deleted entity."""
        self.deleted_at = None
        self.touch()


class AuditableEntity(Entity):
    """
    Entity with audit trail.

    Usage:
        @dataclass
        class Document(AuditableEntity):
            title: str
            content: str

        doc.set_creator("user-123")
        doc.set_modifier("user-456")
    """

    created_by: Optional[str] = field(default=None)
    updated_by: Optional[str] = field(default=None)

    def set_creator(self, user_id: str) -> None:
        """Set the creator."""
        self.created_by = user_id
        self.updated_by = user_id

    def set_modifier(self, user_id: str) -> None:
        """Set the last modifier."""
        self.updated_by = user_id
        self.touch()


class VersionedEntity(Entity):
    """
    Entity with version for optimistic locking.

    Usage:
        @dataclass
        class Account(VersionedEntity):
            balance: float

            def debit(self, amount: float):
                if amount > self.balance:
                    raise ValueError("Insufficient funds")
                self.balance -= amount
                self.increment_version()
    """

    _version: int = field(default=1)

    @property
    def version(self) -> int:
        return self._version

    def increment_version(self) -> None:
        """Increment version on modification."""
        self._version += 1
        self.touch()

    def check_version(self, expected: int) -> bool:
        """Check if version matches for optimistic locking."""
        return self._version == expected
