"""Delete Example Controller."""

from http import HTTPStatus
from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from apis.v1.abstraction import IV1APIController
from dependencies.example_service import ExampleServiceDependency
from services.example_service import ExampleService
from dtos.responses.I import IResponseDTO
from constants.api_status import APIStatus


class DeleteExampleController(IV1APIController):
    """Controller for deleting example data."""

    def __init__(self, urn: str | None = None, *args, **kwargs) -> None:
        """Execute __init__ operation.

        Args:
            urn: The urn parameter.
        """
        super().__init__(urn=urn, api_name="delete_example", *args, **kwargs)

    async def delete(
        self,
        request: Request,
        example_id: str,
        service: ExampleService = Depends(ExampleServiceDependency.derive),
    ) -> JSONResponse:
        """DELETE /api/v1/examples/{example_id}."""

        async def _run() -> JSONResponse:
            """Execute _run operation.

            Returns:
                The result of the operation.
            """
            self.urn = request.state.urn
            success = service.delete(example_id)
            if not success:
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
                    responseMessage="Deleted successfully",
                    responseKey="success_deleted",
                    data={},
                ),
                status_code=HTTPStatus.OK,
            )

        return await self.invoke_with_exception_handling(request, _run)
