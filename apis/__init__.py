"""Main API Router."""

from fastapi import APIRouter
from apis.v1 import router as v1_router
from apis.product import router as apis_product_router

router = APIRouter(prefix="/api")

# /api/apis/product/fetch (no controllers/ or v1/ segment in the URL)
apis_path_router = APIRouter(prefix="/apis", tags=["apis"])
apis_path_router.include_router(apis_product_router)
router.include_router(apis_path_router)

# Versioned feature routers (e.g. /api/v1/examples/...).
router.include_router(v1_router)

__all__ = ["router"]
