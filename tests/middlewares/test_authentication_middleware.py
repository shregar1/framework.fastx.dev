"""Tests for JWT authentication middleware wiring (``fastmiddleware``)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fastmiddleware import (  # pyright: ignore[reportMissingImports]
    AuthConfig,
    AuthenticationMiddleware,
    JWTAuthBackend,
)


class _NoOpAuthMiddleware(BaseHTTPMiddleware):
    """Pass-through stack entry for tests (replaces removed ``NoOpAuthMiddleware``)."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        return await call_next(request)


def test_auth_middleware_wiring() -> None:
    """JWT auth stack rejects unauthenticated requests to protected routes."""
    app = FastAPI()
    backend = JWTAuthBackend(
        secret="0" * 32,
        algorithm="HS256",
    )
    config = AuthConfig(exclude_paths=set())
    app.add_middleware(AuthenticationMiddleware, backend=backend, config=config)

    @app.get("/test-protected")
    async def protected_route():
        return {"message": "success"}

    client = TestClient(app)
    response = client.get("/test-protected")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_auth_noop_fallback() -> None:
    """Pass-through middleware does not block requests."""
    app = FastAPI()
    app.add_middleware(_NoOpAuthMiddleware)

    @app.get("/")
    async def index():
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
