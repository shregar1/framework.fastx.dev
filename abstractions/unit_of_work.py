"""
Unit of Work Pattern.

Manages transactions across multiple repositories, ensuring
all operations succeed or fail together.

Implements:
- Transaction management
- Repository coordination
- Commit/Rollback semantics

SOLID Principles:
- Single Responsibility: Manages transaction boundaries only
- Open/Closed: Extensible for new repository types
- Dependency Inversion: Depends on abstractions, not concrete repos
"""

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Dict, Generic, Optional, Type, TypeVar

T = TypeVar("T")


class IUnitOfWork(ABC):
    """
    Abstract Unit of Work interface.

    Coordinates multiple repository operations within a single transaction.

    Usage:
        async with unit_of_work as uow:
            user = await uow.users.create(user_data)
            await uow.orders.create(order_data)
            await uow.commit()  # Both succeed or both fail
    """

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """Enter the unit of work context."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the unit of work context."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit all changes in the current transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback all changes in the current transaction."""
        pass


class ISyncUnitOfWork(ABC):
    """Synchronous Unit of Work interface."""

    @abstractmethod
    def __enter__(self) -> "ISyncUnitOfWork":
        pass

    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass


class BaseUnitOfWork(IUnitOfWork):
    """
    Base Unit of Work implementation.

    Subclass this to add your repositories as properties.

    Example:
        class AppUnitOfWork(BaseUnitOfWork):
            @property
            def users(self) -> UserRepository:
                return UserRepository(self._session)

            @property
            def orders(self) -> OrderRepository:
                return OrderRepository(self._session)
    """

    def __init__(self, session_factory: Any):
        """
        Initialize Unit of Work.

        Args:
            session_factory: Factory for creating database sessions.
        """
        self._session_factory = session_factory
        self._session: Optional[Any] = None
        self._repositories: Dict[str, Any] = {}

    async def __aenter__(self) -> "BaseUnitOfWork":
        """Create session and begin transaction."""
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Handle transaction completion."""
        if exc_type is not None:
            await self.rollback()
        if self._session:
            await self._close_session()

    async def _close_session(self) -> None:
        """Close the session."""
        if hasattr(self._session, "close"):
            if hasattr(self._session.close, "__call__"):
                result = self._session.close()
                if hasattr(result, "__await__"):
                    await result

    async def commit(self) -> None:
        """Commit the transaction."""
        if self._session and hasattr(self._session, "commit"):
            result = self._session.commit()
            if hasattr(result, "__await__"):
                await result

    async def rollback(self) -> None:
        """Rollback the transaction."""
        if self._session and hasattr(self._session, "rollback"):
            result = self._session.rollback()
            if hasattr(result, "__await__"):
                await result

    def get_repository(self, repo_class: Type[T]) -> T:
        """
        Get or create a repository instance.

        Args:
            repo_class: Repository class to instantiate.

        Returns:
            Repository instance using current session.
        """
        class_name = repo_class.__name__
        if class_name not in self._repositories:
            self._repositories[class_name] = repo_class(self._session)
        return self._repositories[class_name]


class UnitOfWorkManager:
    """
    Factory for creating Unit of Work instances.

    Usage:
        manager = UnitOfWorkManager(session_factory)
        async with manager.create() as uow:
            await uow.users.create(...)
            await uow.commit()
    """

    def __init__(
        self,
        session_factory: Any,
        uow_class: Type[BaseUnitOfWork] = BaseUnitOfWork,
    ):
        self._session_factory = session_factory
        self._uow_class = uow_class

    @asynccontextmanager
    async def create(self):
        """Create a new Unit of Work context."""
        uow = self._uow_class(self._session_factory)
        async with uow:
            yield uow
