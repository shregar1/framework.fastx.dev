"""Generic update body — :class:`ExampleUpdateRequestDTO` (use :mod:`patch` / :mod:`put` for presets)."""

from __future__ import annotations

from typing import Any

from dtos.requests.example.update import ExampleUpdateRequestDTO

from factories.apis.v1.example.common import new_reference_number


class ExampleUpdateRequestFactory:
    """Build payloads for updating an example resource (PUT/PATCH) with explicit fields."""

    @classmethod
    def build(cls, **overrides: Any) -> dict[str, Any]:
        base: dict[str, Any] = {"reference_number": new_reference_number()}
        return {**base, **overrides}

    @classmethod
    def build_dto(cls, **overrides: Any) -> ExampleUpdateRequestDTO:
        return ExampleUpdateRequestDTO(**cls.build(**overrides))
