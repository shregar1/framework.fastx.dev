"""Example delete request DTO.

One concrete request model per file; see ``dtos/README.md`` and ``docs/guide/new-api-scaffolding.md``.
"""

from dtos.requests.example.abstraction import IRequestExampleDTO


class ExampleDeleteRequestDTO(IRequestExampleDTO):
    """Example delete request (correlation / reference only)."""

    pass
