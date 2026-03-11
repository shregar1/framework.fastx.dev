"""
Health Check Router.

Provides FastAPI router with Kubernetes-compatible health endpoints.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from core.health.checks import HealthCheck, HealthCheckResult, HealthStatus


@dataclass
class HealthState:
    """Application health state."""

    started: bool = False
    ready: bool = False
    startup_time: datetime | None = None
    checks: dict[str, HealthCheck] = field(default_factory=dict)
    liveness_checks: list[str] = field(default_factory=list)
    readiness_checks: list[str] = field(default_factory=list)


class HealthRouter:
    """
    Health check router for FastAPI applications.

    Provides three endpoints:
    - /health/live - Liveness probe (is the app running?)
    - /health/ready - Readiness probe (can the app serve traffic?)
    - /health/startup - Startup probe (has the app finished initializing?)

    Usage:
        health = HealthRouter()
        health.add_check("database", DatabaseHealthCheck(db_session))
        health.add_check("redis", RedisHealthCheck(redis_client))

        # Mark as ready when initialization complete
        health.mark_ready()

        app.include_router(health.router, prefix="/health")
    """

    def __init__(self, prefix: str = "/health"):
        """
        Initialize health router.

        Args:
            prefix: URL prefix for health endpoints.
        """
        self._state = HealthState()
        self._router = APIRouter(prefix=prefix, tags=["Health"])
        self._setup_routes()

    @property
    def router(self) -> APIRouter:
        """Get the FastAPI router."""
        return self._router

    def add_check(
        self,
        name: str,
        check: HealthCheck,
        liveness: bool = False,
        readiness: bool = True,
    ) -> None:
        """
        Add a health check.

        Args:
            name: Name for the check.
            check: HealthCheck implementation.
            liveness: Include in liveness probe.
            readiness: Include in readiness probe.
        """
        self._state.checks[name] = check
        if liveness:
            self._state.liveness_checks.append(name)
        if readiness:
            self._state.readiness_checks.append(name)

    def mark_started(self) -> None:
        """Mark application as started."""
        self._state.started = True
        self._state.startup_time = datetime.utcnow()

    def mark_ready(self) -> None:
        """Mark application as ready to receive traffic."""
        self._state.started = True
        self._state.ready = True
        if not self._state.startup_time:
            self._state.startup_time = datetime.utcnow()

    def mark_not_ready(self) -> None:
        """Mark application as not ready (graceful shutdown)."""
        self._state.ready = False

    async def _run_checks(self, check_names: list[str]) -> dict[str, HealthCheckResult]:
        """Run specified health checks."""
        results = {}
        checks_to_run = [
            (name, self._state.checks[name])
            for name in check_names
            if name in self._state.checks
        ]

        if not checks_to_run:
            return results

        check_results = await asyncio.gather(
            *[check.check_with_timeout() for _, check in checks_to_run],
            return_exceptions=True,
        )

        for (name, _), result in zip(checks_to_run, check_results):
            if isinstance(result, Exception):
                results[name] = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(result),
                )
            else:
                results[name] = result

        return results

    def _aggregate_status(self, results: dict[str, HealthCheckResult]) -> HealthStatus:
        """Aggregate multiple check results into single status."""
        if not results:
            return HealthStatus.HEALTHY

        statuses = [r.status for r in results.values()]

        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        if any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def _build_response(
        self,
        status: HealthStatus,
        checks: dict[str, HealthCheckResult],
        extra: dict[str, Any] | None = None,
    ) -> JSONResponse:
        """Build health check response."""
        http_status = 200 if status == HealthStatus.HEALTHY else 503

        body = {
            "status": status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {name: result.to_dict() for name, result in checks.items()},
        }

        if extra:
            body.update(extra)

        return JSONResponse(content=body, status_code=http_status)

    def _setup_routes(self) -> None:
        """Setup health check routes."""

        @self._router.get("/live", summary="Liveness Probe")
        async def liveness() -> Response:
            """
            Liveness probe endpoint.

            Returns 200 if the application is running.
            Used by Kubernetes to determine if the container should be restarted.
            """
            if not self._state.started:
                return JSONResponse(
                    content={"status": "not_started"},
                    status_code=503,
                )

            if self._state.liveness_checks:
                results = await self._run_checks(self._state.liveness_checks)
                status = self._aggregate_status(results)
                return self._build_response(status, results)

            return JSONResponse(
                content={"status": "healthy", "timestamp": datetime.utcnow().isoformat()},
                status_code=200,
            )

        @self._router.get("/ready", summary="Readiness Probe")
        async def readiness() -> Response:
            """
            Readiness probe endpoint.

            Returns 200 if the application is ready to receive traffic.
            Used by Kubernetes to determine if traffic should be routed to this pod.
            """
            if not self._state.ready:
                return JSONResponse(
                    content={"status": "not_ready"},
                    status_code=503,
                )

            results = await self._run_checks(self._state.readiness_checks)
            status = self._aggregate_status(results)
            return self._build_response(status, results)

        @self._router.get("/startup", summary="Startup Probe")
        async def startup() -> Response:
            """
            Startup probe endpoint.

            Returns 200 if the application has completed initialization.
            Used by Kubernetes to know when the application has started.
            """
            if not self._state.started:
                return JSONResponse(
                    content={"status": "starting"},
                    status_code=503,
                )

            return JSONResponse(
                content={
                    "status": "started",
                    "startup_time": (
                        self._state.startup_time.isoformat()
                        if self._state.startup_time
                        else None
                    ),
                },
                status_code=200,
            )

        @self._router.get("", summary="Full Health Check")
        async def full_health() -> Response:
            """
            Full health check endpoint.

            Runs all registered health checks and returns detailed status.
            """
            all_check_names = list(self._state.checks.keys())
            results = await self._run_checks(all_check_names)
            status = self._aggregate_status(results)

            return self._build_response(
                status,
                results,
                extra={
                    "started": self._state.started,
                    "ready": self._state.ready,
                    "startup_time": (
                        self._state.startup_time.isoformat()
                        if self._state.startup_time
                        else None
                    ),
                },
            )
