"""Tests for :class:`utilities.datetime.DateTimeUtility`."""

from __future__ import annotations

from datetime import datetime, timezone

from utilities.datetime import DateTimeUtility


class TestDateTimeUtility:
    def test_init_default_values(self) -> None:
        util = DateTimeUtility()
        assert util.urn is None
        assert util.user_urn is None

    def test_init_with_context(self) -> None:
        util = DateTimeUtility(
            urn="test-urn",
            user_urn="user-123",
            api_name="api-test",
            user_id="user-456",
        )
        assert util.urn == "test-urn"
        assert util.user_urn == "user-123"

    def test_utc_now_timezone_aware(self) -> None:
        result = DateTimeUtility.utc_now()
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

    def test_utc_now_iso_format(self) -> None:
        s = DateTimeUtility.utc_now_iso()
        assert isinstance(s, str)
        assert "T" in s
