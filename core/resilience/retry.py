"""
Retry Pattern.

Provides automatic retry with configurable backoff strategies
for handling transient failures.
"""

import asyncio
import functools
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Type

from loguru import logger


class BackoffStrategy(str, Enum):
    """Backoff strategies for retry."""

    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"


@dataclass
class RetryPolicy:
    """
    Configuration for retry behavior.

    Attributes:
        max_attempts: Maximum number of attempts.
        base_delay: Base delay between retries in seconds.
        max_delay: Maximum delay between retries.
        backoff_strategy: Strategy for increasing delay.
        backoff_multiplier: Multiplier for backoff calculation.
        jitter: Add random jitter to delays.
        retryable_exceptions: Exceptions that trigger retry.
        non_retryable_exceptions: Exceptions that should not be retried.
    """

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL_JITTER
    backoff_multiplier: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[Type[Exception], ...] = (Exception,)
    non_retryable_exceptions: tuple[Type[Exception], ...] = ()

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.

        Args:
            attempt: Current attempt number (0-indexed).

        Returns:
            Delay in seconds.
        """
        if self.backoff_strategy == BackoffStrategy.FIXED:
            delay = self.base_delay

        elif self.backoff_strategy == BackoffStrategy.LINEAR:
            delay = self.base_delay * (attempt + 1)

        elif self.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.base_delay * (self.backoff_multiplier ** attempt)

        elif self.backoff_strategy == BackoffStrategy.EXPONENTIAL_JITTER:
            delay = self.base_delay * (self.backoff_multiplier ** attempt)
            if self.jitter:
                delay = delay * (0.5 + random.random())

        else:
            delay = self.base_delay

        return min(delay, self.max_delay)

    def should_retry(self, exception: Exception) -> bool:
        """
        Check if exception should be retried.

        Args:
            exception: The exception that occurred.

        Returns:
            True if should retry.
        """
        if isinstance(exception, self.non_retryable_exceptions):
            return False
        return isinstance(exception, self.retryable_exceptions)


class RetryExhausted(Exception):
    """Raised when all retry attempts are exhausted."""

    def __init__(
        self,
        message: str,
        last_exception: Exception,
        attempts: int,
    ):
        self.last_exception = last_exception
        self.attempts = attempts
        super().__init__(f"{message} after {attempts} attempts: {last_exception}")


async def retry_async(
    func: Callable,
    policy: RetryPolicy,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Execute async function with retry.

    Args:
        func: Async function to call.
        policy: Retry policy.
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        Result of the function.

    Raises:
        RetryExhausted: If all attempts fail.
    """
    last_exception: Optional[Exception] = None

    for attempt in range(policy.max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            if not policy.should_retry(e):
                raise

            if attempt < policy.max_attempts - 1:
                delay = policy.calculate_delay(attempt)
                logger.warning(
                    f"Retry attempt {attempt + 1}/{policy.max_attempts} "
                    f"for {func.__name__} after {delay:.2f}s: {e}"
                )
                await asyncio.sleep(delay)

    raise RetryExhausted(
        f"Function {func.__name__} failed",
        last_exception or Exception("Unknown error"),
        policy.max_attempts,
    )


def retry_sync(
    func: Callable,
    policy: RetryPolicy,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Execute sync function with retry.

    Args:
        func: Function to call.
        policy: Retry policy.
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        Result of the function.

    Raises:
        RetryExhausted: If all attempts fail.
    """
    last_exception: Optional[Exception] = None

    for attempt in range(policy.max_attempts):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            if not policy.should_retry(e):
                raise

            if attempt < policy.max_attempts - 1:
                delay = policy.calculate_delay(attempt)
                logger.warning(
                    f"Retry attempt {attempt + 1}/{policy.max_attempts} "
                    f"for {func.__name__} after {delay:.2f}s: {e}"
                )
                time.sleep(delay)

    raise RetryExhausted(
        f"Function {func.__name__} failed",
        last_exception or Exception("Unknown error"),
        policy.max_attempts,
    )


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff: float = 2.0,
    strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL_JITTER,
    retryable_exceptions: tuple[Type[Exception], ...] = (Exception,),
    non_retryable_exceptions: tuple[Type[Exception], ...] = (),
) -> Callable:
    """
    Decorator to add retry behavior to a function.

    Usage:
        @retry(max_attempts=3, backoff=2.0)
        async def flaky_operation():
            pass

        @retry(
            max_attempts=5,
            retryable_exceptions=(ConnectionError, TimeoutError),
        )
        async def network_call():
            pass
    """
    policy = RetryPolicy(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        backoff_strategy=strategy,
        backoff_multiplier=backoff,
        retryable_exceptions=retryable_exceptions,
        non_retryable_exceptions=non_retryable_exceptions,
    )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await retry_async(func, policy, *args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return retry_sync(func, policy, *args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Common retry policies
NETWORK_RETRY_POLICY = RetryPolicy(
    max_attempts=5,
    base_delay=0.5,
    max_delay=30.0,
    backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
    retryable_exceptions=(ConnectionError, TimeoutError, OSError),
)

DATABASE_RETRY_POLICY = RetryPolicy(
    max_attempts=3,
    base_delay=0.1,
    max_delay=5.0,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
)

IDEMPOTENT_RETRY_POLICY = RetryPolicy(
    max_attempts=10,
    base_delay=1.0,
    max_delay=60.0,
    backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
)
