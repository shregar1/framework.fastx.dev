"""FastMVC Application Entry Point.

This is the main FastAPI application module that initializes the web server,
configures middleware, registers routes, and handles application lifecycle events.

Usage:
    Run directly (from repo root, or set ``PYTHONPATH=src``):
        python src/app.py

    Or with uvicorn (after ``pip install -e .`` or with ``PYTHONPATH=src``):
        uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Environment Variables:
    HOST: Server host address (default: 0.0.0.0)
    PORT: Server port (default: 8000)
    POSTMAN_EXPORT_ENVIRONMENT: Set to 1/true to also write postman_environment.json on boot
    POSTMAN_COLLECTION_NAME: Override Postman collection/env title (default: git repo folder name)
    POSTMAN_NEGATIVE_TESTS: Set to 0/false to skip extra pm.sendRequest validation scripts per request
    RATE_LIMIT_REQUESTS_PER_MINUTE: Rate limit per minute
    RATE_LIMIT_REQUESTS_PER_HOUR: Rate limit per hour
    RATE_LIMIT_BURST_LIMIT: Maximum burst requests

Endpoints:
    GET /health - Comprehensive health check with dependency status
    GET /health/live - Kubernetes liveness probe (lightweight)
    GET /health/ready - Kubernetes readiness probe (dependency checks)
    POST /user/login - User authentication
    POST /user/register - New user registration
    POST /user/logout - Session termination

Example API (if example module is available):
    GET    /items          - List all items
    POST   /items          - Create new item
    GET    /items/{id}     - Get item by ID
    PATCH  /items/{id}     - Update item
    DELETE /items/{id}     - Delete item
    POST   /items/{id}/complete   - Mark as completed
    POST   /items/{id}/uncomplete - Mark as pending
    POST   /items/{id}/toggle     - Toggle status
    GET    /items/search   - Search items
    GET    /items/completed - List completed items
    GET    /items/pending  - List pending items
    GET    /items/statistics - Get item statistics
"""

import os
from datetime import datetime, timezone
from http import HTTPStatus
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import uvicorn  # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

load_dotenv()

# Import middlewares from fast-middleware package
from fast_middleware import (  # pyright: ignore[reportMissingImports]
    CORSMiddleware,
    LoggingMiddleware,
    RateLimitConfig,
    RateLimitMiddleware,
    RequestContextMiddleware,
    ResponseTimingMiddleware,
    SecurityHeadersMiddleware,
    TrustedHostMiddleware,
)
from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from loguru import logger

from constants.api_status import APIStatus
from constants.default import Default
from constants.health import (
    DEPENDENCY_CONNECTED,
    DEPENDENCY_NOT_CONFIGURED,
    HEALTH_CHECK_SQL_PING,
    HEALTH_STATUS_HEALTHY,
    HEALTH_STATUS_UNHEALTHY,
    LIVENESS_ALIVE,
    READINESS_NOT_READY,
    READINESS_READY,
    dependency_disconnected_message,
)
from constants.http_header import HttpHeader
from core.route_export_engine import RouteExportEngine
from utilities.cors import get_cors_middleware_kwargs
from utilities.security_headers import get_security_headers_middleware_config

# Optional example controllers (can be removed for minimal core)
try:
    from controllers.user import router as UserRouter  # noqa: I001  # pyright: ignore[reportMissingImports]
except ImportError:
    UserRouter = None  # type: ignore

# Optional sample Item API (CRUD demonstration)
try:
    from controllers.apis.v1.item.item_controller import router as ExampleItemRouter
except ImportError:
    ExampleItemRouter = None  # type: ignore

# Optional WebSocket router (requires fast_channels)
try:
    from core.websockets.router import router as WebSocketRouter
except ImportError:
    WebSocketRouter = None  # type: ignore

# Optional observability (requires fast-platform)
try:
    from fast_platform.observability import (  # pyright: ignore[reportMissingImports]
        configure_datadog,
        configure_otel,
    )
except ImportError:
    configure_datadog = None  # type: ignore
    configure_otel = None  # type: ignore

# Optional routers (require corresponding fast_* packages)
try:
    from fast_dashboards import DashboardRouter  # noqa: I001  # pyright: ignore[reportMissingImports, reportAttributeAccessIssue]
except ImportError:
    DashboardRouter = None  # type: ignore[assignment]
try:
    from controllers.channels import router as ChannelsRouter  # noqa: I001  # pyright: ignore[reportMissingImports]
except ImportError:
    ChannelsRouter = None  # type: ignore[assignment]
try:
    from controllers.notifications import router as NotificationsRouter  # noqa: I001  # pyright: ignore[reportMissingImports]
except ImportError:
    NotificationsRouter = None  # type: ignore[assignment]
try:
    from apis import router as MainApiRouter  # pyright: ignore[reportMissingImports]
except ImportError:
    MainApiRouter = None

# Flags for optional routers (used by tests and docs)
DASHBOARD_ROUTER_ENABLED = DashboardRouter is not None

from dtos.responses.apis.abstraction import IResponseAPIDTO

# Domain errors (requires fast-mvc[platform])
try:
    from fast_platform.errors import (  # pyright: ignore[reportMissingImports]
        BadInputError,
        ConflictError,
        ForbiddenError,
        NotFoundError,
        RateLimitError,
        ServiceUnavailableError,
        UnauthorizedError,
        UnexpectedResponseError,
    )

    HAS_PLATFORM_ERRORS = True
except ImportError:
    HAS_PLATFORM_ERRORS = False

# Custom authentication middleware (app-specific with user repository)
from middlewares import (
    AuthenticationMiddleware,
    DocsBasicAuthMiddleware,
    docs_auth_configured,
    docs_logging_exclude_paths,
    normalized_openapi_url,
)

# Configuration validation - fail fast on misconfig
# Set VALIDATE_CONFIG=false to skip validation
# Tests skip strict startup validation to avoid env-coupled imports.
IS_TEST_RUN = os.getenv("PYTEST_CURRENT_TEST") is not None or os.getenv(
    "TESTING", ""
).lower() in ("true", "1", "yes", "on")
try:
    if not IS_TEST_RUN and os.getenv("VALIDATE_CONFIG", "true").lower() not in (
        "false",
        "0",
        "no",
        "off",
    ):
        from utilities.validator import validate_config_or_exit

        validate_config_or_exit()
except ImportError:
    # Config validator is optional
    pass


def _get_int_env(name: str, default: int) -> int:
    """Execute _get_int_env operation.

    Args:
        name: The name parameter.
        default: The default parameter.

    Returns:
        The result of the operation.
    """
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        logger.warning(
            f"Invalid integer value for environment variable {name!r}: "
            f"{value!r}. Falling back to default {default!r}."
        )
        return default


# Initialize FastAPI application (openapi_url must match middlewares.docs_auth)
app = FastAPI(
    title="FastMVC API",
    description="Production-grade FastAPI application with MVC architecture. Includes example Item API at /items",
    version="1.0.1",
    docs_url=None,  # Custom docs setup below
    redoc_url=None,
    openapi_url=normalized_openapi_url(),
)
route_export_engine = RouteExportEngine(app)
route_export_engine.install()

# Setup custom FastMVC branded documentation
try:
    from core.docs import setup_custom_docs

    setup_custom_docs(app)
except ImportError:
    # Fallback to default docs if custom setup fails
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(
    os.getenv(
        "RATE_LIMIT_REQUESTS_PER_MINUTE",
        Default.RATE_LIMIT_REQUESTS_PER_MINUTE,
    )
)
RATE_LIMIT_REQUESTS_PER_HOUR: int = _get_int_env(
    "RATE_LIMIT_REQUESTS_PER_HOUR",
    Default.RATE_LIMIT_REQUESTS_PER_HOUR,
)
RATE_LIMIT_WINDOW_SECONDS: int = _get_int_env(
    "RATE_LIMIT_WINDOW_SECONDS",
    Default.RATE_LIMIT_WINDOW_SECONDS,
)
RATE_LIMIT_BURST_LIMIT: int = _get_int_env(
    "RATE_LIMIT_BURST_LIMIT",
    Default.RATE_LIMIT_BURST_LIMIT,
)

# Optional Datadog / OpenTelemetry integration (requires fast-platform)
if configure_datadog and os.getenv("DATADOG_ENABLED", "").lower() in {
    "1",
    "true",
    "yes",
}:
    configure_datadog()

if configure_otel and os.getenv("TELEMETRY_ENABLED", "").lower() in {
    "1",
    "true",
    "yes",
}:
    configure_otel(app)

# Static launch page at GET /
_STATIC_DIR = Path(__file__).resolve().parent / "static"
_LAUNCH_HTML = _STATIC_DIR / "launch.html"


@app.get("/", include_in_schema=False)
async def launch_page() -> HTMLResponse:
    """Serve the landing page at the application root (same host/port as the API)."""
    if _LAUNCH_HTML.is_file():
        return HTMLResponse(
            _LAUNCH_HTML.read_text(encoding="utf-8"),
            headers={"Cache-Control": "no-cache"},
        )
    return HTMLResponse(
        "<!DOCTYPE html><html><body><p>FastMVC API</p></body></html>",
        status_code=HTTPStatus.OK,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Global exception handler for request validation errors.

    Transforms Pydantic validation errors into a structured JSON response
    format consistent with the application's error handling pattern.

    Args:
        request: The incoming FastAPI request object.
        exc: The RequestValidationError exception instance.

    Returns:
        JSONResponse: Structured error response with validation details.

    Response Format:
        {
            "transactionUrn": "urn:req:abc123",
            "responseMessage": "Bad or missing input.",
            "responseKey": "error_bad_input",
            "errors": [{"loc": [...], "msg": "...", "type": "..."}]
        }

    """
    logger.error(f"Validation error: {exc.errors()}")
    # Remove internal context from error messages
    for error in exc.errors():
        if "ctx" in error:
            error.pop("ctx")
    response_payload: dict = {
        "transactionUrn": getattr(request.state, "urn", None),
        "responseMessage": "Bad or missing input.",
        "responseKey": "error_bad_input",
        "errors": exc.errors(),
    }
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content=response_payload,
        headers=HttpHeader().get_reference_urn_header(
            reference_urn=request.headers.get(HttpHeader.X_REFERENCE_URN)
        ),
    )


def _app_error_response(
    request: Request, exc, log_level: str = "warning"
) -> JSONResponse:
    """Build a JSONResponse for application error types (Unauthorized, Forbidden, etc.)."""
    urn = getattr(request.state, "urn", None) or ""
    try:
        getattr(logger, log_level)(
            f"{exc.__class__.__name__}: {getattr(exc, 'responseMessage', str(exc))} (key={getattr(exc, 'responseKey', 'unknown')})",
            urn=urn,
        )
    except Exception:
        pass

    response_dto = IResponseAPIDTO(
        transactionUrn=urn,
        status=APIStatus.FAILED,
        responseMessage=getattr(exc, "responseMessage", str(exc)),
        responseKey=getattr(exc, "responseKey", "error_unknown"),
        data={},
        errors=None,
    )
    return JSONResponse(
        status_code=getattr(exc, "httpStatusCode", HTTPStatus.INTERNAL_SERVER_ERROR),
        content=response_dto.model_dump(),
        headers=HttpHeader().get_reference_urn_header(
            reference_urn=request.headers.get(HttpHeader.X_REFERENCE_URN)
        ),
    )


if HAS_PLATFORM_ERRORS:

    @app.exception_handler(UnexpectedResponseError)
    async def unexpectedresponseerror_handler(
        request: Request, exc: UnexpectedResponseError
    ):
        """Execute unexpectedresponseerror_handler operation.

        Args:
            request: The request parameter.
            exc: The exc parameter.

        Returns:
            The result of the operation.
        """
        return _app_error_response(request, exc, log_level="error")

    @app.exception_handler(BadInputError)
    async def badinputerror_handler(request: Request, exc: BadInputError):
        """Execute badinputerror_handler operation.

        Args:
            request: The request parameter.
            exc: The exc parameter.

        Returns:
            The result of the operation.
        """
        return _app_error_response(request, exc, log_level="warning")

    @app.exception_handler(NotFoundError)
    async def notfounderror_handler(request: Request, exc: NotFoundError):
        """Execute notfounderror_handler operation.

        Args:
            request: The request parameter.
            exc: The exc parameter.

        Returns:
            The result of the operation.
        """
        return _app_error_response(request, exc, log_level="info")

    @app.exception_handler(UnauthorizedError)
    async def unauthorizederror_handler(request: Request, exc: UnauthorizedError):
        """Execute unauthorizederror_handler operation.

        Args:
            request: The request parameter.
            exc: The exc parameter.

        Returns:
            The result of the operation.
        """
        return _app_error_response(request, exc, log_level="warning")

    @app.exception_handler(ForbiddenError)
    async def forbiddenerror_handler(request: Request, exc: ForbiddenError):
        """Execute forbiddenerror_handler operation.

        Args:
            request: The request parameter.
            exc: The exc parameter.

        Returns:
            The result of the operation.
        """
        return _app_error_response(request, exc, log_level="warning")

    @app.exception_handler(ConflictError)
    async def conflicterror_handler(request: Request, exc: ConflictError):
        """Execute conflicterror_handler operation.

        Args:
            request: The request parameter.
            exc: The exc parameter.

        Returns:
            The result of the operation.
        """
        return _app_error_response(request, exc, log_level="warning")

    @app.exception_handler(RateLimitError)
    async def ratelimiterror_handler(request: Request, exc: RateLimitError):
        """Execute ratelimiterror_handler operation.

        Args:
            request: The request parameter.
            exc: The exc parameter.

        Returns:
            The result of the operation.
        """
        return _app_error_response(request, exc, log_level="info")

    @app.exception_handler(ServiceUnavailableError)
    async def serviceunavailableerror_handler(
        request: Request, exc: ServiceUnavailableError
    ):
        """Execute serviceunavailableerror_handler operation.

        Args:
            request: The request parameter.
            exc: The exc parameter.

        Returns:
            The result of the operation.
        """
        return _app_error_response(request, exc, log_level="error")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unhandled exceptions to avoid leaking internals."""
    urn = getattr(request.state, "urn", None) or ""
    logger.exception("Unhandled exception occurred while processing request.", urn=urn)
    response_dto = IResponseAPIDTO(
        transactionUrn=urn,
        status=APIStatus.FAILED,
        responseMessage="Internal server error.",
        responseKey="error_internal_server_error",
        data={},
        errors=None,
    )
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=response_dto.model_dump(),
        headers=HttpHeader().get_reference_urn_header(
            reference_urn=request.headers.get(HttpHeader.X_REFERENCE_URN)
        ),
    )


def _health_transaction_urn(request: Request) -> str:
    """Transaction URN for health JSON and ``x-transaction-urn`` (always non-empty ``urn:req:...``).

    Reuses :attr:`request.state.urn` from RequestContext middleware when it is already a
    non-empty string (normalizes to ``urn:...``). Otherwise assigns a new id on ``request.state``.
    """
    existing = getattr(request.state, "urn", None)
    if isinstance(existing, str):
        s = existing.strip()
        if s:
            request.state.urn = s
            return s

    urn = str(uuid4())
    request.state.urn = urn
    return urn


def _health_json_response(
    request: Request,
    *,
    http_ok: bool,
    response_key: str,
    response_message: str,
    data: dict,
) -> JSONResponse:
    """Return a :class:`IResponseDTO` envelope for health endpoints."""
    txn_urn = _health_transaction_urn(request)
    ref_header = request.headers.get(HttpHeader.X_REFERENCE_URN)
    dto = IResponseAPIDTO(
        transactionUrn=txn_urn,
        status=APIStatus.SUCCESS if http_ok else APIStatus.FAILED,
        responseMessage=response_message,
        responseKey=response_key,
        data=data,
        errors=None,
        reference_urn=ref_header,
    )
    code = HTTPStatus.OK if http_ok else HTTPStatus.SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=code,
        content=dto.model_dump(mode="json"),
        headers=HttpHeader().correlation_response_headers(
            reference_urn=ref_header,
            transaction_urn=txn_urn,
        ),
    )


@app.get("/health", tags=["Health"])
async def health_check(request: Request):
    """Production health check endpoint with dependency status.

    Performs comprehensive health checks on:
    - Application status
    - DataI connectivity (if configured)
    - Redis cache connectivity (if configured)
    - Application version

    Used by load balancers, container orchestrators (Kubernetes, Docker Swarm),
    and monitoring systems to verify application health.

    Returns:
        IResponseDTO envelope with dependency details in ``data``.

    Example:
        >>> curl http://localhost:8000/health
        {
            "transactionUrn": "urn:req:...",
            "status": "SUCCESS",
            "responseMessage": "All dependencies report healthy.",
            "responseKey": "success_health",
            "data": {
                "status": "healthy",
                "database": "connected",
                "redis": "connected",
                "version": "1.5.0",
                "timestamp": "2024-01-01T00:00:00Z",
                "uptimeSeconds": 3600
            },
            "errors": null,
            "metadata": null,
            "timestamp": "...",
            "referenceUrn": null
        }

    HTTP Status Codes:
        200: All systems healthy
        503: One or more dependencies unhealthy

    """
    try:
        api_version = version("fast-mvc")
    except PackageNotFoundError:
        api_version = "1.5.0"

    # Health check results
    health_status: dict[str, str | int] = {
        "status": HEALTH_STATUS_HEALTHY,
        "version": api_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Check database connectivity
    db_status: str = DEPENDENCY_NOT_CONFIGURED
    try:
        from start_utils import db_session

        if db_session is not None:
            # Try to execute a simple query to verify connectivity
            if hasattr(db_session, "execute"):
                # SQLAlchemy session
                from sqlalchemy import text

                db_session.execute(text(HEALTH_CHECK_SQL_PING))
                db_status = DEPENDENCY_CONNECTED
            else:
                db_status = DEPENDENCY_CONNECTED
        else:
            db_status = DEPENDENCY_NOT_CONFIGURED
    except Exception as e:
        db_status = dependency_disconnected_message(e)
        health_status["status"] = HEALTH_STATUS_UNHEALTHY
        logger.error(f"Health check: DataI connection failed - {e}")

    health_status["database"] = db_status

    # Check Redis connectivity
    redis_status: str = DEPENDENCY_NOT_CONFIGURED
    try:
        from start_utils import redis_session

        if redis_session is not None:
            # Try a ping to verify connectivity
            if hasattr(redis_session, "ping"):
                redis_session.ping()
                redis_status = DEPENDENCY_CONNECTED
            else:
                redis_status = DEPENDENCY_CONNECTED
        else:
            redis_status = DEPENDENCY_NOT_CONFIGURED
    except Exception as e:
        redis_status = dependency_disconnected_message(e)
        health_status["status"] = HEALTH_STATUS_UNHEALTHY
        logger.error(f"Health check: Redis connection failed - {e}")

    health_status["redis"] = redis_status

    # Add uptime if available (requires app start time tracking)
    if hasattr(app.state, "start_time"):
        uptime_seconds = (
            datetime.now(timezone.utc) - app.state.start_time
        ).total_seconds()
        health_status["uptime_seconds"] = int(uptime_seconds)

    # Log health check result
    logger.info(
        f"Health check: status={health_status['status']}, "
        f"database={db_status}, redis={redis_status}"
    )

    ok = health_status["status"] == HEALTH_STATUS_HEALTHY
    data_payload = {
        "status": health_status["status"],
        "version": health_status["version"],
        "timestamp": health_status["timestamp"],
        "database": db_status,
        "redis": redis_status,
    }
    if "uptime_seconds" in health_status:
        data_payload["uptimeSeconds"] = health_status["uptime_seconds"]

    return _health_json_response(
        request,
        http_ok=ok,
        response_key="success_health" if ok else "error_health_unhealthy",
        response_message=(
            "All dependencies report healthy."
            if ok
            else "One or more dependencies are unhealthy."
        ),
        data=data_payload,
    )


@app.get("/health/live", tags=["Health"])
async def liveness_probe(request: Request):
    """Kubernetes liveness probe endpoint.

    Lightweight check that indicates the application is running.
    If this fails, Kubernetes will restart the container.

    Returns:
        IResponseDTO envelope; liveness payload is in ``data``.

    Example:
        >>> curl http://localhost:8000/health/live
        {
            "transactionUrn": "urn:req:...",
            "status": "SUCCESS",
            "responseMessage": "Application process is alive.",
            "responseKey": "success_health_live",
            "data": {"status": "alive"},
            ...
        }

    """
    return _health_json_response(
        request,
        http_ok=True,
        response_key="success_health_live",
        response_message="Application process is alive.",
        data={"status": LIVENESS_ALIVE},
    )


@app.get("/health/ready", tags=["Health"])
async def readiness_probe(request: Request):
    """Kubernetes readiness probe endpoint.

    Checks if the application is ready to receive traffic.
    Includes dependency health checks (database, Redis).

    Returns:
        IResponseDTO envelope with readiness and checks in ``data``.

    Example:
        >>> curl http://localhost:8000/health/ready
        {
            "transactionUrn": "urn:req:...",
            "status": "SUCCESS",
            "responseMessage": "Application is ready to receive traffic.",
            "responseKey": "success_health_ready",
            "data": {
                "status": "ready",
                "checkedAt": "2024-01-01T00:00:00+00:00",
                "checks": {"database": "connected", "redis": "connected"}
            },
            ...
        }

    HTTP Status Codes:
        200: Application is ready to receive traffic
        503: Application is not ready (dependencies unavailable)

    """
    checks = {}
    is_ready = True

    # Check database
    try:
        from start_utils import db_session

        if db_session is not None and hasattr(db_session, "execute"):
            from sqlalchemy import text

            db_session.execute(text(HEALTH_CHECK_SQL_PING))
            checks["database"] = DEPENDENCY_CONNECTED
        else:
            checks["database"] = DEPENDENCY_NOT_CONFIGURED
    except Exception as e:
        checks["database"] = dependency_disconnected_message(e)
        is_ready = False

    # Check Redis
    try:
        from start_utils import redis_session

        if redis_session is not None and hasattr(redis_session, "ping"):
            redis_session.ping()
            checks["redis"] = DEPENDENCY_CONNECTED
        else:
            checks["redis"] = DEPENDENCY_NOT_CONFIGURED
    except Exception as e:
        checks["redis"] = dependency_disconnected_message(e)
        is_ready = False

    status = READINESS_READY if is_ready else READINESS_NOT_READY
    checked_at = datetime.now(timezone.utc).isoformat()
    data_ready = {
        "status": status,
        "checkedAt": checked_at,
        "checks": checks,
    }

    return _health_json_response(
        request,
        http_ok=is_ready,
        response_key="success_health_ready" if is_ready else "error_health_not_ready",
        response_message=(
            "Application is ready to receive traffic."
            if is_ready
            else "Application is not ready to receive traffic."
        ),
        data=data_ready,
    )


# =============================================================================
# MIDDLEWARE CONFIGURATION (using fast-middleware package)
# =============================================================================

logger.info("Initializing middleware stack with fastmiddleware")

# Request Context Middleware - request ID/URN and tracking (from fast-middleware; must be first)
app.add_middleware(RequestContextMiddleware)

# Trusted Host Middleware - Prevents host header attacks
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# CORS Middleware - Cross-Origin Resource Sharing (see utilities.cors)
app.add_middleware(CORSMiddleware, **get_cors_middleware_kwargs())

# Security Headers Middleware - CSP, HSTS, X-Frame-Options, etc. (see utilities.security_headers)
app.add_middleware(
    SecurityHeadersMiddleware,
    config=get_security_headers_middleware_config(),
)


# Rate Limiting Middleware - Protects against abuse
# Base middleware matches exclude_paths by exact URL only; liveness/readiness live under
# /health/* so we skip the whole prefix (including /health/live) for probes.
class _HealthPrefixRateLimitMiddleware(RateLimitMiddleware):
    def should_skip(self, request: Request) -> bool:
        if request.url.path.startswith("/health"):
            return True
        return super().should_skip(request)


if not IS_TEST_RUN:
    rate_limit_config = RateLimitConfig(
        requests_per_minute=RATE_LIMIT_REQUESTS_PER_MINUTE,
        requests_per_hour=RATE_LIMIT_REQUESTS_PER_HOUR,
        burst_limit=RATE_LIMIT_BURST_LIMIT,
        window_size=RATE_LIMIT_WINDOW_SECONDS,
        strategy="sliding",  # Use sliding window algorithm
    )
    app.add_middleware(
        cast(Any, _HealthPrefixRateLimitMiddleware),
        config=rate_limit_config,
        exclude_paths=None,
    )

# Logging Middleware - Request/Response logging
app.add_middleware(
    LoggingMiddleware,
    log_request_body=False,  # Don't log sensitive request bodies
    log_response_body=False,
    exclude_paths=set(docs_logging_exclude_paths()),
)

# Timing Middleware - Response time tracking
app.add_middleware(
    ResponseTimingMiddleware,
    header_name=HttpHeader.X_PROCESS_TIME,
)

# Authentication Middleware - JWT validation (custom, app-specific)
app.add_middleware(AuthenticationMiddleware)

# OpenAPI /docs, /redoc, /openapi.json — HTTP Basic when DOCS_USERNAME + DOCS_PASSWORD are set
app.add_middleware(DocsBasicAuthMiddleware)

logger.info("Initialized middleware stack with fastmiddleware")
if docs_auth_configured():
    logger.info(
        "API docs (Swagger/ReDoc under /docs and /redoc, OpenAPI at {}) require "
        "HTTP Basic auth (DOCS_USERNAME / DOCS_PASSWORD).",
        normalized_openapi_url(),
    )
else:
    logger.info(
        "API docs are public; set DOCS_USERNAME and DOCS_PASSWORD to restrict access."
    )

# =============================================================================
# ROUTER CONFIGURATION
# =============================================================================

logger.info("Initializing routers")
if UserRouter is not None:
    app.include_router(UserRouter, tags=["User"])
if ExampleItemRouter is not None:
    app.include_router(ExampleItemRouter)
    logger.info("Example Item API enabled at /items")
if WebSocketRouter is not None:
    app.include_router(WebSocketRouter)
if NotificationsRouter is not None:
    app.include_router(NotificationsRouter)
if ChannelsRouter is not None:
    app.include_router(ChannelsRouter)
if DashboardRouter is not None:
    app.include_router(cast(APIRouter, DashboardRouter))
if MainApiRouter is not None:
    app.include_router(MainApiRouter)
    logger.info("Nested Production API enabled at /api/v1/examples")
logger.info("Initialized routers")


# =============================================================================
# LIFECYCLE EVENTS
# =============================================================================


@app.on_event("startup")
async def on_startup():
    """Application startup event handler.

    Called when the FastAPI application starts. Use for:
    - Initializing database connections
    - Loading cached data
    - Starting background tasks
    - Logging startup information
    """
    from datetime import datetime, timezone

    # Track application start time for uptime calculation
    app.state.start_time = datetime.now(timezone.utc)

    logger.info("Application startup event triggered")
    logger.info(f"FastMVC API starting on {HOST}:{PORT}")
    logger.info("Using fast-middleware for request processing")
    curl_examples = route_export_engine.build_curl_examples()
    app.state.route_curl_examples = curl_examples
    collection_path, env_path = route_export_engine.export_postman_collection()
    env_msg = (
        f", environment {env_path}"
        if env_path is not None
        else " (collection-only; set POSTMAN_EXPORT_ENVIRONMENT=1 to also write environment file)"
    )
    logger.info(
        f"Generated {len(curl_examples)} cURL examples; Postman collection {collection_path}"
        f"{env_msg} — variables: base_url, reference_id, reference_number, token"
    )
    route_export_engine.clear_memory()


@app.on_event("shutdown")
async def on_shutdown():
    """Application shutdown event handler.

    Called when the FastAPI application shuts down. Use for:
    - Closing database connections
    - Flushing caches
    - Stopping background tasks
    - Cleanup operations
    """
    logger.info("Application shutdown event triggered")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)
