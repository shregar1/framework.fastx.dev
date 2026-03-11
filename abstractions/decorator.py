"""
Decorator Pattern.

Dynamically adds behavior to objects without modifying their
structure, using composition instead of inheritance.

Implements:
- Component/Decorator base classes
- Function decorators for cross-cutting concerns
- Async decorator support

SOLID Principles:
- Single Responsibility: Each decorator adds one behavior
- Open/Closed: Extend functionality without modification
- Liskov Substitution: Decorators are interchangeable with base
"""

from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Generic, Optional, TypeVar
import asyncio
import time
import logging

T = TypeVar("T")
TResult = TypeVar("TResult")


class IComponent(ABC, Generic[T]):
    """
    Base component interface for decorator pattern.

    Usage:
        class DataSource(IComponent[str]):
            @abstractmethod
            def read(self) -> str:
                pass

        class FileDataSource(DataSource):
            def read(self) -> str:
                return read_file()

        class EncryptedDataSource(DataSource):
            def __init__(self, wrapped: DataSource):
                self._wrapped = wrapped

            def read(self) -> str:
                return decrypt(self._wrapped.read())
    """

    @abstractmethod
    def execute(self) -> T:
        """Execute the component operation."""
        pass


class BaseDecorator(IComponent[T]):
    """
    Base decorator class.

    Usage:
        class LoggingDecorator(BaseDecorator):
            def execute(self) -> T:
                print("Before execution")
                result = self._wrapped.execute()
                print("After execution")
                return result
    """

    def __init__(self, wrapped: IComponent[T]):
        self._wrapped = wrapped

    def execute(self) -> T:
        return self._wrapped.execute()


# Function decorators for common cross-cutting concerns


def timing(func: Callable) -> Callable:
    """
    Decorator to measure execution time.

    Usage:
        @timing
        def slow_function():
            time.sleep(1)

        @timing
        async def async_slow_function():
            await asyncio.sleep(1)
    """
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                logging.info(f"{func.__name__} took {elapsed:.4f}s")
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                logging.info(f"{func.__name__} took {elapsed:.4f}s")
        return sync_wrapper


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator to retry failed operations.

    Usage:
        @retry(max_attempts=3, delay=1.0)
        def unreliable_api_call():
            return external_service.call()

        @retry(exceptions=(ConnectionError,))
        async def fetch_data():
            return await http_client.get(url)
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception = None
                current_delay = delay

                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            await asyncio.sleep(current_delay)
                            current_delay *= backoff

                raise last_exception
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                last_exception = None
                current_delay = delay

                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            time.sleep(current_delay)
                            current_delay *= backoff

                raise last_exception
            return sync_wrapper
    return decorator


def cache(ttl_seconds: Optional[int] = None) -> Callable:
    """
    Simple in-memory caching decorator.

    Usage:
        @cache(ttl_seconds=60)
        def get_user(user_id: str) -> User:
            return database.get_user(user_id)
    """
    def decorator(func: Callable) -> Callable:
        _cache: dict = {}
        _timestamps: dict = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))

            if key in _cache:
                if ttl_seconds is None:
                    return _cache[key]

                if time.time() - _timestamps[key] < ttl_seconds:
                    return _cache[key]

            result = func(*args, **kwargs)
            _cache[key] = result
            _timestamps[key] = time.time()
            return result

        wrapper.clear_cache = lambda: (_cache.clear(), _timestamps.clear())
        return wrapper
    return decorator


def log_calls(
    logger: Optional[logging.Logger] = None,
    level: int = logging.DEBUG,
) -> Callable:
    """
    Log function calls with arguments and results.

    Usage:
        @log_calls()
        def process_order(order_id: str, amount: float):
            return {"status": "processed"}
    """
    log = logger or logging.getLogger(__name__)

    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                log.log(level, f"Calling {func.__name__}({args}, {kwargs})")
                try:
                    result = await func(*args, **kwargs)
                    log.log(level, f"{func.__name__} returned {result}")
                    return result
                except Exception as e:
                    log.exception(f"{func.__name__} raised {e}")
                    raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                log.log(level, f"Calling {func.__name__}({args}, {kwargs})")
                try:
                    result = func(*args, **kwargs)
                    log.log(level, f"{func.__name__} returned {result}")
                    return result
                except Exception as e:
                    log.exception(f"{func.__name__} raised {e}")
                    raise
            return sync_wrapper
    return decorator


def validate_args(**validators: Callable[[Any], bool]) -> Callable:
    """
    Validate function arguments.

    Usage:
        @validate_args(
            user_id=lambda x: isinstance(x, str) and len(x) > 0,
            amount=lambda x: isinstance(x, (int, float)) and x > 0
        )
        def transfer(user_id: str, amount: float):
            return process_transfer(user_id, amount)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Validation failed for {param_name}: {value}"
                        )

            return func(*args, **kwargs)
        return wrapper
    return decorator


def deprecated(message: str = "") -> Callable:
    """
    Mark function as deprecated.

    Usage:
        @deprecated("Use new_function() instead")
        def old_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            warnings.warn(
                f"{func.__name__} is deprecated. {message}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def singleton(cls: type) -> type:
    """
    Make a class a singleton.

    Usage:
        @singleton
        class Database:
            def __init__(self):
                self.connection = create_connection()
    """
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def run_in_thread(func: Callable) -> Callable:
    """
    Run synchronous function in a thread pool.

    Usage:
        @run_in_thread
        def blocking_io():
            return read_large_file()

        # Can now be awaited
        result = await blocking_io()
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


def rate_limit(calls: int, period: float) -> Callable:
    """
    Rate limit function calls.

    Usage:
        @rate_limit(calls=10, period=60)  # 10 calls per minute
        def api_call():
            return make_request()
    """
    def decorator(func: Callable) -> Callable:
        call_times: list = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside the period
            while call_times and call_times[0] < now - period:
                call_times.pop(0)

            if len(call_times) >= calls:
                wait_time = call_times[0] + period - now
                raise Exception(f"Rate limit exceeded. Try again in {wait_time:.1f}s")

            call_times.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def timeout(seconds: float) -> Callable:
    """
    Add timeout to async functions.

    Usage:
        @timeout(30)
        async def long_running_task():
            await process_data()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=seconds,
                )
            except asyncio.TimeoutError:
                raise TimeoutError(f"{func.__name__} timed out after {seconds}s")
        return wrapper
    return decorator
