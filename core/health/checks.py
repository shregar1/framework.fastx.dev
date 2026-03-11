"""
Health Check Implementations.

Provides base health check interface and common implementations
for database, Redis, and external service health checks.
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from loguru import logger


class HealthStatus(str, Enum):
    """Health check status values."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    message: Optional[str] = None
    latency_ms: Optional[float] = None
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "latency_ms": self.latency_ms,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class HealthCheck(ABC):
    """
    Abstract base class for health checks.

    Implement this interface to create custom health checks
    for your application's dependencies.

    Example:
        class MyServiceHealthCheck(HealthCheck):
            async def check(self) -> HealthCheckResult:
                try:
                    await my_service.ping()
                    return HealthCheckResult(
                        name="my_service",
                        status=HealthStatus.HEALTHY
                    )
                except Exception as e:
                    return HealthCheckResult(
                        name="my_service",
                        status=HealthStatus.UNHEALTHY,
                        message=str(e)
                    )
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the health check."""
        pass

    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """
        Perform the health check.

        Returns:
            HealthCheckResult with status and optional details.
        """
        pass

    async def check_with_timeout(
        self, timeout_seconds: float = 5.0
    ) -> HealthCheckResult:
        """
        Perform health check with timeout.

        Args:
            timeout_seconds: Maximum time to wait for check.

        Returns:
            HealthCheckResult, with UNHEALTHY status on timeout.
        """
        start_time = datetime.utcnow()
        try:
            result = await asyncio.wait_for(
                self.check(), timeout=timeout_seconds
            )
            end_time = datetime.utcnow()
            result.latency_ms = (end_time - start_time).total_seconds() * 1000
            return result
        except asyncio.TimeoutError:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {timeout_seconds}s",
                latency_ms=timeout_seconds * 1000,
            )
        except Exception as e:
            logger.error(f"Health check {self.name} failed: {e}")
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
            )


class DatabaseHealthCheck(HealthCheck):
    """
    Health check for database connectivity.

    Executes a simple query to verify database is accessible.
    """

    def __init__(self, session_factory: Any, query: str = "SELECT 1"):
        """
        Initialize database health check.

        Args:
            session_factory: SQLAlchemy session factory or async session maker.
            query: Simple query to execute for health check.
        """
        self._session_factory = session_factory
        self._query = query

    @property
    def name(self) -> str:
        return "database"

    async def check(self) -> HealthCheckResult:
        """Check database connectivity."""
        try:
            # Handle both sync and async sessions
            session = self._session_factory()
            try:
                if hasattr(session, "execute"):
                    from sqlalchemy import text
                    result = session.execute(text(self._query))
                    result.fetchone()
                    session.close()
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Database connection successful",
                )
            finally:
                if hasattr(session, "close"):
                    session.close()
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {e}",
            )


class RedisHealthCheck(HealthCheck):
    """
    Health check for Redis connectivity.

    Executes PING command to verify Redis is accessible.
    """

    def __init__(self, redis_client: Any):
        """
        Initialize Redis health check.

        Args:
            redis_client: Redis client instance.
        """
        self._redis = redis_client

    @property
    def name(self) -> str:
        return "redis"

    async def check(self) -> HealthCheckResult:
        """Check Redis connectivity."""
        try:
            if hasattr(self._redis, "ping"):
                # Sync client
                result = self._redis.ping()
                if result:
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.HEALTHY,
                        message="Redis connection successful",
                    )
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Redis ping failed",
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {e}",
            )


class HTTPHealthCheck(HealthCheck):
    """
    Health check for external HTTP services.

    Makes a GET request to verify service is accessible.
    """

    def __init__(
        self,
        name: str,
        url: str,
        expected_status: int = 200,
        headers: Optional[dict[str, str]] = None,
    ):
        """
        Initialize HTTP health check.

        Args:
            name: Name for this health check.
            url: URL to check.
            expected_status: Expected HTTP status code.
            headers: Optional headers to include in request.
        """
        self._name = name
        self._url = url
        self._expected_status = expected_status
        self._headers = headers or {}

    @property
    def name(self) -> str:
        return self._name

    async def check(self) -> HealthCheckResult:
        """Check HTTP service connectivity."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self._url, headers=self._headers)
                if response.status_code == self._expected_status:
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.HEALTHY,
                        message=f"HTTP service returned {response.status_code}",
                        details={"url": self._url, "status_code": response.status_code},
                    )
                else:
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.DEGRADED,
                        message=f"Unexpected status: {response.status_code}",
                        details={"url": self._url, "status_code": response.status_code},
                    )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"HTTP request failed: {e}",
                details={"url": self._url},
            )


class CompositeHealthCheck(HealthCheck):
    """
    Combines multiple health checks into one.

    Useful for checking multiple dependencies as a group.
    """

    def __init__(self, name: str, checks: list[HealthCheck]):
        """
        Initialize composite health check.

        Args:
            name: Name for this composite check.
            checks: List of health checks to run.
        """
        self._name = name
        self._checks = checks

    @property
    def name(self) -> str:
        return self._name

    async def check(self) -> HealthCheckResult:
        """Run all checks and aggregate results."""
        results = await asyncio.gather(
            *[check.check_with_timeout() for check in self._checks],
            return_exceptions=True,
        )

        all_healthy = True
        any_unhealthy = False
        details = {}

        for result in results:
            if isinstance(result, Exception):
                any_unhealthy = True
                all_healthy = False
            elif isinstance(result, HealthCheckResult):
                details[result.name] = result.to_dict()
                if result.status == HealthStatus.UNHEALTHY:
                    any_unhealthy = True
                    all_healthy = False
                elif result.status == HealthStatus.DEGRADED:
                    all_healthy = False

        if any_unhealthy:
            status = HealthStatus.UNHEALTHY
        elif all_healthy:
            status = HealthStatus.HEALTHY
        else:
            status = HealthStatus.DEGRADED

        return HealthCheckResult(
            name=self.name,
            status=status,
            details=details,
        )
