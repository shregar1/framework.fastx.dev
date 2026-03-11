"""
User Logout Request DTO Module.

This module defines the request payload structure for user logout.
The logout endpoint requires minimal payload - just the reference number
for request tracking.

Endpoint: POST /user/logout

Request Body:
    {
        "reference_number": "550e8400-e29b-41d4-a716-446655440000"
    }
"""

from dtos.requests.abstraction import IRequestDTO


class UserLogoutRequestDTO(IRequestDTO):
    """
    Request DTO for user logout/session termination.

    This DTO is minimal as logout requires only the standard
    reference number field for request tracking. The actual
    user identification comes from the JWT token in the
    Authorization header.

    Attributes:
        reference_number (str): Client-provided UUID for request tracking.
            Inherited from IRequestDTO.

    Example:
        >>> from dtos.requests.user.logout import UserLogoutRequestDTO
        >>>
        >>> logout_request = UserLogoutRequestDTO(
        ...     reference_number="550e8400-e29b-41d4-a716-446655440000"
        ... )

    Note:
        The user's identity is determined from the JWT token
        in the Authorization header, not from the request body.
        The token is validated by the authentication middleware.
    """

    pass
