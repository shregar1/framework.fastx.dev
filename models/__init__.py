"""
Models Package.

This package contains SQLAlchemy ORM models that define the database schema.
All models inherit from the Base declarative base defined here.

Usage:
    >>> from models import Base
    >>> from models.user import User
    >>>
    >>> # Create all tables
    >>> Base.metadata.create_all(engine)
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
"""
SQLAlchemy declarative base class.

All ORM models must inherit from this base to be registered
with the SQLAlchemy metadata and participate in table creation.

Example:
    >>> class MyModel(Base):
    ...     __tablename__ = "my_table"
    ...     id = Column(Integer, primary_key=True)
"""

from models.product import Product
