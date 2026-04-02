"""Tests for :class:`utilities.auth.AuthUtility`."""

from __future__ import annotations

import base64

from utilities.auth import AuthUtility


class TestAuthUtility:
    def test_init_default_values(self) -> None:
        util = AuthUtility()
        assert util.urn is None
        assert util.user_urn is None

    def test_init_with_context(self) -> None:
        util = AuthUtility(urn="test", user_urn="user")
        assert util.urn == "test"
        assert util.user_urn == "user"

    def test_parse_basic_authorization_valid(self) -> None:
        raw = base64.b64encode(b"user:secret").decode("ascii")
        parsed = AuthUtility.parse_basic_authorization(f"Basic {raw}")
        assert parsed == ("user", "secret")

    def test_parse_basic_authorization_invalid(self) -> None:
        assert AuthUtility.parse_basic_authorization(None) is None
        assert AuthUtility.parse_basic_authorization("Bearer x") is None
        assert AuthUtility.parse_basic_authorization("Basic !!!") is None

    def test_constant_time_compare_equal(self) -> None:
        assert AuthUtility.constant_time_compare("hello", "hello") is True

    def test_constant_time_compare_different(self) -> None:
        assert AuthUtility.constant_time_compare("hello", "world") is False

    def test_constant_time_compare_different_lengths(self) -> None:
        assert AuthUtility.constant_time_compare("hello", "hello world") is False

    def test_constant_time_compare_empty_strings(self) -> None:
        assert AuthUtility.constant_time_compare("", "") is True


class TestAuthUtilityProperties:
    def test_urn_property(self) -> None:
        util = AuthUtility()
        util.urn = "test"
        assert util.urn == "test"

    def test_logger_access(self) -> None:
        util = AuthUtility()
        assert util.logger is not None
