"""Tests for error abstractions."""

from __future__ import annotations

from typing import Any, Dict

from unittest.mock import MagicMock

import pytest

from abstractions.error import IError


class ConcreteError(IError):
    """Concrete implementation for testing."""

    def __init__(self, message: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._message = message

    def __str__(self) -> str:
        return self._message

    def to_dict(self) -> Dict[str, Any]:
        return {"error": "test", "message": str(self)}


class TestIError:
    """Test class for IError."""

    def test_base_can_be_instantiated(self) -> None:
        """IError is a concrete Exception base with context; it may be constructed directly."""
        err = IError(urn="u1")
        assert err.urn == "u1"

    def test_concrete_can_be_instantiated(self):
        """Test concrete implementation can be instantiated."""
        error = ConcreteError("test message")
        assert isinstance(error, IError)
        assert isinstance(error, Exception)

    def test_init_with_message(self):
        """Test initialization with message."""
        error = ConcreteError("test message")
        assert str(error) == "test message"

    def test_init_with_context(self):
        """Test initialization with context."""
        error = ConcreteError(
            "test",
            urn="error-urn",
            user_urn="user-123",
            api_name="api-test",
            user_id="user-456"
        )
        assert error._urn == "error-urn"
        assert error._user_urn == "user-123"

    def test_urn_property_getter(self):
        """Test urn getter."""
        error = ConcreteError("test", urn="test-urn")
        assert error.urn == "test-urn"

    def test_urn_property_setter(self):
        """Test urn setter."""
        error = ConcreteError("test")
        error.urn = "new-urn"
        assert error.urn == "new-urn"

    def test_user_urn_property(self):
        """Test user_urn property."""
        error = ConcreteError("test", user_urn="user")
        assert error.user_urn == "user"

    def test_api_name_property(self):
        """Test api_name property."""
        error = ConcreteError("test", api_name="api")
        assert error.api_name == "api"

    def test_user_id_property(self):
        """Test user_id property."""
        error = ConcreteError("test", user_id="id")
        assert error.user_id == "id"

    def test_logger_property(self):
        """Test logger property."""
        error = ConcreteError("test")
        assert error.logger is not None

    def test_to_dict_method(self):
        """Test to_dict method."""
        error = ConcreteError("test message")
        result = error.to_dict()
        assert result["error"] == "test"
        assert "message" in result

    def test_error_inheritance(self):
        """Test error inherits from Exception."""
        error = ConcreteError("test")
        assert isinstance(error, Exception)
        with pytest.raises(ConcreteError):
            raise error


class TestIErrorEdgeCases:
    """Test edge cases."""

    def test_empty_message(self):
        """Test empty message."""
        error = ConcreteError("")
        assert str(error) == ""

    def test_unicode_message(self):
        """Test unicode in message."""
        error = ConcreteError("错误消息")
        assert "错误" in str(error)

    def test_long_message(self):
        """Test long message."""
        long_msg = "x" * 10000
        error = ConcreteError(long_msg)
        assert str(error) == long_msg

    def test_error_can_be_caught_as_exception(self):
        """Test error can be caught as Exception."""
        try:
            raise ConcreteError("test")
        except Exception as e:
            assert isinstance(e, ConcreteError)
