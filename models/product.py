"""
Product Database Model.

This module defines the SQLAlchemy ORM model for Product entities.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text

from models import Base


class Product(Base):
    """
    Product database model.

    Represents a product entity in the database.

    Attributes:
        id (int): Primary key.
        urn (str): Unique resource name (ULID).
        name (str): Product name.
        description (str): Optional description.
        is_active (bool): Whether the product is active.
        is_deleted (bool): Soft delete flag.
        created_by (int): ID of user who created this record.
        created_on (datetime): Creation timestamp.
        updated_by (int): ID of user who last updated this record.
        updated_on (datetime): Last update timestamp.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    urn = Column(String(26), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_by = Column(Integer, nullable=False)
    created_on = Column(DateTime, default=datetime.now, nullable=False)
    updated_by = Column(Integer, nullable=True)
    updated_on = Column(DateTime, nullable=True, onupdate=datetime.now)

    __table_args__ = (
        Index("ix_product_name", "name"),
        Index("ix_product_active", "is_active", "is_deleted"),
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "urn": self.urn,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_on": str(self.created_on) if self.created_on else None,
            "updated_on": str(self.updated_on) if self.updated_on else None,
        }
