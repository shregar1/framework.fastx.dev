"""FastX Application Entry Point.

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
    UVICORN_LOG_LEVEL: Uvicorn log level only — default ``error`` (quiet); use ``warning`` or ``info`` for more Uvicorn console output
    LOG_LEVEL: Application Loguru level (TRACE, DEBUG, INFO, …); default INFO. DEBUG shows DEBUG and above (including INFO lines)
    JWT_AUTH_ENABLED: Enable JWT authentication (default: false)
    RATE_LIMIT_REQUESTS_PER_MINUTE: Rate limit per minute (default: 60)
    RATE_LIMIT_REQUESTS_PER_HOUR: Rate limit per hour (default: 1000)
    RATE_LIMIT_WINDOW_SECONDS: Rate limit window size in seconds (default: 60)
    RATE_LIMIT_BURST_LIMIT: Maximum burst requests allowed (default: 10)
    POSTMAN_EXPORT_ENVIRONMENT: Set to 1/true to also write environment JSON under postman/ on boot
    POSTMAN_COLLECTION_NAME: Override Postman collection/env title (default: APP_NAME from env → git repo folder name → fastx)
    POSTMAN_BASE_URL: Override default base_url in collection/environment (else HOST:PORT)
    POSTMAN_OUTPUT_DIR: Directory for Postman exports (default: postman)
    POSTMAN_COLLECTION_FILE: Collection JSON path (default: postman/postman_collection.json)
    POSTMAN_ENV_FILE: Environment JSON filename or path (default: postman/postman_environment.json)
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

"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from http import HTTPStatus
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import uvicorn  # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

load_dotenv()
from constants.logging_setup import configure_loguru

configure_loguru()

# Import middlewares from fast-middleware package (distribution exposes ``fastmiddleware``)
from fastmiddleware import (  # pyright: ignore[reportMissingImports]
    AuthConfig,
    AuthenticationMiddleware,
    CORSMiddleware,
    JWTAuthBackend,
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
from loguru import logger  # noqa: E402 — after configure_loguru()

from constants.api_status import APIStatus
from constants.default import Default
from constants.environment import EnvironmentVar
from constants.health import (
    DEPENDENCY_CONNECTED,
    DEPENDENCY_NOT_CONFIGURED,
    HEALTH_CHECK_SQL_PING,
    HEALTH_STATUS_HEALTHY,
    HEALTH_STATUS_UNHEALTHY,
    HealthMessageUtil,
    LIVENESS_ALIVE,
    READINESS_NOT_READY,
    READINESS_READY,
)
from constants.http_header import HttpHeader
from constants.route import RouteConstant
from constants.response_key import ResponseKey
from core.exception_handlers import ApplicationExceptionHandlers
from core.route_export_engine import RouteExportEngine
from middlewares import (
    DocsAuthConfig,
    DocsBasicAuthMiddleware,
)
from utilities.cors import CorsConfigUtility
from utilities.datetime import DateTimeUtility
from utilities.env import EnvironmentParserUtility
from utilities.security_headers import SecurityHeadersUtility

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

# Domain errors (requires fastx-mvc[platform])
try:
    import fast_platform.errors as platform_errors  # pyright: ignore[reportMissingImports]

    HAS_PLATFORM_ERRORS = True
except ImportError:
    platform_errors = None  # type: ignore[assignment]
    HAS_PLATFORM_ERRORS = False


HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RATE_LIMIT_REQUESTS_PER_MINUTE: int = EnvironmentParserUtility.get_int_with_logging(
    EnvironmentVar.REQUESTS_PER_MINUTE,
    Default.RATE_LIMIT_REQUESTS_PER_MINUTE,
)
RATE_LIMIT_REQUESTS_PER_HOUR: int = EnvironmentParserUtility.get_int_with_logging(
    EnvironmentVar.REQUESTS_PER_HOUR,
    Default.RATE_LIMIT_REQUESTS_PER_HOUR,
)
RATE_LIMIT_WINDOW_SECONDS: int = EnvironmentParserUtility.get_int_with_logging(
    EnvironmentVar.WINDOW_SECONDS,
    Default.RATE_LIMIT_WINDOW_SECONDS,
)
RATE_LIMIT_BURST_LIMIT: int = EnvironmentParserUtility.get_int_with_logging(
    EnvironmentVar.BURST_LIMIT,
    Default.RATE_LIMIT_BURST_LIMIT,
)

IS_TEST_RUN = EnvironmentParserUtility.get_bool_with_logging(
    EnvironmentVar.IS_TEST_RUN,
    False,
) or EnvironmentParserUtility.get_bool_with_logging(
    EnvironmentVar.TESTING,
    False,
)
"""Test run flag (default: false)."""

JWT_AUTH_ENABLED: bool = EnvironmentParserUtility.get_bool_with_logging(
    EnvironmentVar.JWT_AUTH_ENABLED,
    False,
)
"""JWT authentication enabled (default: false)."""

if not IS_TEST_RUN and EnvironmentParserUtility.get_bool_with_logging(
        EnvironmentVar.VALIDATE_CONFIG,
        True,
    ):
    from utilities.validator import validate_config_or_exit  # pyright: ignore[reportMissingImports]
    validate_config_or_exit()


def print_startup_banner() -> None:
    """Print a beautiful startup banner with server information (monochrome)."""
    from constants.banner import  BannerConfig

    banner_config = BannerConfig()
    # Print banner
    print(banner_config.get_banner())

    # Server info
    print(banner_config.SERVER_INFO_HEADER)
    print(f"   {'Host:':<{banner_config.LABEL_WIDTH}} {HOST}")
    print(f"   {'Port:':<{banner_config.LABEL_WIDTH}} {PORT}")
    print(f"   {'URL:':<{banner_config.LABEL_WIDTH}} http://{HOST}:{PORT}")
    print()

    # API Documentation
    print(banner_config.API_DOCS_HEADER)
    print(f"   {'Swagger UI:':<{banner_config.LABEL_WIDTH}} http://{HOST}:{PORT}/docs")
    print(f"   {'ReDoc:':<{banner_config.LABEL_WIDTH}} http://{HOST}:{PORT}/redoc")
    print(f"   {'OpenAPI:':<{banner_config.LABEL_WIDTH}} http://{HOST}:{PORT}/openapi.json")
    print()

    # Health Endpoints
    print(banner_config.HEALTH_ENDPOINTS_HEADER)
    print(f"   {'Live:':<{banner_config.LABEL_WIDTH}} http://{HOST}:{PORT}/health/live")
    print(f"   {'Ready:':<{banner_config.LABEL_WIDTH}} http://{HOST}:{PORT}/health/ready")
    print(f"   {'Full:':<{banner_config.LABEL_WIDTH}} http://{HOST}:{PORT}/health")
    print()

    # Environment
    print(banner_config.ENVIRONMENT_HEADER)
    print(f"   {'Mode:':<{banner_config.LABEL_WIDTH}} {EnvironmentParserUtility.parse_str(EnvironmentVar.APP_ENV, 'development')}")
    print(f"   {'Debug:':<{banner_config.LABEL_WIDTH}} {EnvironmentParserUtility.parse_bool(EnvironmentVar.DEBUG, False)}")
    print(f"   {'Workers:':<{banner_config.LABEL_WIDTH}} {EnvironmentParserUtility.parse_int('WORKERS', 1)}")
    print()

    # Features
    jwt_enabled = EnvironmentParserUtility.parse_bool(EnvironmentVar.JWT_AUTH_ENABLED, False)

    print(banner_config.FEATURES_HEADER)
    print(f"   {banner_config.FEATURE_ENABLED if jwt_enabled else banner_config.FEATURE_DISABLED} JWT Auth")
    print(f"   {banner_config.FEATURE_ENABLED} Request Tracing (URN)")
    print(f"   {banner_config.FEATURE_ENABLED} Auto-generated API Docs")
    print(f"   {banner_config.FEATURE_ENABLED} Middleware Stack")
    print()

    print(banner_config.READY_MESSAGE)
    print()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup and shutdown (replaces deprecated ``@app.on_event`` handlers)."""
    app.state.start_time = DateTimeUtility.utc_now()

    # Print beautiful startup banner
    print_startup_banner()

    logger.info("Application startup event triggered")
    logger.info(f"FastX API starting on {HOST}:{PORT}")
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
        f"{env_msg} — variables: base_url, reference_urn, reference_number, token, refresh_token"
    )
    route_export_engine.clear_memory()

    # BEGINNER TEMPLATE: optional gRPC transport (removable).
    # Enable via GRPC_ENABLED=true (see `.env.example`).
    from core.optional_grpc import maybe_start_grpc, maybe_stop_grpc  # pyright: ignore[reportMissingImports]
    await maybe_start_grpc(app)

    yield

    logger.info("Application shutdown event triggered")

    # Best-effort shutdown of the optional gRPC transport.
    await maybe_stop_grpc(app)


# Initialize FastAPI application (openapi_url must match middlewares.docs_auth)
app = FastAPI(
    title=EnvironmentParserUtility.parse_str(EnvironmentVar.APP_NAME, "FastX API"),
    description="Production-grade FastAPI application with MVC architecture.",
    version=EnvironmentParserUtility.parse_str(EnvironmentVar.APP_VERSION, "1.0.1"),
    docs_url=None,  # Custom docs setup below
    redoc_url=None,
    openapi_url=DocsAuthConfig.normalized_openapi_url(),
    lifespan=lifespan,
)
route_export_engine = RouteExportEngine(app)
route_export_engine.install()

# Setup custom FastX branded documentation
try:
    from core.docs import setup_custom_docs

    setup_custom_docs(app)
except ImportError:
    # Fallback to default docs if custom setup fails
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"

# Optional Datadog / OpenTelemetry integration (requires fast-platform)
if configure_datadog and EnvironmentParserUtility.get_bool_with_logging(
    EnvironmentVar.DATADOG_ENABLED,
    False,
):
    configure_datadog()

if configure_otel and EnvironmentParserUtility.get_bool_with_logging(
    EnvironmentVar.TELEMETRY_ENABLED,
    False,
):
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
            headers={
                HttpHeader.CACHE_CONTROL: HttpHeader.CACHE_CONTROL_VALUE_NO_CACHE,
            },
        )
    return HTMLResponse(
        "<!DOCTYPE html><html><body><p>FastX API</p></body></html>",
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


if HAS_PLATFORM_ERRORS:
    assert platform_errors is not None
    ApplicationExceptionHandlers.register_platform_handlers(app, platform_errors)
ApplicationExceptionHandlers.register_global_handler(app)


def _health_json_response(
    request: Request,
    *,
    http_ok: bool,
    response_key: str,
    response_message: str,
    data: dict,
) -> JSONResponse:
    """Return a :class:`IResponseDTO` envelope for health endpoints."""
    txn_urn = getattr(request.state, "urn", str(uuid4()))
    ref_header = request.headers.get(HttpHeader.X_REFERENCE_URN, "")
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
        api_version = version("fastx-mvc")
    except PackageNotFoundError:
        api_version = "1.5.0"

    # Health check results
    health_status: dict[str, str | int] = {
        "status": HEALTH_STATUS_HEALTHY,
        "version": api_version,
        "timestamp": datetime.utcnow().isoformat() + "Z",
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
        db_status = HealthMessageUtil.dependency_disconnected_message(e)
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
        redis_status = HealthMessageUtil.dependency_disconnected_message(e)
        health_status["status"] = HEALTH_STATUS_UNHEALTHY
        logger.error(f"Health check: Redis connection failed - {e}")

    health_status["redis"] = redis_status

    # Add uptime if available (requires app start time tracking)
    if hasattr(app.state, "start_time"):
        from datetime import timezone

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
        response_key=(
            ResponseKey.SUCCESS_HEALTH if ok else ResponseKey.ERROR_HEALTH_UNHEALTHY
        ),
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
        response_key=ResponseKey.SUCCESS_HEALTH_LIVE,
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
        checks["database"] = HealthMessageUtil.dependency_disconnected_message(e)
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
        checks["redis"] = HealthMessageUtil.dependency_disconnected_message(e)
        is_ready = False

    status = READINESS_READY if is_ready else READINESS_NOT_READY
    checked_at = DateTimeUtility.utc_now_iso()
    data_ready = {
        "status": status,
        "checkedAt": checked_at,
        "checks": checks,
    }

    return _health_json_response(
        request,
        http_ok=is_ready,
        response_key=(
            ResponseKey.SUCCESS_HEALTH_READY
            if is_ready
            else ResponseKey.ERROR_HEALTH_NOT_READY
        ),
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
app.add_middleware(CORSMiddleware, **CorsConfigUtility.get_middleware_kwargs())

# Security Headers Middleware - CSP, HSTS, X-Frame-Options, etc. (see utilities.security_headers)
app.add_middleware(
    SecurityHeadersMiddleware,
    config=SecurityHeadersUtility.get_middleware_config(),
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
    exclude_paths=set(DocsAuthConfig.docs_logging_exclude_paths()),
)

# Timing Middleware - Response time tracking
app.add_middleware(
    ResponseTimingMiddleware,
    header_name=HttpHeader.X_PROCESS_TIME,
)

# Authentication Middleware — JWT via fastmiddleware (Bearer + pyjwt)
if JWT_AUTH_ENABLED:
    _jwt_secret = EnvironmentParserUtility.parse_str(
        EnvironmentVar.SECRET_KEY,
        Default.SECRET_KEY,
    )
    _jwt_algorithm = EnvironmentParserUtility.parse_str(
        EnvironmentVar.ALGORITHM,
        Default.ALGORITHM,
    )
    if not _jwt_secret.strip():
        logger.warning(
            "JWT_AUTH_ENABLED is true but SECRET_KEY is empty; JWT middleware not registered."
        )
    else:
        app.add_middleware(
            AuthenticationMiddleware,
            backend=JWTAuthBackend(secret=_jwt_secret, algorithm=_jwt_algorithm),
            config=AuthConfig(exclude_paths=set(RouteConstant.UNPROTECTED_ROUTES)),
        )

# OpenAPI /docs, /redoc, /openapi.json — HTTP Basic when DOCS_USERNAME + DOCS_PASSWORD are set
app.add_middleware(DocsBasicAuthMiddleware)

logger.info("Initialized middleware stack with fastmiddleware")
if DocsAuthConfig.is_auth_configured():
    logger.info(
        "API docs (Swagger/ReDoc under /docs and /redoc, OpenAPI at {}) require "
        "HTTP Basic auth (DOCS_USERNAME / DOCS_PASSWORD).",
        DocsAuthConfig.normalized_openapi_url(),
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
# MAIN ENTRY POINT
# =============================================================================

def _uvicorn_log_level() -> str:
    """Uvicorn console verbosity; does not affect application ``loguru`` logging."""
    raw = (os.getenv(EnvironmentVar.UVICORN_LOG_LEVEL) or "error").strip().lower()
    allowed = {"critical", "error", "warning", "info", "debug", "trace"}
    return raw if raw in allowed else "error"


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level=_uvicorn_log_level(),
    )
