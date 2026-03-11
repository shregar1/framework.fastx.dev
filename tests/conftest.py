"""
Pytest Configuration and Fixtures.

This module provides shared fixtures and configuration for all tests
in the FastMVC test suite.
"""

import os
import sys
from datetime import datetime
from unittest.mock import MagicMock

import pytest

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock environment variables before importing modules that use them
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("BCRYPT_SALT", "$2b$12$LQv3c1yqBWVHxkd0LHAkCO")
os.environ.setdefault("APP_NAME", "FastMVC-Test")
os.environ.setdefault("RATE_LIMIT_REQUESTS_PER_MINUTE", "60")
os.environ.setdefault("RATE_LIMIT_REQUESTS_PER_HOUR", "1000")
os.environ.setdefault("RATE_LIMIT_WINDOW_SECONDS", "60")
os.environ.setdefault("RATE_LIMIT_BURST_LIMIT", "10")


@pytest.fixture
def sample_user_data():
    """Provide sample user data for tests."""
    return {
        "id": 1,
        "urn": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "email": "test@example.com",
        "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz2Z.5bqz2rqKhG1H8rS1.qjZ.Y1234",
        "is_deleted": False,
        "is_logged_in": False,
        "created_on": datetime.now(),
        "created_by": 1,
        "updated_on": None,
        "updated_by": None,
        "last_login": None,
    }


@pytest.fixture
def valid_uuid():
    """Provide a valid UUID for tests."""
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock()
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.filter.return_value.all.return_value = []
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    return session


@pytest.fixture
def mock_redis_session():
    """Create a mock Redis session."""
    redis = MagicMock()
    redis.get.return_value = None
    redis.set.return_value = True
    redis.delete.return_value = True
    redis.expire.return_value = True
    return redis


@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = MagicMock()
    user.id = 1
    user.urn = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    user.email = "test@example.com"
    user.password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz2Z.5bqz2rqKhG1H8rS1.qjZ.Y1234"
    user.is_deleted = False
    user.is_logged_in = True
    user.created_on = datetime.now()
    user.created_by = 1
    user.updated_on = datetime.now()
    user.last_login = datetime.now()
    return user


@pytest.fixture
def mock_request():
    """Create a mock FastAPI request object."""
    request = MagicMock()
    request.state = MagicMock()
    request.state.urn = "test-urn-123"
    request.state.user_id = 1
    request.state.user_urn = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    request.url.path = "/user/login"
    request.method = "POST"
    request.headers = {"authorization": "Bearer test-token"}
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    return request


@pytest.fixture
def valid_password():
    """Provide a valid password that meets all requirements."""
    return "SecureP@ss123"


@pytest.fixture
def valid_email():
    """Provide a valid email address."""
    return "user@example.com"


@pytest.fixture
def test_urn():
    """Provide a test URN."""
    return "01ARZ3NDEKTSV4RRFFQ69G5FAV"


@pytest.fixture
def jwt_payload():
    """Provide a sample JWT payload."""
    return {
        "user_id": 1,
        "user_urn": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "user_email": "test@example.com",
        "last_login": str(datetime.now()),
    }


# Async fixtures for async tests
@pytest.fixture
def mock_async_call_next():
    """Create a mock async call_next function."""
    async def call_next(request):
        response = MagicMock()
        response.headers = {}
        return response
    return call_next

