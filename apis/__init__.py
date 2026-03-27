"""Main API Router."""

from fastapi import APIRouter
from apis.v1 import router as v1_router

router = APIRouter(prefix="/api")

# Include versioned routers
router.include_router(v1_router)

__all__ = ["router"]
