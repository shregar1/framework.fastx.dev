"""
Tests for configuration loader classes.
"""

import json
import os
import tempfile
from unittest.mock import patch


class TestDBConfiguration:
    """Tests for DBConfiguration."""

    def test_import(self):
        """Test DBConfiguration can be imported."""
        from configurations.db import DBConfiguration
        assert DBConfiguration is not None

    @patch('builtins.open')
    @patch('json.load')
    def test_get_config_returns_dto(self, mock_json_load, mock_open):
        """Test get_config returns proper DTO."""
        mock_json_load.return_value = {
            "user_name": "test",
            "password": "test123",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "connection_string": "postgresql://{user_name}:{password}@{host}:{port}/{database}"
        }

        from configurations.db import DBConfiguration
        config = DBConfiguration()
        result = config.get_config()

        assert result is not None


class TestCacheConfiguration:
    """Tests for CacheConfiguration."""

    def test_import(self):
        """Test CacheConfiguration can be imported."""
        from configurations.cache import CacheConfiguration
        assert CacheConfiguration is not None

    @patch('builtins.open')
    @patch('json.load')
    def test_get_config_returns_dto(self, mock_json_load, mock_open):
        """Test get_config returns proper DTO."""
        mock_json_load.return_value = {
            "host": "localhost",
            "port": 6379,
            "password": "test123"
        }

        from configurations.cache import CacheConfiguration
        config = CacheConfiguration()
        result = config.get_config()

        assert result is not None


class TestSecurityConfiguration:
    """Tests for SecurityConfiguration."""

    def test_import(self):
        """Test SecurityConfiguration can be imported."""
        from configurations.security import SecurityConfiguration
        assert SecurityConfiguration is not None

    def test_initialization_default_path(self):
        """Test default config path."""
        from configurations.security import SecurityConfiguration
        config = SecurityConfiguration()
        assert config.config_path == "config/security/config.json"

    def test_initialization_custom_path(self):
        """Test custom config path."""
        from configurations.security import SecurityConfiguration
        config = SecurityConfiguration(config_path="/custom/path.json")
        assert config.config_path == "/custom/path.json"

    @patch('configurations.security.logger')
    def test_get_config_returns_default_when_file_not_found(self, mock_logger):
        """Test get_config returns default when file doesn't exist."""
        from configurations.security import SecurityConfiguration
        config = SecurityConfiguration(config_path="/nonexistent/path.json")
        result = config.get_config()

        assert result is not None
        assert hasattr(result, 'security_headers')
        assert hasattr(result, 'input_validation')
        assert hasattr(result, 'authentication')

    @patch('configurations.security.logger')
    def test_get_config_with_valid_file(self, mock_logger):
        """Test get_config with valid JSON file."""
        from configurations.security import SecurityConfiguration

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "security_headers": {
                    "hsts_max_age": 31536000,
                    "hsts_include_subdomains": True,
                    "enable_csp": True,
                    "enable_hsts": True
                },
                "input_validation": {
                    "max_string_length": 1000,
                    "min_password_length": 8
                },
                "authentication": {
                    "jwt_expiry_minutes": 60,
                    "max_login_attempts": 5
                }
            }, f)
            f.flush()

            config = SecurityConfiguration(config_path=f.name)
            result = config.get_config()

            assert result is not None
            assert result.security_headers.hsts_max_age == 31536000
            assert result.authentication.jwt_expiry_minutes == 60

        os.unlink(f.name)

    @patch('configurations.security.logger')
    @patch.dict(os.environ, {"SECURITY_HSTS_MAX_AGE": "86400"})
    def test_env_override_integer(self, mock_logger):
        """Test environment variable override for integer value."""
        from configurations.security import SecurityConfiguration

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "security_headers": {
                    "hsts_max_age": 31536000,
                    "hsts_include_subdomains": True,
                    "enable_csp": True,
                    "enable_hsts": True
                },
                "input_validation": {
                    "max_string_length": 1000,
                    "min_password_length": 8
                },
                "authentication": {
                    "jwt_expiry_minutes": 60,
                    "max_login_attempts": 5
                }
            }, f)
            f.flush()

            config = SecurityConfiguration(config_path=f.name)
            result = config.get_config()

            assert result.security_headers.hsts_max_age == 86400

        os.unlink(f.name)

    @patch('configurations.security.logger')
    @patch.dict(os.environ, {"SECURITY_ENABLE_HSTS": "false"})
    def test_env_override_boolean(self, mock_logger):
        """Test environment variable override for boolean value."""
        from configurations.security import SecurityConfiguration

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "security_headers": {
                    "hsts_max_age": 31536000,
                    "hsts_include_subdomains": True,
                    "enable_csp": True,
                    "enable_hsts": True
                },
                "input_validation": {
                    "max_string_length": 1000,
                    "min_password_length": 8
                },
                "authentication": {
                    "jwt_expiry_minutes": 60,
                    "max_login_attempts": 5
                }
            }, f)
            f.flush()

            config = SecurityConfiguration(config_path=f.name)
            result = config.get_config()

            assert result.security_headers.enable_hsts is False

        os.unlink(f.name)

    @patch('configurations.security.logger')
    def test_reload_config(self, mock_logger):
        """Test reload_config clears cache and reloads."""
        from configurations.security import SecurityConfiguration

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "security_headers": {
                    "hsts_max_age": 31536000,
                    "hsts_include_subdomains": True,
                    "enable_csp": True,
                    "enable_hsts": True
                },
                "input_validation": {
                    "max_string_length": 1000,
                    "min_password_length": 8
                },
                "authentication": {
                    "jwt_expiry_minutes": 60,
                    "max_login_attempts": 5
                }
            }, f)
            f.flush()

            config = SecurityConfiguration(config_path=f.name)
            config.get_config()

            # Reload should work
            reloaded = config.reload_config()
            assert reloaded is not None

        os.unlink(f.name)

    @patch('configurations.security.logger')
    def test_get_config_caches_result(self, mock_logger):
        """Test get_config caches the result."""
        from configurations.security import SecurityConfiguration
        config = SecurityConfiguration()

        result1 = config.get_config()
        result2 = config.get_config()

        assert result1 is result2

    @patch('configurations.security.logger')
    def test_invalid_json_falls_back_to_default(self, mock_logger):
        """Test invalid JSON falls back to default config."""
        from configurations.security import SecurityConfiguration

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json {{{")
            f.flush()

            config = SecurityConfiguration(config_path=f.name)
            result = config.get_config()

            assert result is not None

        os.unlink(f.name)

