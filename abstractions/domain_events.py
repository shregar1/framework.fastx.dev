"""
Domain Events Pattern.

Enables loose coupling through event-driven communication
between different parts of the application.

Implements:
- Domain event base class
- Event dispatcher/publisher
- Event handlers/subscribers
- Async event processing

SOLID Principles:
- Single Responsibility: Events represent single occurrences
- Open/Closed: Add handlers without modifying publishers
- Dependency Inversion: Publishers don't know subscribers
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar
import uuid

TEvent = TypeVar("TEvent", bound="IDomainEvent")


@dataclass
class IDomainEvent:
    """
    Base domain event interface.

    Domain events represent something that happened in the domain.
    They are named in past tense (UserCreated, OrderPlaced).

    Usage:
        @dataclass
        class UserCreatedEvent(IDomainEvent):
            user_id: str
            email: str

        @dataclass
        class OrderPlacedEvent(IDomainEvent):
            order_id: str
            user_id: str
            total_amount: float
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None

    @property
    def event_type(self) -> str:
        """Get the event type name."""
        return self.__class__.__name__


class IEventHandler(ABC, Generic[TEvent]):
    """
    Event handler interface.

    Handles a specific type of domain event.

    Usage:
        class SendWelcomeEmailHandler(IEventHandler[UserCreatedEvent]):
            async def handle(self, event: UserCreatedEvent) -> None:
                await email_service.send_welcome(event.email)
    """

    @abstractmethod
    async def handle(self, event: TEvent) -> None:
        """
        Handle the event.

        Args:
            event: Event to handle.
        """
        pass


class EventDispatcher:
    """
    Domain event dispatcher.

    Routes events to registered handlers.

    Usage:
        dispatcher = EventDispatcher()
        dispatcher.subscribe(UserCreatedEvent, SendWelcomeEmailHandler())
        dispatcher.subscribe(UserCreatedEvent, UpdateAnalyticsHandler())

        await dispatcher.dispatch(UserCreatedEvent(user_id="123", email="..."))
    """

    def __init__(self):
        self._handlers: Dict[Type[IDomainEvent], List[IEventHandler]] = {}
        self._global_handlers: List[IEventHandler] = []

    def subscribe(
        self,
        event_type: Type[TEvent],
        handler: IEventHandler[TEvent],
    ) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: Type of event to handle.
            handler: Handler to invoke.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def subscribe_all(self, handler: IEventHandler) -> None:
        """Subscribe a handler to all events."""
        self._global_handlers.append(handler)

    def unsubscribe(
        self,
        event_type: Type[TEvent],
        handler: IEventHandler[TEvent],
    ) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

    async def dispatch(self, event: IDomainEvent) -> None:
        """
        Dispatch an event to all registered handlers.

        Args:
            event: Event to dispatch.
        """
        handlers = self._handlers.get(type(event), [])
        all_handlers = handlers + self._global_handlers

        # Execute all handlers
        await asyncio.gather(
            *[handler.handle(event) for handler in all_handlers],
            return_exceptions=True,
        )

    async def dispatch_all(self, events: List[IDomainEvent]) -> None:
        """Dispatch multiple events."""
        for event in events:
            await self.dispatch(event)


class EventStore:
    """
    Event store for event sourcing.

    Persists all domain events for replay and audit.

    Usage:
        store = EventStore()
        await store.append("user-123", UserCreatedEvent(...))
        await store.append("user-123", UserUpdatedEvent(...))

        events = await store.get_events("user-123")
    """

    def __init__(self):
        self._events: Dict[str, List[IDomainEvent]] = {}
        self._all_events: List[IDomainEvent] = []

    async def append(
        self,
        aggregate_id: str,
        event: IDomainEvent,
    ) -> None:
        """
        Append an event to the store.

        Args:
            aggregate_id: ID of the aggregate.
            event: Event to store.
        """
        if aggregate_id not in self._events:
            self._events[aggregate_id] = []
        self._events[aggregate_id].append(event)
        self._all_events.append(event)

    async def get_events(
        self,
        aggregate_id: str,
        since: Optional[datetime] = None,
    ) -> List[IDomainEvent]:
        """
        Get events for an aggregate.

        Args:
            aggregate_id: ID of the aggregate.
            since: Only events after this time.

        Returns:
            List of events.
        """
        events = self._events.get(aggregate_id, [])
        if since:
            events = [e for e in events if e.occurred_at > since]
        return events

    async def get_all_events(
        self,
        event_types: Optional[List[Type[IDomainEvent]]] = None,
        since: Optional[datetime] = None,
    ) -> List[IDomainEvent]:
        """Get all events, optionally filtered."""
        events = self._all_events
        if event_types:
            events = [e for e in events if type(e) in event_types]
        if since:
            events = [e for e in events if e.occurred_at > since]
        return events


class AggregateRoot:
    """
    Base class for aggregate roots with event sourcing.

    Aggregates collect domain events and can be replayed.

    Usage:
        class User(AggregateRoot):
            def __init__(self, user_id: str):
                super().__init__()
                self.user_id = user_id
                self.email = None

            def create(self, email: str):
                self._raise_event(UserCreatedEvent(
                    user_id=self.user_id,
                    email=email
                ))

            def _apply(self, event: IDomainEvent):
                if isinstance(event, UserCreatedEvent):
                    self.email = event.email
    """

    def __init__(self):
        self._uncommitted_events: List[IDomainEvent] = []
        self._version = 0

    @property
    def uncommitted_events(self) -> List[IDomainEvent]:
        """Get uncommitted events."""
        return self._uncommitted_events.copy()

    def clear_events(self) -> None:
        """Clear uncommitted events after persistence."""
        self._uncommitted_events.clear()

    def _raise_event(self, event: IDomainEvent) -> None:
        """
        Raise a domain event.

        Applies the event and adds to uncommitted list.
        """
        self._apply(event)
        self._uncommitted_events.append(event)
        self._version += 1

    def _apply(self, event: IDomainEvent) -> None:
        """
        Apply an event to update aggregate state.

        Override this to handle specific events.
        """
        pass

    def load_from_history(self, events: List[IDomainEvent]) -> None:
        """
        Replay events to rebuild aggregate state.

        Args:
            events: Historical events to replay.
        """
        for event in events:
            self._apply(event)
            self._version += 1


def event_handler(event_type: Type[TEvent]) -> Callable:
    """
    Decorator to register a function as an event handler.

    Usage:
        @event_handler(UserCreatedEvent)
        async def send_welcome_email(event: UserCreatedEvent):
            await email_service.send_welcome(event.email)
    """
    def decorator(func: Callable) -> Callable:
        func._event_type = event_type
        return func
    return decorator
