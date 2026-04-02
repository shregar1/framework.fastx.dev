"""Tests for service abstractions."""

from __future__ import annotations

from typing import Any, Optional
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from abstractions.service import IService


class _DummyDTO(BaseModel):
    """Minimal request DTO for exercising :meth:`IService.run`."""

    ref: str = "ok"


class ConcreteService(IService):
    """Concrete implementation for testing."""

    def run(self, request_dto: BaseModel) -> dict:
        return {"status": "success", "dto_type": type(request_dto).__name__}


class TestIService:
    """Test class for IService."""

    def test_is_abstract(self):
        """Test IService is abstract."""
        with pytest.raises(TypeError):
            IService()  # pyright: ignore[reportAbstractUsage]

    def test_concrete_can_be_instantiated(self):
        """Test concrete implementation can be instantiated."""
        service = ConcreteService()
        assert isinstance(service, IService)

    def test_init_default_values(self):
        """Test initialization with default values."""
        service = ConcreteService()
        assert service._urn is None
        assert service._user_urn is None
        assert service._api_name is None
        assert service._user_id is None

    def test_init_with_values(self):
        """Test initialization with provided values."""
        service = ConcreteService(
            urn="test-urn",
            user_urn="user-123",
            api_name="api-test",
            user_id="user-456"
        )
        assert service._urn == "test-urn"
        assert service._user_urn == "user-123"
        assert service._api_name == "api-test"
        assert service._user_id == "user-456"

    def test_urn_property_getter(self):
        """Test urn getter."""
        service = ConcreteService(urn="test")
        assert service.urn == "test"

    def test_urn_property_setter(self):
        """Test urn setter."""
        service = ConcreteService()
        service.urn = "new-urn"
        assert service.urn == "new-urn"

    def test_user_urn_property_getter(self):
        """Test user_urn getter."""
        service = ConcreteService(user_urn="user-test")
        assert service.user_urn == "user-test"

    def test_user_urn_property_setter(self):
        """Test user_urn setter."""
        service = ConcreteService()
        service.user_urn = "new-user"
        assert service.user_urn == "new-user"

    def test_api_name_property_getter(self):
        """Test api_name getter."""
        service = ConcreteService(api_name="api-test")
        assert service.api_name == "api-test"

    def test_api_name_property_setter(self):
        """Test api_name setter."""
        service = ConcreteService()
        service.api_name = "new-api"
        assert service.api_name == "new-api"

    def test_user_id_property_getter(self):
        """Test user_id getter."""
        service = ConcreteService(user_id="id-test")
        assert service.user_id == "id-test"

    def test_user_id_property_setter(self):
        """Test user_id setter."""
        service = ConcreteService()
        service.user_id = "new-id"
        assert service.user_id == "new-id"

    def test_logger_property_getter(self):
        """Test logger getter."""
        service = ConcreteService()
        assert service.logger is not None

    def test_logger_property_setter(self):
        """Test logger setter."""
        service = ConcreteService()
        new_logger = MagicMock()
        service.logger = new_logger
        assert service.logger == new_logger

    def test_run_method(self):
        """Test run method."""
        service = ConcreteService()
        result = service.run(_DummyDTO())
        assert result["status"] == "success"
        assert result["dto_type"] == "_DummyDTO"

    def test_run_accepts_subclass_dto(self):
        """``run`` accepts any Pydantic model."""
        service = ConcreteService()
        result = service.run(_DummyDTO(ref="x"))
        assert result["status"] == "success"

    def test_service_context_propagation(self):
        """Test context propagates through service."""
        service = ConcreteService(
            urn="service-urn",
            user_urn="service-user"
        )
        assert service.urn == "service-urn"
        assert service.user_urn == "service-user"

    def test_multiple_services_independent(self):
        """Test multiple service instances are independent."""
        service1 = ConcreteService(urn="urn1", api_name="api1")
        service2 = ConcreteService(urn="urn2", api_name="api2")
        assert service1.urn != service2.urn
        assert service1.api_name != service2.api_name


class TestIServiceEdgeCases:
    """Test edge cases."""

    def test_empty_string_properties(self):
        """Test empty string properties."""
        service = ConcreteService(
            urn="",
            user_urn="",
            api_name="",
            user_id=""
        )
        assert service.urn == ""
        assert service.user_urn == ""

    def test_unicode_properties(self):
        """Test unicode in properties."""
        service = ConcreteService(
            urn="服务-urn",
            api_name="api-测试"
        )
        urn = service.urn
        api = service.api_name
        assert urn is not None and "服务" in urn
        assert api is not None and "测试" in api

    def test_special_characters_in_properties(self):
        """Test special characters."""
        special = "test<>!@#$%^&*()"
        service = ConcreteService(
            urn=special,
            user_urn=special
        )
        assert service.urn == special

    def test_kwargs_forwarding(self):
        """Test kwargs are passed correctly."""
        service = ConcreteService(extra_param="value")
        assert service is not None

    def test_args_forwarding(self):
        """Test args are forwarded."""
        service = ConcreteService("arg1", "arg2")
        assert service is not None


class TestIServiceRunRepeated:
    """``run`` is synchronous; repeated calls stay independent."""

    def test_run_returns_dict(self) -> None:
        service = ConcreteService()
        result = service.run(_DummyDTO())
        assert isinstance(result, dict)

    def test_run_multiple_calls(self) -> None:
        service = ConcreteService()
        dto = _DummyDTO()
        results = [service.run(dto) for _ in range(3)]
        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)
