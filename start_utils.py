"""Startup Utilities Module.

This module initializes core application services and loads configuration
on application startup. It provides shared instances of dataI sessions,
cache connections, and configuration values used throughout the application.

Exports:
    - logger: Configured loguru logger instance
    - db_session: SQLAlchemy dataI session
    - redis_session: Redis cache connection
    - Configuration constants (SECRET_KEY, ALGORITHM, etc.)
    - unprotected_routes: Set of routes that don't require authentication
    - callback_routes: Set of webhook/callback routes

Usage:
    >>> from start_utils import logger, db_session, SECRET_KEY
    >>> logger.info("Starting operation")
    >>> user = db_session.query(User).first()

Environment Variables Required:
    - APP_NAME: Application name
    - SECRET_KEY: JWT signing secret
    - ALGORITHM: JWT algorithm (e.g., HS256)
    - ACCESS_TOKEN_EXPIRE_MINUTES: Token expiry in minutes
    - RATE_LIMIT_*: Rate limiting configuration

Configuration Files:
    - config/db/config.json: DataI configuration
    - config/cache/config.json: Redis configuration
"""

import os
import sys
from pathlib import Path
from urllib.parse import quote
from typing import Any

import redis
from dotenv import load_dotenv
from loguru import logger

# Optional fast_platform configuration (requires pyfastmvc[platform])
try:
    from fast_platform import (
        CacheConfiguration,
        CacheConfigurationDTO,
        DBConfiguration,
        DBConfigurationDTO,
    )
except ImportError:
    CacheConfiguration = None  # type: ignore
    CacheConfigurationDTO = None  # type: ignore
    DBConfiguration = None  # type: ignore
    DBConfigurationDTO = None  # type: ignore

from constants.default import Default

# =============================================================================
# LOGGER CONFIGURATION
# =============================================================================

# Remove default logger and add custom formatted one
logger.remove(0)
logger.add(
    sys.stderr,
    colorize=True,
    format=(
        "<green>{time:MMMM-D-YYYY}</green> | <black>{time:HH:mm:ss}</black> | "
        "<level>{level}</level> | <cyan>{message}</cyan> | "
        "<magenta>{name}:{function}:{line}</magenta> | "
        "<yellow>{extra}</yellow>"
    ),
)
"""
Configured loguru logger with custom format.

Format includes:
    - Timestamp (date and time)
    - Log level (colored)
    - Message
    - Source location (file:function:line)
    - Extra context (bound variables)

Example:
    >>> from start_utils import logger
    >>> logger.info("User logged in", user_id=123)
    >>> logger.bind(urn="urn:req:abc").debug("Processing request")
"""

# =============================================================================
# LOAD ENVIRONMENT AND CONFIGURATION
# =============================================================================

logger.info("Loading .env file and environment variables")
load_dotenv()

# Let packages load config from main repo's config/ (override)
os.environ.setdefault(
    "FASTMVC_CONFIG_I",
    str(Path(__file__).resolve().parent / "config"),
)

logger.info("Loading Configurations")
# Load configurations from fast_platform if available
cache_configuration = None  # type: ignore
db_configuration = None  # type: ignore
channels_configuration = None  # type: ignore

if CacheConfiguration:
    cache_configuration = CacheConfiguration().get_config()
if DBConfiguration:
    db_configuration = DBConfiguration().get_config()

try:
    from fast_channels import ChannelsConfiguration, ChannelsConfigurationDTO

    channels_configuration = ChannelsConfiguration().get_config()
except ImportError:
    pass

logger.info("Loaded Configurations")

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================

logger.info("Loading environment variables")

APP_NAME: str = os.environ.get("APP_NAME", "FastMVC")
"""Application name from environment."""

SECRET_KEY: str = os.getenv("SECRET_KEY")
"""JWT signing secret key. MUST be set in production."""

ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
"""JWT signing algorithm (default: HS256)."""

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        Default.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
)
"""JWT token expiry in minutes (default: 1440 = 24 hours)."""

REFRESH_TOKEN_EXPIRE_DAYS: int = int(
    os.getenv(
        "REFRESH_TOKEN_EXPIRE_DAYS",
        str(Default.REFRESH_TOKEN_EXPIRE_DAYS),
    )
)
"""JWT refresh token expiry in days (default: 7)."""

RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(
    os.getenv(
        "RATE_LIMIT_REQUESTS_PER_MINUTE",
        Default.RATE_LIMIT_REQUESTS_PER_MINUTE,
    )
)
"""Maximum requests per minute per client (default: 60)."""

RATE_LIMIT_REQUESTS_PER_HOUR: int = int(
    os.getenv(
        "RATE_LIMIT_REQUESTS_PER_HOUR",
        Default.RATE_LIMIT_REQUESTS_PER_HOUR,
    )
)
"""Maximum requests per hour per client (default: 1000)."""

RATE_LIMIT_WINDOW_SECONDS: int = int(
    os.getenv(
        "RATE_LIMIT_WINDOW_SECONDS",
        Default.RATE_LIMIT_WINDOW_SECONDS,
    )
)
"""Rate limit window size in seconds (default: 60)."""

RATE_LIMIT_BURST_LIMIT: int = int(
    os.getenv(
        "RATE_LIMIT_BURST_LIMIT",
        Default.RATE_LIMIT_BURST_LIMIT,
    )
)
"""Maximum burst requests allowed (default: 10)."""

logger.info("Loaded environment variables")

# =============================================================================
# DATAI SESSION
# =============================================================================

try:
    from fast_db import create_and_set_session

    db_session = create_and_set_session(db_configuration)
except ImportError:
    create_and_set_session = None  # type: ignore
    db_session = None  # type: ignore
"""
SQLAlchemy dataI session (from fast_db).

Initialized at startup if dataI configuration is complete.
Used throughout the application for dataI operations.

Example:
    >>> from start_utils import db_session
    >>> user = db_session.query(User).filter_by(id=1).first()
"""
if db_session:
    logger.info("Initialized PostgreSQL dataI connection")
else:
    logger.info("DataI session not initialized (fast_db not available)")

# =============================================================================
# REDIS SESSION
# =============================================================================

redis_session: redis.Redis = None
"""
Redis cache connection.

Initialized at startup if cache configuration is complete.
Used for caching, rate limiting data, and session storage.

Example:
    >>> from start_utils import redis_session
    >>> redis_session.set("key", "value", ex=3600)
    >>> value = redis_session.get("key")
"""

redis_url: str | None = None
if cache_configuration is not None:
    redis_url = getattr(cache_configuration, "redis_url", "") or ""
    if not redis_url:
        # Backward compatibility with older cache DTO schema.
        host = (
            getattr(cache_configuration, "host", None) or os.getenv("REDIS_HOST", "localhost")
        )
        port = (
            getattr(cache_configuration, "port", None) or os.getenv("REDIS_PORT", "6379")
        )
        password = getattr(cache_configuration, "password", None) or os.getenv(
            "REDIS_PASSWORD", ""
        )
        if host and port:
            auth = f":{quote(str(password))}@" if password else ""
            redis_url = f"redis://{auth}{host}:{port}/0"

if redis_url:
    logger.info("Initializing Redis dataI connection")
    redis_session = redis.Redis.from_url(redis_url)
    if not redis_session:
        logger.error("No Redis session available")
        raise RuntimeError("No Redis session available")
    logger.info("Initialized Redis dataI connection")
else:
    logger.info("Redis session not initialized (cache configuration not available)")

# =============================================================================
# CHANNELS BACKEND
# =============================================================================

channel_backend: Any = None
"""
Global pub-sub channels backend.

Backed by Redis or Kafka depending on configuration.
"""

CHANNEL_BACKEND: str = (
    os.getenv("CHANNEL_BACKEND", channels_configuration.backend)
    if channels_configuration is not None
    else os.getenv("CHANNEL_BACKEND", "none")
)

if CHANNEL_BACKEND == "redis" and redis_session:
    try:
        import redis.asyncio as aioredis

        from fast_channels import RedisChannelBackend

        channel_redis_url = redis_url
        if not channel_redis_url:
            host = os.getenv("REDIS_HOST", "localhost")
            port = os.getenv("REDIS_PORT", "6379")
            password = os.getenv("REDIS_PASSWORD", "")
            auth = f":{quote(password)}@" if password else ""
            channel_redis_url = f"redis://{auth}{host}:{port}/0"

        redis_async = aioredis.from_url(channel_redis_url)
        channel_backend = RedisChannelBackend(redis_async)
        logger.info("Initialized Redis channels backend")
    except Exception as exc:
        logger.error(f"Failed to initialize Redis channels backend: {exc}")
        channel_backend = None
elif CHANNEL_BACKEND == "kafka":
    logger.info("Kafka channels backend requested but not yet implemented.")

# =============================================================================
# ROUTE CONFIGURATION
# =============================================================================

unprotected_routes: set = {
    "/",
    "/health",
    "/health/live",
    "/health/ready",
    "/user/login",
    "/user/register",
    "/user/refresh",
    "/docs",
    "/redoc",
    "/openapi.json",
}
"""
Set of routes that bypass authentication middleware.

These routes are accessible without a valid JWT token:
    - /: Launch landing page (static HTML)
    - /health: Comprehensive health check endpoint
    - /health/live: Kubernetes liveness probe
    - /health/ready: Kubernetes readiness probe
    - /user/login: Login endpoint
    - /user/register: Registration endpoint
    - /user/refresh: Token refresh endpoint
    - /docs: Swagger UI documentation
    - /redoc: ReDoc documentation
"""

callback_routes: set = set[Any]()
"""
Set of webhook/callback routes.

Routes that receive external callbacks (e.g., payment webhooks).
These may have special authentication handling.
"""

# =============================================================================
# STARTUP COMPLETION
# =============================================================================

if db_session:
    db_session.commit()
    logger.info("DataI session committed and startup complete")
