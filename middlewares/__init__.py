"""Middleware package.

JWT and HTTP middleware implementations live in the ``fast-middleware`` distribution
(import ``fastmiddleware``). This package provides OpenAPI/docs helpers only.

Use::

    from middlewares import DocsAuthConfig, DocsBasicAuthMiddleware

OpenAPI path helpers (``normalized_openapi_url``, logging excludes, auth configured) live on
:class:`DocsAuthConfig` in :mod:`middlewares.docs_auth`.
"""

from .docs_auth import DocsAuthConfig, DocsBasicAuthMiddleware


__all__ = [
    "DocsAuthConfig",
    "DocsBasicAuthMiddleware",
]
