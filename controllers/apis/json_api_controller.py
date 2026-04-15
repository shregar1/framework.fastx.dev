"""JSON API Controller base with structured error handling.

Inherits the common property surface (urn, user_urn, api_name, user_id,
logger, dictionary_utility, jwt_utility) and :meth:`handle_exception`
from the app-level :class:`abstractions.controller.IController`.
"""

from __future__ import annotations

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi.responses import JSONResponse

from constants.api_status import APIStatus
from abstractions.controller import IController
from dtos.responses.base import BaseResponseDTO


class JSONAPIController(IController):
    """Base controller that wraps handler execution in a JSON error envelope.

    Sub-classes override ``post`` / ``get`` etc. and can call
    :meth:`invoke_with_exception_handling` for uniform error wrapping,
    or :meth:`handle_exception` (from the root abstraction) for
    structured error-to-envelope translation.
    """

    def __init__(
        self,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: int | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            *args,
            **kwargs,
        )
        self._dictionary_utility = None
        self._jwt_utility = None

    async def invoke_with_exception_handling(
        self,
        request: Any,
        handler: Callable,
    ) -> JSONResponse:
        """Run *handler* and catch any exception into a JSON error envelope."""
        try:
            return await handler()
        except Exception as err:
            urn = getattr(request.state, "urn", "") if hasattr(request, "state") else ""
            self._logger.error("Unhandled error in %s: %s", self.__class__.__name__, err)
            response_dto = BaseResponseDTO(
                transactionUrn=urn,
                status=APIStatus.FAILED,
                responseMessage=str(err),
                responseKey="error_internal_server_error",
                data={},
            )
            return JSONResponse(
                content=response_dto.model_dump(),
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def build_json_response(
        self,
        response_dto: "BaseResponseDTO",
        status_code: int = HTTPStatus.OK,
    ) -> JSONResponse:
        """Convert a BaseResponseDTO to a JSONResponse with camelCase keys."""
        payload = response_dto.model_dump()
        if self.dictionary_utility is not None:
            payload = self.dictionary_utility.convert_dict_keys_to_camel_case(payload)
        return JSONResponse(content=payload, status_code=status_code)


__all__ = ["JSONAPIController"]
