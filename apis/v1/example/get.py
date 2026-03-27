"""Get Example Controller."""

from http import HTTPStatus
from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from apis.v1.abstraction import IV1APIController
from dependencies.example_service import ExampleServiceDependency
from services.example_service import ExampleService
from dtos.responses.base import BaseResponseDTO
from constants.api_status import APIStatus


class GetExampleController(IV1APIController):
    """Controller for retrieving example data."""

    def __init__(self, urn: str | None = None, *args, **kwargs) -> None:
        """Execute __init__ operation.

        Args:
            urn: The urn parameter.
        """
        super().__init__(urn=urn, api_name="get_example", *args, **kwargs)

    async def get(
        self,
        request: Request,
        example_id: str | None = None,
        service: ExampleService = Depends(ExampleServiceDependency.derive),
    ) -> JSONResponse:
        """GET /api/v1/examples[/id]."""

        async def _run() -> JSONResponse:
            """Execute _run operation.

            Returns:
                The result of the operation.
            """
            self.urn = request.state.urn

            if example_id:
                item = service.get_by_id(example_id)
                if not item:
                    # In Kiv.ai, we would raise NotFoundError here
                    # For this example, we return standardized response or could raise the error
                    from fast_platform.errors import NotFoundError

                    raise NotFoundError(
                        responseMessage="Item not found",
                        responseKey="error_not_found",
                        httpStatusCode=HTTPStatus.NOT_FOUND,
                    )
                data = {"item": item}
                msg = "Item retrieved successfully"
            else:
                items = service.get_all()
                data = {"items": items}
                msg = "Data retrieved successfully"

            return self._to_json_response(
                response_dto=BaseResponseDTO(
                    transactionUrn=self.urn,
                    status=APIStatus.SUCCESS,
                    responseMessage=msg,
                    responseKey="success_retrieved",
                    data=data,
                ),
                status_code=HTTPStatus.OK,
            )

        return await self.invoke_with_exception_handling(request, _run)
