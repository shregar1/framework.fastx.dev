"""
User Controllers Router Module.

This module serves as the entry point for all user-related endpoints.
It registers routes for user authentication operations including
login, registration, and logout.

Routes:
    POST /user/login    - User authentication
    POST /user/register - New user registration
    POST /user/logout   - User session termination

Usage:
    >>> from controllers.user import router
    >>> app.include_router(router)
"""

from fastapi import APIRouter

from constants.api_lk import APILK
from controllers.user.login import UserLoginController
from controllers.user.logout import UserLogoutController
from controllers.user.register import UserRegistrationController
from start_utils import logger

router = APIRouter(prefix="/user")
"""User router with /user prefix. Handles authentication operations."""

# Register login route
logger.debug(f"Registering {UserLoginController.__name__} route.")
router.add_api_route(
    path="/login",
    endpoint=UserLoginController().post,
    methods=["POST"],
    name=APILK.LOGIN,
)
logger.debug(f"Registered {UserLoginController.__name__} route.")

# Register registration route
logger.debug(f"Registering {UserRegistrationController.__name__} route.")
router.add_api_route(
    path="/register",
    endpoint=UserRegistrationController().post,
    methods=["POST"],
    name=APILK.REGISTRATION,
)
logger.debug(f"Registered {UserRegistrationController.__name__} route.")

# Register logout route
logger.debug(f"Registering {UserLogoutController.__name__} route.")
router.add_api_route(
    path="/logout",
    endpoint=UserLogoutController().post,
    methods=["POST"],
    name=APILK.LOGOUT,
)
logger.debug(f"Registered {UserLogoutController.__name__} route.")
