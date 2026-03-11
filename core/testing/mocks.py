"""
Mock Utilities for Testing.

Provides helpers for mocking external services and dependencies.
"""

import functools
from typing import Any, Callable, Dict, Optional, Union
from unittest.mock import AsyncMock, MagicMock, patch


class MockExternalService:
    """
    Context manager for mocking external service calls.

    Usage:
        with MockExternalService("httpx.AsyncClient.get") as mock:
            mock.return_value = Response(200, json={"data": "test"})
            result = await my_function()
    """

    def __init__(
        self,
        target: str,
        return_value: Any = None,
        side_effect: Optional[Union[Exception, Callable]] = None,
        async_mock: bool = True,
    ):
        """
        Initialize mock.

        Args:
            target: Target to mock (e.g., "module.Class.method").
            return_value: Value to return from mock.
            side_effect: Side effect (exception or function).
            async_mock: Use AsyncMock for async functions.
        """
        self._target = target
        self._return_value = return_value
        self._side_effect = side_effect
        self._async_mock = async_mock
        self._patcher = None
        self._mock = None

    def __enter__(self) -> Union[MagicMock, AsyncMock]:
        mock_class = AsyncMock if self._async_mock else MagicMock
        self._mock = mock_class(return_value=self._return_value)

        if self._side_effect:
            self._mock.side_effect = self._side_effect

        self._patcher = patch(self._target, self._mock)
        return self._patcher.__enter__()

    def __exit__(self, *args: Any) -> None:
        if self._patcher:
            self._patcher.__exit__(*args)


def mock_external(
    target: str,
    return_value: Any = None,
    side_effect: Optional[Union[Exception, Callable]] = None,
    async_mock: bool = True,
) -> Callable:
    """
    Decorator to mock external service calls.

    Usage:
        @mock_external("stripe.Charge.create", return_value={"id": "ch_123"})
        async def test_payment():
            result = await process_payment()
            assert result["charge_id"] == "ch_123"

        @mock_external("requests.get", side_effect=TimeoutError())
        async def test_timeout_handling():
            with pytest.raises(TimeoutError):
                await fetch_data()
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with MockExternalService(target, return_value, side_effect, async_mock):
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with MockExternalService(target, return_value, side_effect, async_mock):
                return func(*args, **kwargs)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(
        self,
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: str = "",
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code = status_code
        self._json_data = json_data
        self._text = text
        self.headers = headers or {}

    def json(self) -> Dict[str, Any]:
        return self._json_data or {}

    @property
    def text(self) -> str:
        return self._text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception(f"HTTP Error: {self.status_code}")


class MockRedis:
    """
    Mock Redis client for testing.

    Provides in-memory implementation of common Redis commands.
    """

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        px: Optional[int] = None,
    ) -> bool:
        self._data[key] = value
        return True

    def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                count += 1
        return count

    def exists(self, *keys: str) -> int:
        return sum(1 for key in keys if key in self._data)

    def incr(self, key: str, amount: int = 1) -> int:
        value = int(self._data.get(key, 0)) + amount
        self._data[key] = value
        return value

    def decr(self, key: str, amount: int = 1) -> int:
        return self.incr(key, -amount)

    def hset(self, name: str, key: str, value: Any) -> int:
        if name not in self._data:
            self._data[name] = {}
        self._data[name][key] = value
        return 1

    def hget(self, name: str, key: str) -> Optional[Any]:
        hash_data = self._data.get(name, {})
        return hash_data.get(key)

    def hgetall(self, name: str) -> Dict[str, Any]:
        return self._data.get(name, {})

    def lpush(self, key: str, *values: Any) -> int:
        if key not in self._data:
            self._data[key] = []
        for value in values:
            self._data[key].insert(0, value)
        return len(self._data[key])

    def rpush(self, key: str, *values: Any) -> int:
        if key not in self._data:
            self._data[key] = []
        self._data[key].extend(values)
        return len(self._data[key])

    def lpop(self, key: str) -> Optional[Any]:
        lst = self._data.get(key, [])
        if lst:
            return lst.pop(0)
        return None

    def rpop(self, key: str) -> Optional[Any]:
        lst = self._data.get(key, [])
        if lst:
            return lst.pop()
        return None

    def lrange(self, key: str, start: int, end: int) -> list:
        lst = self._data.get(key, [])
        if end == -1:
            return lst[start:]
        return lst[start:end + 1]

    def sadd(self, key: str, *values: Any) -> int:
        if key not in self._data:
            self._data[key] = set()
        before = len(self._data[key])
        self._data[key].update(values)
        return len(self._data[key]) - before

    def smembers(self, key: str) -> set:
        return self._data.get(key, set())

    def sismember(self, key: str, value: Any) -> bool:
        return value in self._data.get(key, set())

    def ping(self) -> bool:
        return True

    def flushall(self) -> None:
        self._data.clear()


class MockDatabase:
    """
    Mock database session for testing.

    Provides basic CRUD operations in memory.
    """

    def __init__(self):
        self._tables: Dict[str, Dict[str, Any]] = {}
        self._id_counter = 0

    def _get_table(self, table_name: str) -> Dict[str, Any]:
        if table_name not in self._tables:
            self._tables[table_name] = {}
        return self._tables[table_name]

    def insert(self, table: str, record: Dict[str, Any]) -> Dict[str, Any]:
        self._id_counter += 1
        record["id"] = record.get("id", self._id_counter)
        table_data = self._get_table(table)
        table_data[record["id"]] = record
        return record

    def get(self, table: str, record_id: Any) -> Optional[Dict[str, Any]]:
        return self._get_table(table).get(record_id)

    def update(self, table: str, record_id: Any, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        record = self.get(table, record_id)
        if record:
            record.update(updates)
            return record
        return None

    def delete(self, table: str, record_id: Any) -> bool:
        table_data = self._get_table(table)
        if record_id in table_data:
            del table_data[record_id]
            return True
        return False

    def query(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> list[Dict[str, Any]]:
        table_data = self._get_table(table)
        results = list(table_data.values())

        if filters:
            for key, value in filters.items():
                results = [r for r in results if r.get(key) == value]

        return results

    def clear(self) -> None:
        self._tables.clear()
        self._id_counter = 0
