"""
Prometheus Metrics Module.

Provides Prometheus metrics collection and exposure for FastAPI applications.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


@dataclass
class MetricValue:
    """Container for metric values."""

    value: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)


class Counter:
    """
    Prometheus-style counter metric.

    A counter is a cumulative metric that can only increase.
    """

    def __init__(self, name: str, description: str, labels: list[str] | None = None):
        self._name = name
        self._description = description
        self._labels = labels or []
        self._values: dict[tuple, float] = defaultdict(float)
        self._lock = Lock()

    @property
    def name(self) -> str:
        return self._name

    def inc(self, value: float = 1.0, **labels: str) -> None:
        """Increment counter."""
        label_key = tuple(sorted(labels.items()))
        with self._lock:
            self._values[label_key] += value

    def get(self, **labels: str) -> float:
        """Get counter value."""
        label_key = tuple(sorted(labels.items()))
        return self._values.get(label_key, 0.0)

    def to_prometheus(self) -> str:
        """Export in Prometheus format."""
        lines = [
            f"# HELP {self._name} {self._description}",
            f"# TYPE {self._name} counter",
        ]
        with self._lock:
            for label_key, value in self._values.items():
                label_str = ",".join(f'{k}="{v}"' for k, v in label_key) if label_key else ""
                metric_name = f"{self._name}{{{label_str}}}" if label_str else self._name
                lines.append(f"{metric_name} {value}")
        return "\n".join(lines)


class Gauge:
    """
    Prometheus-style gauge metric.

    A gauge is a metric that can increase and decrease.
    """

    def __init__(self, name: str, description: str, labels: list[str] | None = None):
        self._name = name
        self._description = description
        self._labels = labels or []
        self._values: dict[tuple, float] = defaultdict(float)
        self._lock = Lock()

    @property
    def name(self) -> str:
        return self._name

    def set(self, value: float, **labels: str) -> None:
        """Set gauge value."""
        label_key = tuple(sorted(labels.items()))
        with self._lock:
            self._values[label_key] = value

    def inc(self, value: float = 1.0, **labels: str) -> None:
        """Increment gauge."""
        label_key = tuple(sorted(labels.items()))
        with self._lock:
            self._values[label_key] += value

    def dec(self, value: float = 1.0, **labels: str) -> None:
        """Decrement gauge."""
        label_key = tuple(sorted(labels.items()))
        with self._lock:
            self._values[label_key] -= value

    def get(self, **labels: str) -> float:
        """Get gauge value."""
        label_key = tuple(sorted(labels.items()))
        return self._values.get(label_key, 0.0)

    def to_prometheus(self) -> str:
        """Export in Prometheus format."""
        lines = [
            f"# HELP {self._name} {self._description}",
            f"# TYPE {self._name} gauge",
        ]
        with self._lock:
            for label_key, value in self._values.items():
                label_str = ",".join(f'{k}="{v}"' for k, v in label_key) if label_key else ""
                metric_name = f"{self._name}{{{label_str}}}" if label_str else self._name
                lines.append(f"{metric_name} {value}")
        return "\n".join(lines)


class Histogram:
    """
    Prometheus-style histogram metric.

    A histogram samples observations and counts them in buckets.
    """

    DEFAULT_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)

    def __init__(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        buckets: tuple[float, ...] | None = None,
    ):
        self._name = name
        self._description = description
        self._labels = labels or []
        self._buckets = buckets or self.DEFAULT_BUCKETS
        self._counts: dict[tuple, dict[float, int]] = defaultdict(
            lambda: {b: 0 for b in self._buckets}
        )
        self._sums: dict[tuple, float] = defaultdict(float)
        self._totals: dict[tuple, int] = defaultdict(int)
        self._lock = Lock()

    @property
    def name(self) -> str:
        return self._name

    def observe(self, value: float, **labels: str) -> None:
        """Observe a value."""
        label_key = tuple(sorted(labels.items()))
        with self._lock:
            self._sums[label_key] += value
            self._totals[label_key] += 1
            for bucket in self._buckets:
                if value <= bucket:
                    self._counts[label_key][bucket] += 1

    def time(self, **labels: str) -> "HistogramTimer":
        """Context manager to time operations."""
        return HistogramTimer(self, labels)

    def to_prometheus(self) -> str:
        """Export in Prometheus format."""
        lines = [
            f"# HELP {self._name} {self._description}",
            f"# TYPE {self._name} histogram",
        ]
        with self._lock:
            for label_key in self._counts:
                label_str = ",".join(f'{k}="{v}"' for k, v in label_key) if label_key else ""
                cumulative = 0
                for bucket in sorted(self._buckets):
                    cumulative += self._counts[label_key][bucket]
                    bucket_label = f'{label_str},le="{bucket}"' if label_str else f'le="{bucket}"'
                    lines.append(f"{self._name}_bucket{{{bucket_label}}} {cumulative}")
                inf_label = f'{label_str},le="+Inf"' if label_str else 'le="+Inf"'
                lines.append(f"{self._name}_bucket{{{inf_label}}} {self._totals[label_key]}")
                sum_name = f"{self._name}_sum{{{label_str}}}" if label_str else f"{self._name}_sum"
                count_name = f"{self._name}_count{{{label_str}}}" if label_str else f"{self._name}_count"
                lines.append(f"{sum_name} {self._sums[label_key]}")
                lines.append(f"{count_name} {self._totals[label_key]}")
        return "\n".join(lines)


class HistogramTimer:
    """Context manager for timing histogram observations."""

    def __init__(self, histogram: Histogram, labels: dict[str, str]):
        self._histogram = histogram
        self._labels = labels
        self._start: float = 0

    def __enter__(self) -> "HistogramTimer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        duration = time.perf_counter() - self._start
        self._histogram.observe(duration, **self._labels)


class Metrics:
    """
    Metrics registry and exporter.

    Provides a central registry for all metrics and Prometheus export.

    Usage:
        metrics = Metrics()

        # Create metrics
        requests = metrics.counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"]
        )

        # Use metrics
        requests.inc(method="GET", endpoint="/users", status="200")

        # Export
        print(metrics.export())
    """

    def __init__(self):
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}
        self._lock = Lock()

    def counter(
        self, name: str, description: str = "", labels: list[str] | None = None
    ) -> Counter:
        """Get or create a counter."""
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name, description, labels)
            return self._counters[name]

    def gauge(
        self, name: str, description: str = "", labels: list[str] | None = None
    ) -> Gauge:
        """Get or create a gauge."""
        with self._lock:
            if name not in self._gauges:
                self._gauges[name] = Gauge(name, description, labels)
            return self._gauges[name]

    def histogram(
        self,
        name: str,
        description: str = "",
        labels: list[str] | None = None,
        buckets: tuple[float, ...] | None = None,
    ) -> Histogram:
        """Get or create a histogram."""
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = Histogram(name, description, labels, buckets)
            return self._histograms[name]

    def export(self) -> str:
        """Export all metrics in Prometheus format."""
        lines = []
        for counter in self._counters.values():
            lines.append(counter.to_prometheus())
        for gauge in self._gauges.values():
            lines.append(gauge.to_prometheus())
        for histogram in self._histograms.values():
            lines.append(histogram.to_prometheus())
        return "\n\n".join(lines)


# Global metrics instance
_metrics = Metrics()


def get_metrics() -> Metrics:
    """Get global metrics instance."""
    return _metrics


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic HTTP metrics collection.

    Collects:
    - http_requests_total (counter)
    - http_request_duration_seconds (histogram)
    - http_requests_in_progress (gauge)
    """

    def __init__(
        self,
        app: Any,
        metrics: Optional[Metrics] = None,
        exclude_paths: set[str] | None = None,
    ):
        super().__init__(app)
        self._metrics = metrics or get_metrics()
        self._exclude_paths = exclude_paths or {"/metrics", "/health"}

        self._requests_total = self._metrics.counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
        )
        self._request_duration = self._metrics.histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
        )
        self._requests_in_progress = self._metrics.gauge(
            "http_requests_in_progress",
            "Number of HTTP requests in progress",
            ["method", "endpoint"],
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self._exclude_paths:
            return await call_next(request)

        method = request.method
        endpoint = request.url.path

        self._requests_in_progress.inc(method=method, endpoint=endpoint)
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception:
            status = "500"
            raise
        finally:
            duration = time.perf_counter() - start_time
            self._requests_total.inc(method=method, endpoint=endpoint, status=status)
            self._request_duration.observe(duration, method=method, endpoint=endpoint)
            self._requests_in_progress.dec(method=method, endpoint=endpoint)

        return response
