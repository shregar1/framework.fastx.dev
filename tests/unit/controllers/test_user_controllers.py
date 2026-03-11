"""
Tests for user controllers.
"""

# Mock bcrypt before importing controllers that might depend on it
import sys
from unittest.mock import MagicMock

import pytest

sys.modules['bcrypt'] = MagicMock()

from constants.api_lk import APILK
from controllers.user.login import UserLoginController
from controllers.user.logout import UserLogoutController
from controllers.user.register import UserRegistrationController


class TestUserLoginController:
    """Tests for UserLoginController."""

    @pytest.fixture
    def controller(self):
        """Create UserLoginController instance."""
        return UserLoginController(urn="test-urn")

    def test_initialization(self, controller):
        """Test controller initialization."""
        assert controller._urn == "test-urn"
        assert controller._api_name == APILK.LOGIN

    def test_urn_property(self, controller):
        """Test urn property getter and setter."""
        controller.urn = "new-urn"
        assert controller.urn == "new-urn"

    def test_user_urn_property(self, controller):
        """Test user_urn property getter and setter."""
        controller.user_urn = "user-urn"
        assert controller.user_urn == "user-urn"

    def test_api_name_property(self, controller):
        """Test api_name property getter and setter."""
        assert controller.api_name == APILK.LOGIN
        controller.api_name = "NEW_API"
        assert controller.api_name == "NEW_API"

    def test_user_id_property(self, controller):
        """Test user_id property getter and setter."""
        controller.user_id = 123
        assert controller.user_id == 123

    @pytest.mark.asyncio
    async def test_validate_request(self, controller):
        """Test validate_request sets context."""
        await controller.validate_request(
            urn="new-urn",
            user_urn="user-urn",
            request_payload={},
            request_headers={},
            api_name="LOGIN",
            user_id="1"
        )
        assert controller.urn == "new-urn"
        assert controller.api_name == "LOGIN"


class TestUserLogoutController:
    """Tests for UserLogoutController."""

    @pytest.fixture
    def controller(self):
        """Create UserLogoutController instance."""
        return UserLogoutController(urn="test-urn")

    def test_initialization(self, controller):
        """Test controller initialization."""
        assert controller._urn == "test-urn"
        assert controller._api_name == APILK.LOGOUT

    def test_urn_property(self, controller):
        """Test urn property getter and setter."""
        controller.urn = "new-urn"
        assert controller.urn == "new-urn"


class TestUserRegistrationController:
    """Tests for UserRegistrationController."""

    @pytest.fixture
    def controller(self):
        """Create UserRegistrationController instance."""
        return UserRegistrationController(urn="test-urn")

    def test_initialization(self, controller):
        """Test controller initialization."""
        assert controller._urn == "test-urn"
        assert controller._api_name == APILK.REGISTRATION

    def test_urn_property(self, controller):
        """Test urn property getter and setter."""
        controller.urn = "new-urn"
        assert controller.urn == "new-urn"
