"""
Tests for response DTOs.
"""

from constants.api_status import APIStatus
from dtos.responses.base import BaseResponseDTO


class TestBaseResponseDTO:
    """Tests for BaseResponseDTO."""

    def test_success_response(self, test_urn):
        """Test creating success response."""
        dto = BaseResponseDTO(
            transactionUrn=test_urn,
            status=APIStatus.SUCCESS,
            responseMessage="Operation completed",
            responseKey="success_operation",
            data={"result": "value"}
        )
        assert dto.transactionUrn == test_urn
        assert dto.status == APIStatus.SUCCESS
        assert dto.responseMessage == "Operation completed"
        assert dto.responseKey == "success_operation"
        assert dto.data == {"result": "value"}
        assert dto.errors is None

    def test_error_response(self, test_urn):
        """Test creating error response."""
        dto = BaseResponseDTO(
            transactionUrn=test_urn,
            status=APIStatus.FAILED,
            responseMessage="Operation failed",
            responseKey="error_operation",
            data={},
            errors=[{"field": "email", "message": "Invalid format"}]
        )
        assert dto.status == APIStatus.FAILED
        assert dto.errors == [{"field": "email", "message": "Invalid format"}]

    def test_response_with_list_data(self, test_urn):
        """Test response with list data."""
        dto = BaseResponseDTO(
            transactionUrn=test_urn,
            status=APIStatus.SUCCESS,
            responseMessage="Items retrieved",
            responseKey="success_list",
            data=[{"id": 1}, {"id": 2}]
        )
        assert isinstance(dto.data, list)
        assert len(dto.data) == 2

    def test_response_serialization(self, test_urn):
        """Test response serialization to dict."""
        dto = BaseResponseDTO(
            transactionUrn=test_urn,
            status=APIStatus.SUCCESS,
            responseMessage="Test",
            responseKey="test",
            data={"key": "value"}
        )
        result = dto.model_dump()
        assert "transactionUrn" in result
        assert "status" in result
        assert "responseMessage" in result
        assert "responseKey" in result
        assert "data" in result

    def test_response_json_serialization(self, test_urn):
        """Test response JSON serialization."""
        dto = BaseResponseDTO(
            transactionUrn=test_urn,
            status=APIStatus.SUCCESS,
            responseMessage="Test",
            responseKey="test",
            data={"key": "value"}
        )
        json_str = dto.model_dump_json()
        assert "transactionUrn" in json_str
        assert "SUCCESS" in json_str

    def test_optional_data_and_errors(self, test_urn):
        """Test that data and errors are optional."""
        dto = BaseResponseDTO(
            transactionUrn=test_urn,
            status=APIStatus.SUCCESS,
            responseMessage="Test",
            responseKey="test"
        )
        assert dto.data is None
        assert dto.errors is None

    def test_pending_status(self, test_urn):
        """Test pending status response."""
        dto = BaseResponseDTO(
            transactionUrn=test_urn,
            status=APIStatus.PENDING,
            responseMessage="Processing",
            responseKey="pending_operation"
        )
        assert dto.status == APIStatus.PENDING

