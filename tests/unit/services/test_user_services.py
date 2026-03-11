"""
Tests for user services (login, logout, registration).
"""

from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

# Mock bcrypt before importing services
with patch.dict('sys.modules', {'bcrypt': MagicMock()}):
    from services.user.login import UserLoginService
    from services.user.logout import UserLogoutService
    from services.user.registration import UserRegistrationService

from constants.api_status import APIStatus
from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError


class TestUserLoginService:
    """Tests for UserLoginService."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create mock user repository."""
        repo = MagicMock()
        return repo

    @pytest.fixture
    def mock_jwt_utility(self):
        """Create mock JWT utility."""
        jwt_util = MagicMock()
        jwt_util.create_access_token.return_value = "test-jwt-token"
        return jwt_util

    @pytest.fixture
    def service(self, mock_user_repository, mock_jwt_utility):
        """Create UserLoginService instance."""
        return UserLoginService(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="LOGIN",
            user_id=1,
            user_repository=mock_user_repository,
            jwt_utility=mock_jwt_utility
        )

    @pytest.fixture
    def mock_user(self):
        """Create mock user object."""
        user = MagicMock()
        user.id = 1
        user.urn = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
        user.email = "test@example.com"
        user.password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz2Z.5bqz2rqKhG1H8rS1.qjZ.Y1234"
        user.is_logged_in = False
        user.updated_on = datetime.now()
        return user

    # Tests for initialization
    def test_initialization(self, service):
        """Test service initialization."""
        assert service._urn == "test-urn"
        assert service._user_urn == "test-user-urn"
        assert service._api_name == "LOGIN"
        assert service._user_id == 1

    def test_properties(self, service):
        """Test service properties."""
        service.urn = "new-urn"
        assert service.urn == "new-urn"

        service.user_urn = "new-user-urn"
        assert service.user_urn == "new-user-urn"

        service.api_name = "new-api"
        assert service.api_name == "new-api"

        service.user_id = 2
        assert service.user_id == 2

    # Tests for run method
    @pytest.mark.asyncio
    @patch('services.user.login.bcrypt')
    async def test_run_success(self, mock_bcrypt, service, mock_user_repository, mock_user):
        """Test successful login."""
        mock_bcrypt.checkpw.return_value = True
        mock_user_repository.retrieve_record_by_email.return_value = mock_user
        mock_user_repository.update_record.return_value = mock_user

        request = MagicMock()
        request.email = "test@example.com"
        request.password = "SecureP@ss123"

        result = await service.run(request)

        assert result.status == APIStatus.SUCCESS
        assert result.responseKey == "success_user_login"
        assert "token" in result.data

    @pytest.mark.asyncio
    async def test_run_user_not_found(self, service, mock_user_repository):
        """Test login with non-existent user."""
        mock_user_repository.retrieve_record_by_email.return_value = None

        request = MagicMock()
        request.email = "nonexistent@example.com"
        request.password = "SecureP@ss123"

        with pytest.raises(NotFoundError) as exc_info:
            await service.run(request)
        assert exc_info.value.httpStatusCode == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    @patch('services.user.login.bcrypt')
    async def test_run_wrong_password(self, mock_bcrypt, service, mock_user_repository, mock_user):
        """Test login with wrong password."""
        mock_bcrypt.checkpw.return_value = False
        mock_user_repository.retrieve_record_by_email.return_value = mock_user

        request = MagicMock()
        request.email = "test@example.com"
        request.password = "WrongP@ss123"

        with pytest.raises(BadInputError) as exc_info:
            await service.run(request)
        assert exc_info.value.httpStatusCode == HTTPStatus.BAD_REQUEST


class TestUserLogoutService:
    """Tests for UserLogoutService."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create mock user repository."""
        repo = MagicMock()
        return repo

    @pytest.fixture
    def mock_jwt_utility(self):
        """Create mock JWT utility."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_user_repository, mock_jwt_utility):
        """Create UserLogoutService instance."""
        return UserLogoutService(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="LOGOUT",
            user_id=1,
            user_repository=mock_user_repository,
            jwt_utility=mock_jwt_utility
        )

    @pytest.fixture
    def mock_user(self):
        """Create mock logged-in user."""
        user = MagicMock()
        user.id = 1
        user.urn = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
        user.is_logged_in = True
        return user

    def test_initialization(self, service):
        """Test service initialization."""
        assert service._urn == "test-urn"
        assert service._api_name == "LOGOUT"
        assert service._user_id == 1

    @pytest.mark.asyncio
    async def test_run_success(self, service, mock_user_repository, mock_user):
        """Test successful logout."""
        mock_user_repository.retrieve_record_by_id_is_logged_in.return_value = mock_user
        mock_user.is_logged_in = False
        mock_user_repository.update_record.return_value = mock_user

        result = await service.run()

        assert result.status == APIStatus.SUCCESS
        assert result.responseKey == "success_user_logout"

    @pytest.mark.asyncio
    async def test_run_user_not_logged_in(self, service, mock_user_repository):
        """Test logout when user not logged in."""
        mock_user_repository.retrieve_record_by_id_is_logged_in.return_value = None

        with pytest.raises(BadInputError) as exc_info:
            await service.run()
        assert exc_info.value.httpStatusCode == HTTPStatus.BAD_REQUEST


class TestUserRegistrationService:
    """Tests for UserRegistrationService."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create mock user repository."""
        repo = MagicMock()
        return repo

    @pytest.fixture
    def service(self, mock_user_repository):
        """Create UserRegistrationService instance."""
        return UserRegistrationService(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="REGISTRATION",
            user_id=None,
            user_repository=mock_user_repository
        )

    def test_initialization(self, service):
        """Test service initialization."""
        assert service._urn == "test-urn"
        assert service._api_name == "REGISTRATION"

    @pytest.mark.asyncio
    @patch('services.user.registration.bcrypt')
    @patch('services.user.registration.ULID')
    @patch.dict('os.environ', {'BCRYPT_SALT': '$2b$12$LQv3c1yqBWVHxkd0LHAkCO'})
    async def test_run_success(self, mock_ulid_class, mock_bcrypt, service, mock_user_repository):
        """Test successful registration."""
        mock_ulid_class.return_value = MagicMock(__str__=lambda x: "01ARZ3NDEKTSV4RRFFQ69G5FAV")
        mock_bcrypt.hashpw.return_value = b"hashed_password"
        mock_user_repository.retrieve_record_by_email.return_value = None

        created_user = MagicMock()
        created_user.email = "newuser@example.com"
        created_user.created_on = datetime.now()
        mock_user_repository.create_record.return_value = created_user

        request = MagicMock()
        request.email = "newuser@example.com"
        request.password = "SecureP@ss123"

        result = await service.run(request)

        assert result.status == APIStatus.SUCCESS
        assert result.responseKey == "success_user_register"

    @pytest.mark.asyncio
    async def test_run_email_already_exists(self, service, mock_user_repository):
        """Test registration with existing email."""
        existing_user = MagicMock()
        mock_user_repository.retrieve_record_by_email.return_value = existing_user

        request = MagicMock()
        request.email = "existing@example.com"
        request.password = "SecureP@ss123"

        with pytest.raises(BadInputError) as exc_info:
            await service.run(request)
        assert "already registered" in exc_info.value.responseMessage

