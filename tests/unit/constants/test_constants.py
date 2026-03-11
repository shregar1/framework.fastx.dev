"""
Tests for constants classes.
"""

import re

from constants.api_lk import APILK
from constants.api_status import APIStatus
from constants.db.table import Table
from constants.default import Default
from constants.payload_type import RequestPayloadType, ResponsePayloadType
from constants.regular_expression import RegularExpression


class TestAPIStatus:
    """Tests for APIStatus constants."""

    def test_success_value(self):
        """Test SUCCESS constant value."""
        assert APIStatus.SUCCESS == "SUCCESS"

    def test_failed_value(self):
        """Test FAILED constant value."""
        assert APIStatus.FAILED == "FAILED"

    def test_pending_value(self):
        """Test PENDING constant value."""
        assert APIStatus.PENDING == "PENDING"

    def test_all_values_are_strings(self):
        """Test all status values are strings."""
        assert isinstance(APIStatus.SUCCESS, str)
        assert isinstance(APIStatus.FAILED, str)
        assert isinstance(APIStatus.PENDING, str)


class TestAPILK:
    """Tests for APILK constants."""

    def test_login_value(self):
        """Test LOGIN constant value."""
        assert APILK.LOGIN == "LOGIN"

    def test_registration_value(self):
        """Test REGISTRATION constant value."""
        assert APILK.REGISTRATION == "REGISTRATION"

    def test_logout_value(self):
        """Test LOGOUT constant value."""
        assert APILK.LOGOUT == "LOGOUT"


class TestDefault:
    """Tests for Default constants."""

    def test_access_token_expire_minutes(self):
        """Test ACCESS_TOKEN_EXPIRE_MINUTES value."""
        assert Default.ACCESS_TOKEN_EXPIRE_MINUTES == 1440
        assert isinstance(Default.ACCESS_TOKEN_EXPIRE_MINUTES, int)

    def test_rate_limit_max_requests(self):
        """Test RATE_LIMIT_MAX_REQUESTS value."""
        assert Default.RATE_LIMIT_MAX_REQUESTS == 2
        assert isinstance(Default.RATE_LIMIT_MAX_REQUESTS, int)

    def test_rate_limit_window_seconds(self):
        """Test RATE_LIMIT_WINDOW_SECONDS value."""
        assert Default.RATE_LIMIT_WINDOW_SECONDS == 60

    def test_rate_limit_requests_per_minute(self):
        """Test RATE_LIMIT_REQUESTS_PER_MINUTE value."""
        assert Default.RATE_LIMIT_REQUESTS_PER_MINUTE == 60

    def test_rate_limit_requests_per_hour(self):
        """Test RATE_LIMIT_REQUESTS_PER_HOUR value."""
        assert Default.RATE_LIMIT_REQUESTS_PER_HOUR == 1000

    def test_rate_limit_burst_limit(self):
        """Test RATE_LIMIT_BURST_LIMIT value."""
        assert Default.RATE_LIMIT_BURST_LIMIT == 10

    def test_security_configuration_structure(self):
        """Test SECURITY_CONFIGURATION structure."""
        config = Default.SECURITY_CONFIGURATION
        assert "rate_limiting" in config
        assert "security_headers" in config
        assert "input_validation" in config
        assert "authentication" in config
        assert "cors" in config

    def test_security_configuration_rate_limiting(self):
        """Test rate_limiting section of security configuration."""
        config = Default.SECURITY_CONFIGURATION["rate_limiting"]
        assert config["requests_per_minute"] == 60
        assert config["requests_per_hour"] == 1000
        assert config["enable_sliding_window"] is True

    def test_security_configuration_authentication(self):
        """Test authentication section of security configuration."""
        config = Default.SECURITY_CONFIGURATION["authentication"]
        assert "jwt_expiry_minutes" in config
        assert "max_login_attempts" in config
        assert "lockout_duration_minutes" in config


class TestPayloadTypes:
    """Tests for payload type constants."""

    def test_request_json(self):
        """Test RequestPayloadType JSON value."""
        assert RequestPayloadType.JSON == "json"

    def test_request_form(self):
        """Test RequestPayloadType FORM value."""
        assert RequestPayloadType.FORM == "form"

    def test_request_files(self):
        """Test RequestPayloadType FILES value."""
        assert RequestPayloadType.FILES == "files"

    def test_request_query(self):
        """Test RequestPayloadType QUERY value."""
        assert RequestPayloadType.QUERY == "query"

    def test_response_json(self):
        """Test ResponsePayloadType JSON value."""
        assert ResponsePayloadType.JSON == "json"

    def test_response_text(self):
        """Test ResponsePayloadType TEXT value."""
        assert ResponsePayloadType.TEXT == "text"

    def test_response_content(self):
        """Test ResponsePayloadType CONTENT value."""
        assert ResponsePayloadType.CONTENT == "content"


class TestRegularExpression:
    """Tests for RegularExpression patterns."""

    def test_dd_mm_yyyy_pattern(self):
        """Test DD/MM/YYYY date pattern."""
        pattern = RegularExpression.DD_MM_YYYY
        assert re.search(pattern, "01/12/2024") is not None
        assert re.search(pattern, "31/01/2025") is not None

    def test_password_pattern_valid(self):
        """Test password pattern matches valid password."""
        pattern = RegularExpression.PASSWORD_PATTERN
        assert pattern.match("SecureP@ss123") is not None

    def test_password_pattern_invalid(self):
        """Test password pattern rejects weak password."""
        pattern = RegularExpression.PASSWORD_PATTERN
        assert pattern.match("weak") is None
        assert pattern.match("nouppercase@123") is None

    def test_email_pattern_valid(self):
        """Test email pattern matches valid email."""
        pattern = RegularExpression.EMAIL_PATTERN
        assert pattern.match("user@example.com") is not None
        assert pattern.match("user.name@sub.example.com") is not None

    def test_email_pattern_invalid(self):
        """Test email pattern rejects invalid email."""
        pattern = RegularExpression.EMAIL_PATTERN
        assert pattern.match("invalid-email") is None
        assert pattern.match("no@domain") is None

    def test_phone_pattern_valid(self):
        """Test phone pattern matches valid phone."""
        pattern = RegularExpression.PHONE_PATTERN
        assert pattern.match("+14155552671") is not None
        assert pattern.match("4155552671") is not None

    def test_alphanumeric_pattern_valid(self):
        """Test alphanumeric pattern matches valid string."""
        pattern = RegularExpression.ALPHANUMERIC_PATTERN
        assert pattern.match("Hello World") is not None
        assert pattern.match("test-item_1") is not None

    def test_alphanumeric_pattern_invalid(self):
        """Test alphanumeric pattern rejects special chars."""
        pattern = RegularExpression.ALPHANUMERIC_PATTERN
        assert pattern.match("test@item") is None

    def test_sql_injection_patterns(self):
        """Test SQL injection patterns list exists."""
        patterns = RegularExpression.DANGEROUS_SQL_INJECTION_PATTERNS
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_xss_patterns(self):
        """Test XSS patterns list exists."""
        patterns = RegularExpression.DANGEROUS_XSS_PATTERNS
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_path_traversal_patterns(self):
        """Test path traversal patterns list exists."""
        patterns = RegularExpression.DANGEROUS_PATH_TRAVERSAL_PATTERNS
        assert isinstance(patterns, list)
        assert len(patterns) > 0


class TestTable:
    """Tests for Table constants."""

    def test_user_table_name(self):
        """Test USER table name constant."""
        assert Table.USER == "user"
        assert isinstance(Table.USER, str)

