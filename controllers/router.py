"""Example API router."""

from http import HTTPStatus
from fastapi import APIRouter, Request
from controllers.example_controller import ExampleController
from dtos.responses.base import BaseResponseDTO

router = APIRouter(prefix="/example", tags=["Example"])
controller = ExampleController()


@router.post("", response_model=BaseResponseDTO, status_code=HTTPStatus.CREATED)
async def create_example(request: Request, payload: dict) -> BaseResponseDTO:
    """Create an example via class-based controller."""
    # Context injected from RequestContextMiddleware by starlette request state
    urn = getattr(request.state, "urn", "urn:req:default")
    user_urn = getattr(request.state, "user_urn", "")
    user_id = getattr(request.state, "user_id", "")

    return await controller.handle_create_example(
        urn=urn,
        user_urn=user_urn,
        payload=payload,
        headers=dict(request.headers),
        api_name="create_example",
        user_id=str(user_id),
    )
