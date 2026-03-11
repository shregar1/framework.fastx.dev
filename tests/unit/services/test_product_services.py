"""
Tests for Product services.
"""


from services.product.abstraction import IProductService


class ConcreteProductService(IProductService):
    """Concrete implementation for testing."""

    async def run(self, request_dto=None):
        """Implement abstract run method."""
        return {}


class TestIProductService:
    """Tests for IProductService base class."""

    def test_initialization(self):
        """Test service initialization."""
        service = ConcreteProductService(
            urn="test-urn",
            user_urn="user-urn",
            api_name="test-api"
        )
        assert service.urn == "test-urn"
        assert service._user_urn == "user-urn"
        assert service._api_name == "test-api"

    def test_urn_setter(self):
        """Test urn property setter."""
        service = ConcreteProductService()
        service.urn = "new-urn"
        assert service.urn == "new-urn"

    def test_logger_exists(self):
        """Test logger is bound."""
        service = ConcreteProductService(urn="test")
        assert service.logger is not None


class TestProductCRUDService:
    """Tests for ProductCRUDService."""

    def test_import(self):
        """Test ProductCRUDService can be imported."""
        from services.product.crud import ProductCRUDService
        assert ProductCRUDService is not None

    def test_has_create_method(self):
        """Test service has create method."""
        from services.product.crud import ProductCRUDService
        assert hasattr(ProductCRUDService, 'create')

    def test_has_get_by_id_method(self):
        """Test service has get_by_id method."""
        from services.product.crud import ProductCRUDService
        assert hasattr(ProductCRUDService, 'get_by_id')

    def test_has_get_all_method(self):
        """Test service has get_all method."""
        from services.product.crud import ProductCRUDService
        assert hasattr(ProductCRUDService, 'get_all')

    def test_has_update_method(self):
        """Test service has update method."""
        from services.product.crud import ProductCRUDService
        assert hasattr(ProductCRUDService, 'update')

    def test_has_delete_method(self):
        """Test service has delete method."""
        from services.product.crud import ProductCRUDService
        assert hasattr(ProductCRUDService, 'delete')
