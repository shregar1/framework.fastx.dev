"""PUT — full replacement-style body using :class:`ExampleUpdateRequestDTO`."""

from __future__ import annotations

from typing import Any

from dtos.requests.example.update import ExampleUpdateRequestDTO

from factories.apis.v1.example.common import new_reference_number


class ExamplePutRequestFactory:
    """Typical PUT body: send full resource representation."""

    DEFAULT_NAME = "put-replaced-name"
    DEFAULT_DESCRIPTION = "put-replaced-description"

    @classmethod
    def build(cls, **overrides: Any) -> dict[str, Any]:
        base: dict[str, Any] = {
            "reference_number": new_reference_number(),
            "name": cls.DEFAULT_NAME,
            "description": cls.DEFAULT_DESCRIPTION,
        }
        return {**base, **overrides}

    @classmethod
    def build_dto(cls, **overrides: Any) -> ExampleUpdateRequestDTO:
        return ExampleUpdateRequestDTO(**cls.build(**overrides))
