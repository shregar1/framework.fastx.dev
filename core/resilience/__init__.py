"""
Resilience Module.

Provides patterns for building resilient applications:
- Circuit Breaker: Prevent cascade failures
- Retry: Automatic retry with backoff
- Timeout: Operation timeouts
- Bulkhead: Resource isolation

Usage:
    from core.resilience import circuit_breaker, retry, RetryPolicy

    @circuit_breaker(failure_threshold=5, recovery_timeout=30)
    async def call_external_api():
        pass

    @retry(max_attempts=3, backoff=2.0)
    async def flaky_operation():
        pass
"""

from core.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerOpen, circuit_breaker
from core.resilience.retry import RetryPolicy, retry

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerOpen",
    "circuit_breaker",
    "RetryPolicy",
    "retry",
]
