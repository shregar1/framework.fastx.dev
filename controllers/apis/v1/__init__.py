"""
API Version 1 Router Module.

This module serves as the entry point for all v1 API endpoints.
It aggregates all v1 feature routers under the /v1 prefix.

Routes:
    /api/v1/* - All version 1 API endpoints

Usage:
    >>> from controllers.apis.v1 import router
    >>> api_router.include_router(router)
"""

from fastapi import APIRouter

router = APIRouter(prefix="/v1")
"""Version 1 API router with /v1 prefix."""
