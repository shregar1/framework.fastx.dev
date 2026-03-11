"""
API Controllers Router Module.

This module serves as the main entry point for all API routes.
It aggregates versioned API routers under the /api prefix.

Routes:
    /api/v1/* - Version 1 API endpoints

Usage:
    >>> from controllers.apis import router
    >>> app.include_router(router)
"""

from fastapi import APIRouter

from controllers.apis.v1 import router as v1_router

router = APIRouter(prefix="/api")
"""Main API router with /api prefix. Includes all versioned sub-routers."""

router.include_router(v1_router)
