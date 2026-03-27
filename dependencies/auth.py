"""Auth dependency helpers for routes/tests."""

from __future__ import annotations

from fastapi import HTTPException, Request, status


def get_current_user(request: Request) -> dict:
    """Return authenticated user from request state or raise 401."""
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user

