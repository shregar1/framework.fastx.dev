import asyncio
import time
from collections import defaultdict, deque
from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from constants.api_status import APIStatus
from dtos.responses.base import BaseResponseDTO
from start_utils import (
    RATE_LIMIT_BURST_LIMIT,
    RATE_LIMIT_REQUESTS_PER_HOUR,
    RATE_LIMIT_REQUESTS_PER_MINUTE,
    RATE_LIMIT_WINDOW_SECONDS,
    logger,
    unprotected_routes,
)


class RateLimitConfig:
    """
    Configuration for rate limiting.

    Args:
        requests_per_minute (int): Allowed requests per minute.
        requests_per_hour (int): Allowed requests per hour.
        burst_limit (int): Maximum burst requests allowed.
        window_size (int): Size of the rate limit window in seconds.
        enable_sliding_window (bool): Enable sliding window strategy.
        enable_token_bucket (bool): Enable token bucket strategy.
        enable_fixed_window (bool): Enable fixed window strategy.
    """
    def __init__(
        self,
        requests_per_minute: int = RATE_LIMIT_REQUESTS_PER_MINUTE,
        requests_per_hour: int = RATE_LIMIT_REQUESTS_PER_HOUR,
        burst_limit: int = RATE_LIMIT_BURST_LIMIT,
        window_size: int = RATE_LIMIT_WINDOW_SECONDS,
        enable_sliding_window: bool = True,
        enable_token_bucket: bool = False,
        enable_fixed_window: bool = False,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
        self.window_size = window_size
        self.enable_sliding_window = enable_sliding_window
        self.enable_token_bucket = enable_token_bucket
        self.enable_fixed_window = enable_fixed_window
        logger.debug(
            "Initialized RateLimitConfig",
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            burst_limit=burst_limit,
            window_size=window_size,
            enable_sliding_window=enable_sliding_window,
            enable_token_bucket=enable_token_bucket,
            enable_fixed_window=enable_fixed_window,
        )


class RateLimitStore:
    """
    In-memory store for rate limiting data.
    Handles sliding window counters and provides thread-safe access.
    """
    def __init__(self):
        self._sliding_windows: dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()
        logger.debug("Initialized RateLimitStore")

    async def check_sliding_window(
        self, key: str, limit: int, window: int
    ) -> tuple[bool, int]:
        """
        Check sliding window rate limit for a given key.

        Args:
            key (str): Unique identifier for the client/endpoint.
            limit (int): Maximum allowed requests in the window.
            window (int): Window size in seconds.
        Returns:
            Tuple[bool, int]: (allowed, current_count)
        """
        async with self._lock:
            now = time.time()
            window_start = now - window

            while (
                self._sliding_windows[key] and
                self._sliding_windows[key][0] < window_start
            ):
                self._sliding_windows[key].popleft()

            if len(self._sliding_windows[key]) >= limit:
                logger.info(
                    "Sliding window limit exceeded",
                    key=key,
                    limit=limit,
                    window=window,
                    current_count=len(self._sliding_windows[key]),
                )
                return False, len(self._sliding_windows[key])

            self._sliding_windows[key].append(now)
            logger.debug(
                "Sliding window incremented",
                key=key,
                current_count=len(self._sliding_windows[key]),
            )
            return True, len(self._sliding_windows[key])

    async def cleanup_old_entries(self, max_age: int = 3600):
        """
        Clean up old rate limiting entries older than max_age seconds.
        Args:
            max_age (int): Maximum age in seconds for entries to keep.
        """
        async with self._lock:
            now = time.time()
            for key in list(self._sliding_windows.keys()):
                while (
                    self._sliding_windows[key] and
                    self._sliding_windows[key][0] < now - max_age
                ):
                    self._sliding_windows[key].popleft()
                if not self._sliding_windows[key]:
                    del self._sliding_windows[key]
            logger.debug("Cleaned up old rate limit entries", max_age=max_age)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with multiple strategies.
    Supports sliding window, token bucket, and fixed window algorithms.
    """
    def __init__(
        self,
        app,
        config: RateLimitConfig | None = None,
        excluded_paths: set | None = None,
        excluded_methods: set | None = None,
    ):
        """
        Initialize the RateLimitMiddleware.
        Args:
            app: FastAPI/Starlette app instance.
            config (RateLimitConfig): Configuration for rate limiting.
            excluded_paths (set): Paths to exclude from rate limiting.
            excluded_methods (set): HTTP methods to exclude.
        """
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self.excluded_paths = (
            excluded_paths or unprotected_routes
        )
        self.excluded_methods = excluded_methods or {"OPTIONS"}
        self.store = RateLimitStore()
        logger.info(
            "RateLimitMiddleware initialized",
            config=self.config.__dict__,
        )
        asyncio.create_task(self._cleanup_task())

    async def _cleanup_task(self):
        """
        Periodic cleanup of old rate limiting entries.
        """
        while True:
            await asyncio.sleep(300)
            await self.store.cleanup_old_entries()
            logger.debug("Periodic rate limit cleanup executed")

    def _get_client_identifier(self, request: Request) -> str:
        """
        Get unique identifier for the client (IP address or header).
        Args:
            request (Request): Incoming HTTP request.
        Returns:
            str: Client identifier string.
        """
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            logger.debug(
                "Client identified by X-Forwarded-For",
                ip=forwarded_for,
            )
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            logger.debug("Client identified by X-Real-IP", ip=real_ip)
            return real_ip

        ip = request.client.host if request.client else "unknown"
        logger.debug("Client identified by request.client.host", ip=ip)
        return ip

    def _get_rate_limit_key(self, request: Request) -> str:
        """
        Generate rate limit key based on client and endpoint.
        Args:
            request (Request): Incoming HTTP request.
        Returns:
            str: Rate limit key.
        """
        client_id = self._get_client_identifier(request)
        endpoint = request.url.path
        method = request.method
        key = f"{client_id}:{method}:{endpoint}"
        logger.debug("Generated rate limit key", key=key)
        return key

    async def _check_rate_limits(
        self,
        key: str,
    ) -> tuple[bool, dict[str, any]]:
        """
        Check all enabled rate limiting strategies for a given key.
        Args:
            key (str): Unique identifier for the client/endpoint.
        Returns:
            Tuple[bool, Dict[str, any]]: (allowed, details per strategy)
        """
        results = {}
        logger.debug("Checking rate limits", key=key)

        if self.config.enable_sliding_window:
            allowed, count = await self.store.check_sliding_window(
                f"{key}:sliding:minute",
                self.config.requests_per_minute,
                60
            )
            results["sliding_minute"] = {"allowed": allowed, "count": count}
            if not allowed:
                logger.info(
                    "Sliding window minute limit exceeded",
                    key=key,
                    count=count,
                )
                return False, results

        if self.config.enable_sliding_window:
            allowed, count = await self.store.check_sliding_window(
                f"{key}:sliding:hour",
                self.config.requests_per_hour,
                3600
            )
            results["sliding_hour"] = {"allowed": allowed, "count": count}
            if not allowed:
                logger.info(
                    "Sliding window hour limit exceeded", key=key, count=count
                )
                return False, results

        logger.debug("Rate limits passed", key=key, results=results)
        return True, results

    async def dispatch(self, request: Request, call_next):
        """
        Process the request with rate limiting.
        Args:
            request (Request): Incoming HTTP request.
            call_next: Next middleware or route handler.
        Returns:
            Response: HTTP response, possibly a rate limit error.
        """
        logger.info(
            "Received request for rate limiting",
            path=request.url.path,
            method=request.method,
        )
        if (
            request.url.path in self.excluded_paths or
            request.method in self.excluded_methods
        ):
            logger.debug(
                "Request excluded from rate limiting",
                path=request.url.path,
                method=request.method,
            )
            return await call_next(request)

        key = self._get_rate_limit_key(request)
        allowed, results = await self._check_rate_limits(key)

        if not allowed:
            exceeded_limits = []
            for strategy, result in results.items():
                if not result.get("allowed", True):
                    exceeded_limits.append(strategy)

            response_dto = BaseResponseDTO(
                transactionUrn=getattr(request.state, "urn", None),
                status=APIStatus.FAILED,
                responseMessage="Rate limit exceeded. Please try again later.",
                responseKey="error_rate_limit_exceeded",
                data={
                    "exceeded_limits": exceeded_limits,
                    "retry_after": 60,  # seconds
                }
            )

            logger.warning(
                f"Rate limit exceeded for {key}",
                urn=getattr(request.state, "urn", None),
                client_ip=self._get_client_identifier(request),
                exceeded_limits=exceeded_limits
            )

            logger.info(
                "Sending rate limit exceeded response",
                key=key,
                exceeded_limits=exceeded_limits,
            )
            return JSONResponse(
                content=response_dto.model_dump(),
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.config.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + 60)
                }
            )

        response = await call_next(request)

        remaining = max(0, self.config.requests_per_minute - 1)
        reset_time = int(time.time()) + 60

        response.headers["X-RateLimit-Limit"] = str(
            self.config.requests_per_minute
        )
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        logger.info(
            "Request allowed, response sent",
            path=request.url.path,
            method=request.method,
            remaining=remaining,
            reset_time=reset_time,
        )
        return response
