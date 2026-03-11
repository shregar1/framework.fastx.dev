"""
Tests for Product Repository.
"""

from unittest.mock import MagicMock

import pytest

from models.product import Product
from repositories.product import ProductRepository


class TestProductRepositoryInit:
    """Tests for ProductRepository initialization."""

    def test_initialization(self):
        """Test ProductRepository can be initialized."""
        mock_session = MagicMock()
        repo = ProductRepository(session=mock_session)
        assert repo.session == mock_session

    def test_initialization_no_session(self):
        """Test ProductRepository can be initialized without session."""
        repo = ProductRepository()
        assert repo.session is None

    def test_session_setter(self):
        """Test session setter."""
        repo = ProductRepository()
        mock_session = MagicMock()
        repo.session = mock_session
        assert repo.session == mock_session

    def test_has_logger(self):
        """Test repository has logger."""
        repo = ProductRepository()
        assert hasattr(repo, 'logger')


class TestProductRepositoryRetrieve:
    """Tests for ProductRepository retrieve methods."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = MagicMock(spec=Product)
        mock_query.all.return_value = [MagicMock(spec=Product)]
        session.query.return_value = mock_query
        return session

    @pytest.fixture
    def repo(self, mock_session):
        """Create ProductRepository instance."""
        return ProductRepository(session=mock_session)

    def test_retrieve_record_by_id(self, repo, mock_session):
        """Test retrieving by ID."""
        repo.retrieve_record_by_id(1)
        mock_session.query.assert_called_with(Product)

    def test_retrieve_record_by_urn(self, repo, mock_session):
        """Test retrieving by URN."""
        repo.retrieve_record_by_urn("test-urn")
        mock_session.query.assert_called_with(Product)

    def test_retrieve_all_records(self, repo, mock_session):
        """Test retrieving all records."""
        repo.retrieve_all_records()
        mock_session.query.assert_called_with(Product)


class TestProductRepositoryCreate:
    """Tests for ProductRepository create methods."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        session = MagicMock()
        return session

    @pytest.fixture
    def repo(self, mock_session):
        """Create ProductRepository instance."""
        return ProductRepository(session=mock_session)

    def test_create_record(self, repo, mock_session):
        """Test creating a new record."""
        mock_product = MagicMock(spec=Product)

        repo.create_record(mock_product)

        mock_session.add.assert_called_once_with(mock_product)
        mock_session.commit.assert_called_once()


class TestProductRepositoryUpdate:
    """Tests for ProductRepository update methods."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return MagicMock()

    @pytest.fixture
    def repo(self, mock_session):
        """Create ProductRepository instance."""
        return ProductRepository(session=mock_session)

    def test_update_record(self, repo, mock_session):
        """Test updating a record."""
        mock_product = MagicMock(spec=Product)
        mock_product.id = 1

        # update_record takes just the record object
        repo.update_record(record=mock_product)

        mock_session.commit.assert_called()


class TestProductRepositoryDelete:
    """Tests for ProductRepository delete methods."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        session = MagicMock()
        mock_query = MagicMock()
        mock_product = MagicMock(spec=Product)
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_product
        session.query.return_value = mock_query
        return session

    @pytest.fixture
    def repo(self, mock_session):
        """Create ProductRepository instance."""
        return ProductRepository(session=mock_session)

    def test_delete_record(self, repo, mock_session):
        """Test deleting a record."""
        repo.delete_record(record_id=1, deleted_by=1)

        mock_session.commit.assert_called()

    def test_delete_record_not_found(self, repo, mock_session):
        """Test deleting non-existent record returns False."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_session.query.return_value = mock_query

        result = repo.delete_record(record_id=999, deleted_by=1)

        assert result is False
