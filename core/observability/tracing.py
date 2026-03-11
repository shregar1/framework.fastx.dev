"""
Distributed Tracing Module.

Provides OpenTelemetry-compatible distributed tracing for FastAPI applications.
"""

import contextvars
import functools
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variables for trace propagation
_trace_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "trace_id", default=None
)
_span_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "span_id", default=None
)
_parent_span_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "parent_span_id", default=None
)


def get_trace_id() -> Optional[str]:
    """Get current trace ID."""
    return _trace_id.get()


def get_span_id() -> Optional[str]:
    """Get current span ID."""
    return _span_id.get()


@dataclass
class Span:
    """
    Represents a trace span.

    A span is a single operation within a trace.
    """

    name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: str = "OK"
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def add_event(self, name: str, **attributes: Any) -> None:
        """Add an event to the span."""
        self.events.append({
            "name": name,
            "timestamp": datetime.utcnow().isoformat(),
            "attributes": attributes,
        })

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    def set_status(self, status: str, message: Optional[str] = None) -> None:
        """Set span status."""
        self.status = status
        if message:
            self.attributes["status_message"] = message

    def end(self) -> None:
        """End the span."""
        self.end_time = datetime.utcnow()

    @property
    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert span to dictionary."""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events,
        }


class SpanExporter:
    """Base class for span exporters."""

    def export(self, span: Span) -> None:
        """Export a span."""
        pass


class ConsoleSpanExporter(SpanExporter):
    """Export spans to console (for development)."""

    def export(self, span: Span) -> None:
        """Print span to console."""
        import json
        print(json.dumps(span.to_dict(), indent=2))


class CollectorSpanExporter(SpanExporter):
    """
    Export spans to a collector (Jaeger, Zipkin, etc.).

    This is a placeholder for actual collector integration.
    """

    def __init__(self, endpoint: str, headers: Optional[dict[str, str]] = None):
        self._endpoint = endpoint
        self._headers = headers or {}

    def export(self, span: Span) -> None:
        """Send span to collector."""
        # In production, this would send to Jaeger/Zipkin/etc.
        pass


class Tracer:
    """
    Distributed tracer for creating and managing spans.

    Usage:
        tracer = Tracer("my_service")

        with tracer.span("process_order") as span:
            span.set_attribute("order_id", "123")
            # ... do work ...
    """

    def __init__(
        self,
        service_name: str,
        exporter: Optional[SpanExporter] = None,
    ):
        """
        Initialize tracer.

        Args:
            service_name: Name of the service.
            exporter: Span exporter instance.
        """
        self._service_name = service_name
        self._exporter = exporter or ConsoleSpanExporter()

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return uuid.uuid4().hex[:16]

    def start_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
    ) -> Span:
        """
        Start a new span.

        Args:
            name: Span name.
            trace_id: Trace ID (uses current context if not provided).
            parent_span_id: Parent span ID.

        Returns:
            New Span instance.
        """
        if trace_id is None:
            trace_id = _trace_id.get() or self._generate_id()

        span_id = self._generate_id()
        parent = parent_span_id or _span_id.get()

        span = Span(
            name=name,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent,
        )
        span.set_attribute("service.name", self._service_name)

        # Update context
        _trace_id.set(trace_id)
        _parent_span_id.set(_span_id.get())
        _span_id.set(span_id)

        return span

    def end_span(self, span: Span) -> None:
        """End a span and export it."""
        span.end()
        self._exporter.export(span)

        # Restore context
        _span_id.set(_parent_span_id.get())

    def span(self, name: str) -> "SpanContext":
        """
        Context manager for spans.

        Usage:
            with tracer.span("operation") as span:
                span.set_attribute("key", "value")
        """
        return SpanContext(self, name)


class SpanContext:
    """Context manager for spans."""

    def __init__(self, tracer: Tracer, name: str):
        self._tracer = tracer
        self._name = name
        self._span: Optional[Span] = None

    def __enter__(self) -> Span:
        self._span = self._tracer.start_span(self._name)
        return self._span

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._span:
            if exc_type:
                self._span.set_status("ERROR", str(exc_val))
                self._span.add_event(
                    "exception",
                    exception_type=exc_type.__name__ if exc_type else None,
                    exception_message=str(exc_val) if exc_val else None,
                )
            self._tracer.end_span(self._span)


def trace(name: Optional[str] = None) -> Callable:
    """
    Decorator to trace a function.

    Usage:
        @trace("process_order")
        async def process_order(order_id: str):
            pass
    """
    def decorator(func: Callable) -> Callable:
        span_name = name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = Tracer("default")
            with tracer.span(span_name) as span:
                span.set_attribute("function", func.__name__)
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = Tracer("default")
            with tracer.span(span_name) as span:
                span.set_attribute("function", func.__name__)
                return func(*args, **kwargs)

        if asyncio_iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def asyncio_iscoroutinefunction(func: Callable) -> bool:
    """Check if function is async."""
    import asyncio
    return asyncio.iscoroutinefunction(func)


class TracingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic request tracing.

    Automatically creates spans for HTTP requests with:
    - Method, path, status code
    - Request/response headers (configurable)
    - Trace ID propagation via headers
    """

    TRACE_HEADER = "X-Trace-ID"
    SPAN_HEADER = "X-Span-ID"
    PARENT_SPAN_HEADER = "X-Parent-Span-ID"

    def __init__(
        self,
        app: Any,
        service_name: str = "fastmvc",
        exporter: Optional[SpanExporter] = None,
        exclude_paths: set[str] | None = None,
    ):
        super().__init__(app)
        self._tracer = Tracer(service_name, exporter)
        self._exclude_paths = exclude_paths or {"/metrics", "/health"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self._exclude_paths:
            return await call_next(request)

        # Extract trace context from headers
        trace_id = request.headers.get(self.TRACE_HEADER)
        parent_span_id = request.headers.get(self.PARENT_SPAN_HEADER)

        # Start request span
        span = self._tracer.start_span(
            f"{request.method} {request.url.path}",
            trace_id=trace_id,
            parent_span_id=parent_span_id,
        )

        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("http.host", request.url.hostname or "")
        span.set_attribute("http.user_agent", request.headers.get("user-agent", ""))

        try:
            response = await call_next(request)
            span.set_attribute("http.status_code", response.status_code)

            if response.status_code >= 400:
                span.set_status("ERROR", f"HTTP {response.status_code}")
            else:
                span.set_status("OK")

            # Add trace headers to response
            response.headers[self.TRACE_HEADER] = span.trace_id
            response.headers[self.SPAN_HEADER] = span.span_id

            return response
        except Exception as e:
            span.set_status("ERROR", str(e))
            span.add_event("exception", exception_message=str(e))
            raise
        finally:
            self._tracer.end_span(span)
