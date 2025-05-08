"""
alembic/env.py

Alembic migration environment configuration for OptIn Manager database.

This module configures the Alembic migration environment for the OptIn Manager
database. It handles both online and offline migration modes, supports multiple
database backends (SQLite for development, PostgreSQL for production), and ensures
all models are properly tracked for schema migrations.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models and set target_metadata for autogenerate support
# This ensures Alembic can detect model changes and generate appropriate migrations
# All models must be imported here to be included in migrations
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from app.core.database import Base

# Import all models explicitly to ensure they're registered with SQLAlchemy
# As noted in the memories, the models have been renamed and restructured
# (e.g., user.py → contact.py) to better reflect their purpose
import app.models.auth_user     # Authenticated users with roles (Admin/Support)
import app.models.optin         # Opt-in programs (formerly Campaign/Product)
import app.models.customization # UI branding and communication provider settings
import app.models.message       # Message history with audit trail for compliance
import app.models.message_template # Templates for consistent communications
import app.models.contact       # Non-authorized users who verify with a code
import app.models.verification_code # Security codes for contact verification
import app.models.consent       # Consent records for regulatory compliance

# Set the target metadata for Alembic to use in migration generation
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    
    This mode is particularly useful for generating migration scripts
    that can be reviewed before execution or run in environments where
    direct database access is restricted.
    
    As noted in the memories, the system supports SQLite for development
    and testing, with configurations managed via environment variables.
    This function handles the appropriate configuration for different
    database backends.
    """
    # Get the database URL from environment or use the default
    # This ensures compatibility with the database configuration in core/database.py
    import os
    url = os.getenv("DATABASE_URL", "sqlite:///./optin_manager.db")
    
    # Override the URL in the config
    config.set_main_option("sqlalchemy.url", url)
    
    # Detect database type and configure accordingly
    # Different databases require different migration strategies
    schema = None
    is_sqlite = url.startswith("sqlite")
    
    # PostgreSQL supports schemas for better organization
    # SQLite does not support schemas, so we only configure this for PostgreSQL
    if url.startswith("postgresql"):
        schema = "optin_manager"
        
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=schema,
        include_schemas=True if schema else False,
        default_schema_name=schema if schema else None,
        render_as_batch=is_sqlite,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    
    This is the standard mode for applying migrations directly to a
    database. It handles connection pooling and transaction management
    to ensure migrations are applied atomically.
    
    As noted in the memories, the system supports SQLite for development
    and testing. This function detects the database type and applies
    appropriate configuration options, such as using batch operations
    for SQLite which has limited ALTER TABLE support.
    """
    # Get the database URL from environment or use the default
    import os
    db_url = os.getenv("DATABASE_URL", "sqlite:///./optin_manager.db")
    
    # Override the URL in the config
    config.set_main_option("sqlalchemy.url", db_url)
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Detect SQLite and configure accordingly
        is_sqlite = db_url.startswith("sqlite")
        
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # SQLite doesn't support certain operations
            render_as_batch=is_sqlite,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
