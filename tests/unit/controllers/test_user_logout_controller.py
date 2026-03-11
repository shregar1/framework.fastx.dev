"""
Tests for User Logout Controller.
"""


import pytest

from controllers.user.logout import UserLogoutController


class TestUserLogoutControllerInit:
    """Tests for UserLogoutController initialization."""

    def test_initialization(self):
        """Test UserLogoutController can be initialized."""
        controller = UserLogoutController(urn="test-urn")
        assert controller.urn == "test-urn"

    def test_has_post_method(self):
        """Test controller has post method."""
        controller = UserLogoutController(urn="test-urn")
        assert hasattr(controller, 'post')


class TestUserLogoutControllerPost:
    """Tests for UserLogoutController post method."""

    @pytest.fixture
    def controller(self):
        """Create controller instance."""
        return UserLogoutController(urn="test-urn")

    def test_post_method_exists(self, controller):
        """Test post method exists."""
        assert hasattr(controller, 'post')
        assert callable(controller.post)


class TestUserLogoutControllerValidation:
    """Tests for UserLogoutController validation."""

    @pytest.fixture
    def controller(self):
        """Create controller instance."""
        return UserLogoutController(urn="test-urn")

    def test_validate_request_exists(self, controller):
        """Test validate_request method exists."""
        assert hasattr(controller, 'validate_request')
