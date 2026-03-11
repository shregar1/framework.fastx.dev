"""
Tests for Product CRUD Service.
"""

from unittest.mock import MagicMock

import pytest

from dtos.requests.product.create import ProductCreateRequestDTO
from dtos.requests.product.update import ProductUpdateRequestDTO
from errors.not_found_error import NotFoundError
from models.product import Product
from services.product.abstraction import IProductService
from services.product.crud import ProductCRUDService


class TestProductCRUDServiceInit:
    """Tests for ProductCRUDService initialization."""

    def test_initialization(self):
        """Test ProductCRUDService can be initialized."""
        mock_repo = MagicMock()
        service = ProductCRUDService(
            urn="test-urn",
            repository=mock_repo
        )
        assert service.urn == "test-urn"
        assert service.repository == mock_repo

    def test_initialization_with_all_params(self):
        """Test ProductCRUDService with all parameters."""
        mock_repo = MagicMock()
        service = ProductCRUDService(
            urn="test-urn",
            user_urn="user-urn",
            api_name="test_api",
            user_id=123,
            repository=mock_repo
        )
        assert service.urn == "test-urn"
        assert service.user_urn == "user-urn"
        assert service.api_name == "test_api"
        assert service.user_id == 123

    def test_has_create_method(self):
        """Test service has create method."""
        service = ProductCRUDService(urn="test-urn")
        assert hasattr(service, 'create')

    def test_has_get_by_id_method(self):
        """Test service has get_by_id method."""
        service = ProductCRUDService(urn="test-urn")
        assert hasattr(service, 'get_by_id')

    def test_has_update_method(self):
        """Test service has update method."""
        service = ProductCRUDService(urn="test-urn")
        assert hasattr(service, 'update')

    def test_has_delete_method(self):
        """Test service has delete method."""
        service = ProductCRUDService(urn="test-urn")
        assert hasattr(service, 'delete')

    def test_has_run_method(self):
        """Test service has run method."""
        service = ProductCRUDService(urn="test-urn")
        assert hasattr(service, 'run')


class TestProductCRUDServiceCreate:
    """Tests for ProductCRUDService create operation."""

    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        repo = MagicMock()
        mock_product = MagicMock(spec=Product)
        mock_product.id = 1
        mock_product.to_dict.return_value = {"id": 1, "name": "Test"}
        repo.create_record.return_value = mock_product
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        """Create ProductCRUDService instance."""
        return ProductCRUDService(
            urn="test-urn",
            user_id=1,
            repository=mock_repo
        )

    @pytest.mark.asyncio
    async def test_create_product(self, service, mock_repo):
        """Test creating a product."""
        request_dto = ProductCreateRequestDTO(
            reference_number="550e8400-e29b-41d4-a716-446655440000",
            name="Test Product",
            description="A test product"
        )

        result = await service.create(request_dto)
        mock_repo.create_record.assert_called_once()
        assert result.status == "SUCCESS"


class TestProductCRUDServiceGet:
    """Tests for ProductCRUDService get operation."""

    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        repo = MagicMock()
        mock_product = MagicMock(spec=Product)
        mock_product.id = 1
        mock_product.to_dict.return_value = {"id": 1, "name": "Test"}
        repo.retrieve_record_by_id.return_value = mock_product
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        """Create ProductCRUDService instance."""
        return ProductCRUDService(
            urn="test-urn",
            repository=mock_repo
        )

    @pytest.mark.asyncio
    async def test_get_product_by_id(self, service, mock_repo):
        """Test getting a product by ID."""
        result = await service.get_by_id(1)
        mock_repo.retrieve_record_by_id.assert_called()
        assert result.status == "SUCCESS"

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, service, mock_repo):
        """Test getting non-existent product raises error."""
        mock_repo.retrieve_record_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.get_by_id(999)


class TestProductCRUDServiceUpdate:
    """Tests for ProductCRUDService update operation."""

    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        repo = MagicMock()
        mock_product = MagicMock(spec=Product)
        mock_product.id = 1
        mock_product.name = "Old Name"
        mock_product.description = "Old Desc"
        mock_product.is_active = True
        mock_product.to_dict.return_value = {"id": 1, "name": "Updated"}
        repo.retrieve_record_by_id.return_value = mock_product
        repo.update_record.return_value = mock_product
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        """Create ProductCRUDService instance."""
        return ProductCRUDService(
            urn="test-urn",
            user_id=1,
            repository=mock_repo
        )

    @pytest.mark.asyncio
    async def test_update_product(self, service, mock_repo):
        """Test updating a product."""
        request_dto = ProductUpdateRequestDTO(
            reference_number="550e8400-e29b-41d4-a716-446655440000",
            name="New Name",
            description="Updated description"
        )

        result = await service.update(1, request_dto)
        mock_repo.retrieve_record_by_id.assert_called()
        mock_repo.update_record.assert_called()
        assert result.status == "SUCCESS"


class TestProductCRUDServiceDelete:
    """Tests for ProductCRUDService delete operation."""

    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        repo = MagicMock()
        repo.delete_record.return_value = True
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        """Create ProductCRUDService instance."""
        return ProductCRUDService(
            urn="test-urn",
            user_id=1,
            repository=mock_repo
        )

    @pytest.mark.asyncio
    async def test_delete_product(self, service, mock_repo):
        """Test deleting a product."""
        result = await service.delete(1)
        mock_repo.delete_record.assert_called_with(1, 1)
        assert result.status == "SUCCESS"

    @pytest.mark.asyncio
    async def test_delete_product_not_found(self, service, mock_repo):
        """Test deleting non-existent product raises error."""
        mock_repo.delete_record.return_value = False

        with pytest.raises(NotFoundError):
            await service.delete(999)


class TestProductCRUDServiceList:
    """Tests for ProductCRUDService list operation."""

    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        repo = MagicMock()
        mock_products = [
            MagicMock(spec=Product, id=1),
            MagicMock(spec=Product, id=2),
        ]
        for p in mock_products:
            p.to_dict.return_value = {"id": p.id}
        repo.retrieve_all_records.return_value = mock_products
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        """Create ProductCRUDService instance."""
        return ProductCRUDService(
            urn="test-urn",
            repository=mock_repo
        )

    @pytest.mark.asyncio
    async def test_list_products(self, service, mock_repo):
        """Test listing products."""
        result = await service.get_all()
        mock_repo.retrieve_all_records.assert_called()
        assert result.status == "SUCCESS"


class TestIProductService:
    """Tests for IProductService abstraction."""

    def test_has_properties(self):
        """Test IProductService has expected properties."""
        assert hasattr(IProductService, 'urn')
