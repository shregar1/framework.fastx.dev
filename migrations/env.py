"""
Alembic Environment Configuration for FastMVC.

This module configures Alembic to work with FastMVC's database
configuration and SQLAlchemy models. It supports both online
(connected to database) and offline (SQL script generation) modes.

Configuration:
    Database URL is loaded from environment variables via start_utils.
    All models are auto-discovered from the models package.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models and configuration
from models import Base
from start_utils import db_config

# Alembic Config object
config = context.config

# Setup logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set SQLAlchemy metadata for autogenerate
target_metadata = Base.metadata


def get_database_url() -> str:
    """
    Construct database URL from environment configuration.
    
    Returns:
        str: PostgreSQL connection URL.
    """
    return (
        f"postgresql://{db_config.db_user}:{db_config.db_password}"
        f"@{db_config.db_host}:{db_config.db_port}/{db_config.db_name}"
    )


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate
    a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

