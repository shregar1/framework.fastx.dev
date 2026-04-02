"""Tests for :class:`utilities.system.SystemUtility`."""

from __future__ import annotations

from utilities.system import SystemUtility


class TestSystemUtility:
    """Covers the slim system helper (git discovery)."""

    def test_init_default_values(self) -> None:
        util = SystemUtility()
        assert util.urn is None
        assert util.user_urn is None

    def test_init_with_context(self) -> None:
        util = SystemUtility(urn="test", user_urn="user")
        assert util.urn == "test"
        assert util.user_urn == "user"

    def test_git_repository_folder_name(self) -> None:
        name = SystemUtility.git_repository_folder_name()
        assert name is None or isinstance(name, str)
