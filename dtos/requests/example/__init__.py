"""Example-scoped request DTOs (one concrete class per module)."""

from dtos.requests.example.create import ExampleCreateRequestDTO
from dtos.requests.example.delete import ExampleDeleteRequestDTO
from dtos.requests.example.update import ExampleUpdateRequestDTO

__all__ = [
    "ExampleCreateRequestDTO",
    "ExampleDeleteRequestDTO",
    "ExampleUpdateRequestDTO",
]
