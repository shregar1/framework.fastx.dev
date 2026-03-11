"""
Test Fixtures and Utilities.

Provides common fixtures and test utilities for FastMVC applications.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Optional, Type

from fastapi import FastAPI
from fastapi.testclient import TestClient as FastAPITestClient


class TestClient(FastAPITestClient):
    """
    Extended test client with additional utilities.

    Usage:
        client = TestClient(app)

        # Make requests
        response = client.get("/users")

        # With authentication
        client.set_auth_header("Bearer token123")
        response = client.get("/protected")

        # With tenant
        client.set_tenant("tenant-123")
        response = client.get("/data")
    """

    def __init__(self, app: FastAPI, **kwargs: Any):
        super().__init__(app, **kwargs)
        self._default_headers: Dict[str, str] = {}

    def set_auth_header(self, value: str) -> None:
        """Set Authorization header for all requests."""
        self._default_headers["Authorization"] = value

    def set_api_key(self, key: str, header: str = "X-API-Key") -> None:
        """Set API key header for all requests."""
        self._default_headers[header] = key

    def set_tenant(self, tenant_id: str, header: str = "X-Tenant-ID") -> None:
        """Set tenant header for all requests."""
        self._default_headers[header] = tenant_id

    def clear_auth(self) -> None:
        """Clear authentication headers."""
        self._default_headers.pop("Authorization", None)
        self._default_headers.pop("X-API-Key", None)

    def request(self, method: str, url: str, **kwargs: Any) -> Any:
        """Make request with default headers."""
        headers = kwargs.pop("headers", {})
        headers.update(self._default_headers)
        return super().request(method, url, headers=headers, **kwargs)


class DatabaseTestCase:
    """
    Base class for database tests.

    Provides transaction rollback for test isolation.

    Usage:
        class TestUserService(DatabaseTestCase):
            async def test_create_user(self):
                user = await UserService.create(email="test@example.com")
                assert user.email == "test@example.com"
                # Changes are rolled back after test
    """

    _session = None
    _transaction = None

    @classmethod
    def setup_class(cls) -> None:
        """Setup test database connection."""
        pass

    @classmethod
    def teardown_class(cls) -> None:
        """Cleanup test database connection."""
        pass

    def setup_method(self) -> None:
        """Start transaction before each test."""
        pass

    def teardown_method(self) -> None:
        """Rollback transaction after each test."""
        pass


class AsyncDatabaseTestCase:
    """
    Async version of DatabaseTestCase.

    Usage:
        class TestUserRepository(AsyncDatabaseTestCase):
            async def test_get_user(self):
                async with self.session() as session:
                    user = await UserRepository(session).get(1)
    """

    _engine = None
    _session_factory = None

    @classmethod
    async def setup_class(cls) -> None:
        """Setup async database connection."""
        pass

    @classmethod
    async def teardown_class(cls) -> None:
        """Cleanup async database connection."""
        pass

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[Any, None]:
        """Get test session with automatic rollback."""
        # Create session
        session = self._session_factory() if self._session_factory else None
        try:
            yield session
        finally:
            if session:
                await session.rollback()
                await session.close()


def create_test_app(**kwargs: Any) -> FastAPI:
    """
    Create a FastAPI app configured for testing.

    Usage:
        app = create_test_app()
        client = TestClient(app)
    """
    from fastapi import FastAPI

    app = FastAPI(
        title="Test App",
        docs_url=None,  # Disable docs in tests
        redoc_url=None,
        **kwargs,
    )

    return app


async def run_async(coro: Any) -> Any:
    """
    Run async function in sync context.

    Useful for running async tests in synchronous test runners.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


class FixtureRegistry:
    """
    Registry for test fixtures.

    Usage:
        fixtures = FixtureRegistry()

        @fixtures.register("user")
        async def create_user():
            return await UserFactory.create()

        # In tests
        user = await fixtures.get("user")
    """

    def __init__(self):
        self._fixtures: Dict[str, Any] = {}
        self._cache: Dict[str, Any] = {}

    def register(self, name: str) -> Any:
        """Decorator to register a fixture."""

        def decorator(func: Any) -> Any:
            self._fixtures[name] = func
            return func

        return decorator

    async def get(self, name: str, use_cache: bool = True) -> Any:
        """Get fixture value."""
        if use_cache and name in self._cache:
            return self._cache[name]

        if name not in self._fixtures:
            raise ValueError(f"Unknown fixture: {name}")

        func = self._fixtures[name]
        if asyncio.iscoroutinefunction(func):
            value = await func()
        else:
            value = func()

        if use_cache:
            self._cache[name] = value

        return value

    def clear_cache(self) -> None:
        """Clear fixture cache."""
        self._cache.clear()


# Global fixture registry
fixtures = FixtureRegistry()
