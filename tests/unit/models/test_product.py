"""
Tests for Product model.
"""

from datetime import datetime

from models.product import Product


class TestProductModel:
    """Test cases for Product model."""

    def test_create_product(self):
        """Test Product instance creation."""
        product = Product(
            urn="01ABC123DEF456GHI789JKL0",
            name="Test Product",
            description="A test product",
            is_active=True,
            is_deleted=False,
            created_by=1,
            created_on=datetime.now(),
        )

        assert product.name == "Test Product"
        assert product.is_active is True
        assert product.is_deleted is False

    def test_product_to_dict(self):
        """Test Product.to_dict() method."""
        product = Product(
            id=1,
            urn="01ABC123DEF456GHI789JKL0",
            name="Test Product",
            description="Description",
            is_active=True,
            created_on=datetime(2024, 1, 1, 12, 0, 0),
        )

        result = product.to_dict()

        assert result["id"] == 1
        assert result["urn"] == "01ABC123DEF456GHI789JKL0"
        assert result["name"] == "Test Product"
        assert result["description"] == "Description"
        assert result["is_active"] is True

    def test_product_repr(self):
        """Test Product.__repr__() method."""
        product = Product(id=1, name="Test")

        assert "<Product(id=1, name=Test)>" in repr(product)
