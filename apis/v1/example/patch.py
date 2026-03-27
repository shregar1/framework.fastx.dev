"""Patch Example Controller."""

from http import HTTPStatus
from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from apis.v1.abstraction import IV1APIController
from dependencies.example_service import ExampleServiceDependency
from services.example_service import ExampleService
from dtos.requests.example.example_request import ExampleUpdateRequestDTO
from dtos.responses.I import IResponseDTO
from constants.api_status import APIStatus


class PatchExampleController(IV1APIController):
    """Controller for updating example data."""

    def __init__(self, urn: str | None = None, *args, **kwargs) -> None:
        """Execute __init__ operation.

        Args:
            urn: The urn parameter.
        """
        super().__init__(urn=urn, api_name="patch_example", *args, **kwargs)

    async def patch(
        self,
        request: Request,
        example_id: str,
        payload: ExampleUpdateRequestDTO,
        service: ExampleService = Depends(ExampleServiceDependency.derive),
    ) -> JSONResponse:
        """PATCH /api/v1/examples/{example_id}."""

        async def _run() -> JSONResponse:
            """Execute _run operation.

            Returns:
                The result of the operation.
            """
            self.urn = request.state.urn
            item = service.update(example_id, payload)
            if not item:
                from fast_platform.errors import NotFoundError

                raise NotFoundError(
                    responseMessage="Item not found",
                    responseKey="error_not_found",
                    httpStatusCode=HTTPStatus.NOT_FOUND,
                )

            return self._to_json_response(
                response_dto=IResponseDTO(
                    transactionUrn=self.urn,
                    status=APIStatus.SUCCESS,
                    responseMessage="Updated successfully",
                    responseKey="success_updated",
                    data=item,
                ),
                status_code=HTTPStatus.OK,
            )

        return await self.invoke_with_exception_handling(request, _run)
