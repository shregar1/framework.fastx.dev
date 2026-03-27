"""App-specific wiring for :class:`JWTBearerAuthMiddleware` from ``fastmiddleware``.

JWT decode and user session lookup use this application's repositories and DTOs.

Note: This middleware requires pyfastmvc[platform] for full functionality.
Without the platform package, it will pass through all requests (development mode).
"""

from http import HTTPStatus

from fastapi.responses import JSONResponse

from constants.api_status import APIStatus
from dtos.responses.base import BaseResponseDTO

# Optional dependencies (requires pyfastmvc[platform])
try:
    from fastmiddleware import ErrorKind, JWTBearerAuthMiddleware
except ImportError:
    JWTBearerAuthMiddleware = None  # type: ignore
    ErrorKind = None  # type: ignore

try:
    from fast_database.persistence.repositories.user import UserRepository
except ImportError:
    UserRepository = None  # type: ignore

try:
    from fast_utilities.jwt import JWTUtility
except ImportError:
    JWTUtility = None  # type: ignore

from start_utils import callback_routes, db_session, logger, unprotected_routes


def _decode_bearer(token: str, urn: str) -> dict:
    """Decode JWT bearer token."""
    if JWTUtility:
        return JWTUtility(urn=urn).decode_token(token=token)
    # Fallback: return empty payload for development
    logger.warning("JWTUtility not available, returning empty payload")
    return {"user_id": None}


def _load_user(user_data: dict, urn: str):
    """Load user from database."""
    if UserRepository and db_session:
        return UserRepository(
            urn=urn, session=db_session
        ).retrieve_record_by_id_and_is_logged_in(
            id=user_data.get("user_id"),
            is_logged_in=True,
            is_deleted=False,
        )
    # Fallback: return None for development
    logger.warning("UserRepository not available, returning None")
    return None


# Create the middleware only if dependencies are available
if JWTBearerAuthMiddleware:
    AuthenticationMiddleware = JWTBearerAuthMiddleware(
        decode_bearer=_decode_bearer,
        load_user=_load_user,
        unprotected_routes=unprotected_routes,
        callback_routes=callback_routes,
        error_response_factory=lambda request, error: JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content=BaseResponseDTO(
                transactionUrn=getattr(request.state, "urn", None),
                status=APIStatus.FAILED,
                responseMessage=error.message,
                responseKey=f"error_{error.kind.name.lower()}"
                if hasattr(error.kind, "name")
                else "error_authentication",
                data={},
                errors=None,
            ).model_dump(),
        ),
    )
else:
    # Fallback middleware that allows all requests
    class _NoOpAuthMiddleware:
        """No-op authentication middleware for development without fastmiddleware."""

        def __init__(self, app):
            """Execute __init__ operation.

            Args:
                app: The app parameter.
            """
            self.app = app

        async def __call__(self, scope, receive, send):
            """Execute __call__ operation.

            Args:
                scope: The scope parameter.
                receive: The receive parameter.
                send: The send parameter.

            Returns:
                The result of the operation.
            """
            await self.app(scope, receive, send)

    AuthenticationMiddleware = _NoOpAuthMiddleware
