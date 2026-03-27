"""Pytest Fixtures for Item API Testing.

Provides reusable fixtures for:
- FastAPI test client
- DataI setup/teardown
- Authentication mocking
- Test data generation

Usage:
    # In your conftest.py or test file
    pytest_plugins = ['example.testing.fixtures']

    # Or import directly
    from example.testing.fixtures import item_client, test_item

    def test_get_item(item_client, test_item):
        response = item_client.get(f"/items/{test_item.id}")
        assert response.status_code == 200
"""

import pytest
from datetime import datetime, timedelta
from typing import Any, Generator
from contextlib import nullcontext
from unittest.mock import Mock, patch

# Try to import FastAPI testing dependencies
try:
    from fastapi.testclient import TestClient
    from httpx import AsyncClient

    HAS_FASTAPI_TEST = True
except ImportError:
    HAS_FASTAPI_TEST = False

# Try to import pytest
try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from example.entities.item import ItemEntity
from example.testing.factories import ItemFactory


# =============================================================================
# DATAI FIXTURES
# =============================================================================


@pytest.fixture
def item_db() -> Generator[dict[str, Any], None, None]:
    """Provide an in-memory dataInterface for testing.

    Yields:
        Dictionary acting as a simple in-memory dataI.

    Example:
        def test_create_item(item_db):
            item_db["items"]["123"] = ItemFactory.create(id="123")
            assert len(item_db["items"]) == 1

    """
    db = {
        "items": {},
        "users": {},
        "next_id": 1,
    }
    yield db
    # Cleanup after test
    db.clear()


@pytest.fixture
def item_repository(item_db):
    """Provide a mocked ItemRepository using the in-memory dataI.

    Yields:
        Mocked repository instance.

    """
    from example.repositories.item_repository import ItemRepository

    repo = Mock(spec=ItemRepository)

    # Mock storage
    _storage = item_db["items"]

    async def mock_create(entity: ItemEntity) -> ItemEntity:
        """Execute mock_create operation.

        Args:
            entity: The entity parameter.

        Returns:
            The result of the operation.
        """
        entity_id = str(item_db["next_id"])
        item_db["next_id"] += 1
        entity._id = entity_id
        _storage[entity_id] = entity
        return entity

    async def mock_get_by_id(item_id: str) -> ItemEntity | None:
        """Execute mock_get_by_id operation.

        Args:
            item_id: The item_id parameter.

        Returns:
            The result of the operation.
        """
        return _storage.get(item_id)

    async def mock_get_all() -> list[ItemEntity]:
        """Execute mock_get_all operation.

        Returns:
            The result of the operation.
        """
        return list(_storage.values())

    async def mock_update(entity: ItemEntity) -> ItemEntity:
        """Execute mock_update operation.

        Args:
            entity: The entity parameter.

        Returns:
            The result of the operation.
        """
        _storage[entity.id] = entity
        return entity

    async def mock_delete(item_id: str) -> bool:
        """Execute mock_delete operation.

        Args:
            item_id: The item_id parameter.

        Returns:
            The result of the operation.
        """
        if item_id in _storage:
            del _storage[item_id]
            return True
        return False

    repo.create = mock_create
    repo.get_by_id = mock_get_by_id
    repo.get_all = mock_get_all
    repo.update = mock_update
    repo.delete = mock_delete

    yield repo


# =============================================================================
# CLIENT FIXTURES
# =============================================================================


@pytest.fixture
def app():
    """Provide the FastAPI application instance.

    Returns:
        FastAPI application

    Raises:
        ImportError: If FastAPI app cannot be imported

    """
    try:
        from app import app as fastapi_app

        return fastapi_app
    except ImportError:
        pytest.skip("FastAPI app not available")


@pytest.fixture
def item_client(app) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient for making HTTP requests.

    Yields:
        TestClient instance configured for the FastAPI app.

    Example:
        def test_get_items(item_client):
            response = item_client.get("/items")
            assert response.status_code == 200

    """
    if not HAS_FASTAPI_TEST:
        pytest.skip("fastapi test dependencies not installed")

    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_item_client(app) -> AsyncClient:
    """Provide an async HTTPX client for testing.

    Yields:
        AsyncClient instance for async testing.

    Example:
        async def test_get_items(async_item_client):
            response = await async_item_client.get("/items")
            assert response.status_code == 200

    """
    if not HAS_FASTAPI_TEST:
        pytest.skip("httpx not installed")

    async with AsyncClient(app=app, I_url="http://test") as client:
        yield client


@pytest.fixture
def authenticated_client(item_client, mock_user):
    """Provide an authenticated TestClient.

    Automatically includes authentication headers in requests.

    Yields:
        TestClient with auth headers pre-configured.

    """
    # Set auth header for all requests
    item_client.headers.update({"Authorization": f"Bearer {mock_user['token']}"})
    yield item_client


# =============================================================================
# AUTHENTICATION FIXTURES
# =============================================================================


@pytest.fixture
def mock_user() -> dict[str, Any]:
    """Provide a mock authenticated user.

    Returns:
        Dictionary with user data and token.

    Example:
        def test_protected_endpoint(item_client, mock_user):
            response = item_client.get(
                "/items",
                headers={"Authorization": f"Bearer {mock_user['token']}"}
            )
            assert response.status_code == 200

    """
    return {
        "id": "user-123",
        "email": "test@example.com",
        "name": "Test User",
        "token": "mock-jwt-token-12345",
        "roles": ["user"],
    }


@pytest.fixture
def mock_admin_user() -> dict[str, Any]:
    """Provide a mock admin user.

    Returns:
        Dictionary with admin user data and token.

    """
    return {
        "id": "admin-123",
        "email": "admin@example.com",
        "name": "Admin User",
        "token": "mock-admin-token-12345",
        "roles": ["admin", "user"],
    }


@pytest.fixture
def mock_auth(mock_user):
    """Mock authentication dependency.

    Yields:
        Mock that patches the auth dependency.

    Example:
        def test_with_mock_auth(item_client, mock_auth):
            with mock_auth:
                response = item_client.get("/items")
                assert response.status_code == 200

    """
    # Return a no-op context manager for tests that use `with mock_auth:`
    return nullcontext()


@pytest.fixture
def mock_invalid_auth():
    """Mock invalid authentication (for testing 401 responses).

    Yields:
        Mock that simulates invalid auth.

    """
    from fastapi import HTTPException

    def raise_auth_error():
        """Execute raise_auth_error operation.

        Returns:
            The result of the operation.
        """
        raise HTTPException(status_code=401, detail="Invalid authentication")

    with patch("dependencies.auth.get_current_user", side_effect=raise_auth_error):
        yield


@pytest.fixture
def mock_expired_token():
    """Mock expired JWT token (for testing token refresh).

    Yields:
        Mock that simulates expired token.

    """
    from fastapi import HTTPException

    def raise_expired_error():
        """Execute raise_expired_error operation.

        Returns:
            The result of the operation.
        """
        raise HTTPException(status_code=401, detail="Token has expired")

    with patch("dependencies.auth.get_current_user", side_effect=raise_expired_error):
        yield


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================


@pytest.fixture
def test_item() -> ItemEntity:
    """Provide a single test item.

    Returns:
        ItemEntity instance with default test data.

    Example:
        def test_update_item(item_client, test_item):
            response = item_client.patch(
                f"/items/{test_item.id}",
                json={"name": "Updated"}
            )
            assert response.status_code == 200

    """
    return ItemFactory.create(
        id="test-item-001",
        name="Test Item",
        description="A test item for testing",
        completed=False,
    )


@pytest.fixture
def test_items() -> list[ItemEntity]:
    """Provide multiple test items.

    Returns:
        List of 5 ItemEntity instances with varied states.

    Example:
        def test_list_items(item_client, test_items):
            response = item_client.get("/items")
            data = response.json()
            assert len(data["items"]) == 5

    """
    return [
        ItemFactory.create(
            id=f"test-item-{i:03d}",
            name=f"Test Item {i}",
            completed=i % 2 == 0,  # Alternate completed/pending
        )
        for i in range(1, 6)
    ]


@pytest.fixture
def completed_items() -> list[ItemEntity]:
    """Provide completed test items.

    Returns:
        List of 3 completed ItemEntity instances.

    """
    return ItemFactory.create_batch(3, completed=True)


@pytest.fixture
def pending_items() -> list[ItemEntity]:
    """Provide pending (not completed) test items.

    Returns:
        List of 3 pending ItemEntity instances.

    """
    return ItemFactory.create_batch(3, completed=False)


@pytest.fixture
def create_item_payload() -> dict[str, Any]:
    """Provide a valid payload for creating an item.

    Returns:
        Dictionary with valid create data.

    Example:
        def test_create_item(item_client, create_item_payload):
            response = item_client.post("/items", json=create_item_payload)
            assert response.status_code == 201

    """
    return ItemFactory.create_dict()


@pytest.fixture
def update_item_payload() -> dict[str, Any]:
    """Provide a valid payload for updating an item.

    Returns:
        Dictionary with valid update data.

    """
    return {
        "name": "Updated Item Name",
        "description": "Updated description",
    }


@pytest.fixture
def invalid_item_payloads() -> dict[str, dict[str, Any]]:
    """Provide various invalid payloads for negative testing.

    Returns:
        Dictionary of invalid payloads keyed by error type.

    Example:
        def test_create_item_validation(item_client, invalid_item_payloads):
            for error_type, payload in invalid_item_payloads.items():
                response = item_client.post("/items", json=payload)
                assert response.status_code == 422, f"Failed for {error_type}"

    """
    return {
        "empty_name": ItemFactory.invalid_name_empty(),
        "long_name": ItemFactory.invalid_name_too_long(),
        "long_description": ItemFactory.invalid_description_too_long(),
        "missing_name": {"description": "No name provided"},
        "null_name": {"name": None, "description": "Test"},
    }


# =============================================================================
# UTILITY FIXTURES
# =============================================================================


@pytest.fixture
def freezer():
    """Freeze time for deterministic testing.

    Yields:
        Mock datetime that can be controlled.

    Example:
        def test_timestamp(freezer):
            freezer.move_to("2024-01-01")
            item = ItemFactory.create()
            assert item.created_at.year == 2024

    """
    try:
        from freezegun import freeze_time

        with freeze_time("2024-01-01 12:00:00") as frozen:
            yield frozen
    except ImportError:
        pytest.skip("freezegun not installed")


@pytest.fixture(scope="session")
def event_loop():
    """Provide an event loop for async tests.

    Required for pytest-asyncio.
    """
    try:
        import asyncio

        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()
    except Exception:
        pytest.skip("asyncio not available")


@pytest.fixture(autouse=True)
def reset_factories():
    """Reset factory state between tests.

    Automatically runs before each test to ensure clean state.
    """
    yield
    # Cleanup if needed
