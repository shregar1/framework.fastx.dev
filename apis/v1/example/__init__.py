"""V1 API Examples Router."""

from fastapi import APIRouter
from apis.v1.example.get import GetExampleController
from apis.v1.example.post import PostExampleController
from apis.v1.example.patch import PatchExampleController
from apis.v1.example.delete import DeleteExampleController

router = APIRouter(prefix="/examples")

# Instantiate controllers
get_controller = GetExampleController()
post_controller = PostExampleController()
patch_controller = PatchExampleController()
delete_controller = DeleteExampleController()

router.add_api_route(
    path="",
    endpoint=get_controller.get,
    methods=["GET"],
    name="example_list",
)

router.add_api_route(
    path="/{example_id}",
    endpoint=get_controller.get,
    methods=["GET"],
    name="example_detail",
)

router.add_api_route(
    path="",
    endpoint=post_controller.post,
    methods=["POST"],
    name="example_create",
)

router.add_api_route(
    path="/{example_id}",
    endpoint=patch_controller.patch,
    methods=["PATCH"],
    name="example_update",
)

router.add_api_route(
    path="/{example_id}",
    endpoint=delete_controller.delete,
    methods=["DELETE"],
    name="example_delete",
)

__all__ = ["router"]
