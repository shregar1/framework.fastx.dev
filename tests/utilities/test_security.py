"""Tests for :class:`utilities.security_headers.SecurityHeadersUtility`."""

from __future__ import annotations

from utilities.security_headers import SecurityHeadersUtility


class TestSecurityHeadersUtility:
    def test_init_with_context(self) -> None:
        util = SecurityHeadersUtility(urn="a", user_urn="b")
        assert util.urn == "a"
        assert util.user_urn == "b"

    def test_load_settings_from_env_returns_dto(self) -> None:
        dto = SecurityHeadersUtility.load_settings_from_env()
        assert dto.x_frame_options
        assert dto.x_content_type_options

    def test_get_middleware_config(self) -> None:
        cfg = SecurityHeadersUtility.get_middleware_config()
        assert cfg is not None
