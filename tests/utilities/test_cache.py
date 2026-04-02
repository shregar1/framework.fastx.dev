"""Tests for cache utilities."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from unittest.mock import patch, MagicMock

import pytest

from utilities.cache import CacheUtility


class TestCacheUtility:
    """Test class for CacheUtility."""

    def test_init_default_values(self):
        """Test initialization with default values."""
        util = CacheUtility()
        assert util.urn is None
        assert util.user_urn is None

    def test_init_with_context(self):
        """Test initialization with context."""
        util = CacheUtility(urn="test", user_urn="user")
        assert util.urn == "test"
        assert util.user_urn == "user"

    def test_generate_key_string(self):
        """Test generating key from string."""
        key = CacheUtility.generate_key("test")
        assert isinstance(key, str)

    def test_generate_key_multiple_parts(self):
        """Test generating key from multiple parts."""
        key = CacheUtility.generate_key("users", "123", "profile")
        assert "users" in key
        assert "123" in key

    def test_generate_key_with_special_chars(self):
        """Test generating key with special characters."""
        key = CacheUtility.generate_key("user:test", "name")
        assert isinstance(key, str)

    def test_ttl_from_seconds(self):
        """Test TTL from seconds."""
        ttl = CacheUtility.ttl_from_seconds(3600)
        assert ttl == 3600

    def test_ttl_from_minutes(self):
        """Test TTL from minutes."""
        ttl = CacheUtility.ttl_from_minutes(60)
        assert ttl == 3600

    def test_ttl_from_hours(self):
        """Test TTL from hours."""
        ttl = CacheUtility.ttl_from_hours(1)
        assert ttl == 3600

    def test_ttl_from_days(self):
        """Test TTL from days."""
        ttl = CacheUtility.ttl_from_days(1)
        assert ttl == 86400

    def test_is_cacheable_primitive(self):
        """Test primitive types are cacheable."""
        assert CacheUtility.is_cacheable("string") is True
        assert CacheUtility.is_cacheable(123) is True
        assert CacheUtility.is_cacheable(12.34) is True

    def test_is_cacheable_collection(self):
        """Test collections are cacheable."""
        assert CacheUtility.is_cacheable([1, 2, 3]) is True
        assert CacheUtility.is_cacheable({"key": "value"}) is True

    def test_is_cacheable_none(self):
        """Test None is not cacheable."""
        assert CacheUtility.is_cacheable(None) is False

    def test_serialize_value_dict(self):
        """Test serializing dict."""
        value = {"key": "value"}
        serialized = CacheUtility.serialize_value(value)
        assert isinstance(serialized, str)

    def test_serialize_value_list(self):
        """Test serializing list."""
        value = [1, 2, 3]
        serialized = CacheUtility.serialize_value(value)
        assert isinstance(serialized, str)

    def test_deserialize_value_dict(self):
        """Test deserializing to dict."""
        value = {"key": "value"}
        serialized = CacheUtility.serialize_value(value)
        deserialized = CacheUtility.deserialize_value(serialized)
        assert deserialized == value

    def test_deserialize_value_list(self):
        """Test deserializing to list."""
        value = [1, 2, 3]
        serialized = CacheUtility.serialize_value(value)
        deserialized = CacheUtility.deserialize_value(serialized)
        assert deserialized == value

    def test_compute_size_string(self):
        """Test computing size of string."""
        size = CacheUtility.compute_size("hello")
        assert size > 0

    def test_compute_size_dict(self):
        """Test computing size of dict."""
        size = CacheUtility.compute_size({"key": "value"})
        assert size > 0

    def test_is_oversized_small(self):
        """Test small value is not oversized."""
        assert CacheUtility.is_oversized("small", max_size=1024) is False

    def test_is_oversized_large(self):
        """Test large value is oversized."""
        large_value = "x" * 10000
        assert CacheUtility.is_oversized(large_value, max_size=1024) is True

    def test_pattern_match_exact(self):
        """Test exact pattern match."""
        assert CacheUtility.pattern_match("user:123", "user:123") is True

    def test_pattern_match_wildcard(self):
        """Test wildcard pattern match."""
        assert CacheUtility.pattern_match("user:123", "user:*") is True

    def test_pattern_match_no_match(self):
        """Test pattern no match."""
        assert CacheUtility.pattern_match("post:456", "user:*") is False

    def test_extract_tags_from_key(self):
        """Test extracting tags from key."""
        tags = CacheUtility.extract_tags("user:123:profile")
        assert "user" in tags

    def test_invalidate_by_tag(self):
        """Test invalidating by tag."""
        keys = ["user:123", "user:456", "post:789"]
        to_invalidate = CacheUtility.invalidate_by_tag(keys, "user")
        assert len(to_invalidate) == 2

    def test_get_stats_empty(self):
        """Test stats for empty cache."""
        stats = CacheUtility.get_stats({})
        assert stats["count"] == 0

    def test_get_stats_with_data(self):
        """Test stats with data."""
        cache = {"key1": "value1", "key2": "value2"}
        stats = CacheUtility.get_stats(cache)
        assert stats["count"] == 2


class TestCacheUtilityProperties:
    """Test properties."""

    def test_urn_property(self):
        """Test urn property."""
        util = CacheUtility()
        util.urn = "test"
        assert util.urn == "test"

    def test_user_urn_property(self):
        """Test user_urn property."""
        util = CacheUtility()
        util.user_urn = "user"
        assert util.user_urn == "user"


class TestCacheUtilityEdgeCases:
    """Test edge cases."""

    def test_generate_key_empty(self):
        """Test generating key with empty parts."""
        key = CacheUtility.generate_key()
        assert key == ""

    def test_generate_key_none(self):
        """Test generating key with None."""
        key = CacheUtility.generate_key(None)
        assert "None" in key

    def test_ttl_zero(self):
        """Test TTL of zero."""
        assert CacheUtility.ttl_from_seconds(0) == 0

    def test_ttl_negative(self):
        """Test negative TTL."""
        assert CacheUtility.ttl_from_seconds(-1) == -1

    def test_serialize_none(self):
        """Test serializing None."""
        serialized = CacheUtility.serialize_value(None)
        assert serialized == "null"

    def test_deserialize_none(self):
        """Test deserializing None."""
        deserialized = CacheUtility.deserialize_value("null")
        assert deserialized is None

    def test_compute_size_none(self):
        """Test computing size of None."""
        size = CacheUtility.compute_size(None)
        assert size == 0

    def test_pattern_match_empty(self):
        """Test pattern match with empty strings."""
        assert CacheUtility.pattern_match("", "") is True

    def test_invalidate_by_tag_empty(self):
        """Test invalidating empty list."""
        result = CacheUtility.invalidate_by_tag([], "tag")
        assert result == []
