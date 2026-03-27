"""HTTP DTO contracts for the application layer.

These abstract Is anchor :mod:`dtos` request and response models to the
:mod:`abstractions` package so layered DTOs form an explicit inheritance
chain (e.g. ``IRequestUserV1DTO`` → … → :class:`IRequestDTO`).
"""

from abc import ABC


class AbstractRequestDTO(ABC):
    """Root contract for all HTTP request DTOs.

    Concrete request models combine this with
    :class:`dtos.I.EnhancedIModel` via :class:`dtos.requests.abstraction.IRequestDTO`
    and nested ``dtos.requests.*.abstraction`` Is.
    """


class AbstractResponseDTO(ABC):
    """Root contract for all HTTP response envelope DTOs.

    Concrete response models combine this with :class:`dtos.responses.I.IResponseDTO`
    via :class:`dtos.responses.abstraction.IResponseDTO` when applicable.
    """
