"""
Observer/Publisher-Subscriber Pattern.

Defines a one-to-many dependency between objects so that
when one object changes state, all dependents are notified.

Implements:
- Subject/Observable interface
- Observer interface
- Event-based notifications
- Async observer support

SOLID Principles:
- Single Responsibility: Observers handle one notification
- Open/Closed: Add observers without modification
- Dependency Inversion: Subjects don't know observer details
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, Optional, Set, TypeVar
from weakref import WeakSet
import asyncio

T = TypeVar("T")


class IObserver(ABC, Generic[T]):
    """
    Observer interface.

    Usage:
        class EmailNotifier(IObserver[OrderEvent]):
            def update(self, event: OrderEvent) -> None:
                send_email(event.customer_email, "Order update!")

        class StockUpdater(IObserver[OrderEvent]):
            def update(self, event: OrderEvent) -> None:
                update_inventory(event.items)
    """

    @abstractmethod
    def update(self, event: T) -> None:
        """
        Handle notification from subject.

        Args:
            event: Event data from subject.
        """
        pass


class IAsyncObserver(ABC, Generic[T]):
    """Async observer interface."""

    @abstractmethod
    async def update(self, event: T) -> None:
        """Handle notification asynchronously."""
        pass


class ISubject(ABC, Generic[T]):
    """
    Subject/Observable interface.

    Usage:
        class OrderService(ISubject[OrderEvent]):
            def place_order(self, order: Order):
                # Process order
                self.notify(OrderEvent(order_id=order.id, status="placed"))
    """

    @abstractmethod
    def attach(self, observer: IObserver[T]) -> None:
        """Attach an observer."""
        pass

    @abstractmethod
    def detach(self, observer: IObserver[T]) -> None:
        """Detach an observer."""
        pass

    @abstractmethod
    def notify(self, event: T) -> None:
        """Notify all observers."""
        pass


class Subject(ISubject[T]):
    """
    Base subject implementation.

    Usage:
        subject = Subject()
        subject.attach(EmailNotifier())
        subject.attach(LoggingObserver())

        subject.notify(UserCreatedEvent(user_id="123"))
    """

    def __init__(self):
        self._observers: Set[IObserver[T]] = set()

    def attach(self, observer: IObserver[T]) -> None:
        """Add observer to notification list."""
        self._observers.add(observer)

    def detach(self, observer: IObserver[T]) -> None:
        """Remove observer from notification list."""
        self._observers.discard(observer)

    def notify(self, event: T) -> None:
        """Notify all attached observers."""
        for observer in self._observers:
            observer.update(event)


class AsyncSubject(Generic[T]):
    """
    Async subject for async observers.

    Usage:
        subject = AsyncSubject()
        subject.attach(AsyncEmailNotifier())

        await subject.notify(event)
    """

    def __init__(self):
        self._observers: Set[IAsyncObserver[T]] = set()

    def attach(self, observer: IAsyncObserver[T]) -> None:
        self._observers.add(observer)

    def detach(self, observer: IAsyncObserver[T]) -> None:
        self._observers.discard(observer)

    async def notify(self, event: T) -> None:
        """Notify all observers concurrently."""
        await asyncio.gather(
            *[observer.update(event) for observer in self._observers],
            return_exceptions=True,
        )


class WeakSubject(ISubject[T]):
    """
    Subject using weak references.

    Observers are automatically removed when garbage collected.
    """

    def __init__(self):
        self._observers: WeakSet = WeakSet()

    def attach(self, observer: IObserver[T]) -> None:
        self._observers.add(observer)

    def detach(self, observer: IObserver[T]) -> None:
        self._observers.discard(observer)

    def notify(self, event: T) -> None:
        for observer in self._observers:
            observer.update(event)


@dataclass
class EventChannel(Generic[T]):
    """
    Named event channel for pub/sub.

    Usage:
        channel = EventChannel("orders")
        channel.subscribe(OrderProcessor())
        channel.subscribe(AnalyticsCollector())

        channel.publish(OrderEvent(...))
    """

    name: str
    _subscribers: Set[IObserver[T]] = field(default_factory=set)

    def subscribe(self, observer: IObserver[T]) -> None:
        """Subscribe to channel."""
        self._subscribers.add(observer)

    def unsubscribe(self, observer: IObserver[T]) -> None:
        """Unsubscribe from channel."""
        self._subscribers.discard(observer)

    def publish(self, event: T) -> None:
        """Publish event to all subscribers."""
        for subscriber in self._subscribers:
            subscriber.update(event)


class EventBus:
    """
    Central event bus for application-wide pub/sub.

    Usage:
        bus = EventBus()

        # Subscribe to specific event types
        bus.subscribe("user.created", SendWelcomeEmailObserver())
        bus.subscribe("user.created", CreateDefaultSettingsObserver())
        bus.subscribe("order.placed", ProcessPaymentObserver())

        # Publish events
        bus.publish("user.created", UserCreatedEvent(...))
    """

    def __init__(self):
        self._channels: Dict[str, EventChannel] = {}
        self._global_observers: List[IObserver] = []

    def subscribe(
        self,
        event_type: str,
        observer: IObserver,
    ) -> None:
        """Subscribe to an event type."""
        if event_type not in self._channels:
            self._channels[event_type] = EventChannel(event_type)
        self._channels[event_type].subscribe(observer)

    def subscribe_all(self, observer: IObserver) -> None:
        """Subscribe to all events."""
        self._global_observers.append(observer)

    def unsubscribe(
        self,
        event_type: str,
        observer: IObserver,
    ) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._channels:
            self._channels[event_type].unsubscribe(observer)

    def publish(self, event_type: str, event: Any) -> None:
        """Publish an event."""
        # Notify specific subscribers
        if event_type in self._channels:
            self._channels[event_type].publish(event)

        # Notify global observers
        for observer in self._global_observers:
            observer.update(event)


class AsyncEventBus:
    """Async version of EventBus."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(
        self,
        event_type: str,
        handler: Callable,
    ) -> None:
        """Subscribe a handler."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event_type: str, event: Any) -> None:
        """Publish event asynchronously."""
        handlers = self._handlers.get(event_type, [])
        await asyncio.gather(
            *[
                handler(event) if asyncio.iscoroutinefunction(handler)
                else asyncio.to_thread(handler, event)
                for handler in handlers
            ],
            return_exceptions=True,
        )


class LambdaObserver(IObserver[T]):
    """
    Observer from a lambda function.

    Usage:
        observer = LambdaObserver(lambda e: print(f"Event: {e}"))
        subject.attach(observer)
    """

    def __init__(self, callback: Callable[[T], None]):
        self._callback = callback

    def update(self, event: T) -> None:
        self._callback(event)


class FilteredObserver(IObserver[T]):
    """
    Observer that filters events before processing.

    Usage:
        observer = FilteredObserver(
            predicate=lambda e: e.priority == "high",
            handler=lambda e: send_alert(e)
        )
    """

    def __init__(
        self,
        predicate: Callable[[T], bool],
        handler: Callable[[T], None],
    ):
        self._predicate = predicate
        self._handler = handler

    def update(self, event: T) -> None:
        if self._predicate(event):
            self._handler(event)


class BufferedObserver(IObserver[T]):
    """
    Observer that buffers events and processes in batches.

    Usage:
        observer = BufferedObserver(
            batch_size=10,
            handler=lambda events: bulk_insert(events)
        )
    """

    def __init__(
        self,
        batch_size: int,
        handler: Callable[[List[T]], None],
    ):
        self._batch_size = batch_size
        self._handler = handler
        self._buffer: List[T] = []

    def update(self, event: T) -> None:
        self._buffer.append(event)
        if len(self._buffer) >= self._batch_size:
            self.flush()

    def flush(self) -> None:
        """Process buffered events."""
        if self._buffer:
            self._handler(self._buffer)
            self._buffer = []


def on_event(event_type: str):
    """
    Decorator to register an event handler.

    Usage:
        @on_event("user.created")
        def handle_user_created(event: UserCreatedEvent):
            send_welcome_email(event.email)
    """
    def decorator(func: Callable) -> Callable:
        func._event_type = event_type
        return func
    return decorator
