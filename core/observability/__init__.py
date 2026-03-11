"""
Observability Module.

Provides comprehensive observability features:
- Structured logging with context propagation
- Prometheus metrics
- Distributed tracing (OpenTelemetry)
- Audit logging

Usage:
    from core.observability import StructuredLogger, Metrics, AuditLog
    
    logger = StructuredLogger("my_service")
    logger.info("User action", user_id=123, action="purchase")
    
    metrics = Metrics()
    metrics.counter("orders_total").inc()
    
    @audit_log(action="user.update")
    async def update_user(user_id: str):
        pass
"""

from core.observability.audit import AuditLog, audit_log
from core.observability.logging import StructuredLogger
from core.observability.metrics import Metrics, MetricsMiddleware
from core.observability.tracing import Tracer, TracingMiddleware

__all__ = [
    "StructuredLogger",
    "Metrics",
    "MetricsMiddleware",
    "Tracer",
    "TracingMiddleware",
    "AuditLog",
    "audit_log",
]
