"""
Tests for Repository abstraction with filter methods.
"""

from unittest.mock import MagicMock

import pytest
from cachetools import LRUCache

from abstractions.repository import FilterOperator, IRepository


class TestFilterOperator:
    """Tests for FilterOperator constants."""

    def test_equality_operators(self):
        """Test equality operators exist."""
        assert FilterOperator.EQ == "eq"
        assert FilterOperator.NE == "ne"

    def test_comparison_operators(self):
        """Test comparison operators exist."""
        assert FilterOperator.LT == "lt"
        assert FilterOperator.LE == "le"
        assert FilterOperator.GT == "gt"
        assert FilterOperator.GE == "ge"
        assert FilterOperator.GTE == "ge"
        assert FilterOperator.LTE == "le"

    def test_collection_operators(self):
        """Test collection operators exist."""
        assert FilterOperator.IN == "in"
        assert FilterOperator.NOT_IN == "not_in"

    def test_string_operators(self):
        """Test string operators exist."""
        assert FilterOperator.LIKE == "like"
        assert FilterOperator.ILIKE == "ilike"

    def test_null_operators(self):
        """Test null operators exist."""
        assert FilterOperator.IS_NULL == "is_null"
        assert FilterOperator.IS_NOT_NULL == "is_not_null"

    def test_range_operators(self):
        """Test range operators exist."""
        assert FilterOperator.BETWEEN == "between"


class ConcreteRepository(IRepository):
    """Concrete repository for testing."""

    def __init__(self, session=None, **kwargs):
        super().__init__(**kwargs)
        self.session = session or MagicMock()


class TestIRepositoryInit:
    """Tests for IRepository initialization."""

    def test_initialization_with_all_params(self):
        """Test initialization with all parameters."""
        cache = LRUCache(maxsize=100)
        mock_model = MagicMock()
        repo = ConcreteRepository(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="test-api",
            user_id="1",
            model=mock_model,
            cache=cache,
        )
        assert repo.urn == "test-urn"
        assert repo.user_urn == "test-user-urn"
        assert repo.api_name == "test-api"
        assert repo.user_id == "1"
        assert repo.model == mock_model
        assert repo.cache == cache

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters."""
        repo = ConcreteRepository()
        assert repo.urn is None
        assert repo.user_urn is None
        assert repo.api_name is None
        assert repo.user_id is None
        assert repo.model is None
        assert repo.cache is None

    def test_property_setters(self):
        """Test all property setters."""
        repo = ConcreteRepository()
        mock_model = MagicMock()

        repo.urn = "new-urn"
        assert repo.urn == "new-urn"

        repo.user_urn = "new-user-urn"
        assert repo.user_urn == "new-user-urn"

        repo.api_name = "new-api"
        assert repo.api_name == "new-api"

        repo.user_id = "2"
        assert repo.user_id == "2"

        repo.model = mock_model
        assert repo.model == mock_model

        cache = LRUCache(maxsize=50)
        repo.cache = cache
        assert repo.cache == cache

    def test_logger_property(self):
        """Test logger property."""
        repo = ConcreteRepository(urn="test-urn")
        assert repo.logger is not None

    def test_logger_setter(self):
        """Test logger setter."""
        repo = ConcreteRepository()
        new_logger = MagicMock()
        repo.logger = new_logger
        assert repo.logger == new_logger


class TestBuildFilterCondition:
    """Tests for _build_filter_condition method."""

    def test_unsupported_operator_raises_error(self):
        """Test unsupported operator raises ValueError."""
        mock_model = MagicMock()
        mock_model.email = MagicMock()
        repo = ConcreteRepository(model=mock_model)

        with pytest.raises(ValueError, match="Unsupported operator"):
            repo._build_filter_condition("email", "unsupported_op", "value")


class TestBuildQueryFilters:
    """Tests for _build_query_filters method."""

    def test_empty_dict_filters(self):
        """Test empty dict filters returns empty list."""
        mock_model = MagicMock()
        repo = ConcreteRepository(model=mock_model)

        conditions = repo._build_query_filters({})
        assert conditions == []

    def test_empty_list_filters(self):
        """Test empty list filters returns empty list."""
        mock_model = MagicMock()
        repo = ConcreteRepository(model=mock_model)

        conditions = repo._build_query_filters([])
        assert conditions == []

    def test_invalid_filter_spec_raises_error(self):
        """Test invalid filter specification raises ValueError."""
        mock_model = MagicMock()
        repo = ConcreteRepository(model=mock_model)

        with pytest.raises(ValueError, match="Invalid filter specification"):
            repo._build_query_filters([("field",)])  # Only 1 element


class TestCreateRecord:
    """Tests for create_record method."""

    def test_create_record(self):
        """Test creating a record."""
        session = MagicMock()
        mock_model = MagicMock()
        repo = ConcreteRepository(session=session, model=mock_model)

        record = MagicMock()
        result = repo.create_record(record)

        session.add.assert_called_once_with(record)
        session.commit.assert_called_once()
        assert result == record


class TestExistsByFilter:
    """Tests for exists_by_filter method."""

    def test_exists_uses_retrieve_record_by_filter(self):
        """Test exists_by_filter calls retrieve_record_by_filter."""
        mock_model = MagicMock()
        repo = ConcreteRepository(model=mock_model)

        # Mock retrieve_record_by_filter
        repo.retrieve_record_by_filter = MagicMock(return_value={"id": 1})

        result = repo.exists_by_filter(filters={"email": "test@example.com"})

        assert result is True
        repo.retrieve_record_by_filter.assert_called_once()

    def test_exists_false_when_not_found(self):
        """Test exists_by_filter returns False when not found."""
        mock_model = MagicMock()
        repo = ConcreteRepository(model=mock_model)

        # Mock retrieve_record_by_filter to return None
        repo.retrieve_record_by_filter = MagicMock(return_value=None)

        result = repo.exists_by_filter(filters={"email": "notfound@example.com"})

        assert result is False


class TestUpdateRecord:
    """Tests for update_record method."""

    def test_update_record_not_found_raises_error(self):
        """Test updating non-existent record raises error."""
        session = MagicMock()
        mock_model = MagicMock()
        mock_model.__name__ = "MockModel"
        repo = ConcreteRepository(session=session, model=mock_model)

        # Mock retrieve_record_by_filter to return None
        repo.retrieve_record_by_filter = MagicMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            repo.update_record("999", {"name": "Updated Name"})


class TestUpdateRecordByFilter:
    """Tests for update_record_by_filter method."""

    def test_update_by_filter_not_found_returns_none(self):
        """Test updating non-existent record returns None."""
        session = MagicMock()
        mock_model = MagicMock()
        repo = ConcreteRepository(session=session, model=mock_model)

        # Mock retrieve_record_by_filter to return None
        repo.retrieve_record_by_filter = MagicMock(return_value=None)

        result = repo.update_record_by_filter(
            filters={"email": "notfound@example.com"},
            new_data={"email": "new@example.com"}
        )

        assert result is None


class TestDeleteRecordByFilter:
    """Tests for delete_record_by_filter method."""

    def test_delete_not_found_returns_false(self):
        """Test deleting non-existent record returns False."""
        session = MagicMock()
        mock_model = MagicMock()
        repo = ConcreteRepository(session=session, model=mock_model)

        # Mock retrieve_record_by_filter to return None
        repo.retrieve_record_by_filter = MagicMock(return_value=None)

        result = repo.delete_record_by_filter(filters={"id": 999})

        assert result is False
