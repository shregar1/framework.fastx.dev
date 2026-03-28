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
from http import HTTPStatus
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, cast

import uvicorn  # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse

# Import middlewares from fast-middleware package
from fastmiddleware import (  # pyright: ignore[reportMissingImports]
    CORSMiddleware,
    LoggingMiddleware,
    RateLimitConfig,
    RateLimitMiddleware,
    RequestContextMiddleware,
    ResponseTimingMiddleware,
    SecurityHeadersConfig,
    SecurityHeadersMiddleware,
    TrustedHostMiddleware,
)
from loguru import logger

from constants.api_status import APIStatus
from constants.default import Default
from constants.http_headers import X_REFERENCE_URN, x_reference_urn_headers

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

from dtos.responses.I import IResponseDTO

# Domain errors (requires pyfastmvc[platform])
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
from middlewares import AuthenticationMiddleware

# Configuration validation - fail fast on misconfig
# Set VALIDATE_CONFIG=false to skip validation
# Tests skip strict startup validation to avoid env-coupled imports.
IS_TEST_RUN = (
    os.getenv("PYTEST_CURRENT_TEST") is not None
    or os.getenv("TESTING", "").lower() in ("true", "1", "yes", "on")
)
try:
    if (
        not IS_TEST_RUN
        and os.getenv("VALIDATE_CONFIG", "true").lower()
        not in ("false", "0", "no", "off")
    ):
        from config.validator import validate_config_or_exit

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


# Initialize FastAPI application
app = FastAPI(
    title="FastMVC API",
    description="Production-grade FastAPI application with MVC architecture. Includes example Item API at /items",
    version="1.0.1",
    docs_url=None,  # Custom docs setup below
    redoc_url=None,
)

# Setup custom FastMVC branded documentation
try:
    from core.docs import setup_custom_docs

    setup_custom_docs(app)
except ImportError:
    # Fallback to default docs if custom setup fails
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"

# Load environment variables
load_dotenv()
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
        headers=x_reference_urn_headers(request.headers.get(X_REFERENCE_URN)),
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

    response_dto = IResponseDTO(
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
        headers=x_reference_urn_headers(request.headers.get(X_REFERENCE_URN)),
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
    response_dto = IResponseDTO(
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
        headers=x_reference_urn_headers(request.headers.get(X_REFERENCE_URN)),
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Production health check endpoint with dependency status.

    Performs comprehensive health checks on:
    - Application status
    - DataI connectivity (if configured)
    - Redis cache connectivity (if configured)
    - Application version

    Used by load balancers, container orchestrators (Kubernetes, Docker Swarm),
    and monitoring systems to verify application health.

    Returns:
        HealthCheckResponse: Status of all system components.

    Example:
        >>> curl http://localhost:8000/health
        {
            "status": "healthy",
            "dataI": "connected",
            "redis": "connected",
            "version": "1.5.0",
            "timestamp": "2024-01-01T00:00:00Z",
            "uptime_seconds": 3600
        }

    HTTP Status Codes:
        200: All systems healthy
        503: One or more dependencies unhealthy

    """
    from datetime import datetime, timezone

    try:
        api_version = version("pyfastmvc")
    except PackageNotFoundError:
        api_version = "1.5.0"

    # Health check results
    health_status: dict[str, str | int] = {
        "status": "healthy",
        "version": api_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Check dataI connectivity
    db_status: str = "not_configured"
    try:
        from start_utils import db_session

        if db_session is not None:
            # Try to execute a simple query to verify connectivity
            if hasattr(db_session, "execute"):
                # SQLAlchemy session
                from sqlalchemy import text

                db_session.execute(text("SELECT 1"))
                db_status = "connected"
            else:
                db_status = "connected"
        else:
            db_status = "not_configured"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        health_status["status"] = "unhealthy"
        logger.error(f"Health check: DataI connection failed - {e}")

    health_status["dataI"] = db_status

    # Check Redis connectivity
    redis_status: str = "not_configured"
    try:
        from start_utils import redis_session

        if redis_session is not None:
            # Try a ping to verify connectivity
            if hasattr(redis_session, "ping"):
                redis_session.ping()
                redis_status = "connected"
            else:
                redis_status = "connected"
        else:
            redis_status = "not_configured"
    except Exception as e:
        redis_status = f"disconnected: {str(e)}"
        health_status["status"] = "unhealthy"
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
        f"dataI={db_status}, redis={redis_status}"
    )

    # Return appropriate HTTP status code
    status_code = (
        HTTPStatus.OK
        if health_status["status"] == "healthy"
        else HTTPStatus.SERVICE_UNAVAILABLE
    )

    return JSONResponse(status_code=status_code, content=health_status)


@app.get("/health/live", tags=["Health"])
async def liveness_probe():
    """Kubernetes liveness probe endpoint.

    Lightweight check that indicates the application is running.
    If this fails, Kubernetes will restart the container.

    Returns:
        dict: Simple status indicating the application is alive.

    Example:
        >>> curl http://localhost:8000/health/live
        {"status": "alive"}

    """
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def readiness_probe():
    """Kubernetes readiness probe endpoint.

    Checks if the application is ready to receive traffic.
    Includes dependency health checks (dataI, Redis).

    Returns:
        dict: Readiness status with dependency information.

    Example:
        >>> curl http://localhost:8000/health/ready
        {
            "status": "ready",
            "checks": {
                "dataI": "connected",
                "redis": "connected"
            }
        }

    HTTP Status Codes:
        200: Application is ready to receive traffic
        503: Application is not ready (dependencies unavailable)

    """
    from datetime import datetime, timezone

    checks = {}
    is_ready = True

    # Check dataI
    try:
        from start_utils import db_session

        if db_session is not None and hasattr(db_session, "execute"):
            from sqlalchemy import text

            db_session.execute(text("SELECT 1"))
            checks["dataI"] = "connected"
        else:
            checks["dataI"] = "not_configured"
    except Exception as e:
        checks["dataI"] = f"disconnected: {str(e)}"
        is_ready = False

    # Check Redis
    try:
        from start_utils import redis_session

        if redis_session is not None and hasattr(redis_session, "ping"):
            redis_session.ping()
            checks["redis"] = "connected"
        else:
            checks["redis"] = "not_configured"
    except Exception as e:
        checks["redis"] = f"disconnected: {str(e)}"
        is_ready = False

    status = "ready" if is_ready else "not_ready"
    status_code = HTTPStatus.OK if is_ready else HTTPStatus.SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
        },
    )


# =============================================================================
# MIDDLEWARE CONFIGURATION (using fast-middleware package)
# =============================================================================

logger.info("Initializing middleware stack with fastmiddleware")

# Request Context Middleware - request ID/URN and tracking (from fast-middleware; must be first)
app.add_middleware(RequestContextMiddleware)

# Trusted Host Middleware - Prevents host header attacks
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# CORS Middleware - Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# Security Headers Middleware - CSP, HSTS, X-Frame-Options, etc.
security_config = SecurityHeadersConfig(
    enable_hsts=True,
    hsts_max_age=31536000,
    hsts_include_subdomains=True,
    hsts_preload=False,
    x_frame_options="DENY",
    x_content_type_options="nosniff",
    x_xss_protection="1; mode=block",
    referrer_policy="strict-origin-when-cross-origin",
    # Allow Swagger/ReDoc assets from jsdelivr and Google Fonts (launch page, docs UIs)
    content_security_policy=(
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
        "font-src 'self' data: https://fonts.gstatic.com; "
        "img-src 'self' data: https: blob:; "
        "connect-src 'self'"
    ),
    remove_server_header=True,
)
app.add_middleware(SecurityHeadersMiddleware, config=security_config)

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
    exclude_paths={"/", "/health", "/docs", "/redoc", "/openapi.json"},
)

# Timing Middleware - Response time tracking
app.add_middleware(
    ResponseTimingMiddleware,
    header_name="X-Process-Time",
)

# Authentication Middleware - JWT validation (custom, app-specific)
app.add_middleware(AuthenticationMiddleware)

logger.info("Initialized middleware stack with fastmiddleware")

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
    - Initializing dataI connections
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


@app.on_event("shutdown")
async def on_shutdown():
    """Application shutdown event handler.

    Called when the FastAPI application shuts down. Use for:
    - Closing dataI connections
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
