"""Post Example Controller."""

from http import HTTPStatus
from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from apis.v1.abstraction import IV1APIController
from dependencies.example_service import ExampleServiceDependency
from services.example_service import ExampleService
from dtos.requests.example.example_request import ExampleCreateRequestDTO
from dtos.responses.I import IResponseDTO
from constants.api_status import APIStatus


class PostExampleController(IV1APIController):
    """Controller for creating example data."""

    def __init__(self, urn: str | None = None, *args, **kwargs) -> None:
        """Execute __init__ operation.

        Args:
            urn: The urn parameter.
        """
        super().__init__(urn=urn, api_name="post_example", *args, **kwargs)

    async def post(
        self,
        request: Request,
        payload: ExampleCreateRequestDTO,
        service: ExampleService = Depends(ExampleServiceDependency.derive),
    ) -> JSONResponse:
        """POST /api/v1/examples."""

        async def _run() -> JSONResponse:
            """Execute _run operation.

            Returns:
                The result of the operation.
            """
            self.urn = request.state.urn
            result = service.run(payload)

            return self._to_json_response(
                response_dto=IResponseDTO(
                    transactionUrn=self.urn,
                    status=APIStatus.SUCCESS,
                    responseMessage=result["message"],
                    responseKey="success_created",
                    data=result["item"],
                ),
                status_code=HTTPStatus.CREATED,
            )

        return await self.invoke_with_exception_handling(request, _run)
