"""Application core integration layer (FastAPI wiring, optional services).

This module provides re-exports for optional fast_platform services.
Each import is wrapped in try/except to allow the core to work without
the optional dependencies.

Usage:
    # Core only (no optional dependencies)
    from core import app

    # With optional services (requires fast-platform)
    from core import CircuitBreaker, Metrics
"""

# Optional fast_platform services - gracefully degrade if not installed
# These require: pip install pyfastmvc[platform] or specific extras

# Observability (fast_platform.observability)
try:
    from core.observability import AuditLog, Metrics, StructuredLogger, Tracer
except ImportError:
    AuditLog = None  # type: ignore
    Metrics = None  # type: ignore
    StructuredLogger = None  # type: ignore
    Tracer = None  # type: ignore

# Resilience (fast_platform.resilience)
try:
    from core.resilience import CircuitBreaker, RetryPolicy, retry
except ImportError:
    CircuitBreaker = None  # type: ignore
    RetryPolicy = None  # type: ignore
    retry = None  # type: ignore

# Tasks/Jobs (fast_platform.jobs)
try:
    from core.tasks import (
        JobsConfiguration,
        JobsConfigurationDTO,
        cancel_job,
        enqueue,
        get_job_status,
    )
except ImportError:
    JobsConfiguration = None  # type: ignore
    JobsConfigurationDTO = None  # type: ignore
    cancel_job = None  # type: ignore
    enqueue = None  # type: ignore
    get_job_status = None  # type: ignore

# Security (fast_platform.security)
try:
    from core.security import APIKeyManager, FieldEncryption, WebhookVerifier
except ImportError:
    APIKeyManager = None  # type: ignore
    FieldEncryption = None  # type: ignore
    WebhookVerifier = None  # type: ignore

# Feature Flags (fast_platform.features)
try:
    from core.features import FeatureFlags, feature_flag
except ImportError:
    FeatureFlags = None  # type: ignore
    feature_flag = None  # type: ignore

# Tenancy (fast_platform.tenancy)
try:
    from core.tenancy import Tenant, TenantContext, get_current_tenant
except ImportError:
    Tenant = None  # type: ignore
    TenantContext = None  # type: ignore
    get_current_tenant = None  # type: ignore

# Versioning (fast_platform.utils.versioning)
try:
    from utils.versioning import APIVersion, versioned_router
except ImportError:
    APIVersion = None  # type: ignore
    versioned_router = None  # type: ignore


__all__ = [
    # Observability
    "StructuredLogger",
    "Metrics",
    "Tracer",
    "AuditLog",
    # Resilience
    "CircuitBreaker",
    "RetryPolicy",
    "retry",
    # Jobs (fast_jobs)
    "enqueue",
    "cancel_job",
    "get_job_status",
    "JobsConfiguration",
    "JobsConfigurationDTO",
    # Security
    "APIKeyManager",
    "WebhookVerifier",
    "FieldEncryption",
    # Features
    "FeatureFlags",
    "feature_flag",
    # Tenancy (fast_tenancy)
    "Tenant",
    "TenantContext",
    "get_current_tenant",
    # Versioning
    "APIVersion",
    "versioned_router",
]
