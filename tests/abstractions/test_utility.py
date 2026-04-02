"""Tests for utility abstractions."""

from __future__ import annotations

from typing import Any, Optional
from unittest.mock import patch, MagicMock

import pytest

from abstractions.utility import IUtility


class ConcreteUtility(IUtility):
    """Concrete implementation for testing."""

    def do_something(self) -> str:
        return "done"


class TestIUtility:
    """Test class for IUtility."""

    def test_base_can_be_instantiated(self) -> None:
        """IUtility has no abstract methods; the base class is instantiable."""
        util = IUtility()
        assert util.urn is None

    def test_concrete_can_be_instantiated(self):
        """Test concrete implementation can be instantiated."""
        util = ConcreteUtility()
        assert isinstance(util, IUtility)

    def test_init_default_values(self):
        """Test initialization with default values."""
        util = ConcreteUtility()
        assert util._urn is None
        assert util._user_urn is None
        assert util._api_name is None
        assert util._user_id is None
        assert util._logger is not None

    def test_init_with_values(self):
        """Test initialization with provided values."""
        util = ConcreteUtility(
            urn="test-urn",
            user_urn="user-123",
            api_name="api-test",
            user_id="user-456"
        )
        assert util._urn == "test-urn"
        assert util._user_urn == "user-123"
        assert util._api_name == "api-test"
        assert util._user_id == "user-456"

    def test_urn_property_getter(self):
        """Test urn getter."""
        util = ConcreteUtility(urn="test")
        assert util.urn == "test"

    def test_urn_property_setter(self):
        """Test urn setter."""
        util = ConcreteUtility()
        util.urn = "new-urn"
        assert util.urn == "new-urn"
        assert util._urn == "new-urn"

    def test_user_urn_property_getter(self):
        """Test user_urn getter."""
        util = ConcreteUtility(user_urn="user-test")
        assert util.user_urn == "user-test"

    def test_user_urn_property_setter(self):
        """Test user_urn setter."""
        util = ConcreteUtility()
        util.user_urn = "new-user"
        assert util.user_urn == "new-user"

    def test_api_name_property_getter(self):
        """Test api_name getter."""
        util = ConcreteUtility(api_name="api-test")
        assert util.api_name == "api-test"

    def test_api_name_property_setter(self):
        """Test api_name setter."""
        util = ConcreteUtility()
        util.api_name = "new-api"
        assert util.api_name == "new-api"

    def test_user_id_property_getter(self):
        """Test user_id getter."""
        util = ConcreteUtility(user_id="id-test")
        assert util.user_id == "id-test"

    def test_user_id_property_setter(self):
        """Test user_id setter."""
        util = ConcreteUtility()
        util.user_id = "new-id"
        assert util.user_id == "new-id"

    def test_logger_property_getter(self):
        """Test logger getter."""
        util = ConcreteUtility()
        assert util.logger is not None

    def test_logger_property_setter(self):
        """Test logger setter."""
        util = ConcreteUtility()
        new_logger = MagicMock()
        util.logger = new_logger
        assert util.logger == new_logger

    def test_positional_context_parameters(self) -> None:
        """First positional args map to ``urn`` and ``user_urn`` (see ``IUtility.__init__``)."""
        util = ConcreteUtility("arg1", "arg2")
        assert util.urn == "arg1"
        assert util.user_urn == "arg2"

    def test_unknown_kwargs_not_consumed_by_mro(self) -> None:
        """Extra kwargs are forwarded to ``object.__init__`` and raise."""
        with pytest.raises(TypeError):
            ConcreteUtility(urn="test", extra_param1="value1")

    def test_inheritance_chain(self):
        """Test inheritance chain."""
        util = ConcreteUtility()
        assert isinstance(util, IUtility)

    def test_context_tracking(self):
        """Test context tracking works."""
        util = ConcreteUtility(urn="urn1", user_urn="user1")
        util.urn = "urn2"
        util.user_urn = "user2"
        assert util.urn == "urn2"
        assert util.user_urn == "user2"

    def test_multiple_instances_independent(self):
        """Test multiple instances are independent."""
        util1 = ConcreteUtility(urn="urn1")
        util2 = ConcreteUtility(urn="urn2")
        assert util1.urn == "urn1"
        assert util2.urn == "urn2"
        util1.urn = "new-urn"
        assert util1.urn == "new-urn"
        assert util2.urn == "urn2"


class TestIUtilityEdgeCases:
    """Test edge cases."""

    def test_empty_string_urn(self):
        """Test empty string urn."""
        util = ConcreteUtility(urn="")
        assert util.urn == ""

    def test_none_urn(self):
        """Test None urn."""
        util = ConcreteUtility(urn=None)
        assert util.urn is None

    def test_very_long_urn(self):
        """Test very long urn."""
        long_urn = "x" * 10000
        util = ConcreteUtility(urn=long_urn)
        assert util.urn == long_urn

    def test_unicode_values(self):
        """Test unicode in properties."""
        util = ConcreteUtility(
            urn="urn-测试",
            user_urn="用户-123",
            api_name="api-测试"
        )
        assert util.urn == "urn-测试"
        assert util.user_urn == "用户-123"
        assert util.api_name == "api-测试"

    def test_special_characters(self):
        """Test special characters in values."""
        special = "test<>!@#$%^&*()_+-=[]{}|;':\",./<>?"
        util = ConcreteUtility(
            urn=special,
            user_urn=special,
            api_name=special
        )
        assert util.urn == special


class TestIUtilityWithKwargs:
    """Test IUtility with various kwargs."""

    def test_kwargs_override(self):
        """Test kwargs properly override defaults."""
        util = ConcreteUtility(
            urn="initial",
            user_urn="initial-user"
        )
        util.urn = "updated"
        util.user_urn = "updated-user"
        assert util.urn == "updated"
        assert util.user_urn == "updated-user"
