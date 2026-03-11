"""
Health Check Module.

Provides Kubernetes-compatible health check endpoints:
- /health/live - Liveness probe (app is running)
- /health/ready - Readiness probe (dependencies available)
- /health/startup - Startup probe (initialization complete)

Usage:
    from core.health import HealthRouter, HealthCheck
    
    health_router = HealthRouter()
    health_router.add_check("database", DatabaseHealthCheck())
    health_router.add_check("redis", RedisHealthCheck())
    
    app.include_router(health_router.router)
"""

from core.health.checks import (
    DatabaseHealthCheck,
    HealthCheck,
    HealthStatus,
    RedisHealthCheck,
)
from core.health.router import HealthRouter

__all__ = [
    "HealthCheck",
    "HealthStatus",
    "HealthRouter",
    "DatabaseHealthCheck",
    "RedisHealthCheck",
]
