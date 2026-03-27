"""DELETE — correlation payload using :class:`ExampleDeleteRequestDTO`."""

from __future__ import annotations

from typing import Any

from dtos.requests.example.delete import ExampleDeleteRequestDTO

from factories.apis.v1.example.common import new_reference_number


class ExampleDeleteRequestFactory:
    """Body for delete requests that only carry ``reference_number`` (plus optional overrides)."""

    @classmethod
    def build(cls, **overrides: Any) -> dict[str, Any]:
        base: dict[str, Any] = {"reference_number": new_reference_number()}
        return {**base, **overrides}

    @classmethod
    def build_dto(cls, **overrides: Any) -> ExampleDeleteRequestDTO:
        return ExampleDeleteRequestDTO(**cls.build(**overrides))
