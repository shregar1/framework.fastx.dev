"""
Tests for custom error classes.
"""

from http import HTTPStatus

import pytest

from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from errors.unexpected_response_error import UnexpectedResponseError


class TestBadInputError:
    """Tests for BadInputError class."""

    def test_creation(self):
        """Test creating BadInputError."""
        error = BadInputError(
            responseMessage="Invalid email format",
            responseKey="error_invalid_email",
            httpStatusCode=HTTPStatus.BAD_REQUEST
        )
        assert error.responseMessage == "Invalid email format"
        assert error.responseKey == "error_invalid_email"
        assert error.httpStatusCode == HTTPStatus.BAD_REQUEST

    def test_is_exception(self):
        """Test BadInputError is a proper exception."""
        error = BadInputError(
            responseMessage="Test",
            responseKey="test",
            httpStatusCode=HTTPStatus.BAD_REQUEST
        )
        assert isinstance(error, BaseException)

    def test_can_be_raised(self):
        """Test BadInputError can be raised and caught."""
        with pytest.raises(BadInputError) as exc_info:
            raise BadInputError(
                responseMessage="Test error",
                responseKey="error_test",
                httpStatusCode=HTTPStatus.BAD_REQUEST
            )
        assert exc_info.value.responseMessage == "Test error"


class TestNotFoundError:
    """Tests for NotFoundError class."""

    def test_creation(self):
        """Test creating NotFoundError."""
        error = NotFoundError(
            responseMessage="User not found",
            responseKey="error_user_not_found",
            httpStatusCode=HTTPStatus.NOT_FOUND
        )
        assert error.responseMessage == "User not found"
        assert error.responseKey == "error_user_not_found"
        assert error.httpStatusCode == HTTPStatus.NOT_FOUND

    def test_is_exception(self):
        """Test NotFoundError is a proper exception."""
        error = NotFoundError(
            responseMessage="Test",
            responseKey="test",
            httpStatusCode=HTTPStatus.NOT_FOUND
        )
        assert isinstance(error, BaseException)

    def test_can_be_raised(self):
        """Test NotFoundError can be raised and caught."""
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError(
                responseMessage="Resource not found",
                responseKey="error_resource_not_found",
                httpStatusCode=HTTPStatus.NOT_FOUND
            )
        assert exc_info.value.responseMessage == "Resource not found"


class TestUnexpectedResponseError:
    """Tests for UnexpectedResponseError class."""

    def test_creation(self):
        """Test creating UnexpectedResponseError."""
        error = UnexpectedResponseError(
            responseMessage="Unexpected error occurred",
            responseKey="error_unexpected",
            httpStatusCode=HTTPStatus.INTERNAL_SERVER_ERROR
        )
        assert error.responseMessage == "Unexpected error occurred"
        assert error.responseKey == "error_unexpected"
        assert error.httpStatusCode == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_is_exception(self):
        """Test UnexpectedResponseError is a proper exception."""
        error = UnexpectedResponseError(
            responseMessage="Test",
            responseKey="test",
            httpStatusCode=HTTPStatus.INTERNAL_SERVER_ERROR
        )
        assert isinstance(error, BaseException)

    def test_can_be_raised(self):
        """Test UnexpectedResponseError can be raised and caught."""
        with pytest.raises(UnexpectedResponseError) as exc_info:
            raise UnexpectedResponseError(
                responseMessage="Service unavailable",
                responseKey="error_service",
                httpStatusCode=HTTPStatus.SERVICE_UNAVAILABLE
            )
        assert exc_info.value.responseMessage == "Service unavailable"

    def test_different_status_codes(self):
        """Test with different HTTP status codes."""
        error = UnexpectedResponseError(
            responseMessage="Bad gateway",
            responseKey="error_gateway",
            httpStatusCode=HTTPStatus.BAD_GATEWAY
        )
        assert error.httpStatusCode == HTTPStatus.BAD_GATEWAY

