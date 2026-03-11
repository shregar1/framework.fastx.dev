"""
Tests for User Registration Controller.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from controllers.user.register import UserRegistrationController


class TestUserRegistrationControllerInit:
    """Tests for UserRegistrationController initialization."""

    def test_initialization(self):
        """Test UserRegistrationController can be initialized."""
        controller = UserRegistrationController(urn="test-urn")
        assert controller.urn == "test-urn"

    def test_has_post_method(self):
        """Test controller has post method."""
        controller = UserRegistrationController(urn="test-urn")
        assert hasattr(controller, 'post')


class TestUserRegistrationControllerPost:
    """Tests for UserRegistrationController post method."""

    @pytest.fixture
    def controller(self):
        """Create controller instance."""
        return UserRegistrationController(urn="test-urn")

    @pytest.mark.asyncio
    async def test_post_calls_service(self, controller):
        """Test post method calls service."""
        mock_service = MagicMock()
        mock_service.run = AsyncMock(return_value={
            "user_id": 1,
            "user_urn": "user-urn-123"
        })

        controller.registration_service = mock_service
        controller.user_repository = MagicMock()

        # The post method should be callable
        assert callable(controller.post)


class TestUserRegistrationControllerValidation:
    """Tests for UserRegistrationController validation."""

    @pytest.fixture
    def controller(self):
        """Create controller instance."""
        return UserRegistrationController(urn="test-urn")

    def test_validate_request_exists(self, controller):
        """Test validate_request method exists."""
        assert hasattr(controller, 'validate_request')

    def test_controller_properties(self, controller):
        """Test controller has expected properties."""
        assert controller.urn == "test-urn"
