# Core (`core/`)

## What this module does

The **`core`** package provides **cross-cutting infrastructure** shared by the whole app: request **context** (URN, user), **logging**, **testing** helpers (factories, mocks, fixtures), **documentation** helpers, **taxonomy** labels, and optional subsystems such as **WebSockets** routing. It sits **below** controllers/services in the sense that features **import** from `core` for shared behavior, not the other way around.

This is not where business rules live—that remains in **`services/`** and **`models/`** (domain models). `core` is for **plumbing** that every layer can rely on.

---

## FastMVC Core Module

Production-grade features for enterprise FastAPI applications.

## 📦 Features

| Module | Description | Status |
|--------|-------------|--------|
| **Health Checks** | Kubernetes-compatible liveness/readiness probes | ✅ |
| **Observability** | Structured logging, metrics, tracing, audit | ✅ |
| **Resilience** | Circuit breaker, retry with backoff | ✅ |
| **Tasks** | Background task queue with Redis | ✅ |
| **Security** | API keys, webhook verification, encryption | ✅ |
| **Features** | Feature flags with targeting | ✅ |
| **Tenancy** | Multi-tenant support | ✅ |
| **Versioning** | API versioning (URL, header, query) | ✅ |
| **Testing** | Factories, mocks, fixtures | ✅ |

## 🚀 Quick Start

### Health Checks

```python
from core.health import HealthRouter, DataIHealthCheck, RedisHealthCheck

health = HealthRouter()
health.add_check("dataI", DataIHealthCheck(db_session))
health.add_check("redis", RedisHealthCheck(redis_client))
health.mark_ready()

app.include_router(health.router)
# Endpoints: /health/live, /health/ready, /health/startup
```

### Circuit Breaker

```python
from core.resilience import circuit_breaker, retry

@circuit_breaker(failure_threshold=5, recovery_timeout=30)
async def call_payment_api():
    return await payment_service.charge()

@retry(max_attempts=3, backoff=2.0)
async def flaky_operation():
    return await external_api.fetch()
```

### Feature Flags

```python
from core.features import FeatureFlags, feature_flag

flags = FeatureFlags()
await flags.set("new_checkout", enabled=True, percentage=50)

@feature_flag("new_checkout", default=False)
async def checkout():
    # Only runs for users in the rollout
    pass

# Or check manually
if await flags.is_enabled("new_checkout", user_id="user123"):
    use_new_checkout()
```

### Background Tasks

```python
from core.tasks import task, get_task_queue

@task(name="send_email", queue="emails", retry=3)
async def send_email(to: str, subject: str, body: str):
    await email_service.send(to, subject, body)

# Enqueue task
await send_email.delay(to="user@example.com", subject="Welcome!")
```

### Multi-Tenancy

```python
from core.tenancy import TenantMiddleware, HeaderTenantResolver, get_current_tenant

resolver = HeaderTenantResolver(store, "X-Tenant-ID")
app.add_middleware(TenantMiddleware, resolver=resolver, required=True)

# In your services
@router.get("/data")
async def get_data():
    tenant = get_current_tenant()
    return await repo.get_all(tenant_id=tenant.id)
```

### API Keys

```python
from core.security import APIKeyManager, APIKeyValidator

manager = APIKeyManager()
key, plain_key = await manager.create(
    name="my-service",
    scopes=["read", "write"],
    expires_in_days=365,
)
# Give plain_key to user - it cannot be retrieved later!

# Protect endpoints
validator = APIKeyValidator(manager, required_scopes=["read"])

@router.get("/protected")
async def protected(api_key = Depends(validator)):
    return {"key": api_key.name}
```

### Webhook Verification

```python
from core.security import WebhookVerifier

verifier = WebhookVerifier(secret="webhook_secret")

@router.post("/webhook")
async def handle_webhook(request: Request):
    body = await verifier.verify_request(request)
    payload = json.loads(body)
    # Process verified webhook
```

### Structured Logging

```python
from core.observability import StructuredLogger, set_log_context

logger = StructuredLogger("my_service")

# Set context for request
set_log_context(request_id="req-123", user_id="user-456")

# All logs include context
logger.info("Processing order", order_id="ord-789", amount=99.99)
# Output: {"timestamp": "...", "request_id": "req-123", "user_id": "user-456", "order_id": "ord-789", ...}
```

### Metrics

```python
from core.observability import Metrics, MetricsMiddleware

metrics = Metrics()
app.add_middleware(MetricsMiddleware, metrics=metrics)

# Custom metrics
orders = metrics.counter("orders_total", "Total orders", ["status"])
orders.inc(status="completed")

# Export at /metrics
@router.get("/metrics")
async def get_metrics():
    return Response(content=metrics.export(), media_type="text/plain")
```

### API Versioning

```python
from core.versioning import VersioningMiddleware, VersioningStrategy, get_api_version

app.add_middleware(
    VersioningMiddleware,
    strategy=VersioningStrategy.URL_PATH,  # /api/v1/users
    available_versions=["v1", "v2"],
)

@router.get("/users")
async def get_users():
    version = get_api_version()
    if version == "v2":
        return {"users": [], "meta": {"total": 0}}
    return {"users": []}
```

### Testing

```python
from core.testing import Factory, mock_external, TestClient

# Define factories
class UserFactory(Factory):
    email = Factory.faker("email")
    name = Factory.faker("name")
    is_active = True

# Use in tests
user = await UserFactory.create()
users = await UserFactory.create_batch(10)

# Mock external services
@mock_external("stripe.Charge.create", return_value={"id": "ch_123"})
async def test_payment():
    result = await process_payment()
    assert result["charge_id"] == "ch_123"
```

## 📁 Module Structure

```text
core/
├── __init__.py          # Main exports
├── health/              # Health checks
│   ├── checks.py        # Check implementations
│   └── router.py        # FastAPI router
├── observability/       # Logging, metrics, tracing
│   ├── logging.py       # Structured logging
│   ├── metrics.py       # Prometheus metrics
│   ├── tracing.py       # Distributed tracing
│   └── audit.py         # Audit logging
├── resilience/          # Fault tolerance
│   ├── circuit_breaker.py
│   └── retry.py
├── tasks/               # Background tasks
│   └── queue.py
├── security/            # Security features
│   ├── api_keys.py
│   ├── webhooks.py
│   └── encryption.py
├── features/            # Feature flags
│   └── flags.py
├── tenancy/             # Multi-tenancy
│   ├── context.py
│   └── middleware.py
├── versioning/          # API versioning
│   └── router.py
└── testing/             # Test utilities
    ├── factories.py
    ├── mocks.py
    └── fixtures.py
```

## 📋 Dependencies

The core module requires these additional packages:

```text
cryptography>=41.0.0  # For field encryption
```

Optional dependencies for specific features:

- `opentelemetry-*`: For production tracing export
- `prometheus-client`: Alternative metrics library
