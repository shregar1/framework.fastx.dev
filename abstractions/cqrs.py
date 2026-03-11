"""
Command Query Responsibility Segregation (CQRS) Pattern.

Separates read (query) and write (command) operations
for better scalability and optimization.

Implements:
- Command handlers for write operations
- Query handlers for read operations
- Command/Query bus for dispatching

SOLID Principles:
- Single Responsibility: Separate read/write concerns
- Interface Segregation: Distinct command/query interfaces
- Dependency Inversion: Handlers depend on abstractions
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar

TCommand = TypeVar("TCommand", bound="ICommand")
TQuery = TypeVar("TQuery", bound="IQuery")
TResult = TypeVar("TResult")


@dataclass
class ICommand:
    """
    Base command interface.

    Commands represent intent to change system state.
    They should be named in imperative form (CreateUser, UpdateOrder).

    Usage:
        @dataclass
        class CreateUserCommand(ICommand):
            email: str
            name: str
            password: str
    """

    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


@dataclass
class IQuery(Generic[TResult]):
    """
    Base query interface.

    Queries represent requests for data.
    They should be named as questions (GetUserById, ListActiveOrders).

    Usage:
        @dataclass
        class GetUserByIdQuery(IQuery[User]):
            user_id: str

        @dataclass
        class ListUsersQuery(IQuery[List[User]]):
            page: int = 1
            page_size: int = 20
    """

    pass


class ICommandHandler(ABC, Generic[TCommand]):
    """
    Command handler interface.

    Processes a specific command type and modifies system state.

    Usage:
        class CreateUserHandler(ICommandHandler[CreateUserCommand]):
            async def handle(self, command: CreateUserCommand) -> str:
                user = User(email=command.email, name=command.name)
                await self.repository.create(user)
                return user.id
    """

    @abstractmethod
    async def handle(self, command: TCommand) -> Any:
        """
        Handle the command.

        Args:
            command: Command to process.

        Returns:
            Result of command execution.
        """
        pass


class IQueryHandler(ABC, Generic[TQuery, TResult]):
    """
    Query handler interface.

    Processes a specific query type and returns data.

    Usage:
        class GetUserByIdHandler(IQueryHandler[GetUserByIdQuery, User]):
            async def handle(self, query: GetUserByIdQuery) -> User:
                return await self.repository.get_by_id(query.user_id)
    """

    @abstractmethod
    async def handle(self, query: TQuery) -> TResult:
        """
        Handle the query.

        Args:
            query: Query to process.

        Returns:
            Query result.
        """
        pass


class CommandBus:
    """
    Command dispatcher/bus.

    Routes commands to their appropriate handlers.

    Usage:
        bus = CommandBus()
        bus.register(CreateUserCommand, CreateUserHandler())

        result = await bus.dispatch(CreateUserCommand(
            email="user@example.com",
            name="John Doe"
        ))
    """

    def __init__(self):
        self._handlers: Dict[Type[ICommand], ICommandHandler] = {}
        self._middlewares: List[Callable] = []

    def register(
        self,
        command_type: Type[TCommand],
        handler: ICommandHandler[TCommand],
    ) -> None:
        """Register a handler for a command type."""
        self._handlers[command_type] = handler

    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware for command processing."""
        self._middlewares.append(middleware)

    async def dispatch(self, command: ICommand) -> Any:
        """
        Dispatch a command to its handler.

        Args:
            command: Command to dispatch.

        Returns:
            Result from handler.

        Raises:
            ValueError: If no handler is registered.
        """
        handler = self._handlers.get(type(command))
        if handler is None:
            raise ValueError(f"No handler registered for {type(command).__name__}")

        # Apply middlewares
        async def execute():
            return await handler.handle(command)

        result = execute
        for middleware in reversed(self._middlewares):
            result = middleware(result, command)

        return await result()


class QueryBus:
    """
    Query dispatcher/bus.

    Routes queries to their appropriate handlers.

    Usage:
        bus = QueryBus()
        bus.register(GetUserByIdQuery, GetUserByIdHandler())

        user = await bus.dispatch(GetUserByIdQuery(user_id="123"))
    """

    def __init__(self):
        self._handlers: Dict[Type[IQuery], IQueryHandler] = {}
        self._middlewares: List[Callable] = []

    def register(
        self,
        query_type: Type[TQuery],
        handler: IQueryHandler[TQuery, Any],
    ) -> None:
        """Register a handler for a query type."""
        self._handlers[query_type] = handler

    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware for query processing."""
        self._middlewares.append(middleware)

    async def dispatch(self, query: IQuery[TResult]) -> TResult:
        """
        Dispatch a query to its handler.

        Args:
            query: Query to dispatch.

        Returns:
            Query result.

        Raises:
            ValueError: If no handler is registered.
        """
        handler = self._handlers.get(type(query))
        if handler is None:
            raise ValueError(f"No handler registered for {type(query).__name__}")

        # Apply middlewares
        async def execute():
            return await handler.handle(query)

        result = execute
        for middleware in reversed(self._middlewares):
            result = middleware(result, query)

        return await result()


class Mediator:
    """
    Combined mediator for commands and queries.

    Provides a unified interface for dispatching both.

    Usage:
        mediator = Mediator()
        mediator.register_command(CreateUserCommand, CreateUserHandler())
        mediator.register_query(GetUserByIdQuery, GetUserByIdHandler())

        # Send command
        user_id = await mediator.send(CreateUserCommand(...))

        # Send query
        user = await mediator.send(GetUserByIdQuery(user_id=user_id))
    """

    def __init__(self):
        self._command_bus = CommandBus()
        self._query_bus = QueryBus()

    def register_command(
        self,
        command_type: Type[TCommand],
        handler: ICommandHandler[TCommand],
    ) -> None:
        """Register a command handler."""
        self._command_bus.register(command_type, handler)

    def register_query(
        self,
        query_type: Type[TQuery],
        handler: IQueryHandler[TQuery, Any],
    ) -> None:
        """Register a query handler."""
        self._query_bus.register(query_type, handler)

    async def send(self, message: Any) -> Any:
        """
        Send a command or query.

        Args:
            message: Command or query to dispatch.

        Returns:
            Result from handler.
        """
        if isinstance(message, ICommand):
            return await self._command_bus.dispatch(message)
        elif isinstance(message, IQuery):
            return await self._query_bus.dispatch(message)
        else:
            raise ValueError(f"Unknown message type: {type(message)}")
