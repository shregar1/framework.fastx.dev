"""
Startup Utilities Module.

This module initializes core application services and loads configuration
on application startup. It provides shared instances of database sessions,
cache connections, and configuration values used throughout the application.

Exports:
    - logger: Configured loguru logger instance
    - db_session: SQLAlchemy database session
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
    - config/db/config.json: Database configuration
    - config/cache/config.json: Redis configuration
"""

import os
import sys
from typing import Any

import redis
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from configurations.cache import CacheConfiguration, CacheConfigurationDTO
from configurations.db import DBConfiguration, DBConfigurationDTO
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

logger.info("Loading Configurations")
cache_configuration: CacheConfigurationDTO = CacheConfiguration().get_config()
db_configuration: DBConfigurationDTO = DBConfiguration().get_config()
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
# DATABASE SESSION
# =============================================================================

db_session: Session = None
"""
SQLAlchemy database session.

Initialized at startup if database configuration is complete.
Used throughout the application for database operations.

Example:
    >>> from start_utils import db_session
    >>> user = db_session.query(User).filter_by(id=1).first()
"""

if (
    db_configuration.user_name
    and db_configuration.password
    and db_configuration.host
    and db_configuration.port
    and db_configuration.database
    and db_configuration.connection_string
):
    logger.info("Initializing PostgreSQL database connection")
    engine = create_engine(
        db_configuration.connection_string.format(
            user_name=db_configuration.user_name,
            password=db_configuration.password,
            host=db_configuration.host,
            port=db_configuration.port,
            database=db_configuration.database,
        )
    )
    Session = sessionmaker[Session](bind=engine)
    db_session: Session = Session()
    logger.info("Initialized PostgreSQL database connection")

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

if (
    cache_configuration.host
    and cache_configuration.port
    and cache_configuration.password
):
    logger.info("Initializing Redis database connection")
    redis_session = redis.Redis(
        host=cache_configuration.host,
        port=cache_configuration.port,
        password=cache_configuration.password,
    )
    if not redis_session:
        logger.error("No Redis session available")
        raise RuntimeError("No Redis session available")
    logger.info("Initialized Redis database connection")

# =============================================================================
# ROUTE CONFIGURATION
# =============================================================================

unprotected_routes: set = {
    "/health",
    "/user/login",
    "/user/register",
    "/docs",
    "/redoc",
    "/openapi.json",
}
"""
Set of routes that bypass authentication middleware.

These routes are accessible without a valid JWT token:
    - /health: Health check endpoint
    - /user/login: Login endpoint
    - /user/register: Registration endpoint
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
    logger.info("Database session committed and startup complete")
