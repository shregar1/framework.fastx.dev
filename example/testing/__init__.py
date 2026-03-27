"""FastMVC Example Testing Utilities.

Provides factories and fixtures for testing the example Item API.

Usage:
    from example.testing import ItemFactory, item_client

    def test_create_item(item_client):
        # Use factory to create test data
        data = ItemFactory.create_dict()
        response = item_client.post("/items", json=data)
        assert response.status_code == 201
"""

from example.testing.factories import ItemFactory
from example.testing.fixtures import (
    item_client,
    item_db,
    mock_auth,
    mock_user,
    test_item,
    test_items,
)

__all__ = [
    # Factory
    "ItemFactory",
    # Fixtures
    "item_client",
    "item_db",
    "mock_auth",
    "mock_user",
    "test_item",
    "test_items",
]
