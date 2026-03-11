"""
Tests for abstraction base classes.
"""

import pytest

from abstractions.error import IError
from abstractions.utility import IUtility


class TestIError:
    """Tests for IError base class."""

    def test_initialization_with_all_params(self):
        """Test initialization with all parameters."""
        error = IError(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="test-api",
            user_id="1"
        )
        assert error._urn == "test-urn"
        assert error._user_urn == "test-user-urn"
        assert error._api_name == "test-api"
        assert error._user_id == "1"

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters."""
        error = IError()
        assert error._urn is None
        assert error._user_urn is None
        assert error._api_name is None
        assert error._user_id is None

    def test_urn_property_getter(self):
        """Test urn property getter."""
        error = IError(urn="test-urn")
        assert error.urn == "test-urn"

    def test_urn_property_setter(self):
        """Test urn property setter."""
        error = IError()
        error.urn = "new-urn"
        assert error.urn == "new-urn"

    def test_user_urn_property(self):
        """Test user_urn property getter and setter."""
        error = IError()
        error.user_urn = "test-user-urn"
        assert error.user_urn == "test-user-urn"

    def test_api_name_property(self):
        """Test api_name property getter and setter."""
        error = IError()
        error.api_name = "test-api"
        assert error.api_name == "test-api"

    def test_user_id_property(self):
        """Test user_id property getter and setter."""
        error = IError()
        error.user_id = "1"
        assert error.user_id == "1"

    def test_logger_property(self):
        """Test logger property."""
        error = IError(urn="test-urn")
        assert error.logger is not None

    def test_logger_setter(self):
        """Test logger setter."""
        error = IError()
        new_logger = object()
        error.logger = new_logger
        assert error.logger == new_logger

    def test_is_base_exception(self):
        """Test IError is a BaseException."""
        error = IError()
        assert isinstance(error, BaseException)

    def test_can_be_raised(self):
        """Test IError can be raised."""
        with pytest.raises(IError):
            raise IError(urn="test-urn")


class TestIUtility:
    """Tests for IUtility base class."""

    class ConcreteUtility(IUtility):
        """Concrete implementation for testing."""
        pass

    def test_initialization_with_all_params(self):
        """Test initialization with all parameters."""
        utility = self.ConcreteUtility(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="test-api",
            user_id="1"
        )
        assert utility._urn == "test-urn"
        assert utility._user_urn == "test-user-urn"
        assert utility._api_name == "test-api"
        assert utility._user_id == "1"

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters."""
        utility = self.ConcreteUtility()
        assert utility._urn is None
        assert utility._user_urn is None
        assert utility._api_name is None
        assert utility._user_id is None

    def test_urn_property(self):
        """Test urn property getter and setter."""
        utility = self.ConcreteUtility()
        utility.urn = "new-urn"
        assert utility.urn == "new-urn"

    def test_user_urn_property(self):
        """Test user_urn property getter and setter."""
        utility = self.ConcreteUtility()
        utility.user_urn = "test-user-urn"
        assert utility.user_urn == "test-user-urn"

    def test_api_name_property(self):
        """Test api_name property getter and setter."""
        utility = self.ConcreteUtility()
        utility.api_name = "test-api"
        assert utility.api_name == "test-api"

    def test_user_id_property(self):
        """Test user_id property getter and setter."""
        utility = self.ConcreteUtility()
        utility.user_id = "1"
        assert utility.user_id == "1"

    def test_logger_property(self):
        """Test logger property."""
        utility = self.ConcreteUtility(urn="test-urn")
        assert utility.logger is not None

    def test_logger_setter(self):
        """Test logger setter."""
        utility = self.ConcreteUtility()
        new_logger = object()
        utility.logger = new_logger
        assert utility.logger == new_logger

