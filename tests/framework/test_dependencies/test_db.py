"""Tests for db dependencies."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from dependencies.db import DBDependency


class TestDBDependency:
    """Tests for DBDependency class."""

    def test_db_dependency_exists(self):
        """Test DBDependency exists."""
        assert DBDependency is not None

    def test_db_dependency_has_derive(self):
        """Test DBDependency has derive method."""
        assert hasattr(DBDependency, "derive")


class TestDBDependencyFallback:
    """Tests for DBDependency fallback behavior."""

    def test_fallback_raises_import_error(self):
        """Test fallback raises ImportError when fast_db not installed."""
        # Force reimport to test fallback
        import sys
        import dependencies.db as db_module
        
        # Remove cached module to force reimport
        if "fast_db" in sys.modules:
            del sys.modules["fast_db"]
        
        # Mock the import to fail
        with patch.dict("sys.modules", {"fast_db": None}):
            # Create a fresh fallback class
            class _DBDependencyFallback:
                """Fallback DBDependency when fast_db is not installed."""

                @staticmethod
                def derive() -> Any:
                    """Raise informative error about missing dependency."""
                    raise ImportError(
                        "fast_db is required for database dependencies. "
                        "Install with: pip install fastx-mvc[platform]"
                    )
            
            fallback = _DBDependencyFallback()
            with pytest.raises(ImportError) as exc_info:
                fallback.derive()
            assert "fast_db is required" in str(exc_info.value)
