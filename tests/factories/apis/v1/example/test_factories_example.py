"""Example tests for top-level ``factories`` package (CRUD-style helpers)."""

import uuid

import pytest

from dtos.requests.apis.v1.user.fetch import FetchUserRequestDTO
from dtos.requests.example import (
    ExampleCreateRequestDTO,
    ExampleDeleteRequestDTO,
    ExampleUpdateRequestDTO,
)
from factories.apis.v1.example.create import ExampleCreateRequestFactory
from factories.apis.v1.example.delete import ExampleDeleteRequestFactory
from factories.apis.v1.example.fetch import ExampleFetchRequestFactory
from factories.apis.v1.example.patch import ExamplePatchRequestFactory
from factories.apis.v1.example.put import ExamplePutRequestFactory
from factories.apis.v1.example.update import ExampleUpdateRequestFactory


@pytest.mark.unit
def test_example_fetch_request_factory() -> None:
    payload = ExampleFetchRequestFactory.build()
    uuid.UUID(payload["reference_number"])
    dto = ExampleFetchRequestFactory.build_dto()
    assert isinstance(dto, FetchUserRequestDTO)


@pytest.mark.unit
def test_example_create_request_factory() -> None:
    dto = ExampleCreateRequestFactory.build_dto(name="New")
    assert isinstance(dto, ExampleCreateRequestDTO)
    assert dto.name == "New"


@pytest.mark.unit
def test_example_update_request_factory() -> None:
    dto = ExampleUpdateRequestFactory.build_dto(name="U", description="D")
    assert isinstance(dto, ExampleUpdateRequestDTO)
    assert dto.name == "U"


@pytest.mark.unit
def test_example_patch_request_factory() -> None:
    dto = ExamplePatchRequestFactory.build_dto()
    assert isinstance(dto, ExampleUpdateRequestDTO)
    assert dto.name == ExamplePatchRequestFactory.DEFAULT_NAME


@pytest.mark.unit
def test_example_put_request_factory() -> None:
    dto = ExamplePutRequestFactory.build_dto()
    assert isinstance(dto, ExampleUpdateRequestDTO)
    assert dto.description == ExamplePutRequestFactory.DEFAULT_DESCRIPTION


@pytest.mark.unit
def test_example_delete_request_factory() -> None:
    dto = ExampleDeleteRequestFactory.build_dto()
    assert isinstance(dto, ExampleDeleteRequestDTO)
    uuid.UUID(str(dto.reference_number))


def test_fetch_example_request_payload_fixture(fetch_example_request_payload: dict) -> None:
    assert "reference_number" in fetch_example_request_payload
    dto = FetchUserRequestDTO(**fetch_example_request_payload)
    assert dto.name == ExampleFetchRequestFactory.DEFAULT_NAME
