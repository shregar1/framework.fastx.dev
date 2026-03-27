"""V1 API Router."""

from fastapi import APIRouter
from apis.v1.example import router as example_router

router = APIRouter(prefix="/v1")

# Include feature routers
router.include_router(example_router)

__all__ = ["router"]
