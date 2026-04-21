"""User Registration Service."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from constants.api_status import APIStatus
from constants.response_keys import ResponseKey
from dtos.requests.user.registration import UserRegistrationRequestDTO
from dtos.responses.base import BaseResponseDTO
from fast_platform.errors import ConflictError
from services.user.abstraction import IUserService
from utilities.security import hash_password


class UserRegistrationService(IUserService):
    """Creates a new user account.

    Validates uniqueness, hashes password, persists user, and returns
    success response DTO.
    """

    def __init__(
        self,
        user_repository: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.user_repository = user_repository

    async def run(self, request_dto: UserRegistrationRequestDTO) -> BaseResponseDTO:
        """Register a new user."""
        existing = self.user_repository.retrieve_record_by_email(
            request_dto.email, is_deleted=False
        )
        if existing:
            raise ConflictError(
                responseMessage="An account with this email already exists.",
                responseKey=ResponseKey.ERROR_DUPLICATE_EMAIL,
            )

        hashed = hash_password(request_dto.password)
        user = self.user_repository.create_record({
            "email": request_dto.email,
            "password": hashed,
            "urn": f"urn:user:{uuid4()}",
            "user_type_id": 1,
        })
        session = self.user_repository.session
        session.commit()
        session.refresh(user)

        user_id = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)

        return BaseResponseDTO(
            transactionUrn=self.urn or "",
            status=APIStatus.SUCCESS,
            responseMessage="Registration successful.",
            responseKey=ResponseKey.SUCCESS_REGISTRATION,
            data={
                "user_id": user_id,
                "user_email": request_dto.email,
            },
        )


__all__ = ["UserRegistrationService"]
