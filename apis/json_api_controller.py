"""JSON API controller base: shared structured responses and exception handling."""

from __future__ import annotations
from http import HTTPStatus
from typing import Awaitable, Callable, Optional, TypeVar

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from fast_platform.errors import (
    BadInputError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    UnauthorizedError,
    UnexpectedResponseError,
)

from abstractions.controller import IController
from constants.api_status import APIStatus
from dtos.responses.base import BaseResponseDTO
from loguru import logger
from fastmvc_utilities.dictionary import DictionaryUtility

TResponse = TypeVar("TResponse", bound=Response)


class JSONAPIController(IController):
    """Base for API controllers that emit structured JSON.

    Provides:
        - _to_json_response success DTO -> JSONResponse
        - _to_error_json_response exception -> error JSONResponse
        - _handle_controller_exception log + error response
        - invoke_with_exception_handling template wrapper for endpoint bodies
    """

    def __init__(
        self,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: int | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Execute __init__ operation.

        Args:
            urn: The urn parameter.
            user_urn: The user_urn parameter.
            api_name: The api_name parameter.
            user_id: The user_id parameter.
        """
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            *args,
            **kwargs,
        )

    @staticmethod
    def _transaction_urn_from_request(request: Request) -> str:
        """Best-effort URN from request.state.urn for error payloads."""
        try:
            return str(getattr(getattr(request, "state", None), "urn", "") or "")
        except Exception:
            return ""

    def _to_json_response(
        self,
        response_dto: BaseResponseDTO,
        status_code: int,
        dictionary_utility: Optional[DictionaryUtility] = None,
    ) -> JSONResponse:
        """Build a JSONResponse from a BaseResponseDTO."""
        content = (
            dictionary_utility.convert_dict_keys_to_camel_case(
                response_dto.model_dump()
            )
            if dictionary_utility is not None
            else response_dto.model_dump()
        )
        return JSONResponse(content=content, status_code=status_code)

    def _to_error_json_response(
        self,
        err: Exception,
        transaction_urn: str,
        dictionary_utility: Optional[DictionaryUtility] = None,
    ) -> JSONResponse:
        """Convert a known domain error into a standardized JSON error response."""
        known_error_types = (
            BadInputError,
            ConflictError,
            ForbiddenError,
            NotFoundError,
            RateLimitError,
            ServiceUnavailableError,
            UnauthorizedError,
            UnexpectedResponseError,
        )

        if isinstance(err, known_error_types):
            response_dto = BaseResponseDTO(
                transactionUrn=transaction_urn,
                status=APIStatus.FAILED,
                responseMessage=getattr(err, "responseMessage", str(err)),
                responseKey=getattr(err, "responseKey", "error_unknown"),
                data={},
            )
            status_code = getattr(
                err, "httpStatusCode", HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            response_dto = BaseResponseDTO(
                transactionUrn=transaction_urn,
                status=APIStatus.FAILED,
                responseMessage="Internal server error.",
                responseKey="error_internal_server_error",
                data={},
            )
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR

        content = (
            dictionary_utility.convert_dict_keys_to_camel_case(
                response_dto.model_dump()
            )
            if dictionary_utility is not None
            else response_dto.model_dump()
        )
        return JSONResponse(content=content, status_code=status_code)

    def _handle_controller_exception(
        self,
        request: Request,
        err: Exception,
        dictionary_utility: Optional[DictionaryUtility] = None,
    ) -> JSONResponse:
        """Log the exception and return a standardized JSON error response."""
        transaction_urn = self._transaction_urn_from_request(request)
        self.logger.error(
            f"{err.__class__.__name__} unhandled controller exception; "
            f"api_name={self.api_name} urn={transaction_urn}: {err}"
        )
        return self._to_error_json_response(
            err=err,
            transaction_urn=transaction_urn,
            dictionary_utility=dictionary_utility,
        )

    async def invoke_with_exception_handling(
        self,
        request: Request,
        action: Callable[[], Awaitable[TResponse]],
        *,
        dictionary_utility: Optional[DictionaryUtility] = None,
    ) -> Response:
        """Template method: run async endpoint logic and map failures to JSON errors."""
        try:
            return await action()
        except Exception as err:
            return self._handle_controller_exception(request, err, dictionary_utility)


__all__ = ["JSONAPIController"]
