"""
FastMVC Application Entry Point.

This is the main FastAPI application module that initializes the web server,
configures middleware, registers routes, and handles application lifecycle events.

Usage:
    Run directly:
        python app.py

    Or with uvicorn:
        uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Environment Variables:
    HOST: Server host address (default: 0.0.0.0)
    PORT: Server port (default: 8000)
    RATE_LIMIT_REQUESTS_PER_MINUTE: Rate limit per minute
    RATE_LIMIT_REQUESTS_PER_HOUR: Rate limit per hour
    RATE_LIMIT_BURST_LIMIT: Maximum burst requests

Endpoints:
    GET /health - Health check endpoint
    POST /user/login - User authentication
    POST /user/register - New user registration
    POST /user/logout - Session termination
"""

import os
from http import HTTPStatus

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Import middlewares from fastmvc-middleware package
from fastmiddleware import (
    CORSMiddleware,
    LoggingMiddleware,
    RateLimitConfig,
    # Rate Limiting
    RateLimitMiddleware,
    SecurityHeadersConfig,
    # Security
    SecurityHeadersMiddleware,
    TimingMiddleware,
    TrustedHostMiddleware,
)
from loguru import logger

from constants.api_status import APIStatus
from constants.default import Default
from controllers.channels import router as ChannelsRouter
from controllers.notifications import router as NotificationsRouter
from controllers.user import router as UserRouter
from controllers.webrtc import router as WebRTCRouter
from core.dashboard.router import router as DashboardRouter
from core.websockets.router import router as WebSocketRouter
from core.observability import configure_datadog, configure_otel
from dtos.responses.base import BaseResponseDTO
from errors.unexpected_response_error import UnexpectedResponseError

# Custom authentication middleware (app-specific with user repository)
from middlewares.authetication import AuthenticationMiddleware
from middlewares.request_context import RequestContextMiddleware


def _get_int_env(name: str, default: int) -> int:
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


app = FastAPI()
# Initialize FastAPI application
app = FastAPI(
    title="FastMVC API",
    description="Production-grade FastAPI application with MVC architecture",
    version="1.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
)

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

# Optional Datadog / OpenTelemetry integration
if os.getenv("DATADOG_ENABLED", "").lower() in {"1", "true", "yes"}:
    configure_datadog()

if os.getenv("TELEMETRY_ENABLED", "").lower() in {"1", "true", "yes"}:
    configure_otel(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Global exception handler for request validation errors.

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
    )


@app.exception_handler(UnexpectedResponseError)
async def unexpected_response_error_handler(
    request: Request, exc: UnexpectedResponseError
):
    """
    Handle application-specific unexpected response errors with a structured payload.
    """
    urn = getattr(request.state, "urn", None) or ""
    logger.error(
        f"UnexpectedResponseError occurred: {exc.responseMessage} "
        f"(key={exc.responseKey}, status={exc.httpStatusCode})",
        urn=urn,
    )
    response_dto = BaseResponseDTO(
        transactionUrn=urn,
        status=APIStatus.FAILED,
        responseMessage=exc.responseMessage,
        responseKey=exc.responseKey,
        data={},
        errors=None,
    )
    return JSONResponse(
        status_code=exc.httpStatusCode,
        content=response_dto.model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unhandled exceptions to avoid leaking internals.
    """
    urn = getattr(request.state, "urn", None) or ""
    logger.exception(
        "Unhandled exception occurred while processing request.", urn=urn
    )
    response_dto = BaseResponseDTO(
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
    )


@app.get("/health")
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Used by load balancers, container orchestrators, and monitoring systems
    to verify the application is running and responsive.

    Returns:
        dict: {"status": "ok"} indicating healthy status.

    Example:
        >>> curl http://localhost:8000/health
        {"status": "ok"}
    """
    logger.info("Health check endpoint called")
    return {"status": "ok"}


# =============================================================================
# MIDDLEWARE CONFIGURATION (using fastmvc-middleware package)
# =============================================================================

logger.info("Initializing middleware stack with fastmiddleware")

# Request Context Middleware - URN generation and request tracking (must be first)
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
    content_security_policy="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    remove_server_header=True,
)
app.add_middleware(SecurityHeadersMiddleware, config=security_config)

# Rate Limiting Middleware - Protects against abuse
rate_limit_config = RateLimitConfig(
    requests_per_minute=RATE_LIMIT_REQUESTS_PER_MINUTE,
    requests_per_hour=RATE_LIMIT_REQUESTS_PER_HOUR,
    burst_limit=RATE_LIMIT_BURST_LIMIT,
    window_size=RATE_LIMIT_WINDOW_SECONDS,
    strategy="sliding",  # Use sliding window algorithm
)
app.add_middleware(RateLimitMiddleware, config=rate_limit_config)

# Logging Middleware - Request/Response logging
app.add_middleware(
    LoggingMiddleware,
    log_request_body=False,  # Don't log sensitive request bodies
    log_response_body=False,
    exclude_paths={"/health", "/docs", "/redoc", "/openapi.json"},
)

# Timing Middleware - Response time tracking
app.add_middleware(
    TimingMiddleware,
    header_name="X-Process-Time",
)

# Authentication Middleware - JWT validation (custom, app-specific)
app.add_middleware(AuthenticationMiddleware)

logger.info("Initialized middleware stack with fastmiddleware")

# =============================================================================
# ROUTER CONFIGURATION
# =============================================================================

logger.info("Initializing routers")
app.include_router(UserRouter, tags=["User"])
app.include_router(WebRTCRouter)
app.include_router(NotificationsRouter)
app.include_router(ChannelsRouter)
app.include_router(DashboardRouter)
app.include_router(WebSocketRouter)
logger.info("Initialized routers")


# =============================================================================
# LIFECYCLE EVENTS
# =============================================================================

@app.on_event("startup")
async def on_startup():
    """
    Application startup event handler.

    Called when the FastAPI application starts. Use for:
    - Initializing database connections
    - Loading cached data
    - Starting background tasks
    - Logging startup information
    """
    logger.info("Application startup event triggered")
    logger.info(f"FastMVC API starting on {HOST}:{PORT}")
    logger.info("Using fastmvc-middleware for request processing")


@app.on_event("shutdown")
async def on_shutdown():
    """
    Application shutdown event handler.

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
