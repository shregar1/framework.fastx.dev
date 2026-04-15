"""Example-domain services."""

from services.example.abstraction import IExampleService
from services.example.create import ExampleCreateService
from services.example.delete import ExampleDeleteService
from services.example.fetch import ExampleFetchService
from services.example.fetch_all import ExampleFetchAllService
from services.example.update import ExampleUpdateService

__all__ = [
    "IExampleService",
    "ExampleCreateService",
    "ExampleFetchAllService",
    "ExampleFetchService",
    "ExampleUpdateService",
    "ExampleDeleteService",
]
