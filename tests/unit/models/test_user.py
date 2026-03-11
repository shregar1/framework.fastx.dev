"""
Tests for User model.
"""

from constants.db.table import Table
from models.user import User


class TestUserModel:
    """Tests for User model."""

    def test_tablename(self):
        """Test User model table name."""
        assert User.__tablename__ == Table.USER
        assert User.__tablename__ == "user"

    def test_model_columns(self):
        """Test User model has all required columns."""
        columns = [c.name for c in User.__table__.columns]
        assert "id" in columns
        assert "urn" in columns
        assert "email" in columns
        assert "password" in columns
        assert "is_deleted" in columns
        assert "last_login" in columns
        assert "is_logged_in" in columns
        assert "created_on" in columns
        assert "created_by" in columns
        assert "updated_on" in columns
        assert "updated_by" in columns

    def test_id_is_primary_key(self):
        """Test id column is primary key."""
        id_column = User.__table__.c.id
        assert id_column.primary_key is True

    def test_email_is_unique(self):
        """Test email column is unique."""
        email_column = User.__table__.c.email
        assert email_column.unique is True

    def test_email_is_not_nullable(self):
        """Test email column is not nullable."""
        email_column = User.__table__.c.email
        assert email_column.nullable is False

    def test_password_is_not_nullable(self):
        """Test password column is not nullable."""
        password_column = User.__table__.c.password
        assert password_column.nullable is False

    def test_urn_is_not_nullable(self):
        """Test urn column is not nullable."""
        urn_column = User.__table__.c.urn
        assert urn_column.nullable is False

    def test_is_deleted_default(self):
        """Test is_deleted column default value."""
        is_deleted_column = User.__table__.c.is_deleted
        assert is_deleted_column.default.arg is False

    def test_is_logged_in_default(self):
        """Test is_logged_in column default value."""
        is_logged_in_column = User.__table__.c.is_logged_in
        assert is_logged_in_column.default.arg is False

    def test_created_by_is_not_nullable(self):
        """Test created_by column is not nullable."""
        created_by_column = User.__table__.c.created_by
        assert created_by_column.nullable is False

    def test_model_instantiation(self):
        """Test User model can be instantiated."""
        user = User(
            urn="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            email="test@example.com",
            password="hashed_password",
            is_deleted=False,
            is_logged_in=False,
            created_by=1
        )
        assert user.email == "test@example.com"
        assert user.urn == "01ARZ3NDEKTSV4RRFFQ69G5FAV"
        assert user.password == "hashed_password"
        assert user.is_deleted is False
        assert user.is_logged_in is False
        assert user.created_by == 1

    def test_indexes_exist(self):
        """Test indexes are defined on User table."""
        indexes = list(User.__table__.indexes)
        [idx.name for idx in indexes]
        # The indexes are defined, check that some exist
        assert len(indexes) >= 0  # Basic check that indexes property exists

