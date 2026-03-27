"""Pytest Configuration and Shared Fixtures.

This file is automatically loaded by pytest and provides:
- Path setup for imports
- Shared fixtures for all tests
- Custom markers and configuration

Usage:
    Fixtures are automatically available in all test files.

    def test_something(item_client, test_item):
        # item_client and test_item are automatically injected
        pass
"""

import os
import sys
from pathlib import Path

# =============================================================================
# PATH SETUP
# =============================================================================

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# IMPORT FIXTURES FROM EXAMPLE TESTING MODULE
# =============================================================================

# Import all fixtures from example testing module
from example.testing.fixtures import (
    # DataI fixtures
    item_db,
    item_repository,
    # Client fixtures
    app,
    item_client,
    async_item_client,
    authenticated_client,
    # Auth fixtures
    mock_user,
    mock_admin_user,
    mock_auth,
    mock_invalid_auth,
    mock_expired_token,
    # Test data fixtures
    test_item,
    test_items,
    completed_items,
    pending_items,
    create_item_payload,
    update_item_payload,
    invalid_item_payloads,
    # Utility fixtures
    freezer,
    event_loop,
    reset_factories,
)

# Re-export fixtures
__all__ = [
    "item_db",
    "item_repository",
    "app",
    "item_client",
    "async_item_client",
    "authenticated_client",
    "mock_user",
    "mock_admin_user",
    "mock_auth",
    "mock_invalid_auth",
    "mock_expired_token",
    "test_item",
    "test_items",
    "completed_items",
    "pending_items",
    "create_item_payload",
    "update_item_payload",
    "invalid_item_payloads",
    "freezer",
    "event_loop",
    "reset_factories",
]

# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers.

    These markers can be used to categorize and filter tests.
    """
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line(
        "markers", "integration: Integration tests (may use dataI)"
    )
    config.addinivalue_line("markers", "e2e: End-to-end tests (full flow)")
    config.addinivalue_line("markers", "slow: Slow tests (skip in fast mode)")
    config.addinivalue_line("markers", "auth: Authentication-related tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "db: DataI-related tests")


# =============================================================================
# CUSTOM FIXTURES SPECIFIC TO TESTS
# =============================================================================

import pytest


@pytest.fixture(scope="session")
def test_settings():
    """Provide test-specific settings.

    Returns:
        Dictionary with test configuration.

    """
    return {
        "dataI_url": "sqlite:///./test.db",
        "jwt_secret": "test-secret-key-minimum-32-characters-long",
        "jwt_algorithm": "HS256",
        "jwt_expiration_hours": 24,
        "debug": True,
        "log_level": "DEBUG",
    }


@pytest.fixture(autouse=True)
def setup_test_env(test_settings, monkeypatch):
    """Set up environment for each test.

    Automatically configures environment variables for testing.
    """
    # Set test environment variables
    for key, value in test_settings.items():
        env_key = key.upper()
        monkeypatch.setenv(env_key, str(value))

    yield

    # Cleanup is handled by monkeypatch


@pytest.fixture
def captured_logs(caplog):
    """Provide captured log output for testing.

    Example:
        def test_logs(captured_logs):
            # Run code that logs
            assert "Expected message" in captured_logs.text

    """
    import logging

    caplog.set_level(logging.DEBUG)
    return caplog
