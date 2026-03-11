"""
Circuit Breaker Pattern.

Prevents cascade failures by stopping calls to a failing service
and allowing it time to recover.

States:
- CLOSED: Normal operation, calls pass through
- OPEN: Service is failing, calls are rejected
- HALF_OPEN: Testing if service has recovered
"""

import asyncio
import functools
import time
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Any, Callable, Optional

from loguru import logger


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""

    def __init__(self, circuit_name: str, time_until_retry: float):
        self.circuit_name = circuit_name
        self.time_until_retry = time_until_retry
        super().__init__(
            f"Circuit breaker '{circuit_name}' is open. "
            f"Retry in {time_until_retry:.1f} seconds."
        )


@dataclass
class CircuitStats:
    """Statistics for circuit breaker."""

    failures: int = 0
    successes: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    total_calls: int = 0
    rejected_calls: int = 0

    def record_success(self) -> None:
        """Record a successful call."""
        self.successes += 1
        self.consecutive_successes += 1
        self.consecutive_failures = 0
        self.last_success_time = time.time()
        self.total_calls += 1

    def record_failure(self) -> None:
        """Record a failed call."""
        self.failures += 1
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        self.last_failure_time = time.time()
        self.total_calls += 1

    def record_rejected(self) -> None:
        """Record a rejected call."""
        self.rejected_calls += 1

    def reset(self) -> None:
        """Reset statistics."""
        self.failures = 0
        self.successes = 0
        self.consecutive_failures = 0
        self.consecutive_successes = 0


class CircuitBreaker:
    """
    Circuit breaker implementation.

    Monitors calls to a service and opens the circuit when failures
    exceed a threshold, preventing further calls until recovery.

    Usage:
        breaker = CircuitBreaker(
            name="payment_service",
            failure_threshold=5,
            recovery_timeout=30,
        )

        try:
            result = await breaker.call(payment_service.charge, amount=100)
        except CircuitBreakerOpen as e:
            # Handle circuit open
            pass
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 2,
        half_open_max_calls: int = 3,
        excluded_exceptions: tuple[type[Exception], ...] = (),
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Name of the circuit breaker.
            failure_threshold: Number of failures before opening.
            recovery_timeout: Seconds before attempting recovery.
            success_threshold: Successes needed to close from half-open.
            half_open_max_calls: Max calls allowed in half-open state.
            excluded_exceptions: Exceptions that don't count as failures.
        """
        self._name = name
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._success_threshold = success_threshold
        self._half_open_max_calls = half_open_max_calls
        self._excluded_exceptions = excluded_exceptions

        self._state = CircuitState.CLOSED
        self._stats = CircuitStats()
        self._opened_at: Optional[float] = None
        self._half_open_calls = 0
        self._lock = Lock()

    @property
    def name(self) -> str:
        """Get circuit breaker name."""
        return self._name

    @property
    def state(self) -> CircuitState:
        """Get current state."""
        return self._state

    @property
    def stats(self) -> CircuitStats:
        """Get statistics."""
        return self._stats

    def _should_allow_call(self) -> bool:
        """Check if a call should be allowed."""
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self._opened_at and time.time() - self._opened_at >= self._recovery_timeout:
                    self._transition_to_half_open()
                    return True
                return False

            if self._state == CircuitState.HALF_OPEN:
                # Allow limited calls in half-open state
                if self._half_open_calls < self._half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False

            return False

    def _transition_to_open(self) -> None:
        """Transition to open state."""
        logger.warning(f"Circuit breaker '{self._name}' opened")
        self._state = CircuitState.OPEN
        self._opened_at = time.time()

    def _transition_to_half_open(self) -> None:
        """Transition to half-open state."""
        logger.info(f"Circuit breaker '{self._name}' half-open")
        self._state = CircuitState.HALF_OPEN
        self._half_open_calls = 0
        self._stats.reset()

    def _transition_to_closed(self) -> None:
        """Transition to closed state."""
        logger.info(f"Circuit breaker '{self._name}' closed")
        self._state = CircuitState.CLOSED
        self._opened_at = None
        self._stats.reset()

    def _record_success(self) -> None:
        """Record successful call."""
        with self._lock:
            self._stats.record_success()

            if self._state == CircuitState.HALF_OPEN:
                if self._stats.consecutive_successes >= self._success_threshold:
                    self._transition_to_closed()

    def _record_failure(self, exception: Exception) -> None:
        """Record failed call."""
        # Check if exception should be excluded
        if isinstance(exception, self._excluded_exceptions):
            return

        with self._lock:
            self._stats.record_failure()

            if self._state == CircuitState.CLOSED:
                if self._stats.consecutive_failures >= self._failure_threshold:
                    self._transition_to_open()

            elif self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open reopens the circuit
                self._transition_to_open()

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Call a function through the circuit breaker.

        Args:
            func: Function to call.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Result of the function.

        Raises:
            CircuitBreakerOpen: If circuit is open.
        """
        if not self._should_allow_call():
            self._stats.record_rejected()
            time_until_retry = (
                self._recovery_timeout - (time.time() - (self._opened_at or 0))
                if self._opened_at
                else self._recovery_timeout
            )
            raise CircuitBreakerOpen(self._name, max(0, time_until_retry))

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            raise

    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        with self._lock:
            self._transition_to_closed()
            self._stats = CircuitStats()


# Global circuit breakers registry
_circuit_breakers: dict[str, CircuitBreaker] = {}
_registry_lock = Lock()


def get_circuit_breaker(name: str, **kwargs: Any) -> CircuitBreaker:
    """Get or create a circuit breaker."""
    with _registry_lock:
        if name not in _circuit_breakers:
            _circuit_breakers[name] = CircuitBreaker(name, **kwargs)
        return _circuit_breakers[name]


def circuit_breaker(
    name: Optional[str] = None,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    success_threshold: int = 2,
    excluded_exceptions: tuple[type[Exception], ...] = (),
) -> Callable:
    """
    Decorator to wrap a function with a circuit breaker.

    Usage:
        @circuit_breaker(failure_threshold=5, recovery_timeout=30)
        async def call_external_api():
            pass
    """

    def decorator(func: Callable) -> Callable:
        breaker_name = name or func.__name__
        breaker = get_circuit_breaker(
            breaker_name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            success_threshold=success_threshold,
            excluded_exceptions=excluded_exceptions,
        )

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await breaker.call(func, *args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # For sync functions
            if not breaker._should_allow_call():
                breaker._stats.record_rejected()
                raise CircuitBreakerOpen(breaker_name, breaker._recovery_timeout)
            try:
                result = func(*args, **kwargs)
                breaker._record_success()
                return result
            except Exception as e:
                breaker._record_failure(e)
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
