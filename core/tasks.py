"""Celery application entrypoint.

Celery CLI expects an importable module with an `app` attribute when invoked as:
  celery -A core.tasks worker
"""

from __future__ import annotations

import os
from typing import Any, Optional


def _make_fallback_celery_app() -> Any:
    """Create a minimal Celery app when optional job dependencies are missing."""

    # Celery itself is installed in the Docker image; broker/backends come from env.
    from celery import Celery

    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    # Use Redis for both broker and result backend in this fallback.
    return Celery("fastmvc", broker=redis_url, backend=redis_url)


try:
    # Preferred: use the upstream JobsConfiguration-based Celery app.
    from messaging.jobs.celery_app import make_celery_app

    app: Any = make_celery_app()
except Exception:
    # This repo's Docker build may not include the full `fast_platform` job stack.
    # Fallback keeps worker/scheduler containers healthy (even if no jobs are configured).
    app = _make_fallback_celery_app()

