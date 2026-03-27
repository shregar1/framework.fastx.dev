"""Product fetch handler — registered on the product router (see :attr:`constants.api_lk.APILK.Product.FETCH`)."""

from constants.api_lk import APILK


async def fetch_placeholder() -> dict:
    """Placeholder; replace with a controller-backed handler."""
    return {
        "path": "/api/apis/product/fetch",
        "module": "apis.product.fetch",
        "api": APILK.PRODUCT.FETCH.NAME,
    }


__all__ = ["fetch_placeholder"]
