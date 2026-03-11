"""
Authentication Middleware.

Validates JWT tokens and enforces authentication on protected routes.
Compatible with fastmiddleware's RequestContextMiddleware.
"""

from http import HTTPStatus

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError

from constants.api_status import APIStatus
from dtos.responses.base import BaseResponseDTO
from repositories.user import UserRepository
from start_utils import callback_routes, db_session, logger, unprotected_routes
from utilities.jwt import JWTUtility

# Import FastMiddleware's request context helper
try:
    from fastmiddleware import get_request_id
    HAS_FAST_MIDDLEWARE = True
except ImportError:
    HAS_FAST_MIDDLEWARE = False
    def get_request_id():
        return None


def _get_request_urn(request: Request) -> str:
    """
    Get request URN from request state.

    Compatible with both local RequestContextMiddleware (sets .urn)
    and fastmiddleware's RequestContextMiddleware (sets .request_id).

    Args:
        request: The FastAPI request object.

    Returns:
        Request URN/ID string, or 'unknown' if not available.
    """
    # Try local middleware's urn first
    if hasattr(request.state, 'urn'):
        return request.state.urn

    # Try fastmiddleware's request_id
    if hasattr(request.state, 'request_id'):
        return request.state.request_id

    # Try context variable from fastmiddleware
    if HAS_FAST_MIDDLEWARE:
        request_id = get_request_id()
        if request_id:
            return request_id

    return "unknown"


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication Middleware.

    Validates JWT tokens and enforces authentication on protected routes.
    Skips authentication for OPTIONS requests and unprotected routes.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process authentication for each request.

        Args:
            request: The incoming FastAPI request.
            call_next: The next middleware/handler in the chain.

        Returns:
            Response from the handler or 401 Unauthorized.
        """
        logger.debug("Inside authentication middleware")

        urn: str = _get_request_urn(request)
        endpoint: str = request.url.path

        if request.method == "OPTIONS":
            return await call_next(request)

        logger.debug(f"Received request for endpoint: {endpoint}")

        if endpoint in unprotected_routes.union(callback_routes):
            logger.debug("Accessing Unprotected Route", urn=urn)
            response: Response = await call_next(request)
            return response

        logger.debug("Accessing Protected Route", urn=urn)
        token: str = request.headers.get("authorization")
        if not token or "bearer" not in token.lower():
            logger.debug("Preparing response metadata", urn=urn)
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transactionUrn=urn,
                status=APIStatus.FAILED,
                responseMessage="JWT Authentication failed.",
                responseKey="error_authetication_error",
                data={},
            )
            httpStatusCode = HTTPStatus.UNAUTHORIZED
            logger.debug("Prepared response metadata", urn=urn)
            return JSONResponse(
                content=response_dto.model_dump(), status_code=httpStatusCode
            )

        try:
            logger.debug("Decoding the authetication token", urn=urn)
            token = token.split(" ")[1]

            user_data: dict = JWTUtility(urn=urn).decode_token(token=token)
            logger.debug("Decoded the authetication token", urn=urn)

            logger.debug("Fetching user logged in status.", urn=urn)
            user = UserRepository(
                urn=urn, session=db_session
            ).retrieve_record_by_id_and_is_logged_in(
                id=user_data.get("user_id"),
                is_logged_in=True,
                is_deleted=False,
            )
            logger.debug("Fetched user logged in status.", urn=urn)

            if not user:
                logger.debug("Preparing response metadata", urn=urn)
                response_dto: BaseResponseDTO = BaseResponseDTO(
                    transactionUrn=urn,
                    status=APIStatus.FAILED,
                    responseMessage="User Session Expired.",
                    responseKey="error_session_expiry",
                )
                httpStatusCode = HTTPStatus.UNAUTHORIZED
                logger.debug("Prepared response metadata", urn=urn)
                return JSONResponse(
                    content=response_dto.model_dump(),
                    status_code=httpStatusCode,
                )

            request.state.user_id = user_data.get("user_id")
            request.state.user_urn = user_data.get("user_urn")

        except (ValueError, KeyError) as err:

            logger.debug(
                f"{err.__class__} occured while parsing auth header or token "
                f"payload, {err}",
                urn=request.state.urn,
            )

            logger.debug("Preparing response metadata", urn=request.state.urn)
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transactionUrn=urn,
                status=APIStatus.FAILED,
                responseMessage="JWT Authentication failed.",
                responseKey="error_authetication_error",
                data={},
            )
            httpStatusCode = HTTPStatus.UNAUTHORIZED
            logger.debug("Prepared response metadata", urn=request.state.urn)
            return JSONResponse(
                content=response_dto.model_dump(), status_code=httpStatusCode
            )

        except SQLAlchemyError as err:

            logger.error(
                f"{err.__class__} occured while querying user repository, "
                f"{err}",
                urn=request.state.urn,
            )

            logger.debug("Preparing response metadata", urn=request.state.urn)
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transactionUrn=urn,
                status=APIStatus.FAILED,
                responseMessage="Authentication service temporarily unavailable.",
                responseKey="error_authentication_service_unavailable",
                data={},
            )
            httpStatusCode = HTTPStatus.SERVICE_UNAVAILABLE
            logger.debug("Prepared response metadata", urn=request.state.urn)
            return JSONResponse(
                content=response_dto.model_dump(), status_code=httpStatusCode
            )

        except Exception as err:
            logger.debug(
                f"{err.__class__} occured while authentiacting jwt token, "
                f"{err}",
                urn=urn,
            )

            logger.debug("Preparing response metadata", urn=urn)
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transactionUrn=urn,
                status=APIStatus.FAILED,
                responseMessage="JWT Authentication failed.",
                responseKey="error_authetication_error",
                data={},
            )
            httpStatusCode = HTTPStatus.UNAUTHORIZED
            logger.debug("Prepared response metadata", urn=urn)
            return JSONResponse(
                content=response_dto.model_dump(), status_code=httpStatusCode
            )

        logger.debug("Procceding with the request execution.", urn=urn)
        response: Response = await call_next(request)

        return response
