from datetime import datetime

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from ulid import ULID

from start_utils import logger


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug("Inside request context middleware")

        start_time: datetime = datetime.now()
        logger.debug("Generating request urn", urn=None)
        request_urn: str = str(ULID())
        request.state.urn = request_urn
        request.state.request_timestamp = start_time
        logger.debug("Generated request urn", urn=request_urn)

        response: Response = await call_next(request)

        end_time: datetime = datetime.now()
        process_time = end_time - start_time
        logger.debug("Updating process time header", urn=request_urn)
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-URN"] = request_urn
        logger.debug("Updated process time header", urn=request_urn)

        return response
