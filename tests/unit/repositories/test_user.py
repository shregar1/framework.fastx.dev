"""
Tests for UserRepository class.
"""

from unittest.mock import MagicMock

import pytest

from models.user import User
from repositories.user import UserRepository


class TestUserRepository:
    """Tests for UserRepository class."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = MagicMock()
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Create a UserRepository instance with mock session."""
        return UserRepository(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="test-api",
            session=mock_session,
            user_id="1"
        )

    # Tests for initialization
    def test_initialization(self, mock_session):
        """Test repository initialization."""
        repo = UserRepository(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="test-api",
            session=mock_session,
            user_id="1"
        )
        assert repo._urn == "test-urn"
        assert repo._user_urn == "test-user-urn"
        assert repo._api_name == "test-api"
        assert repo._session == mock_session
        assert repo._user_id == "1"

    def test_initialization_no_session_raises_error(self):
        """Test initialization without session raises error."""
        with pytest.raises(RuntimeError) as exc_info:
            UserRepository(urn="test-urn", session=None)
        assert "DB session not found" in str(exc_info.value)

    # Tests for properties
    def test_urn_property(self, repository):
        """Test urn property."""
        repository.urn = "new-urn"
        assert repository.urn == "new-urn"

    def test_user_urn_property(self, repository):
        """Test user_urn property."""
        repository.user_urn = "new-user-urn"
        assert repository.user_urn == "new-user-urn"

    def test_api_name_property(self, repository):
        """Test api_name property."""
        repository.api_name = "new-api"
        assert repository.api_name == "new-api"

    def test_user_id_property(self, repository):
        """Test user_id property."""
        repository.user_id = "2"
        assert repository.user_id == "2"

    def test_session_property(self, repository, mock_session):
        """Test session property getter."""
        assert repository.session == mock_session

    def test_session_setter_with_invalid_type(self, repository):
        """Test session setter with invalid type raises error."""
        with pytest.raises(ValueError) as exc_info:
            repository.session = "not a session"
        assert "SQLAlchemy Session" in str(exc_info.value)

    # Tests for retrieve_record_by_email_and_password
    def test_retrieve_record_by_email_and_password_found(self, repository, mock_session):
        """Test retrieving user by email and password when found."""
        mock_user = MagicMock(spec=User)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user

        result = repository.retrieve_record_by_email_and_password(
            email="test@example.com",
            password="hashed_password"
        )

        assert result == mock_user
        mock_session.query.assert_called()

    def test_retrieve_record_by_email_and_password_not_found(self, repository, mock_session):
        """Test retrieving user by email and password when not found."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        result = repository.retrieve_record_by_email_and_password(
            email="nonexistent@example.com",
            password="wrong_password"
        )

        assert result is None

    # Tests for retrieve_record_by_email
    def test_retrieve_record_by_email_found(self, repository, mock_session):
        """Test retrieving user by email when found."""
        mock_user = MagicMock(spec=User)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user

        result = repository.retrieve_record_by_email(email="test@example.com")

        assert result == mock_user

    def test_retrieve_record_by_email_not_found(self, repository, mock_session):
        """Test retrieving user by email when not found."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        result = repository.retrieve_record_by_email(email="nonexistent@example.com")

        assert result is None

    def test_retrieve_record_by_email_with_deleted(self, repository, mock_session):
        """Test retrieving deleted user by email."""
        mock_user = MagicMock(spec=User)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user

        result = repository.retrieve_record_by_email(
            email="test@example.com",
            is_deleted=True
        )

        assert result == mock_user

    # Tests for retrieve_record_by_id_and_is_logged_in
    def test_retrieve_record_by_id_and_is_logged_in(self, repository, mock_session):
        """Test retrieving users by ID and login status."""
        mock_users = [MagicMock(spec=User), MagicMock(spec=User)]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_users

        result = repository.retrieve_record_by_id_and_is_logged_in(
            id="1",
            is_logged_in=True
        )

        assert result == mock_users
        assert len(result) == 2

    def test_retrieve_record_by_id_and_is_logged_in_empty(self, repository, mock_session):
        """Test retrieving users by ID and login status when empty."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        result = repository.retrieve_record_by_id_and_is_logged_in(
            id="999",
            is_logged_in=True
        )

        assert result == []

    # Tests for retrieve_record_by_id_is_logged_in
    def test_retrieve_record_by_id_is_logged_in_found(self, repository, mock_session):
        """Test retrieving single user by ID and login status."""
        mock_user = MagicMock(spec=User)
        mock_session.query.return_value.filter.return_value.one_or_none.return_value = mock_user

        result = repository.retrieve_record_by_id_is_logged_in(
            id=1,
            is_logged_in=True
        )

        assert result == mock_user

    def test_retrieve_record_by_id_is_logged_in_not_found(self, repository, mock_session):
        """Test retrieving single user by ID when not found."""
        mock_session.query.return_value.filter.return_value.one_or_none.return_value = None

        result = repository.retrieve_record_by_id_is_logged_in(
            id=999,
            is_logged_in=True
        )

        assert result is None

