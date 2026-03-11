"""
Tests for EnhancedBaseModel class.
"""

import pytest
from pydantic import ValidationError

from dtos.base import EnhancedBaseModel


class SampleDTO(EnhancedBaseModel):
    """Sample DTO for testing EnhancedBaseModel."""
    name: str
    description: str


class TestEnhancedBaseModel:
    """Tests for EnhancedBaseModel class."""

    # Tests for string sanitization
    def test_sanitize_strings_trims_whitespace(self):
        """Test that strings are trimmed."""
        dto = SampleDTO(name="  hello  ", description="  world  ")
        assert dto.name == "hello"
        assert dto.description == "world"

    def test_sanitize_strings_non_string_unchanged(self):
        """Test that non-string values are unchanged."""
        class IntDTO(EnhancedBaseModel):
            value: int

        dto = IntDTO(value=123)
        assert dto.value == 123

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError):
            SampleDTO(name="test", description="test", extra_field="not allowed")

    # Tests for validate_security
    def test_validate_security_clean_input(self):
        """Test security validation with clean input."""
        dto = SampleDTO(name="John", description="A normal description")
        result = dto.validate_security()
        assert result["is_valid"] is True
        assert result["issues"] == []

    def test_validate_security_sql_injection(self):
        """Test security validation detects SQL injection."""
        dto = SampleDTO(name="John", description="SELECT * FROM users")
        result = dto.validate_security()
        assert result["is_valid"] is False
        assert any("SQL injection" in issue for issue in result["issues"])

    def test_validate_security_xss(self):
        """Test security validation detects XSS."""
        dto = SampleDTO(name="John", description="<script>alert('xss')</script>")
        result = dto.validate_security()
        assert result["is_valid"] is False
        assert any("XSS" in issue for issue in result["issues"])

    def test_validate_security_path_traversal(self):
        """Test security validation detects path traversal."""
        dto = SampleDTO(name="John", description="../../../etc/passwd")
        result = dto.validate_security()
        assert result["is_valid"] is False
        assert any("path traversal" in issue for issue in result["issues"])

    def test_validate_security_multiple_issues(self):
        """Test security validation detects multiple issues."""
        class MultiFieldDTO(EnhancedBaseModel):
            field1: str
            field2: str

        dto = MultiFieldDTO(
            field1="SELECT * FROM users",
            field2="<script>alert('xss')</script>"
        )
        result = dto.validate_security()
        assert result["is_valid"] is False
        assert len(result["issues"]) >= 2

    # Tests for Config
    def test_config_validate_assignment(self):
        """Test that assignment triggers validation."""
        dto = SampleDTO(name="test", description="test")
        dto.name = "  new value  "
        assert dto.name == "new value"

    def test_config_use_enum_values(self):
        """Test that enum values are used in serialization."""
        from enum import Enum

        class Status(Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"

        class EnumDTO(EnhancedBaseModel):
            status: Status

        dto = EnumDTO(status=Status.ACTIVE)
        assert dto.model_dump()["status"] == "active"

    def test_config_json_encoder_datetime(self):
        """Test that datetime is encoded correctly."""
        from datetime import datetime

        class DateDTO(EnhancedBaseModel):
            created: datetime

        now = datetime(2024, 1, 15, 10, 30, 0)
        dto = DateDTO(created=now)
        json_output = dto.model_dump_json()
        assert "2024-01-15" in json_output

