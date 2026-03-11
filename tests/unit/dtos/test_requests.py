"""
Tests for request DTOs.
"""

from unittest.mock import patch

import pytest
from pydantic import ValidationError

from dtos.requests.abstraction import IRequestDTO
from dtos.requests.user.login import UserLoginRequestDTO
from dtos.requests.user.logout import UserLogoutRequestDTO
from dtos.requests.user.registration import UserRegistrationRequestDTO


class TestIRequestDTO:
    """Tests for IRequestDTO base class."""

    class ConcreteRequestDTO(IRequestDTO):
        """Concrete implementation for testing."""
        pass

    def test_valid_reference_number(self, valid_uuid):
        """Test valid UUID reference number."""
        dto = self.ConcreteRequestDTO(reference_number=valid_uuid)
        assert dto.reference_number == valid_uuid

    def test_empty_reference_number(self):
        """Test empty reference number raises error."""
        with pytest.raises(ValidationError) as exc_info:
            self.ConcreteRequestDTO(reference_number="")
        assert "cannot be empty" in str(exc_info.value).lower()

    def test_whitespace_reference_number(self):
        """Test whitespace reference number raises error."""
        with pytest.raises(ValidationError) as exc_info:
            self.ConcreteRequestDTO(reference_number="   ")
        assert "cannot be empty" in str(exc_info.value).lower()

    def test_invalid_uuid_reference_number(self):
        """Test invalid UUID reference number raises error."""
        with pytest.raises(ValidationError) as exc_info:
            self.ConcreteRequestDTO(reference_number="not-a-uuid")
        assert "valid uuid" in str(exc_info.value).lower()


class TestUserLoginRequestDTO:
    """Tests for UserLoginRequestDTO."""

    @patch('dtos.requests.user.login.ValidationUtility.validate_email_format')
    def test_valid_login_request(self, mock_validate_email, valid_uuid, valid_password):
        """Test valid login request."""
        mock_validate_email.return_value = {
            'is_valid': True,
            'normalized_email': 'user@example.com'
        }
        dto = UserLoginRequestDTO(
            reference_number=valid_uuid,
            email="user@example.com",
            password=valid_password
        )
        assert dto.email == "user@example.com"
        assert dto.password == valid_password

    @patch('dtos.requests.user.login.ValidationUtility.validate_email_format')
    def test_email_normalization(self, mock_validate_email, valid_uuid, valid_password):
        """Test email is normalized to lowercase."""
        mock_validate_email.return_value = {
            'is_valid': True,
            'normalized_email': 'user@example.com'
        }
        dto = UserLoginRequestDTO(
            reference_number=valid_uuid,
            email="User@EXAMPLE.COM",
            password=valid_password
        )
        assert dto.email == "user@example.com"

    def test_invalid_email_format(self, valid_uuid, valid_password):
        """Test invalid email format raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserLoginRequestDTO(
                reference_number=valid_uuid,
                email="invalid-email",
                password=valid_password
            )
        assert "email" in str(exc_info.value).lower()

    @patch('dtos.requests.user.login.ValidationUtility.validate_email_format')
    def test_empty_password(self, mock_validate_email, valid_uuid):
        """Test empty password raises error."""
        mock_validate_email.return_value = {
            'is_valid': True,
            'normalized_email': 'user@example.com'
        }
        with pytest.raises(ValidationError) as exc_info:
            UserLoginRequestDTO(
                reference_number=valid_uuid,
                email="user@example.com",
                password=""
            )
        assert "password" in str(exc_info.value).lower()

    @patch('dtos.requests.user.login.ValidationUtility.validate_email_format')
    def test_weak_password(self, mock_validate_email, valid_uuid):
        """Test weak password raises error."""
        mock_validate_email.return_value = {
            'is_valid': True,
            'normalized_email': 'user@example.com'
        }
        with pytest.raises(ValidationError) as exc_info:
            UserLoginRequestDTO(
                reference_number=valid_uuid,
                email="user@example.com",
                password="weak"
            )
        assert "password" in str(exc_info.value).lower()

    @patch('dtos.requests.user.login.ValidationUtility.validate_email_format')
    def test_password_without_special_char(self, mock_validate_email, valid_uuid):
        """Test password without special character raises error."""
        mock_validate_email.return_value = {
            'is_valid': True,
            'normalized_email': 'user@example.com'
        }
        with pytest.raises(ValidationError) as exc_info:
            UserLoginRequestDTO(
                reference_number=valid_uuid,
                email="user@example.com",
                password="NoSpecial123"
            )
        assert "password" in str(exc_info.value).lower()

    @patch('dtos.requests.user.login.ValidationUtility.validate_email_format')
    def test_password_without_uppercase(self, mock_validate_email, valid_uuid):
        """Test password without uppercase raises error."""
        mock_validate_email.return_value = {
            'is_valid': True,
            'normalized_email': 'user@example.com'
        }
        with pytest.raises(ValidationError) as exc_info:
            UserLoginRequestDTO(
                reference_number=valid_uuid,
                email="user@example.com",
                password="nouppercase@123"
            )
        assert "password" in str(exc_info.value).lower()


class TestUserRegistrationRequestDTO:
    """Tests for UserRegistrationRequestDTO."""

    @patch('dtos.requests.user.registration.ValidationUtility.validate_email_format')
    def test_valid_registration_request(self, mock_validate_email, valid_uuid, valid_password):
        """Test valid registration request."""
        mock_validate_email.return_value = {
            'is_valid': True,
            'normalized_email': 'user@example.com'
        }
        dto = UserRegistrationRequestDTO(
            reference_number=valid_uuid,
            email="user@example.com",
            password=valid_password
        )
        assert dto.email == "user@example.com"
        assert dto.password == valid_password

    @patch('dtos.requests.user.registration.ValidationUtility.validate_email_format')
    def test_email_normalization(self, mock_validate_email, valid_uuid, valid_password):
        """Test email is normalized to lowercase."""
        mock_validate_email.return_value = {
            'is_valid': True,
            'normalized_email': 'newuser@example.com'
        }
        dto = UserRegistrationRequestDTO(
            reference_number=valid_uuid,
            email="NewUser@EXAMPLE.COM",
            password=valid_password
        )
        assert dto.email == "newuser@example.com"

    def test_invalid_email_format(self, valid_uuid, valid_password):
        """Test invalid email format raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegistrationRequestDTO(
                reference_number=valid_uuid,
                email="invalid-email",
                password=valid_password
            )
        assert "email" in str(exc_info.value).lower()

    @patch('dtos.requests.user.registration.ValidationUtility.validate_email_format')
    def test_empty_password(self, mock_validate_email, valid_uuid):
        """Test empty password raises error."""
        mock_validate_email.return_value = {
            'is_valid': True,
            'normalized_email': 'user@example.com'
        }
        with pytest.raises(ValidationError) as exc_info:
            UserRegistrationRequestDTO(
                reference_number=valid_uuid,
                email="user@example.com",
                password=""
            )
        assert "password" in str(exc_info.value).lower()

    @patch('dtos.requests.user.registration.ValidationUtility.validate_email_format')
    def test_password_validation(self, mock_validate_email, valid_uuid):
        """Test password strength validation."""
        mock_validate_email.return_value = {
            'is_valid': True,
            'normalized_email': 'user@example.com'
        }
        with pytest.raises(ValidationError) as exc_info:
            UserRegistrationRequestDTO(
                reference_number=valid_uuid,
                email="user@example.com",
                password="weak123"
            )
        assert "password" in str(exc_info.value).lower()


class TestUserLogoutRequestDTO:
    """Tests for UserLogoutRequestDTO."""

    def test_valid_logout_request(self, valid_uuid):
        """Test valid logout request."""
        dto = UserLogoutRequestDTO(reference_number=valid_uuid)
        assert dto.reference_number == valid_uuid

    def test_empty_reference_number(self):
        """Test empty reference number raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserLogoutRequestDTO(reference_number="")
        assert "cannot be empty" in str(exc_info.value).lower()

    def test_invalid_uuid(self):
        """Test invalid UUID raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserLogoutRequestDTO(reference_number="not-valid")
        assert "uuid" in str(exc_info.value).lower()

