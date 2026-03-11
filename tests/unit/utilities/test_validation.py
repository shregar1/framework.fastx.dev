"""
Tests for ValidationUtility and SecurityValidators classes.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from utilities.validation import SecurityValidators, ValidationUtility


class TestValidationUtility:
    """Tests for ValidationUtility class."""

    # Tests for validate_password_strength
    def test_validate_password_strength_valid(self):
        """Test valid strong password."""
        result = ValidationUtility.validate_password_strength("SecureP@ss123")
        assert result["is_valid"] is True
        assert result["issues"] == []

    def test_validate_password_strength_too_short(self):
        """Test password too short."""
        result = ValidationUtility.validate_password_strength("Sh@rt1")
        assert result["is_valid"] is False
        assert any("8 characters" in issue for issue in result["issues"])

    def test_validate_password_strength_no_lowercase(self):
        """Test password without lowercase."""
        result = ValidationUtility.validate_password_strength("NOLOWER@123")
        assert result["is_valid"] is False
        assert any("lowercase" in issue for issue in result["issues"])

    def test_validate_password_strength_no_uppercase(self):
        """Test password without uppercase."""
        result = ValidationUtility.validate_password_strength("noupper@123")
        assert result["is_valid"] is False
        assert any("uppercase" in issue for issue in result["issues"])

    def test_validate_password_strength_no_digit(self):
        """Test password without digit."""
        result = ValidationUtility.validate_password_strength("NoDigit@Password")
        assert result["is_valid"] is False
        assert any("digit" in issue for issue in result["issues"])

    def test_validate_password_strength_no_special(self):
        """Test password without special character."""
        result = ValidationUtility.validate_password_strength("NoSpecial123")
        assert result["is_valid"] is False
        assert any("special character" in issue for issue in result["issues"])

    def test_validate_password_strength_consecutive_chars(self):
        """Test password with consecutive identical characters."""
        result = ValidationUtility.validate_password_strength("Secuuure@123")
        assert result["is_valid"] is False
        assert any("consecutive" in issue for issue in result["issues"])

    def test_validate_password_strength_weak_password(self):
        """Test weak/common password."""
        result = ValidationUtility.validate_password_strength("password")
        assert result["is_valid"] is False
        assert any("common" in issue for issue in result["issues"])

    # Tests for validate_email_format
    @patch('utilities.validation.validate_email')
    def test_validate_email_format_valid(self, mock_validate_email):
        """Test valid email."""
        mock_result = MagicMock()
        mock_result.email = "user@example.com"
        mock_validate_email.return_value = mock_result

        result = ValidationUtility.validate_email_format("user@example.com")
        assert result["is_valid"] is True
        assert "normalized_email" in result

    def test_validate_email_format_invalid(self):
        """Test invalid email."""
        result = ValidationUtility.validate_email_format("invalid-email")
        assert result["is_valid"] is False
        assert "error" in result

    @patch('utilities.validation.validate_email')
    def test_validate_email_format_with_plus(self, mock_validate_email):
        """Test email with plus sign."""
        mock_result = MagicMock()
        mock_result.email = "user+tag@example.com"
        mock_validate_email.return_value = mock_result

        result = ValidationUtility.validate_email_format("user+tag@example.com")
        assert result["is_valid"] is True

    # Tests for validate_uuid_format
    def test_validate_uuid_format_valid(self):
        """Test valid UUID."""
        assert ValidationUtility.validate_uuid_format(
            "550e8400-e29b-41d4-a716-446655440000"
        ) is True

    def test_validate_uuid_format_invalid(self):
        """Test invalid UUID."""
        assert ValidationUtility.validate_uuid_format("not-a-uuid") is False

    def test_validate_uuid_format_empty(self):
        """Test empty string UUID."""
        assert ValidationUtility.validate_uuid_format("") is False

    # Tests for validate_date_range
    def test_validate_date_range_valid(self):
        """Test valid date range."""
        start = datetime.now()
        end = start + timedelta(days=30)
        result = ValidationUtility.validate_date_range(start, end)
        assert result["is_valid"] is True

    def test_validate_date_range_start_after_end(self):
        """Test start date after end date."""
        end = datetime.now()
        start = end + timedelta(days=1)
        result = ValidationUtility.validate_date_range(start, end)
        assert result["is_valid"] is False
        assert "before end date" in result["error"]

    def test_validate_date_range_exceeds_max(self):
        """Test date range exceeds maximum."""
        start = datetime.now()
        end = start + timedelta(days=400)
        result = ValidationUtility.validate_date_range(start, end, max_days=365)
        assert result["is_valid"] is False
        assert "cannot exceed" in result["error"]

    def test_validate_date_range_custom_max(self):
        """Test date range with custom max days."""
        start = datetime.now()
        end = start + timedelta(days=10)
        result = ValidationUtility.validate_date_range(start, end, max_days=30)
        assert result["is_valid"] is True

    # Tests for sanitize_string
    def test_sanitize_string_normal(self):
        """Test sanitizing normal string."""
        result = ValidationUtility.sanitize_string("  hello world  ")
        assert result == "hello world"

    def test_sanitize_string_empty(self):
        """Test sanitizing empty string."""
        result = ValidationUtility.sanitize_string("")
        assert result == ""

    def test_sanitize_string_none(self):
        """Test sanitizing None."""
        result = ValidationUtility.sanitize_string(None)
        assert result == ""

    def test_sanitize_string_max_length(self):
        """Test sanitizing string exceeding max length."""
        long_string = "a" * 2000
        result = ValidationUtility.sanitize_string(long_string, max_length=100)
        assert len(result) == 100

    def test_sanitize_string_control_chars(self):
        """Test sanitizing string with control characters."""
        result = ValidationUtility.sanitize_string("hello\x00world")
        assert "\x00" not in result

    # Tests for validate_numeric_range
    def test_validate_numeric_range_in_range(self):
        """Test value in range."""
        assert ValidationUtility.validate_numeric_range(5, 1, 10) is True

    def test_validate_numeric_range_at_min(self):
        """Test value at minimum."""
        assert ValidationUtility.validate_numeric_range(1, 1, 10) is True

    def test_validate_numeric_range_at_max(self):
        """Test value at maximum."""
        assert ValidationUtility.validate_numeric_range(10, 1, 10) is True

    def test_validate_numeric_range_below_min(self):
        """Test value below minimum."""
        assert ValidationUtility.validate_numeric_range(0, 1, 10) is False

    def test_validate_numeric_range_above_max(self):
        """Test value above maximum."""
        assert ValidationUtility.validate_numeric_range(11, 1, 10) is False

    def test_validate_numeric_range_float(self):
        """Test float values."""
        assert ValidationUtility.validate_numeric_range(5.5, 1.0, 10.0) is True

    # Tests for validate_string_length
    def test_validate_string_length_in_range(self):
        """Test string length in range."""
        assert ValidationUtility.validate_string_length("hello", 1, 10) is True

    def test_validate_string_length_at_min(self):
        """Test string length at minimum."""
        assert ValidationUtility.validate_string_length("h", 1, 10) is True

    def test_validate_string_length_at_max(self):
        """Test string length at maximum."""
        assert ValidationUtility.validate_string_length("hellohello", 1, 10) is True

    def test_validate_string_length_below_min(self):
        """Test string length below minimum."""
        assert ValidationUtility.validate_string_length("", 1, 10) is False

    def test_validate_string_length_above_max(self):
        """Test string length above maximum."""
        assert ValidationUtility.validate_string_length("hello world!", 1, 10) is False


class TestSecurityValidators:
    """Tests for SecurityValidators class."""

    # Tests for validate_sql_injection_prevention
    def test_sql_injection_safe_string(self):
        """Test safe string passes."""
        assert SecurityValidators.validate_sql_injection_prevention(
            "normal user input"
        ) is True

    def test_sql_injection_select(self):
        """Test SELECT injection detection."""
        assert SecurityValidators.validate_sql_injection_prevention(
            "SELECT * FROM users"
        ) is False

    def test_sql_injection_union(self):
        """Test UNION injection detection."""
        assert SecurityValidators.validate_sql_injection_prevention(
            "1 UNION SELECT password FROM users"
        ) is False

    def test_sql_injection_drop(self):
        """Test DROP injection detection."""
        assert SecurityValidators.validate_sql_injection_prevention(
            "DROP TABLE users"
        ) is False

    def test_sql_injection_or_equals(self):
        """Test OR 1=1 injection detection."""
        assert SecurityValidators.validate_sql_injection_prevention(
            "' OR 1=1 --"
        ) is False

    def test_sql_injection_empty(self):
        """Test empty string passes."""
        assert SecurityValidators.validate_sql_injection_prevention("") is True

    def test_sql_injection_none(self):
        """Test None passes."""
        assert SecurityValidators.validate_sql_injection_prevention(None) is True

    # Tests for validate_xss_prevention
    def test_xss_safe_string(self):
        """Test safe string passes."""
        assert SecurityValidators.validate_xss_prevention("normal text") is True

    def test_xss_script_tag(self):
        """Test script tag detection."""
        assert SecurityValidators.validate_xss_prevention(
            "<script>alert('xss')</script>"
        ) is False

    def test_xss_javascript_uri(self):
        """Test javascript: URI detection."""
        assert SecurityValidators.validate_xss_prevention(
            "javascript:alert('xss')"
        ) is False

    def test_xss_event_handler(self):
        """Test event handler detection."""
        assert SecurityValidators.validate_xss_prevention(
            '<img onerror="alert(1)">'
        ) is False

    def test_xss_iframe(self):
        """Test iframe detection."""
        assert SecurityValidators.validate_xss_prevention(
            '<iframe src="evil.com"></iframe>'
        ) is False

    def test_xss_empty(self):
        """Test empty string passes."""
        assert SecurityValidators.validate_xss_prevention("") is True

    def test_xss_none(self):
        """Test None passes."""
        assert SecurityValidators.validate_xss_prevention(None) is True

    # Tests for validate_path_traversal_prevention
    def test_path_traversal_safe_string(self):
        """Test safe string passes."""
        assert SecurityValidators.validate_path_traversal_prevention(
            "/valid/path/file.txt"
        ) is True

    def test_path_traversal_unix(self):
        """Test Unix path traversal detection."""
        assert SecurityValidators.validate_path_traversal_prevention(
            "../../../etc/passwd"
        ) is False

    def test_path_traversal_windows(self):
        """Test Windows path traversal detection."""
        assert SecurityValidators.validate_path_traversal_prevention(
            "..\\..\\windows\\system32"
        ) is False

    def test_path_traversal_url_encoded(self):
        """Test URL encoded path traversal detection."""
        assert SecurityValidators.validate_path_traversal_prevention(
            "%2e%2e%2f%2e%2e%2fetc"
        ) is False

    def test_path_traversal_empty(self):
        """Test empty string passes."""
        assert SecurityValidators.validate_path_traversal_prevention("") is True

    def test_path_traversal_none(self):
        """Test None passes."""
        assert SecurityValidators.validate_path_traversal_prevention(None) is True

