"""Product router: ``/api/apis/product/...`` (see ``apis/__init__.py``)."""

from enum import Enum


from fastapi import APIRouter

from apis.product.fetch import fetch_placeholder
from constants.api_lk import APILK

apis_product_router = APIRouter(prefix="/product", tags=["apis-product"])
apis_product_router.add_api_route(
    path=APILK.PRODUCT.FETCH.PATH,
    endpoint=fetch_placeholder,
    methods=[APILK.PRODUCT.FETCH.METHOD],
    name=APILK.PRODUCT.FETCH.NAME,
    status_code=APILK.PRODUCT.FETCH.STATUS_CODE,
    summary=APILK.PRODUCT.FETCH.SUMMARY,
    tags=list[str | Enum](APILK.PRODUCT.FETCH.TAGS) if APILK.PRODUCT.FETCH.TAGS is not None else None,
)

router = apis_product_router

__all__ = ["apis_product_router", "router"]
