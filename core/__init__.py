"""
FastMVC Core Module.

Production-grade features for enterprise applications:
- Health checks & readiness probes
- Observability (logging, metrics, tracing)
- Resilience (circuit breaker, retry)
- Background tasks
- Security (API keys, webhooks, encryption)
- Feature flags
- Multi-tenancy
- API versioning
- Testing utilities
"""

from core.health import HealthCheck, HealthRouter, HealthStatus
from core.observability import AuditLog, Metrics, StructuredLogger, Tracer
from core.resilience import CircuitBreaker, RetryPolicy, retry
from core.tasks import TaskQueue, task
from core.security import APIKeyManager, FieldEncryption, WebhookVerifier
from core.features import FeatureFlags, feature_flag
from core.tenancy import TenantContext, get_current_tenant
from core.versioning import APIVersion, versioned_router

__all__ = [
    # Health
    "HealthCheck",
    "HealthRouter",
    "HealthStatus",
    # Observability
    "StructuredLogger",
    "Metrics",
    "Tracer",
    "AuditLog",
    # Resilience
    "CircuitBreaker",
    "RetryPolicy",
    "retry",
    # Tasks
    "TaskQueue",
    "task",
    # Security
    "APIKeyManager",
    "WebhookVerifier",
    "FieldEncryption",
    # Features
    "FeatureFlags",
    "feature_flag",
    # Tenancy
    "TenantContext",
    "get_current_tenant",
    # Versioning
    "APIVersion",
    "versioned_router",
]
